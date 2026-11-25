import os

from setuptools import setup

install_requires = ["cffi", "findlibs>=0.1.0", "pandas", "packaging"]
# CI builds set DEPEND_ON_ODCLIB=0 to load their own odc rather than the PyPI binary.
if os.getenv("DEPEND_ON_ODCLIB", "1") != "0":
    install_requires.append("odclib>=1.6.0,<1.7.0")

setup(install_requires=install_requires)
