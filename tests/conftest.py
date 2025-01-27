import pytest

from jschon import create_catalogue


def pytest_addoption(parser):
    testsuite = parser.getgroup("testsuite", "JSON Schema Test Suite")
    testsuite.addoption("--testsuite-version", choices=["2019-09", "2020-12"], help="Only run tests for the specified version")
    testsuite.addoption("--testsuite-optionals", action="store_true", help="Include optional tests")
    testsuite.addoption("--testsuite-formats", action="store_true", help="Include format tests")


@pytest.fixture(scope='session', autouse=True)
def catalogue():
    return create_catalogue('2019-09', '2020-12', default=True)
