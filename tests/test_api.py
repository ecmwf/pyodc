import pytest


def test_error_handling(odyssey, exception_map):
    """Ensure that exceptions in the C++ layer are caught and forwarded as python exceptions"""
    with pytest.raises(exception_map(odyssey, FileNotFoundError)):
        r = odyssey.Reader("No such ODB file")
