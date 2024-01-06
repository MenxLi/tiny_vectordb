import pkg_resources, os, shutil
VERSION = pkg_resources.get_distribution("tiny_vectordb").version

__this_dir = os.path.dirname(os.path.abspath(__file__))
__this_dir = os.path.abspath(os.path.realpath(__this_dir))
SRC_DIR = os.path.join(__this_dir, "src")
HEADER_DIR = os.path.join(__this_dir, "include")
CACHE_DIR = os.path.join(__this_dir, "_cache")
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)

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
