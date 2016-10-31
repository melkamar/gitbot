import os
import pytest
from gitbot import github_issues_bot
import betamax

fetch_issues_url = 'https://api.github.com/repos/{}/issues?state={}'
repository = "melkamar/mi-pyt-test-issues"

with betamax.Betamax.configure() as config:
    if 'AUTH_FILE' in os.environ:
        print("Auth file set")
        TOKEN = github_issues_bot.read_auth(os.environ['AUTH_FILE'], 'auth', 'gittoken')
        config.default_cassette_options['record_mode'] = 'all'
    else:
        print("Auth file NOT set")
        TOKEN = 'no_token'
        config.default_cassette_options['record_mode'] = 'none'

    config.define_cassette_placeholder('<TOKEN>', TOKEN)

    config.cassette_library_dir = 'tests/fixtures/cassettes'


@pytest.fixture
def auth_session(betamax_session):
    betamax_session.headers.update({'Authorization': 'token ' + TOKEN, 'User-Agent': 'Python'})
    return betamax_session


@pytest.fixture
def not_auth_session(betamax_session):
    betamax_session.headers.update({'Authorization': ''})
    return betamax_session


def test_parse_correct(auth_session):
    response = auth_session.get(fetch_issues_url.format(repository, 'all'))

    json = response.json()
    for issue_json in json:
        issue = github_issues_bot.Issue.parse(issue_json, repository)
        assert issue
        assert issue.url == issue_json.get("url")
        assert issue.labels == issue_json.get("labels")
        assert issue.comments_url == issue_json.get("comments_url")
        assert issue.body == issue_json.get("body")
        assert issue.title == issue_json.get("title")
        assert issue.number == issue_json.get("number")


def test_parse_fail(not_auth_session):
    response = not_auth_session.get(fetch_issues_url.format(repository, 'all'))
    json = response.json()

    print("JSON: {}".format(json))
    issue = github_issues_bot.Issue.parse(json, repository)
    assert not issue
