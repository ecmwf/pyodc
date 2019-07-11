import pytest
import codyssey


def test_error_handling():
    """Ensure that exceptions in the C++ layer are caught and forwarded as python exceptions"""
    with pytest.raises(codyssey.ODCException):
        r = codyssey.Reader("No such ODB file")
