import os, shutil
from platformdirs import user_cache_dir
import importlib.metadata
VERSION = importlib.metadata.version("tiny_vectordb")

__this_dir = os.path.dirname(os.path.abspath(__file__))
__this_dir = os.path.abspath(os.path.realpath(__this_dir))
SRC_DIR = os.path.join(__this_dir, "src")
HEADER_DIR = os.path.join(__this_dir, "include")
CACHE_DIR = os.getenv("TVDB_CACHE_DIR", user_cache_dir(appname="tiny_vectordb", ensure_exists=True))

def cleanup():
    """
    Should be called before using `pip uninstall`
    """
    global CACHE_DIR
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)

BUILD_DIR = os.path.join(CACHE_DIR, f"build{VERSION}")
BIN_DIR = os.path.join(BUILD_DIR, "bin")
for _d in [BUILD_DIR, BIN_DIR]:
    if not os.path.exists(_d):
        os.makedirs(_d, exist_ok=True)
