import pytest

import odyssey as odyssey_python
import codyssey
odyssey_modules = [odyssey_python, codyssey]

def exception_map(module, exception):
    return codyssey.ODCException if module == codyssey else exception

@pytest.mark.parametrize("odyssey", odyssey_modules)
def test_error_handling(odyssey):
    """Ensure that exceptions in the C++ layer are caught and forwarded as python exceptions"""
    with pytest.raises(exception_map(odyssey, FileNotFoundError)):
        r = odyssey.Reader("No such ODB file")
