import configparser
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

github_issues_bot.init_rules(os.path.join(os.path.dirname(__file__), "rules.cfg"))
web_token = github_issues_bot.read_token(os.path.join(os.path.dirname(__file__), "auth.cfg"))

with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    readme_text = f.read()


def read_github_secret():
    config = configparser.ConfigParser()
    try:
        config.read(os.path.join(os.path.dirname(__file__), "auth.cfg"))
        token = config['auth']['hook_secret']
        return token
    except KeyError:
        github_issues_bot.logger.error(
            "Could not find hook secret in file auth.cfg. It has to be named 'hook_secret' in section [auth].")
        exit(1)


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
