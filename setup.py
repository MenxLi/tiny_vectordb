from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    packages=find_packages(),
    include_package_data = True,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
