import os
from typing import List

from fastapi import FastAPI
from fastapi import HTTPException
from demo.models.documents.user import User
from demo.models.requests.user import UserModelRequest
from motor.motor_asyncio import AsyncIOMotorClient
from motormongo import connect
import bcrypt

app = FastAPI()


print(f"Mongo url = {os.getenv('MONGODB_URL')}")

@app.on_event("startup")
async def startup_db_client():
    await connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION"))


@app.on_event("shutdown")
async def shutdown_db_client():
    pass


@app.post("/users/")
async def create_user(user: UserModelRequest):
    print(f"REQUEST = {user.model_dump()}")
    new_user = await User.insert_one(**user.model_dump())
    print(f"saved user {new_user.to_dict()}")
    return {}  # Assuming BaseDocument has a to_dict method


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    print(f"Got user {user.to_dict()}")
    return {}


@app.put("/users/{user_id}")
async def update_user(user_id: str, user_data: UserModelRequest):
    update_fields = {
        "username": user_data.username,
        "email": user_data.email,
        "alive": user_data.alive
    }
    user = await User.update_one({"_id": user_id}, update_fields)
    # print(f"Returned after find_one: {user.to_dict()}")
    # if user is None:
    #     raise HTTPException(status_code=404, detail="user not found")
    # updated_user = await user.update({"name": user_data.name})
    return {}

@app.put("/users/kill/{user_id}")
async def kill_user(user_id: str):
    user = await User.find_one(_id=user_id)
    user.alive = False
    await user.save()
    return {}

@app.put("/users/location/{user_id}")
async def user_field_exists(user_id, location: List[float] = [38.8977, 77.0365]):
    user = await User.find_one(_id=user_id)
    user.location = location
    await user.save()
    return {}

@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    await user.delete()
    return {"status": "success"}
