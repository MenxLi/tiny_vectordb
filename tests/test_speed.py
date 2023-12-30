import time
import numpy as np
from numpy.testing import assert_approx_equal
import torch
from tiny_vectordb import VectorCollection

LEN = 512
torch_device = "cuda" if torch.cuda.is_available() else "cpu"
# torch_device = "mps" 

def cos_sim_np(tgt, query):
    """
    target: (N, LEN)
    query: (LEN, )
    """
    assert isinstance(tgt, np.ndarray)
    assert isinstance(query, np.ndarray)
    return np.dot(tgt, query) / (np.linalg.norm(tgt, axis=1) * np.linalg.norm(query))

def search_np(ids: list[str], tgt, query, k):
    assert isinstance(tgt, np.ndarray)
    assert isinstance(query, np.ndarray)
    assert isinstance(k, int)

    scores = cos_sim_np(tgt, query)
    topk_indices = np.argsort(scores)[::-1][:k]
    # return [ids[i] for i in topk_indices], scores[topk_indices]
    return ids[topk_indices], scores[topk_indices]

def cos_sim_torch(tgt, query):
    """
    target: (N, LEN)
    query: (LEN, )
    """
    assert isinstance(tgt, torch.Tensor)
    assert isinstance(query, torch.Tensor)
    return torch.matmul(tgt, query) / (torch.norm(tgt, dim=1) * torch.norm(query))

def search_torch(ids: list[str], tgt, query, k):
    assert isinstance(tgt, torch.Tensor)
    assert isinstance(query, torch.Tensor)
    assert isinstance(k, int)

    scores = cos_sim_torch(tgt, query)
    topk_indices = torch.argsort(scores, descending=True)[:k]
    # return [ids[i] for i in topk_indices], scores[topk_indices]
    return ids[topk_indices.cpu().numpy()], scores[topk_indices]

def compare(n: int, k = 16):
    collection = VectorCollection[float](None, "test", LEN, quite_loading=True)
    print(f"Compare for {n} vectors of length {LEN} numpy | torch-{torch_device}:")

    np.random.seed(0)
    vectors = np.random.rand(n, LEN).tolist()
    ids = [str(x) for x in range(n)]

    query = [float(x) for x in range(LEN)]
    target = vectors

    collection.addBlock(ids, vectors)
    _t = time.time()
    sc_0 = collection._impl.score(query)
    t_0 = time.time() - _t
    print("[Eigen] Matrix multiplication time taken:", t_0, "seconds")
    _t = time.time()
    s0 = collection.search(query, k)
    t_01 = time.time() - _t
    print("[Eigen] Search time taken:", t_01, "seconds")

    target_np = np.array(target)
    query_np = np.array(query)
    _t = time.time()
    sc_1 = cos_sim_np(target_np, query_np)
    t_1 = time.time() - _t
    print("[Numpy] Matrix multiplication time taken:", t_1, "seconds")
    _t = time.time()
    s1 = search_np(np.array(ids), target_np, query_np, k)   # type: ignore
    t_11 = time.time() - _t
    print("[Numpy] Search time taken:", t_11, "seconds")

    target_torch = torch.tensor(target).to(torch_device)
    query_torch = torch.tensor(query).to(torch_device)
    _t = time.time()
    sc_2 = cos_sim_torch(target_torch, query_torch)
    t_2 = time.time() - _t
    print("[PyTorch] Matrix multiplication time taken:", t_2, "seconds")
    _t = time.time()
    s2 = search_torch(np.array(ids), target_torch, query_torch, k)      # type: ignore
    t_21 = time.time() - _t
    print("[PyTorch] Search time taken:", t_21, "seconds")

    step = 1 if n < 1000 else n//100
    for i in range(0, n, step):
        assert_approx_equal(sc_0[i], sc_1[i], significant=4)
    
    for i in range(k):
        assert s0[0][i] == s1[0][i]
        assert_approx_equal(s0[1][i], s1[1][i], significant=4)
        assert s0[0][i] == s2[0][i]
        assert_approx_equal(s0[1][i], s2[1][i], significant=4)

    print("----------------------------------")
    print(f"Matrix mult. superiority: {t_1 / t_0 : .2f} | {t_2 / t_0} times faster", end="\n")
    print(f"Search superiority: {t_11 / t_01 : .2f} | {t_21 / t_01} times faster", end="\n\n")

for i in range(2,6)[::-1]:
    compare(10**i)
