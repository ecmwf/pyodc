import pytest
import odyssey


def test_error_handling():
    """Ensure that exceptions in the C++ layer are caught and forwarded as python exceptions"""
    with pytest.raises(odyssey.ODCException):
        o = odyssey.Odb("No such ODB file")
