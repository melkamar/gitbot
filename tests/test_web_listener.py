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
    data = test_flask_app.get('/').data.decode('utf-8')
    print("DATA: {}".format(data))

    if expected[0]:
        assert expected[1] in data
    else:
        assert expected[1] not in data
