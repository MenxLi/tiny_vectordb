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
```
For more usage, see `example.py`.

---

**Designing Note:**  

1. No numpy array is used in the database, because I want it to be as lightweight as possible, and lists of numbers are eaiser to be converted into json for communication with http requests.

2. The data are always stored in contiguous memory to ensure the best searching performance.  
So the addition and deletion are preferred to be done in batches as they envolve memory reallocation.   
Here are some useful functions for batch operations:
```python
class VectorCollection(Generic[NumVar]):
    def addBlock(self, ids: list[str], vectors: list[list[NumVar]]) -> None:
    def setBlock(self, ids: list[str], vectors: list[list[NumVar]]) -> None:
    def deleteBlock(self, ids: list[str]) -> None:
    def getBlock(self, ids: list[str]) -> list[list[NumVar]]:
```
