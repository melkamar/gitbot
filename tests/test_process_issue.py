import pytest
from gitbot import github_issues_bot

rules = [
    github_issues_bot.Rule(".*", "everything"),
    github_issues_bot.Rule("title test", "title label"),
    github_issues_bot.Rule("body test", "body label"),
    github_issues_bot.Rule("comment test", "comment label"),
]

# default_label | process_title | remove_current | predef_comments | predef_rules | dry_run | issues_param

issues_param = [
    (
        github_issues_bot.Issue("http://test.org",
                                "http://test.org/comments",
                                [
                                    {'name': "default_label_A"},
                                    {'name': "default_label_B"}
                                ],
                                True,
                                "Issue 1 title",
                                "Issue 1 body.",
                                1,
                                "melkamar/test"),
        ["default_label_A", "default_label_B", "everything"],
        "", True, False, False, ["comment"], rules, True
    ),
    (
        github_issues_bot.Issue("http://test.org",
                                "http://test.org/comments",
                                [
                                    {'name': "default_label_A"},
                                    {'name': "default_label_B"}
                                ],
                                True,
                                "Issue 1 title test",
                                "Issue 1 body.",
                                1,
                                "melkamar/test"),
        ["default_label_A", "default_label_B", "everything", "title label"],
        "", True, False, False, ["comment test"], rules, True
    ),

    # Test processing comments
    (
        github_issues_bot.Issue("http://test.org",
                                "http://test.org/comments",
                                [
                                    {'name': "default_label_A"},
                                    {'name': "default_label_B"}
                                ],
                                True,
                                "Issue 1 title test",
                                "Issue 1 body test.",
                                1,
                                "melkamar/test"),
        ["default_label_A", "default_label_B", "everything", "body label", "title label", "comment label"],
        "", True, True, False, ["comment test", "something else"], rules, True
    ),

    # Test ignoring title
    (
        github_issues_bot.Issue("http://test.org",
                                "http://test.org/comments",
                                [
                                    {'name': "default_label_A"},
                                    {'name': "default_label_B"}
                                ],
                                True,
                                "Issue 1 title test",
                                "Issue 1 body test.",
                                1,
                                "melkamar/test"),
        ["default_label_A", "default_label_B", "everything", "body label", "comment label"],
        "", False, True, False, ["comment test", "something else"], rules, True
    ),

    # Test default label
    (
        github_issues_bot.Issue("http://test.org",
                                "http://test.org/comments",
                                [
                                    {'name': "default_label_A"},
                                    {'name': "default_label_B"}
                                ],
                                True,
                                "Issue 1 title test",
                                "Issue 1 body test.",
                                1,
                                "melkamar/test"),
        ["default_label_A", "default_label_B", "default label"],
        "default label", True, True, False, ["comment test", "something else"], [github_issues_bot.Rule('abcdxyz', 'something')], True
    ),

    # Test removing current labels
    (
        github_issues_bot.Issue("http://test.org",
                                "http://test.org/comments",
                                [
                                    {'name': "default_label_A"},
                                    {'name': "default_label_B"}
                                ],
                                True,
                                "Issue 1 title test",
                                "Issue 1 body test.",
                                1,
                                "melkamar/test"),
        ["everything", "title label", "body label"],
        "", True, False, True, ["comment test", "something else"], rules, True
    ),
]


@pytest.mark.parametrize('issues_param', issues_param)
def test_process_issue(issues_param):
    issue = issues_param[0]
    expected_labels = issues_param[1]

    labels = github_issues_bot.process_issue(issue,
                                             default_label=issues_param[2],
                                             process_title=issues_param[3],
                                             process_comments=issues_param[4],
                                             remove_current=issues_param[5],
                                             predef_comments=issues_param[6],
                                             predef_rules=issues_param[7],
                                             dry_run=issues_param[8]
                                             )

    print("Expected labels: {}".format(expected_labels))
    print("Applied labels:  {}".format(labels))

    for expected_label in expected_labels:
        assert expected_label in labels

    assert len(expected_labels) == len(labels)
