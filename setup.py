import os

from setuptools import setup

install_requires = ["cffi", "findlibs>=0.1.0", "pandas", "packaging"]
# The PyPI build sets DEPEND_ON_ODCLIB=1; CI loads its own odc instead.
if os.getenv("DEPEND_ON_ODCLIB", "") == "1":
    install_requires.append("odclib>=1.6.0,<1.7.0")

setup(install_requires=install_requires)
