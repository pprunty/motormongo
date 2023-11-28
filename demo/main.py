import os

from fastapi import FastAPI
from fastapi import HTTPException
from demo.models.documents.user import User
from demo.models.requests.user import UserModelRequest
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt

app = FastAPI()


print(f"Mongo url = {os.getenv('MONGODB_URL')}")

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    app.mongodb = app.mongodb_client["test"]  # Replace with your database name


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


@app.post("/users/")
async def create_user(user: UserModelRequest):
    print(f"REUQEST = {user.model_dump()}")
    new_user = await User.insert_one(**user.model_dump())
    print(f"saved user {new_user.to_dict()}")
    return {}  # Assuming BaseDocument has a to_dict method


@app.get("/users/{user_id}", response_model=UserModelRequest)
async def get_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user.to_dict()


@app.put("/users/{user_id}")
async def update_user(user_id: str, user_data: UserModelRequest):
    update_fields = {
        "username": user_data.username,
        "email": user_data.email
    }
    user = await User.update_one({"_id": user_id}, update_fields)
    # print(f"Returned after find_one: {user.to_dict()}")
    # if user is None:
    #     raise HTTPException(status_code=404, detail="user not found")
    # updated_user = await user.update({"name": user_data.name})
    return {}


@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    await user.delete()
    return {"status": "success"}
