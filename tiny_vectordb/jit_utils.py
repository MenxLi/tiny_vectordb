import os, subprocess, platform

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