import os
import subprocess
import sys


def test_setup():
    """Performs some tests on the meta-data of a package"""
    repodir = os.path.dirname(os.path.dirname(__file__))
    setup_py = os.path.join(repodir, 'setup.py')
    subprocess.check_call([sys.executable, setup_py, "check"])
