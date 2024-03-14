from __future__ import annotations
import os, subprocess, platform, time, random
from typing import TYPE_CHECKING
from .config import CACHE_DIR
if TYPE_CHECKING:
    from .wrap import CompileConfig

def checkCommandExists(cmd: str) -> bool:
    if platform.system() == "Windows":
        return subprocess.call(["where", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    return subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def initEigenSrc(eigen_src_path: str, eigen_version: str = "3.4.0"):
    if not os.path.exists(eigen_src_path):
        os.makedirs(eigen_src_path)

    __downloading_lock_file = os.path.join(CACHE_DIR, "downloading.lock")
    while os.path.exists(__downloading_lock_file):
        print(f"Find lock file [{__downloading_lock_file}], waiting...")
        time.sleep(random.random() * 1 + 1)     # wait for 1~2 seconds, avoid resource competition

    if os.listdir(eigen_src_path) == [] or \
        not os.path.exists(os.path.join(eigen_src_path, "Eigen", "src", "Core")):

        print("Downloading Eigen...")
        if not checkCommandExists("git"):
            raise RuntimeError("git not found.")
        
        open(__downloading_lock_file, "w").close()
        try:
            subprocess.check_call([
                "git", "clone", "--depth=1", f"--branch={eigen_version}",
                "https://gitlab.com/libeigen/eigen.git", eigen_src_path]
                )
        except: pass
        finally:
            os.remove(__downloading_lock_file)

# TODO: improve this...
def autoCompileConfig() -> CompileConfig:
    """
    Return automatically detected compile config for the current environment. 
    Will check existence of compilers and files.
    """
    def getCxxCompiler():
        cxx = os.getenv("CXX", None)
        if cxx is not None:
            return cxx
        for _cxx in ["g++", "clang++"]:
            if checkCommandExists(_cxx):
                cxx = _cxx
                break
        if cxx is None:
            raise RuntimeError("No C++ compiler found. Please install g++ or clang++.")
        return cxx
    
    cxx = getCxxCompiler()
    additional_compile_flags = [
        "-march=native", "-mtune=native",
    ]
    additional_link_flags = []
    
    return {
        "cxx": cxx,
        "additional_compile_flags": additional_compile_flags,
        "additional_link_flags": additional_link_flags
    }