import pytest
import sys

import subprocess

def test_setup():
    """Performs some tests on the meta-data of a package"""
    process = subprocess.run([sys.executable, "setup.py", "check"], text=True)
    assert process.returncode == 0
