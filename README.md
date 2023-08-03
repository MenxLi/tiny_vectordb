## Tiny Vector Database

A lightweight vector database designed for small projects.

**Features**
- Just-in-time (JIT) compiling to optimize vector operations by setting the vector size at compile time.
- Accelerates vector operations using [Eigen](https://eigen.tuxfamily.org/index.php?title=Main_Page).
- Processes vectors using only Python lists, no need for any additional third-party data formats.
- Stores vectors as base-64 encoded strings in a SQLite database.

**Performance**  
More than 10x Faster than numpy-based vector operations.

### Development Status

The project is currently under development. 
It is compatible with Linux and Mac OS using g++ or clang++. 
For Windows, you will need to write your own compile script. Please refer to the `tiny_vectordb.jit` file for more information.

### Installation

```bash
git submodule update --init --recursive
pip install -e .
```
Good to go!

### Usage:
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

collection.addBlock(vector_ids, vectors)

search_ids, search_scores = collection.search([random.random() for _ in range(256)], k=10)

database.flush()
database.commit()
```