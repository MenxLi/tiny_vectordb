from __future__ import annotations
from setuptools import setup, find_packages
import os

__this_dir = os.path.dirname(__file__)

setup(
    packages=find_packages(),
    include_package_data = True,
)
