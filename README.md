
A tiny vector database for small projects (vectors are able to be stored in memory)

- It use jit compiling to speed up the vector operation by setting the vector size at compile time 
and speedup the vector operation by using [Eigen](https://eigen.tuxfamily.org/index.php?title=Main_Page).
- Process with only python list, without requiring any other third-party data format.
- The actual storage is base-64 encoded string, in a sqlite database.

**More than 10x Faster than numpy-based vector operation.**

**Under development...**
( Only on Linux and Mac OS with `g++`/`clang++` for now, need to write compile script for Windows on your own, refer to `tiny_vectordb.jit` )


Usage:
```python
import random
from tiny_vectordb import VectorDatabase

collection_configs = [
    {
        "name": "hello",
        "dimension": 256,
    },
    {
        "name": "world",
        "dimension": 1000,
    }
]

database = VectorDatabase("test.db", collection_configs)

collection = database["hello"]

# 50 vectors of 256 dimension
vectors = [[random.random() for _ in range(256)] for _ in range(50)]
vector_ids = [f"vector_{i}" for i in range(50)]

collection.addBulk(vector_ids, vectors)

search_ids, search_scores = collection.search([random.random() for _ in range(256)], k=10)

database.flush()
database.commit()
```