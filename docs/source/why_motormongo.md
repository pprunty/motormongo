# Why use motormongo?

Integrating `motormongo`, an asynchronous Object-Document Mapper (ODM) for MongoDB, into a backend built with an
asynchronous web framework like `FastAPI`, enhances the system's ability to handle I/O-bound operations efficiently.
Using the `await` keyword with `motormongo` operations allows the event loop to manage concurrent requests effectively,
freeing up the main thread to handle other tasks while waiting for database operations to complete.

## Understanding the Efficiency of Asynchronous Operations

### Traditional (Synchronous) Approach with `pymongo` and `mongoengine`

Typically, a web server handling multiple requests that involve fetching documents from MongoDB would face bottlenecks
with synchronous database operations:

```python
from mongoengine import connect, Document, StringField, BooleanField
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder

connect(db="testdb", host="mongodb://localhost:27017/", alias="default")

class User(Document):
    name = StringField(required=True)
    active = BooleanField()

app = FastAPI()

@app.get("/users/")
async def get_users_with_interests(active: bool):
    users = User.objects(active=active)
    if users:
        return [jsonable_encoder(user.to_mongo().to_dict()) for user in users]
    else:
        raise HTTPException(status_code=404, detail="No users are currently active")

```

In this setup, operations such as `User.objects(active=active)` block the thread until completion, hindering the
server's ability to process other requests concurrently, leading to inefficient resource use and potential performance
bottlenecks.

### Modern (Asynchronous) Approach with `motor` and `motormongo`

Switching to an asynchronous ODM like `motormongo` allows FastAPI to handle database operations without blocking:

```python
from fastapi import FastAPI, HTTPException
from motormongo import DataBase, Document, StringField, BooleanField

class User(Document):
    name = StringField(required=True)
    active = BooleanField()

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri="mongodb://localhost:27017/", db="testdb")

@app.get("/users/")
async def get_users_with_interests(active: bool):
    users = await User.find_many({'active': active})
    if users:
        return [user.to_dict() for user in users]
    else:
        raise HTTPException(status_code=404, detail="No users are currently active")

```

Using `await` with `motormongo` operations such as `User.find_one()` allows the application to perform non-blocking
database operations. This asynchronous model is particularly advantageous for I/O-bound applications, allowing the
server to handle multiple requests efficiently by utilizing Python's `asyncio`.

## Maximizing Performance with Multiple FastAPI Workers

To further enhance the performance of FastAPI applications utilizing `motormongo`, deploying multiple worker processes
can significantly increase the application's ability to handle high volumes of concurrent requests:

- **Scalability**: Deploying FastAPI with multiple workers enables the application to scale across multiple CPU cores,
  offering better handling of concurrent requests by running multiple instances of the application, each in its own
  process.
- **Resource Utilization**: More workers mean that the application can utilize more system resources, effectively
  distributing the load and preventing any single worker from becoming a bottleneck.
- **Deployment Strategy**: Use an ASGI server like `uvicorn` with the `--workers` option to specify the number of worker
  processes. For example, `uvicorn app:app --workers 4` would run the application with four worker processes.

By leveraging `motormongo` with FastAPI, developers can build backend systems capable of handling asynchronous I/O-bound
operations efficiently. This setup not only improves the application's responsiveness and throughput by utilizing the
asynchronous capabilities of Python's `asyncio` but also maximizes performance through the strategic deployment of
multiple workers. Together, these strategies enable the creation of highly scalable, efficient, and modern web
applications.
