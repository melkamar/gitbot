import betamax
import pytest
import os
from gitbot import github_issues_bot

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