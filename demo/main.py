import os
from typing import List
from fastapi import FastAPI, HTTPException
from demo.models.documents.user import User, UserDetails
from demo.models.requests.user import UserModelRequest
from demo.models.requests.user_details import UserDetailsRequest, UpdateUserDetailsRequest
from motormongo import DataBase

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_DB"))

@app.on_event("shutdown")
async def shutdown_db_client():
    await DataBase.close()

@app.post("/users/", status_code=201)
async def create_user(user: UserModelRequest):
    new_user = await User.insert_one(**user.dict())
    return new_user.to_dict()


@app.get("/users")
async def get_users():
    users = await User.find_many()
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return [user.to_dict() for user in users]

@app.post("/user/auth", status_code=200)
async def is_authenticated(username: str, password: str):
    user = await User.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.verify_password(password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    else:
      return "You are authenticated! You can see this!"



@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()

@app.put("/users/{user_id}", status_code=200)
async def update_user(user_id: str, user_data: UserModelRequest):
    updated_user = await User.update_one({"_id": user_id}, user_data.dict())
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

@app.put("/users/kill/{user_id}", status_code=204)
async def kill_user(user_id: str):
    user = await User.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.alive = False
    await user.save()
    return {"status": "User marked as not alive"}

@app.put("/users/location/{user_id}", status_code=204)
async def update_user_location(user_id: str, location: List[float]):
    user = await User.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.location = location
    await user.save()
    return {"status": "Location updated"}


@app.post("/user-details/", response_model=UserDetailsRequest)
async def create_user_details(details: UserDetailsRequest):
    print(f"create user details req = {details.dict()}")
    # Assuming UserDetails has a field `user` that links to the User document.
    user_details = await UserDetails.insert_one(**details.dict())
    return user_details.to_dict()

@app.get("/user-details/{user_id}", response_model=UserDetailsRequest)
async def get_user_details(user_id: str):
    details = await UserDetails.find_one({"user": user_id})
    # todo: get this working
    # user = await User.find_one(_id=user_id)
    # details = await UserDetails.find_one({"user": user})
    if details is None:
        raise HTTPException(status_code=404, detail="User details not found")
    print(f"GOT USER = {await details.user}")
    print(f"GOT USER DETAILS = {details.to_dict(id_as_string=False)}")
    return details.to_dict()

@app.put("/user-details/{user_id}", response_model=UserDetailsRequest)
async def update_user_details(user_id: str, details: UserDetailsRequest):
    update_fields = {
        "dob": details.dob,
        "gender": details.gender,
        "metadata": details.metadata
    }
    print(f"update fielfzzz = {update_fields} and dict = {details.dict()}")
    updated_details = await UserDetails.update_one({"user": user_id}, update_fields)
    if updated_details is None:
        raise HTTPException(status_code=404, detail="User details not found")
    return updated_details.to_dict()

@app.delete("/user-details/{user_id}")
async def delete_user_details(user_id: str):
    details = await UserDetails.find_one({"user": user_id})
    if details is None:
        raise HTTPException(status_code=404, detail="User details not found")
    await details.delete()
    return {"status": "User details deleted successfully"}