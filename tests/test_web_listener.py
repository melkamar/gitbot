import json
import pytest


@pytest.fixture
def test_flask_app():
    from gitbot import web_listener
    web_listener.app.config['TESTING'] = True
    return web_listener.app.test_client()


expected_root_html_strings = [
    (True, "<h1>GitHub issues bot index page</h1>"),
    (True, "<!DOCTYPE html>"),
    (True, "Set up the <code>webhook secret</code> to secret defined in file <code>auth.cfg</code>."),
    (False, "teststring that should not be in the readme page"),
]

not_expected_root_html_strings = [
]


@pytest.mark.parametrize('expected', expected_root_html_strings)
def test_root_route(test_flask_app, expected):
    """
    Test if default (root) route returns Markdown-enabled info transformed into HTML.
    :param test_flask_app:
    :param expected:
    :return:
    """
    data = test_flask_app.get('/').data.decode('utf-8')
    print("DATA: {}".format(data))

    if expected[0]:
        assert expected[1] in data
    else:
        assert expected[1] not in data


def test_callback_empty_body(test_flask_app):
    """
    Test response when passed an empty request body.
    :param test_flask_app:
    :return:
    """
    response = test_flask_app.post('/callback')
    data = response.data.decode('utf-8')
    print(response.status_code)
    print(data)
    assert response.status_code == 400
    assert json.loads(data)['code'] == 2


def test_callback_wrong_secret(test_flask_app):
    """
    Test response when given a wrong SHA1 secret.
    :param test_flask_app:
    :return:
    """
    response = test_flask_app.post('/callback', headers={'X-Hub-Signature': 'sha1=this is a wrong signature'})
    data = response.data.decode('utf-8')
    print(response.status_code)
    print(data)
    assert response.status_code == 400
    assert json.loads(data)['code'] == 1


# Sample issues. Use Betamax in the future like in test_fetch_issues or test_issue_class.
contents_new_issue = """{"action":"opened","issue":{"url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/27","repository_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues","labels_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/27/labels{/name}","comments_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/27/comments","events_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/27/events","html_url":"https://github.com/melkamar/mi-pyt-test-issues/issues/27","id":186340662,"number":27,"title":"Another. Hello. Why is this?","user":{"login":"melkamar","id":3999871,"avatar_url":"https://avatars.githubusercontent.com/u/3999871?v=3","gravatar_id":"","url":"https://api.github.com/users/melkamar","html_url":"https://github.com/melkamar","followers_url":"https://api.github.com/users/melkamar/followers","following_url":"https://api.github.com/users/melkamar/following{/other_user}","gists_url":"https://api.github.com/users/melkamar/gists{/gist_id}","starred_url":"https://api.github.com/users/melkamar/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/melkamar/subscriptions","organizations_url":"https://api.github.com/users/melkamar/orgs","repos_url":"https://api.github.com/users/melkamar/repos","events_url":"https://api.github.com/users/melkamar/events{/privacy}","received_events_url":"https://api.github.com/users/melkamar/received_events","type":"User","site_admin":false},"labels":[],"state":"open","locked":false,"assignee":null,"assignees":[],"milestone":null,"comments":0,"created_at":"2016-10-31T17:07:55Z","updated_at":"2016-10-31T17:07:55Z","closed_at":null,"body":""},"repository":{"id":70399705,"name":"mi-pyt-test-issues","full_name":"melkamar/mi-pyt-test-issues","owner":{"login":"melkamar","id":3999871,"avatar_url":"https://avatars.githubusercontent.com/u/3999871?v=3","gravatar_id":"","url":"https://api.github.com/users/melkamar","html_url":"https://github.com/melkamar","followers_url":"https://api.github.com/users/melkamar/followers","following_url":"https://api.github.com/users/melkamar/following{/other_user}","gists_url":"https://api.github.com/users/melkamar/gists{/gist_id}","starred_url":"https://api.github.com/users/melkamar/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/melkamar/subscriptions","organizations_url":"https://api.github.com/users/melkamar/orgs","repos_url":"https://api.github.com/users/melkamar/repos","events_url":"https://api.github.com/users/melkamar/events{/privacy}","received_events_url":"https://api.github.com/users/melkamar/received_events","type":"User","site_admin":false},"private":false,"html_url":"https://github.com/melkamar/mi-pyt-test-issues","description":null,"fork":false,"url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues","forks_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/forks","keys_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/keys{/key_id}","collaborators_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/collaborators{/collaborator}","teams_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/teams","hooks_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/hooks","issue_events_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/events{/number}","events_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/events","assignees_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/assignees{/user}","branches_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/branches{/branch}","tags_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/tags","blobs_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/blobs{/sha}","git_tags_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/tags{/sha}","git_refs_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/refs{/sha}","trees_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/trees{/sha}","statuses_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/statuses/{sha}","languages_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/languages","stargazers_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/stargazers","contributors_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/contributors","subscribers_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/subscribers","subscription_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/subscription","commits_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/commits{/sha}","git_commits_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/commits{/sha}","comments_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/comments{/number}","issue_comment_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/comments{/number}","contents_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/contents/{+path}","compare_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/compare/{base}...{head}","merges_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/merges","archive_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/{archive_format}{/ref}","downloads_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/downloads","issues_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues{/number}","pulls_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/pulls{/number}","milestones_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/milestones{/number}","notifications_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/notifications{?since,all,participating}","labels_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/labels{/name}","releases_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/releases{/id}","deployments_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/deployments","created_at":"2016-10-09T11:50:47Z","updated_at":"2016-10-09T11:50:47Z","pushed_at":"2016-10-23T13:22:14Z","git_url":"git://github.com/melkamar/mi-pyt-test-issues.git","ssh_url":"git@github.com:melkamar/mi-pyt-test-issues.git","clone_url":"https://github.com/melkamar/mi-pyt-test-issues.git","svn_url":"https://github.com/melkamar/mi-pyt-test-issues","homepage":null,"size":0,"stargazers_count":0,"watchers_count":0,"language":null,"has_issues":true,"has_downloads":true,"has_wiki":true,"has_pages":false,"forks_count":0,"mirror_url":null,"open_issues_count":19,"forks":0,"open_issues":19,"watchers":0,"default_branch":"master"},"sender":{"login":"melkamar","id":3999871,"avatar_url":"https://avatars.githubusercontent.com/u/3999871?v=3","gravatar_id":"","url":"https://api.github.com/users/melkamar","html_url":"https://github.com/melkamar","followers_url":"https://api.github.com/users/melkamar/followers","following_url":"https://api.github.com/users/melkamar/following{/other_user}","gists_url":"https://api.github.com/users/melkamar/gists{/gist_id}","starred_url":"https://api.github.com/users/melkamar/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/melkamar/subscriptions","organizations_url":"https://api.github.com/users/melkamar/orgs","repos_url":"https://api.github.com/users/melkamar/repos","events_url":"https://api.github.com/users/melkamar/events{/privacy}","received_events_url":"https://api.github.com/users/melkamar/received_events","type":"User","site_admin":false}}"""
contents_labeled_issue = """{"action":"labeled","issue":{"url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/27","repository_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues","labels_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/27/labels{/name}","comments_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/27/comments","events_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/27/events","html_url":"https://github.com/melkamar/mi-pyt-test-issues/issues/27","id":186340662,"number":27,"title":"Another. Hello. Why is this?","user":{"login":"melkamar","id":3999871,"avatar_url":"https://avatars.githubusercontent.com/u/3999871?v=3","gravatar_id":"","url":"https://api.github.com/users/melkamar","html_url":"https://github.com/melkamar","followers_url":"https://api.github.com/users/melkamar/followers","following_url":"https://api.github.com/users/melkamar/following{/other_user}","gists_url":"https://api.github.com/users/melkamar/gists{/gist_id}","starred_url":"https://api.github.com/users/melkamar/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/melkamar/subscriptions","organizations_url":"https://api.github.com/users/melkamar/orgs","repos_url":"https://api.github.com/users/melkamar/repos","events_url":"https://api.github.com/users/melkamar/events{/privacy}","received_events_url":"https://api.github.com/users/melkamar/received_events","type":"User","site_admin":false},"labels":[{"id":457964918,"url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/labels/question","name":"question","color":"cc317c","default":true}],"state":"open","locked":false,"assignee":null,"assignees":[],"milestone":null,"comments":0,"created_at":"2016-10-31T17:07:55Z","updated_at":"2016-10-31T17:07:56Z","closed_at":null,"body":""},"label":{"id":457964918,"url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/labels/question","name":"question","color":"cc317c","default":true},"repository":{"id":70399705,"name":"mi-pyt-test-issues","full_name":"melkamar/mi-pyt-test-issues","owner":{"login":"melkamar","id":3999871,"avatar_url":"https://avatars.githubusercontent.com/u/3999871?v=3","gravatar_id":"","url":"https://api.github.com/users/melkamar","html_url":"https://github.com/melkamar","followers_url":"https://api.github.com/users/melkamar/followers","following_url":"https://api.github.com/users/melkamar/following{/other_user}","gists_url":"https://api.github.com/users/melkamar/gists{/gist_id}","starred_url":"https://api.github.com/users/melkamar/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/melkamar/subscriptions","organizations_url":"https://api.github.com/users/melkamar/orgs","repos_url":"https://api.github.com/users/melkamar/repos","events_url":"https://api.github.com/users/melkamar/events{/privacy}","received_events_url":"https://api.github.com/users/melkamar/received_events","type":"User","site_admin":false},"private":false,"html_url":"https://github.com/melkamar/mi-pyt-test-issues","description":null,"fork":false,"url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues","forks_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/forks","keys_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/keys{/key_id}","collaborators_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/collaborators{/collaborator}","teams_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/teams","hooks_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/hooks","issue_events_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/events{/number}","events_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/events","assignees_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/assignees{/user}","branches_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/branches{/branch}","tags_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/tags","blobs_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/blobs{/sha}","git_tags_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/tags{/sha}","git_refs_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/refs{/sha}","trees_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/trees{/sha}","statuses_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/statuses/{sha}","languages_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/languages","stargazers_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/stargazers","contributors_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/contributors","subscribers_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/subscribers","subscription_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/subscription","commits_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/commits{/sha}","git_commits_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/git/commits{/sha}","comments_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/comments{/number}","issue_comment_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues/comments{/number}","contents_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/contents/{+path}","compare_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/compare/{base}...{head}","merges_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/merges","archive_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/{archive_format}{/ref}","downloads_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/downloads","issues_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/issues{/number}","pulls_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/pulls{/number}","milestones_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/milestones{/number}","notifications_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/notifications{?since,all,participating}","labels_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/labels{/name}","releases_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/releases{/id}","deployments_url":"https://api.github.com/repos/melkamar/mi-pyt-test-issues/deployments","created_at":"2016-10-09T11:50:47Z","updated_at":"2016-10-09T11:50:47Z","pushed_at":"2016-10-23T13:22:14Z","git_url":"git://github.com/melkamar/mi-pyt-test-issues.git","ssh_url":"git@github.com:melkamar/mi-pyt-test-issues.git","clone_url":"https://github.com/melkamar/mi-pyt-test-issues.git","svn_url":"https://github.com/melkamar/mi-pyt-test-issues","homepage":null,"size":0,"stargazers_count":0,"watchers_count":0,"language":null,"has_issues":true,"has_downloads":true,"has_wiki":true,"has_pages":false,"forks_count":0,"mirror_url":null,"open_issues_count":19,"forks":0,"open_issues":19,"watchers":0,"default_branch":"master"},"sender":{"login":"melkamar-bot","id":22726301,"avatar_url":"https://avatars.githubusercontent.com/u/22726301?v=3","gravatar_id":"","url":"https://api.github.com/users/melkamar-bot","html_url":"https://github.com/melkamar-bot","followers_url":"https://api.github.com/users/melkamar-bot/followers","following_url":"https://api.github.com/users/melkamar-bot/following{/other_user}","gists_url":"https://api.github.com/users/melkamar-bot/gists{/gist_id}","starred_url":"https://api.github.com/users/melkamar-bot/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/melkamar-bot/subscriptions","organizations_url":"https://api.github.com/users/melkamar-bot/orgs","repos_url":"https://api.github.com/users/melkamar-bot/repos","events_url":"https://api.github.com/users/melkamar-bot/events{/privacy}","received_events_url":"https://api.github.com/users/melkamar-bot/received_events","type":"User","site_admin":false}}"""


def test_callback_wrong_action(test_flask_app):
    """
    Test response when given a correct secret and message, but wrong action (label instead of create).
    :param test_flask_app:
    :return:
    """
    response = test_flask_app.post('/callback',
                                   headers={'X-Hub-Signature': 'sha1=978fe7d2c7b14762626e197814b340ef604a297a'},
                                   data=contents_labeled_issue)
    data = response.data.decode('utf-8')
    print(response.status_code)
    print(data)
    assert response.status_code == 200
    assert json.loads(data)['code'] == 3


def test_callback_right_secret(test_flask_app):
    """
    Test response when everything is correct.
    :param test_flask_app:
    :return:
    """
    response = test_flask_app.post('/callback',
                                   headers={'X-Hub-Signature': 'sha1=a23236860fd3bd42091bf4a249683ef20aed4cbf'},
                                   data=contents_new_issue
                                   )
    data = response.data.decode('utf-8')
    print(response.status_code)
    print(data)
    assert response.status_code == 200
    assert json.loads(data)['code'] == 5
    assert json.loads(data)['issue_number'] == 27
