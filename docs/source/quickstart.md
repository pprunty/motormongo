# Quickstart

### Create a motormongo client:

```python
import asyncio
from motormongo import DataBase


async def init_db():
    # This 'connect' method needs to be called inside of an async function
    await DataBase.connect(uri="<mongo_uri>", database="<mongo_database>")


if __name__ == "__main__":
    asyncio.run(init_db())
```

or, in a FastAPI application:

```python
from fastapi import FastAPI
from motormongo import DataBase

app = FastAPI()


@app.on_event("startup")
async def startup_db_client():
    await DataBase.connect(uri="<mongo_uri>", db="<mongo_database>")


@app.on_event("shutdown")
async def shutdown_db_client():
    await DataBase.close()
```

The `mongo_uri` should look something like this:

```text
mongodb+srv://<username>:<password>@<cluster>.mongodb.net
```

and `database` should be the name of an existing MongoDB database in your MongoDB instance.

For details on how to set up a local or cloud MongoDB database instance,
see [here](https://www.mongodb.com/cloud/atlas/lp/try4?utm_source=google&utm_campaign=search_gs_pl_evergreen_atlas_general_prosp-brand_gic-null_emea-ie_ps-all_desktop_eng_lead&utm_term=using%20mongodb&utm_medium=cpc_paid_search&utm_ad=p&utm_ad_campaign_id=9510384711&adgroup=150907565274&cq_cmp=9510384711&gad_source=1&gclid=Cj0KCQiAyeWrBhDDARIsAGP1mWQ6B0kPYX9Tqmzku-4r-uUzOGL1PKDgSTlfpYeZ0I6HE3C-dgh1xF4aArHqEALw_wcB).

You can also specify and pass `pooling_options` to the Motor on the `DataBase.connect()` method, like so:

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

See [Pooling Options Configuration](#pooling-options-configuration) section for more details.

### Define a motormongo Document:

Define a `motormongo` `User` document:

```python
import re
import bcrypt
from motormongo import Document, BinaryField, StringField


def hash_password(password: str) -> bytes:
    # Example hashing function
    return bcrypt.hashpw(password.encode('utf-8'), salt=bcrypt.gensalt())


class User(Document):
    username = StringField(help_text="The username for the user", min_length=3, max_length=50)
    email = StringField(help_text="The email for the user", regex=re.compile(r'^\S+@\S+\.\S+$'))  # Simple email regex
    password = BinaryField(help_text="The hashed password for the user", hash_function=hash_password)

    def verify_password(self, password: str) -> bool:
        """ Utility function which can be used to validate user's salted password later...
        
        ex.     user = await User.find_one({"_id": request.user_id})
                is_authenticated = user.verify_password(request.password)
        """
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    class Meta:
        collection = "users"  # < If not provided, will default to class name (ex. User->user, UserDetails->user_details)
        created_at_timestamp = True  # < Provide a DateTimeField for document creation
        updated_at_timestamp = True  # < Provide a DateTimeField for document updates
```

### Create a MongoDB document using the User class

```python
import bcrypt

await User.insert_one(
    {
        "username": "johndoe",
        "email": "johndoe@portmarnock.ie",
        "password": "password123"
        # < hash_functon will hash the string literal password and store binary field in the database
    }
)
```

### Validate user was created in your MongoDB collection

You can do this by using [MongoDB compass](https://www.mongodb.com/products/tools/compass) GUI, or alternatively, add a
query to find all documents in the user
collection after doing the insert in step 3:

```python
users = User.find_many({})
if users:
    print("User collection contains the following documents:")
    for user in users:
        print(user.to_dict())
else:
    print("User collection failed to update! Check your MongoDB connection details and try again!")
```

### Put all the code above into one file and run it

```shell
python main.py
```

or in a FastAPI application:

```shell
uvicorn main:app --reload
```

Please refer to [FastAPI Documentation](https://fastapi.tiangolo.com/tutorial/) for more details on how to get setup
with FastAPI.

## Congratulations 🎉

You've successfully created your first `motormongo` Object Document Mapper class. 🥳

The subsequent sections detail the datatype fields provided by `motormongo`, as well as the CRUD
operations available on the classmethods and object instance methods of a `motormongo` document.

If you wish to get straight into how to integrate `motormongo` with your `FastAPI` application, skip ahead to the
[FastAPI Integration](#fastapi-integration) section.
