import pytest
import os
import subprocess


# Skip this test if not all documentation dependencies are installed.
docs_dependencies = [
    'ipykernel',
    'nbsphinx',
    'sphinx_rtd_theme',
    'pandas',
]

for dependency in docs_dependencies:
    pytest.importorskip(dependency, reason=f"requires {dependency}")


def test_docs_build():
    """Check if documentation can be built"""

    os.chdir('./docs')
    subprocess.check_call(['make', 'html'])
    os.chdir('..')

    assert os.path.exists('docs/_build/html/index.html')
