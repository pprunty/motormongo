# Aggregation

The `aggregate` class method is designed to perform aggregation operations on the documents within the collection. It
allows the execution of a sequence of data aggregation operations defined by the `pipeline` parameter. This method can
return the results either as a list of documents or as a cursor, based on the `return_as_list` flag.

**Parameters:**

- `pipeline`: A list of dictionaries defining the aggregation operations to be performed on the collection.
- `return_as_list` (optional): A boolean flag that determines the format of the returned results. If set to `True`, the
  method returns a list of documents. If `False` (default), it returns a cursor.

**Returns:**

- If `return_as_list` is `True`, returns a list of documents resulting from the aggregation pipeline.
- If `return_as_list` is `False`, returns a Cursor to iterate over the results.

**Raises:**

- `ValueError`: If an error occurs during the execution of the pipeline.

**Example Usage:**

```python
from yourmodule import YourDocumentClass

# Connect to the database (Assuming the database connection is already set up)
# Define an aggregation pipeline
pipeline = [
    {"$match": {"status": "active"}},
    {"$project": {"_id": 0, "username": 1, "status": 1}},
    {"$sort": {"username": 1}}
]

# Execute the aggregation without returning a list
cursor = await YourDocumentClass.aggregate(pipeline)
async for doc in cursor:
    print(doc)

# Execute the aggregation and return results as a list
docs_list = await YourDocumentClass.aggregate(pipeline, return_as_list=True)
print(docs_list)
```