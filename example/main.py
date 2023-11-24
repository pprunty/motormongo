from fastapi import FastAPI
from fastapi import HTTPException
from example.models.documents.user import User
from example.models.requests.user import UserModelRequest
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient("mongodb+srv://pprunty:Cracker123!@cluster0.7o5omuv.mongodb.net")
    app.mongodb = app.mongodb_client["test"]  # Replace with your database name


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


@app.post("/users/")
async def create_user(user: UserModelRequest):
    new_user = User(**user.model_dump())
    await new_user.save()
    return new_user.to_dict()  # Assuming BaseDocument has a to_dict method


@app.get("/users/{user_id}", response_model=UserModelRequest)
async def get_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user.to_dict()


@app.put("/users/{user_id}", response_model=UserModelRequest)
async def update_user(user_id: str, user_data: UserModelRequest):
    user = await User.update_one({"_id": user_id}, user_data.model_dump())
    # print(f"Returned after find_one: {user.to_dict()}")
    # if user is None:
    #     raise HTTPException(status_code=404, detail="user not found")
    # updated_user = await user.update({"name": user_data.name})
    print(f"updated user = {user}")
    return user


@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    await user.delete()
    return {"status": "success"}