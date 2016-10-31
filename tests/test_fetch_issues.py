from gitbot import github_issues_bot

fetch_issues_url = 'https://api.github.com/repos/{}/issues?state={}'
repository = "melkamar/mi-pyt-test-issues"


def test_fetch_issues(auth_session):
    # TODO
    # response = auth_session.get(fetch_issues_url.format(repository, 'all'))
    # issues = github_issues_bot.fetch_issues(repository, 'all', auth_session)

    # assert len(issues) == len(response.json())
    assert True
