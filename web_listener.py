from flask import Flask
from flask import request
import github_issues_bot

app = Flask(__name__)

actions_to_process = ['opened', 'edited']
github_issues_bot.init_rules("rules.cfg")


def should_process_issue(json_txt):
    return json_txt['action'] in actions_to_process


def parse_repo(json_txt):
    return json_txt['repository']['full_name']


@app.route('/')
def handle_root():
    return "Root bohoo."


@app.route('/callback', methods=['POST'])
def handle_callback():
    data = request.get_json()
    # data = json.load(sample_json)

    if not should_process_issue(data):
        return "Not processing issue. Will only process actions: {}. Received: {}.".format(actions_to_process,
                                                                                           data['action'])

    web_token = github_issues_bot.read_token('auth.cfg')

    github_issues_bot.init_session(web_token)
    github_issues_bot.process_issue(github_issues_bot.Issue.parse(data['issue'], parse_repo(data)))
    return "Callback done."

