import pytest

import odyssey as odyssey_python
import codyssey
odyssey_modules = [odyssey_python, codyssey]


@pytest.mark.parametrize("odyssey", odyssey_modules)
def test_error_handling(odyssey):
    """Ensure that exceptions in the C++ layer are caught and forwarded as python exceptions"""
    with pytest.raises(odyssey.ODCException):
        r = odyssey.Reader("No such ODB file")
