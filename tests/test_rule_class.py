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
    rule = github_issues_bot.Rule.parse(input)
    assert rule


@pytest.mark.parametrize('input', incorrect_rules)
def test_parse_correct(input):
    rule = github_issues_bot.Rule.parse(input)
    assert not rule
