import time
import numpy as np
from tiny_vectordb import getVectorCollectionBackend

def test_speed_numpy():
    collection_cxx = getVectorCollectionBackend('cxx')(
        None, 
        quite_loading=True, 
        name="Test", 
        dimension=512
    )
    collection_np = getVectorCollectionBackend('numpy')(
        None, 
        quite_loading=True, 
        name="Test", 
        dimension=512
    )

    _g_counter = 0
    def _test(n: int):
        nonlocal _g_counter
        _g_counter += n
        np.random.seed(0)
        vectors = np.random.rand(n, 512).tolist()
        ids = [str(x+_g_counter) for x in range(n)]

        collection_cxx.addBlock(ids, vectors)
        collection_np.addBlock(ids, vectors)

        query = [float(x) for x in range(512)]

        _t = time.time()
        collection_cxx.search(query)
        t_c = time.time() - _t
        print(f"Search {n} vectors with cxx backend: {t_c}")
        _t = time.time()
        collection_np.search(query)
        t_np = time.time() - _t
        print(f"Search {n} vectors with numpy backend: {t_np}")
        print("--------- {:.2f}x faster -------".format(t_np / t_c))
    
    _test(100)
    _test(1000)
    _test(10000)
    _test(100000)

if __name__ == "__main__":
    test_speed_numpy()