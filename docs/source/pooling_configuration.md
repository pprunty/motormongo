# Pooling Options & Configuration

In `motormongo`, you have the flexibility to customize the pooling options for the Motor client. This allows you to
fine-tune the behavior of database connections according to your application's needs. Below are some of the parameters
you can configure, along with their descriptions and example usage.

## Configuration Parameters

- **Max Pool Size**: The maximum number of connections in the connection pool.
- **Min Pool Size**: The minimum number of connections in the connection pool.
- **Max Idle Time**: The maximum time (in milliseconds) a connection can remain idle in the pool before being closed.
- **Wait Queue Timeout**: The time (in milliseconds) a thread will wait for a connection to become available when the
  pool is exhausted.
- **Connect Timeout**: The time (in milliseconds) to wait for a connection to the MongoDB server to be established
  before timing out.
- **Socket Timeout**: The time (in milliseconds) to wait for a socket read or write to complete before timing out.

## Example Configuration

```python
import asyncio
from motormongo import DataBase

# Example pooling options
pooling_options = {
    'maxPoolSize': 50,
    'minPoolSize': 10,
    'maxIdleTimeMS': 30000,
    'waitQueueTimeoutMS': 5000,
    'connectTimeoutMS': 10000,
    'socketTimeoutMS': 20000
}


async def init_db():
    # This 'connect' method needs to be called inside of an async function
    await DataBase.connect(uri="<mongo_uri>", database="<mongo_database>", **pooling_options)


if __name__ == "__main__":
    asyncio.run(init_db())
```

or in FastAPI:

```python
from fastapi import FastAPI
from motormongo import DataBase

app = FastAPI()

# Example pooling options
pooling_options = {
    'maxPoolSize': 50,
    'minPoolSize': 10,
    'maxIdleTimeMS': 30000,
    'waitQueueTimeoutMS': 5000,
    'connectTimeoutMS': 10000,
    'socketTimeoutMS': 20000
}


@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri="<mongodb_uri>", db="<mongodb_db>", **pooling_options)

```

This configuration demonstrates how to set up `motormongo` with specific pooling options to optimize performance
and resource utilization in high-throughput environments.

For more information, consult the official documentation:

- [Motor: Asynchronous Python driver for MongoDB](https://motor.readthedocs.io/en/stable/)
- [MongoDB Manual: Tuning Your Connection Pool Settings](https://www.mongodb.com/docs/manual/reference/connection-string/#mongodb-urioption-urioption.maxPoolSize)
