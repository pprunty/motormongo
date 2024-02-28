import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from motormongo import DataBase, Document, BinaryField, StringField
import re
import bcrypt


def hash_password(password: str) -> bytes:
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), salt=bcrypt.gensalt())


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=150)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password)


class UserModelRequest(BaseModel):
    username: str = Field(example="johndoe")
    email: str = Field(example="johndoe@coldmail.com")
    password: str = Field(example="password123")


class UpdateUserModelRequest(BaseModel):
    username: str = Field(example="johndoe")
    email: str = Field(example="johndoe@coldmail.com")


class UserAuthModelRequest(BaseModel):
    username: str = Field(example="johndoe")
    password: str = Field(example="password123")


app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))


@app.on_event("shutdown")
async def shutdown_db_client():
    await DataBase.close()


@app.post("/users/", status_code=201)
async def create_user(user: UserModelRequest):
    new_user = await User.insert_one(user.model_dump())
    return new_user.to_dict()


@app.post("/user/auth", status_code=200)
async def is_authenticated(request: UserAuthModelRequest):
    user = await User.find_one({"username": request.username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.verify_password(request.password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        return "You are authenticated! You can see this!"


@app.get("/users")
async def get_users():
    users = await User.find_many()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return [user.to_dict() for user in users]


@app.get("/users/{username}")
async def get_user(username: str):
    user = await User.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@app.put("/users/{username}", status_code=200)
async def update_user(username: str, request: UpdateUserModelRequest):
    updated_user = await User.update_one({"username": username}, {"email": request.email})
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user.to_dict()


@app.delete("/users/{username}", status_code=204)
async def delete_user(username: str):
    print(f"delete username = {username}")
    user = await User.find_one({"username": username})
    print(f"user = {user.to_dict()}")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"status": "User deleted successfully"}
