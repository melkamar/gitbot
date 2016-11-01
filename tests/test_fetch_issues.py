from gitbot import github_issues_bot

fetch_issues_url = 'https://api.github.com/repos/{}/issues?state={}'
repository = "melkamar/mi-pyt-test-issues"


def test_fetch_issues(auth_session):
    """
    Test if number of issues obtained directly from GitHub API (as JSON)
    is equal to the number of parsed Issue objects.
    :param auth_session:
    :return:
    """
    response = auth_session.get(fetch_issues_url.format(repository, 'all'))
    issues = github_issues_bot.fetch_issues(repository, 'all', auth_session)

    assert len(issues) == len(response.json())
