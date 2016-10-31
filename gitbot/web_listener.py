import hashlib
import hmac
import os
import textwrap

import jinja2
import markdown
from flask import Flask, request, render_template

from gitbot import github_issues_bot

app = Flask(__name__)

actions_to_process = ['opened', 'edited']

github_issues_bot.init_rules(os.path.join(github_issues_bot.get_app_dir(), "rules.cfg"))


def read_github_secret():
    return github_issues_bot.read_auth(os.path.join(github_issues_bot.get_app_dir(), "auth.cfg"), "auth", "hook_secret")


if 'TESTING' in app.config:
    web_token = "foo-web-token"
    HOOK_SECRET_KEY = "foo-secret-hook"
else:
    web_token = github_issues_bot.read_auth(os.path.join(github_issues_bot.get_app_dir(), "auth.cfg"), "auth",
                                            "gittoken")
    HOOK_SECRET_KEY = read_github_secret()


def should_process_issue(json_data):
    """
    Check request json to see if reported issue should be processed.
    :param json_data:
    :return:
    """
    try:
        return json_data['action'] in actions_to_process
    except KeyError as e:
        github_issues_bot.logger.warn("""Key "action" was not found in request JSON. This may mean that GitHub
        sent a webhook for a non-issue event.""")
        raise e


def parse_repo(json_data):
    """
    Parse repository full name from request json.
    :param json_data:
    :return:
    """
    try:
        return json_data['repository']['full_name']
    except KeyError as e:
        github_issues_bot.logger.warn("""Key "repository":"full_name" was not found in request JSON. This may mean that GitHub
        sent a webhook for a non-issue event.""")
        raise e


def check_secret_integrity():
    secret_header = request.headers['X-Hub-Signature']
    sha_name, signature = secret_header.split('=')
    if sha_name != 'sha1':
        return False

    # HMAC requires its key to be bytes, but data is strings.
    mac = hmac.new(bytearray(HOOK_SECRET_KEY, encoding="utf-8"), msg=request.data, digestmod=hashlib.sha1)
    github_issues_bot.logger.warn("Calculated hash: {}".format(mac.hexdigest()))
    return str(mac.hexdigest()) == str(signature)


@app.template_filter('markdown')
def convert_markdown(text):
    text = textwrap.dedent(text)
    result = jinja2.Markup(markdown.markdown(text, extensions=['markdown.extensions.fenced_code']))
    return result


@app.route('/')
def handle_root():
    return render_template("about.html", bodytext=readme_text)


@app.route('/callback', methods=['POST'])
def handle_callback():
    """
    Handle GitHub issue callback.
    :return:
    """
    try:
        if not check_secret_integrity():
            github_issues_bot.logger.error(
                "Secret signature does not match!!! {} - Request will not be processed.".format(
                    request.headers['X-Hub-Signature']))
            return "Secret signature does not match!!! {} - Request will not be processed.".format(
                request.headers['X-Hub-Signature'])
        else:
            github_issues_bot.logger.info("Secret signature did match.")
    except KeyError as e:
        github_issues_bot.logger.error(
            "Secret signature was not sent with request!!! It will not be processed.")
        return "Secret signature was not sent with request!!! It will not be processed."

    github_issues_bot.logger.debug("Processing callback. Request: {}".format(request.get_json()))
    data = request.get_json()

    try:
        if not should_process_issue(data):
            txt = "Not processing issue. Will only process actions: {}. Received: {}.".format(actions_to_process,
                                                                                              data['action'])
            github_issues_bot.logger.warning(txt)
            return txt

        github_issues_bot.init_session(web_token)

        github_issues_bot.process_issue(github_issues_bot.Issue.parse(data['issue'], parse_repo(data)))
    except KeyError as e:
        github_issues_bot.logger.warn("""Key was not found in request JSON. This may mean that GitHub
        sent a webhook for a non-issue event.""")
        return """Key was not found in request JSON. This may mean that GitHub
        sent a webhook for a non-issue event."""

    github_issues_bot.logger.info("Callback done.")
    return "Callback done."


readme_text = """# GitHub issues bot

![Travis status](https://travis-ci.com/melkamar/gitbot.svg?token=vMAJz6sAMcPRgk9vRaTy&branch=master)

## Description

Will label issues on GitHub based on the issues' title, contents and/or comments. Labelling is determined by
a set of regular expression rules.

### pip installation
`pip install gitbot`

Installs a `gitbot` executable.


### Operation modes
There are two ways of running the bot:

* **Console** - actively polls GitHub for new issues and based on given options labels them. Run as `github_issues_bot.py console (...)`
* **Web app** - passively listens for GitHub's webhooks informing about new or changed issues. The endpoint listening
for GitHub calls is `/callback`.
May be run from command line as `github_issues_bot.py web`
  or deployed as a WSGI application using this wsgi config:
```
import sys
path = '/path/to/script/folder'
if path not in sys.path:
    sys.path.append(path)

from web_listener import app as application
```

## Quick oneliner
`python ./github_issues_bot.py console -i 30 -d default-tag --no-comments --no-process-title melkamar/mi-pyt-test-issues`
Will process only body of the issue report. Any further comments nor the title of the issue will not be matched against rules.

## Rules
Rules are located in file `rules.cfg`. Any other file needs to be passed as a command line option.
The format for rules is `regexp=>desired label`.

## Authentication
Bot needs an authentication token with permissions to label issues. Token is stored in `auth.cfg` file by default. See the example file for details.

For web usage, the webhook secret has to be set in `auth.cfg` as well as the repository to be handled. The script will not do anything if the security check fails.

## Detailed parameters for console mode

```
Usage: github_issues_bot.py console [OPTIONS] REPOSITORIES...

Options:
  -a, --auth TEXT                 Authentication file. See auth.cfg.sample.
  -v, --verbose                   Much verbosity. May be repeated multiple
                                  times. More v's, more info!
  -r, --rules-file TEXT           File containing tagging rules.
  -i, --interval INTEGER          Interval of repository checking in seconds.
                                  Default is 60 seconds.
  -d, --default-label TEXT        Label to apply to an issue if no other rule
                                  applies. If empty, no label is applied.
                                  Defaults to no label.
  --process-title / --no-process-title
                                  Should the title of the issue be matched
                                  against the rules as well? Defaults to true.
  --comments / --no-comments      Should comments be also matched against the
                                  rules? Defaults to true.
  --closed-issues / --no-closed-issues
                                  Should closed issues be still processed?
                                  Defaults to false.
  --skip-labelled / --no-skip-labelled
                                  Should issues that are labelled already be
                                  skipped? Defaults to true.
  --remove-current / --no-remove-current
                                  Should the current labels on an issue be
                                  removed if a rule matches? Defaults to
                                  false.
  --help                          Show this message and exit.
```
"""
