import subprocess
import sys


def test_setup():
    """Performs some tests on the meta-data of a package"""
    subprocess.check_call([sys.executable, "setup.py", "check"])
