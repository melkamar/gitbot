import click
import requests
import configparser
import logging
import re
import time

logging.basicConfig(format="%(asctime)s: %(levelname)s: %(message)s")
logger = logging.getLogger(__file__)

fetch_issues_url = 'https://api.github.com/repos/{}/issues?state={}'
edit_issue_url = 'https://api.github.com/repos/{}/issues/{}'
github_session = None
rules = []

init_message = """
_____________________________________________
Repository processing started. Configuration:
Repository: {}
Verbosity: {}
Using auth file: {}
File of rules: {}
Checking interval: {}
Default label: {}
Skip labelled issues: {}
Search in comments: {}
Process closed issues: {}
Process issue title: {}
Remove current labels: {}
_____________________________________________
"""


class Rule:
    def __init__(self, regex, label):
        self.label = label.strip()
        self.regex = re.compile(regex)

    def __str__(self, *args, **kwargs):
        return 'RULE: {}   --->   {}'.format(self.regex, self.label)

    def check_fits(self, text):
        # logger.debug("  ## check_fits [{}] and reg [{}]".format(text, self.regex))
        if re.match(self.regex, text):
            # logger.debug("  ##    --> yeah, fits.")
            return self.label
        else:
            return None

    @staticmethod
    def parse(text):
        parts = text.split("=>", 1)
        return Rule(parts[0], parts[1])


class Issue:
    def __init__(self, url, comments_url, labels, state_open, title, body, number, reponame):
        self.url = url
        self.comments_url = comments_url
        self.labels = labels
        self.state_open = state_open
        self.title = title
        self.body = body
        self.number = number
        self.reponame = reponame

    def __str__(self):
        return 'Number #{}, Title: [{}], Body: [{}], URL: {}, ' \
               'Open: {}, Labels: {}'.format(self.number,
                                             self.title,
                                             self.body,
                                             self.url,
                                             self.state_open,
                                             self.labels)

    def has_labels(self):
        return len(self.labels) > 0

    @staticmethod
    def parse(json, repository):
        """
        Parse an issue from GitHub API response.
        :param json: JSON response
        :return:
        """
        url = json.get("url")
        labels = json.get("labels")
        comments_url = json.get("comments_url")
        body = json.get("body")
        title = json.get("title")
        number = json.get("number")

        if json.get("state") == "open":
            state_open = True
        else:
            state_open = False

        issue = Issue(url, comments_url, labels, state_open, title, body, number, repository)
        return issue


def init_session(token):
    global github_session
    github_session = requests.Session()
    github_session.headers.update({'Authorization': 'token ' + token, 'User-Agent': 'Python'})


def init_rules(filename):
    global rules
    rules = []

    line_cnt = 0
    with open(filename) as f:
        for line in f:
            line_cnt += 1

            if line.startswith("#;"):
                continue

            if "=>" not in line:
                logger.warning(
                    "Skipping rules config line #{} because it does not contain [=>]:\n    [{}]".format(line_cnt,
                                                                                                        line.strip()))
                continue

            rules.append(Rule.parse(line))


def process_issues(token, repository, default_label, skip_labelled, process_comments, process_closed_issues,
                   process_title, remove_current):
    """
    Main handling logic of the robot.
    :return:
    """

    init_session(token)

    if process_closed_issues:
        state_param = "all"
    else:
        state_param = "open"

    issues = fetch_issues(repository, state_param)

    for issue in issues:
        logger.debug("ISSUE: {}".format(issue))

        if skip_labelled and issue.has_labels():
            logger.debug("  -> Skipping because it has labels and skip_labelled is True.")
            continue

        process_issue(issue, default_label, process_comments, process_title, remove_current)


def apply_labels(issue, labels, remove_current):
    if not labels:
        return

    logger.info("Applying labels {} to issue {}.".format(labels, issue))

    patchurl = edit_issue_url.format(issue.reponame, issue.number)

    if not remove_current:
        # Init data with the current labels - we do not want to overwrite any
        data = {
            "labels": list(labels)
        }
    else:
        data = []

    for label in issue.labels:
        data['labels'].append(label['name'])

    logger.debug("  Sending PATCH to {}. Data: {}".format(patchurl, data))

    try:
        res = github_session.patch(patchurl, json=data, headers={"Content-Type": "text/plain"})
        res.raise_for_status()
    except requests.HTTPError:
        logger.error("A HTTP error occurred when updating an issue. Code: {}\nFull error: {}".format(res.status_code,
                                                                                                     res.content))


def process_issue(issue, default_label, process_comments, process_title, remove_current):
    labels = []
    for rule in rules:
        logger.debug("  Checking rule {}".format(rule))
        new_label = rule.check_fits(issue.body)

        if not new_label and process_title:
            new_label = rule.check_fits(issue.title)

        # try to match anything beside comments first,
        # comments need to be fetched and that should be avoided if possible
        if not new_label and process_comments:
            comments = fetch_comments(issue)
            for comment in comments:
                new_label = rule.check_fits(comment)
                if new_label:
                    break

        if new_label:
            labels.append(new_label)

    if default_label and not labels:
        labels.append(default_label)

    apply_labels(issue, labels, remove_current)


def fetch_issues(repository, state):
    get_url = fetch_issues_url.format(repository, state)
    logger.info("Fetching issues: {}".format(get_url))

    try:
        response = github_session.get(get_url)
        response.raise_for_status()
    except requests.HTTPError:
        logger.error(
            "A HTTP error occurred when fetching issues. Code: {}\nFull error: {}".format(response.status_code,
                                                                                          response.content))
        return []
    except requests.ConnectionError as e:
        logger.error("Could not establish connection with GitHub. Full error: {}".format(e))
        return []

    issues = []
    json_res = response.json()
    for issue in json_res:
        issues.append(Issue.parse(issue, repository))

    return issues


def fetch_comments(issue):
    try:
        response = github_session.get(issue.comments_url)
        response.raise_for_status()
        return [comment['body'] for comment in response.json()]
    except requests.HTTPError:
        logger.error(
            "A HTTP error occurred when fetching comments. Code: {}\nFull error: {}".format(response.status_code,
                                                                                            response.content))
        return []


def get_token(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config['auth']['gittoken']


def log_num_to_level(value):
    return {
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(value, logging.WARNING)


@click.command()
@click.argument('repository')
@click.option('-a', '--auth', default="auth.cfg", help="Authentication file. See auth.cfg.sample.")
@click.option('-v', '--verbose', count=True)
@click.option('-r', '--rules-file', 'rules_file', default="rules.cfg", help="File containing tagging rules.")
@click.option('-i', '--interval', default=60, help="Interval of repository checking in seconds. Default is 60 seconds.")
@click.option('-d', '--default-label', 'default_label', default="",
              help="Label to apply to an issue if no other rule worked.")
@click.option('--skip-labelled/--no-skip-labelled', 'skip_labelled', default=False,
              help="If true, all issues that are already labelled will be skipped.")
@click.option('--comments/--no-comments', 'process_comments', default=True,
              help="If true, comments will be also processed by the rules.")
@click.option('--closed-issues/--no-closed-issues', 'process_closed_issues', default=False,
              help="Should closed issues be still processed?")
@click.option('--process-title/--no-process-title', 'process_title', default=True,
              help="Should the title of the issue be matched against the rules as well?")
@click.option('--remove-current/--no-remove-current', 'remove_current', default=False,
              help="Should the current labels on an issue be removed if a rule matches?")
def main(repository, auth, verbose, rules_file, interval, default_label, skip_labelled, process_comments,
         process_closed_issues, process_title, remove_current):
    """
    REPOSITORY - Name of the repository to process, e.g. melkamar/mi-pyt-1
    """

    logger.level = log_num_to_level(verbose)
    while True:
        logger.warning(init_message.format(repository, logger.level, auth, rules_file, interval,
                                           default_label,
                                           skip_labelled,
                                           process_comments, process_closed_issues, process_title,
                                           remove_current))
        init_rules(rules_file)
        for rule in rules:
            logger.debug(rule)

        process_issues(get_token(auth), repository, default_label, skip_labelled, process_comments,
                       process_closed_issues,
                       process_title, remove_current)

        time.sleep(interval)


if __name__ == '__main__':
    main()
