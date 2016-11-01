import pytest
from gitbot import github_issues_bot

correct_rules = ['.*=>test',
                 'abcd =>abc',
                 'abcd=> ab',
                 '^something$ => label']

incorrect_rules = ['.*',
                   'abc>abc',
                   'abc=abc',
                   'abc>=abc',
                   'abc= >abc'
                   'abc = > abc',
                   'abc= > abc',
                   'abc = >abc']


@pytest.mark.parametrize('input', correct_rules)
def test_parse_correct(input):
    """
    Test if rules are parsed correctly from valid input.
    :param input:
    :return:
    """
    rule = github_issues_bot.Rule.parse(input)
    assert rule


@pytest.mark.parametrize('input', incorrect_rules)
def test_parse_correct(input):
    """
    Test if no rules are generated from an invalid input.
    :param input:
    :return:
    """
    rule = github_issues_bot.Rule.parse(input)
    assert not rule
