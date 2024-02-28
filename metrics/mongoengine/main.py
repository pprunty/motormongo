import os

from fastapi import FastAPI, HTTPException
from mongoengine import Document, StringField, BinaryField, connect
from pydantic import BaseModel, Field
import re
import bcrypt

# Connect to MongoDB
connect(db=os.getenv("MONGODB_URL"), host=os.getenv("MONGODB_DB"), alias="default")


def hash_password(password: str) -> bytes:
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


class User(Document):
    username = StringField(required=True, min_length=3, max_length=50, help_text="The username for the user")
    email = StringField(required=True, regex=r'^\S+@\S+\.\S+$',
                        help_text="The email for the user")  # Simple email regex
    password = BinaryField(required=True, help_text="The hashed password for the user")

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    meta = {
        'collection': 'users',
        'indexes': [
            'username',
            'email',
            # Add any other indexes here
        ],
        #todo: add created_at, updated_at timestamps sometime after
        # Note: mongoengine does not automatically handle timestamp fields like motormongo, so you might need to manage them manually.
    }


class UserModelRequest(BaseModel):
    username: str = Field(example="johndoe")
    email: str = Field(example="johndoe@coldmail.com")
    password: str = Field(example="password123")


app = FastAPI()


@app.post("/users/", status_code=201)
def create_user(user: UserModelRequest):
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password=hashed_password).save()
    return new_user.to_mongo().to_dict()  # Convert the user document to a dictionary


@app.post("/user/auth", status_code=200)
def is_authenticated(username: str, password: str):
    user = User.objects(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "You are authenticated! You can see this!"


@app.get("/users")
def get_users():
    users = User.objects.all()
    return [user.to_mongo().to_dict() for user in users]  # Convert each user document to a dictionary


@app.get("/users/{user_id}")
def get_user(user_id: str):
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_mongo().to_dict()


@app.put("/users/{user_id}", status_code=200)
def update_user(user_id: str, user_data: UserModelRequest):
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.update(**user_data.dict(exclude_unset=True))
    return user.reload().to_mongo().to_dict()


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str):
    user = User.objects(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.delete()
    return {"status": "User deleted successfully"}
