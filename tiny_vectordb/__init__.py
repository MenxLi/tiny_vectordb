"""
vecotr related modules.
vector database and related functions.
"""
from .wrap import VectorDatabase, CompileConfig, CollectionConfig, getVectorCollectionBackend
from .config import cleanup
from .jit_utils import autoCompileConfig
from . import jit

VectorCollection = getVectorCollectionBackend()
__all__ = [
    "VectorDatabase",
    "VectorCollection",
    "CompileConfig",
    "CollectionConfig",
    "autoCompileConfig",
    "cleanup", 
    "jit", 
]