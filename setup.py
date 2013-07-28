import os
from setuptools import setup, find_packages

# def read(fname):
#     return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "quadpy",
    version = "0.1.0",
    description = ("Quadtree implementation for Python"),
    author = "bgr",
    author_email = "bgrgyk@gmail.com",
    url = "https://github.com/bgr/quadpy",
    packages = find_packages(),
    install_requires = [],

)
