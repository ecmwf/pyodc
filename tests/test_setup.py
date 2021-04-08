import pytest

import subprocess

def test_setup():
    """Performs some tests on the meta-data of a package"""
    process = subprocess.run(["python", "setup.py", "check"], text=True)
    assert process.returncode == 0
