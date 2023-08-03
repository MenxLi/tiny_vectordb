import time
import numpy as np
from numpy.testing import assert_approx_equal
from tiny_vectordb import VectorCollection

LEN = 512
N = 10000

def cos_sim_np(tgt, query):
    """
    target: (N, LEN)
    query: (LEN, )
    """
    assert isinstance(tgt, np.ndarray)
    assert isinstance(query, np.ndarray)
    return np.dot(tgt, query) / (np.linalg.norm(tgt, axis=1) * np.linalg.norm(query))

def compareTime(n: int):
    collection = VectorCollection[float]("test", LEN, quite_loading=True)
    print("Compare time taken for", n, "vectors")

    np.random.seed(0)
    vectors = np.random.rand(n, LEN).tolist()
    ids = [str(x) for x in range(n)]

    query = [float(x) for x in range(LEN)]
    target = vectors

    collection.addBulk(ids, vectors)
    _t = time.time()
    sc_0 = collection.__impl.score(query)
    t_0 = time.time() - _t
    print("[Eigen] Time taken:", t_0, "seconds")
    _t = time.time()

    target = np.array(target)
    query = np.array(query)
    _t = time.time()
    sc_1 = cos_sim_np(target, query)
    t_1 = time.time() - _t
    print("[Numpy] Time taken:", t_1, "seconds")

    step = 1 if n < 1000 else n//100
    for i in range(0, n, step):
        assert_approx_equal(sc_0[i], sc_1[i], significant=4)
    print(f"Time superiority: {t_1 / t_0 : .2f} times faster", end="\n\n")

# compareTime(1000000)
compareTime(100000)
compareTime(10000)
compareTime(5000)
compareTime(1000)
compareTime(500)
compareTime(100)
