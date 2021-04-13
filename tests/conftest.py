import pytest
import pyodc

codc = None

try:
    import codc as codc_module
    codc = codc_module
except ImportError:
    """Skip codc tests if the odc library is not present"""


@pytest.fixture
def exception_map():
    """Returns specific exception if testing the codc module"""

    def get_exception(module, exception):
        return codc.ODCException if module == codc else exception

    return get_exception


def pytest_generate_tests(metafunc):
    """Parametrize the test functions to run over all available modules"""

    # If the `odyssey` fixture name is used, parametrize it at the time of test generation.
    #   Recipe from: https://docs.pytest.org/en/stable/parametrize.html#pytest-generate-tests
    if 'odyssey' in metafunc.fixturenames:
        odc_modules = [pyodc]

        if codc:
            odc_modules.append(codc)

        metafunc.parametrize('odyssey', odc_modules)


def pytest_terminal_summary(terminalreporter):
    """Print out a warning if the codc tests were skipped"""

    if not codc:
        reports = terminalreporter.getreports('')
        terminalreporter.ensure_newline()
        terminalreporter.section('WARNING', sep='-', yellow=True, bold=True)
        terminalreporter.line('codc tests skipped because odc library could not be found', yellow=True)
