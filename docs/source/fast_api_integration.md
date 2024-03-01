## FastAPI integration

`motormongo` can be easily integrated in FastAPI APIs to leverage the asynchronous ability of
FastAPI. To leverage `motormongo`'s ease-of-use, Pydantic model's should be created to represent the MongoDB
`motormongo` Document as a Pydantic model. Below is a light-weight CRUD FastAPI application using `motormongo`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from motormongo import DataBase, Document, BinaryField, StringField
import re
import bcrypt


def hash_password(password: str) -> bytes:
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), salt=bcrypt.gensalt())


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    class Meta:
        collection = "users"  # < If not provided, will default to class name (ex. User->user, UserDetails->user_details)
        created_at_timestamp = True  # < Provide a DateTimeField for document creation
        updated_at_timestamp = True  # < Provide a DateTimeField for document updates


class UserModelRequest(BaseModel):
    username: str = Field(example="johndoe")
    email: str = Field(example="johndoe@coldmail.com")
    password: str = Field(example="password123")


app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri="<mongodb_uri>", db="<mongodb_db>")


@app.on_event("shutdown")
async def shutdown_db_client():
    await DataBase.close()


@app.post("/users/", status_code=201)
async def create_user(user: UserModelRequest):
    new_user = await User.insert_one(**user.dict())
    return new_user.to_dict()


@app.post("/user/auth", status_code=200)
async def is_authenticated(username: str, password: str):
    user = await User.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
        return "You are authenticated! You can see this!"


@app.get("/users")
async def get_users():
    users = await User.find_many()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return [user.to_dict() for user in users]


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@app.put("/users/{user_id}", status_code=200)
async def update_user(user_id: str, user_data: UserModelRequest):
    updated_user = await User.update_one({"_id": user_id}, user_data.model_dump())
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user.to_dict()


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"status": "User deleted successfully"}
```
