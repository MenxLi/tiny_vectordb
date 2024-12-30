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

It is currently compatible with g++ or clang++.   
You may need to modify `compile_config` parameter in `VectorDatabase` initialization to inject your compile commands.   
To make it work with other compiler, you may need to change `tiny_vectordb.jit` module.

### Installation

```bash
pip install tiny_vectordb
```
Good to go!

<details>
<summary> Uninstallation (before version 0.1.11) </summary>

### Uninstallation
Previous to version 0.1.11, the package will emit some compiled files in the source directory, which may not be automatically removed using `pip uninstall`, so you need to run the following command manually if you want to uninstall the package comletely. 
(After 0.1.11, you can also use the following command to clean up the cache files.)
```bash
python -c "import tiny_vectordb; tiny_vectordb.cleanup()"
```
After that, you can safely uninstall the package with: 
```bash
pip uninstall tiny_vectordb
```
</details>

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

# add vectors
collection.setBlock(
    ["id1", "id2"],             # ids
    [[1] * 256, [2] * 256]      # vectors
)

# search for nearest vectors
search_ids, search_scores = collection.search([1.9] * 256)  
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
