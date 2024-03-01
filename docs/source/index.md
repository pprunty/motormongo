# motormongo

| Description             | Badge                                                                                                                                                   |
|-------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| **PyPI - Version**      | [![PyPI - Version](https://img.shields.io/pypi/v/motormongo)](https://pypi.org/project/motormongo/)                                                     |
| **Downloads**           | [![Downloads](https://static.pepy.tech/badge/motormongo/month)](https://pepy.tech/project/motormongo)                                                   |
| **PyPI License**        | [![PyPI License](https://img.shields.io/pypi/l/motormongo.svg)](https://pypi.org/project/motormongo/)                                                   |
| **GitHub Contributors** | [![GitHub Contributors](https://img.shields.io/github/contributors/pprunty/motormongo.svg)](https://github.com/pprunty/motormongo/graphs/contributors)  |
| **Code Coverage**       | [![codecov](https://codecov.io/gh/pprunty/motormongo/graph/badge.svg?token=XSNQ1ZBWIF)](https://codecov.io/gh/pprunty/motormongo)                       |
| **Code Style**          | ![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)                                                                        |
| **Documentation**       | [![Documentation Status](https://readthedocs.org/projects/motormongo/badge/?version=latest)](https://motormongo.readthedocs.io/en/latest/?badge=latest) |


`motormongo` - An Object Document Mapper (ODM) for [MongoDB](https://www.mongodb.com) built on top
of [`motor`](https://github.com/mongodb/motor), the MongoDB
recommended asynchronous Python driver for MongoDB Python applications, designed to work with Tornado or
asyncio and enable non-blocking access to MongoDB.

Asynchronous operations in a backend system, built using [FastAPI](https://github.com/tiangolo/fastapi) for
example, enhances performance and scalability by enabling non-blocking, concurrent handling of multiple I/O requests,
leading to more efficient use of server resources, by forcing the CPU usage on the backend server's main thread to be
maximized across concurrent requests. For more low-level details on the advantages of asynchronous `motormongo` over
existing MongoDB ODMs, such as `mongoengine` [see here](#why-use-motormongo).

The interface for instantiating Document classes follows similar logic
to [`mongoengine`](https://github.com/MongoEngine/mongoengine), enabling ease-of-transition and
migration from `mongoengine` to the asynchronous `motormongo`.

## Installation

To install `motormongo`, you can use `pip` inside your virtual environment:

```shell
python -m pip install motormongo
```

Alternatively, to install `motormongo` into your `poetry` environment:

```shell
poetry add motormongo
```

```{toctree}
   :maxdepth: 2
   :numbered:

quickstart.md
why_motormongo.md
fields.md
crud_classmethods.md
aggregation.md
crud_instance_methods.md
polymorphism_and_inheritance.md
pooling_configuration.md
fast_api_integration.md
```