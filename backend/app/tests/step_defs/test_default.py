import pytest
from pytest_bdd import scenarios, given, when, then, parsers


scenarios('../features/default.feature')


@given('nothing')
def default_given():
    print('Im here!')


@then(parsers.parse('test is ok'))
def default():
    """Test pytest-bdd
    """
    assert True, 'not checked'
