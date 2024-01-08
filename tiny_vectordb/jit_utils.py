from __future__ import annotations
import os, subprocess, platform
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .wrap import CompileConfig

def checkCommandExists(cmd: str) -> bool:
    if platform.system() == "Windows":
        return subprocess.call(["where", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    return subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def initEigenSrc(eigen_src_path: str, eigen_version: str = "3.4.0"):
    if not os.path.exists(eigen_src_path):
        os.makedirs(eigen_src_path)

    if os.listdir(eigen_src_path) == [] or \
        not os.path.exists(os.path.join(eigen_src_path, "Eigen", "src", "Core")):

        print("Downloading Eigen...")
        if not checkCommandExists("git"):
            raise RuntimeError("git not found.")
        subprocess.check_call([
            "git", "clone", "--depth=1", f"--branch={eigen_version}",
            "https://gitlab.com/libeigen/eigen.git", eigen_src_path]
            )

def autoCompileConfig() -> CompileConfig:
    """
    Return automatically detected compile config for the current environment. 
    Will check existence of compilers and files.
    """
    # TODO: improve this...
    cxx = None
    for _cxx in ["g++", "clang++"]:
        if checkCommandExists(_cxx):
            cxx = _cxx
            break
    if cxx is None:
        raise RuntimeError("No C++ compiler found. Please install g++ or clang++.")
    
    additional_compile_flags = [
        "-march=native", "-mtune=native",
    ]

    additional_link_flags = []
    
    return {
        "cxx": cxx,
        "additional_compile_flags": additional_compile_flags,
        "additional_link_flags": additional_link_flags
    }