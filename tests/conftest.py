import os

import pytest

import pyodc

odc_modules = [pyodc]

codc = None
ODC_VERSION = None

if "PYODC_SKIP_CODC" not in os.environ:
    try:
        import codc

        odc_modules.append(codc)

        tmp_str = codc.lib.ffi.new("char**")
        codc.lib.lib.odc_version(tmp_str)
        ODC_VERSION = codc.lib.ffi.string(tmp_str[0]).decode("utf-8")

    except ImportError:
        msg = "Could not import codc, do you have odc installed?\nTo skip codc tests, set PYODC_SKIP_CODC flag."
        pytest.exit(msg)


def pytest_terminal_summary(terminalreporter):
    """Print out a warning if the codc tests were skipped"""

    if not codc:
        terminalreporter.ensure_newline()
        terminalreporter.section("WARNING", sep="-", yellow=True, bold=True)
        terminalreporter.line("PYODC_SKIP_CODC flag set, codc tests were skipped", yellow=True)
