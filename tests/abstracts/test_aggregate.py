import os

import pytest

from motormongo import DataBase
from tests.test_documents.user import User, Status


@pytest.mark.asyncio
async def test_user_aggregation():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )
    users = [
        {"username": "user1", "email": "user1@example.com", "password": "password123", "age": 20,
         "status": Status.ACTIVE.value},
        {"username": "user2", "email": "user2@example.com", "password": "password123", "age": 25,
         "status": Status.INACTIVE.value},
        {"username": "user3", "email": "user3@example.com", "password": "password123", "age": 30,
         "status": Status.ACTIVE.value},
    ]
    await User.insert_many(users)
    # Define an aggregation pipeline to filter active users and project specific fields
    pipeline = [
        {"$match": {"status": Status.ACTIVE.value}},
        {"$project": {"_id": 0, "username": 1, "age": 1}},
        {"$sort": {"age": 1}}
    ]

    # Execute the aggregate function
    cursor = await User.aggregate(pipeline)
    results = await cursor.to_list(length=100)

    # Expected results based on the test data and pipeline
    expected_results = [
        {"username": "user1", "age": 20},
        {"username": "user3", "age": 30}
    ]

    assert results == expected_results, "Aggregation results did not match expected values."
    await User.delete_many({})

@pytest.mark.asyncio
async def test_user_aggregation_w_list():
    await DataBase.connect(
        uri=os.getenv("MONGODB_URL"), db=os.getenv("MONGODB_COLLECTION")
    )
    users = [
        {"username": "user1", "email": "user1@example.com", "password": "password123", "age": 20,
         "status": Status.ACTIVE.value},
        {"username": "user2", "email": "user2@example.com", "password": "password123", "age": 25,
         "status": Status.INACTIVE.value},
        {"username": "user3", "email": "user3@example.com", "password": "password123", "age": 30,
         "status": Status.ACTIVE.value},
    ]
    await User.insert_many(users)
    # Define an aggregation pipeline to filter active users and project specific fields
    pipeline = [
        {"$match": {"status": Status.ACTIVE.value}},
        {"$project": {"_id": 0, "username": 1, "age": 1}},
        {"$sort": {"age": 1}}
    ]

    # Execute the aggregate function
    user_results = await User.aggregate(pipeline, return_as_list=True)

    # Expected results based on the test data and pipeline
    expected_results = [
        {"username": "user1", "age": 20, "alive": True},
        {"username": "user3", "age": 30, "alive": True}
    ]

    for idx, user in enumerate(user_results):
        assert user.to_dict() == expected_results[idx]

    await User.delete_many({})