import pytest

import pyodc
import codc
odc_modules = [pyodc, codc]

def exception_map(module, exception):
    return codc.ODCException if module == codc else exception

@pytest.mark.parametrize("odyssey", odc_modules)
def test_error_handling(odyssey):
    """Ensure that exceptions in the C++ layer are caught and forwarded as python exceptions"""
    with pytest.raises(exception_map(odyssey, FileNotFoundError)):
        r = odyssey.Reader("No such ODB file")
