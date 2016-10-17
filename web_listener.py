import os
from flask import Flask
from flask import request
import github_issues_bot

app = Flask(__name__)

actions_to_process = ['opened', 'edited']

github_issues_bot.init_rules(os.path.join(os.path.dirname(__file__), "rules.cfg"))
web_token = github_issues_bot.read_token(os.path.join(os.path.dirname(__file__), "auth.cfg"))


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


@app.route('/')
def handle_root():
    return """This web app will label issues based on their content and defined regexp rules.
    See https://github.com/melkamar/mi-pyt-1/ for more information.

    To quickly start, fill in auth.cfg and rules.cfg files and set up your GitHub repository to report
    newly created issues via a webhook to <servername>/callback."""


@app.route('/callback', methods=['POST'])
def handle_callback():
    """
    Handle GitHub issue callback.
    :return:
    """
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
