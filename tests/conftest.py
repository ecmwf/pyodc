import pytest
import os
import pyodc


odc_modules = [pyodc]

codc = None

if 'PYODC_SKIP_CODC' not in os.environ:
    try:
        import codc
        odc_modules.append(codc)
    except:
        msg = 'Could not import codc, do you have odc installed?\nTo skip codc tests, set PYODC_SKIP_CODC flag.'
        pytest.exit(msg)


def pytest_terminal_summary(terminalreporter):
    """Print out a warning if the codc tests were skipped"""

    if not codc:
        reports = terminalreporter.getreports('')
        terminalreporter.ensure_newline()
        terminalreporter.section('WARNING', sep='-', yellow=True, bold=True)
        terminalreporter.line('PYODC_SKIP_CODC flag set, codc tests were skipped', yellow=True)
