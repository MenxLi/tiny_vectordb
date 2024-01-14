"""
vecotr related modules.
vector database and related functions.
"""
from .wrap import VectorDatabase, CompileConfig, CollectionConfig, getVectorCollectionBackend
from .vector_collection import VectorCollectionAbstract as VectorCollectionT
from .config import cleanup
from .jit_utils import autoCompileConfig
from . import jit

VectorCollection = getVectorCollectionBackend()
__all__ = [
    "getVectorCollectionBackend",
    "VectorDatabase",
    "VectorCollection",
    "VectorCollectionT",
    "CompileConfig",
    "CollectionConfig",
    "autoCompileConfig",
    "cleanup", 
    "jit", 
]