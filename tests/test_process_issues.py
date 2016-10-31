from gitbot import github_issues_bot

fetch_issues_url = 'https://api.github.com/repos/{}/issues?state={}'
repository = "melkamar/mi-pyt-test-issues"


def test_fetch_issues_label(auth_session):
    issues = github_issues_bot.fetch_issues(repository, 'all', auth_session)
    response = auth_session.get(fetch_issues_url.format(repository, 'all'))

    assert len(issues) == len(response.json())
