from gitbot import github_issues_bot

fetch_issues_url = 'https://api.github.com/repos/{}/issues?state={}'
repository = "melkamar/mi-pyt-test-issues"


def test_parse_correct(auth_session):
    """
    Test if Issues are parsed correctly by comparing the object's fields directly to JSON values.
    :param auth_session:
    :return:
    """
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
    """
    Test that no issue is created when an invalid JSON is passed.
    :param not_auth_session:
    :return:
    """
    response = not_auth_session.get(fetch_issues_url.format(repository, 'all'))
    json = response.json()

    print("JSON: {}".format(json))
    issue = github_issues_bot.Issue.parse(json, repository)
    assert not issue
