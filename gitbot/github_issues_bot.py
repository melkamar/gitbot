import configparser
import logging
import re
import os
import time

import click
import requests
import appdirs

logging.basicConfig(format="%(asctime)s: %(levelname)s: %(message)s", level=logging.DEBUG, filename="bot.log")
logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler())

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
    """
    Class representing a Gitbot labelling rule.

    It contains two pieces of information - a regexp pattern and the associated label.

    It also provides methods for ease of work with rules.
    """

    def __init__(self, regex, label):
        self.label = label.strip()
        self.regex = re.compile(regex, re.IGNORECASE)

    def __str__(self, *args, **kwargs):
        return 'RULE: {}   --->   {}'.format(self.regex, self.label)

    def check_fits(self, text):
        """
        Check if this rule fits (applies to) the given text.

        .. testsetup::

           from gitbot.github_issues_bot import Rule

        Usage example:
           >>> rule = Rule("[Hh]ello", "welcoming")
           >>> rule.check_fits("hello dev!")
           'welcoming'
           >>> rule.check_fits("Hello, how are you?")
           'welcoming'
           >>> rule.check_fits("Hell no.") is None
           True


        Args:
            text (str): Text for which to test the rule.

        Returns:
            str: Label name if the rule does fit, or None if it does not fit.

        """
        # logger.debug("  ## check_fits [{}] and reg [{}]".format(text, self.regex))
        if re.search(self.regex, text):
            # logger.debug("  ##    --> yeah, fits.")
            return self.label
        else:
            return None

    @staticmethod
    def parse(text):
        """
        Create a new Rule instance from a line of text.

        .. testsetup::

           from gitbot.github_issues_bot import Rule

        Usage example:
           >>> rule = Rule.parse("some\s+regexp=>new label")
           >>> rule is not None
           True
           >>> rule.regex.pattern
           'some\\\\s+regexp'
           >>> rule.label
           'new label'

        Args:
            text (str): String defining the Rule instance. The syntax is "regexp=>label_name".

        Returns:
           Rule: Returns a new instance of Rule if parsing succeeded, None otherwise.
        """
        if "=>" in text:
            parts = text.split("=>", 1)
            return Rule(parts[0], parts[1])
        else:
            logger.warn("Cannot parse rule \"{}\". There is no \"=>\".")
            return None


class Issue:
    """
    Class representing an issue on GitHub. It contains information relevant to labelling of the issue, but not all
    the information that GitHub provides.
    """

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
        return 'Number #{}, Title: [{}], Body: [{}], URL: {}'.format(self.number,
                                                                     self.title,
                                                                     self.body,
                                                                     self.url)

    def has_labels(self):
        return len(self.labels) > 0

    @staticmethod
    def parse(json_response, repository):
        """
        Create an issue from GitHub API response.

        .. testsetup::

           from gitbot.github_issues_bot import Issue
           import json

        Usage example:
           >>> issue_json = json.loads('''{
           ...    "url": "https://api.github.com/repos/somethingsomething",
           ...    "comments_url": "https://api.github.com/repos/somethingsomething/comments",
           ...    "labels":[
           ...       {
           ...           "id": 208045946,
           ...           "url": "https://api.github.com/repos/somethingsomething/labels/bug",
           ...           "name": "bug",
           ...           "color": "f29513",
           ...           "default": true
           ...       }
           ...    ],
           ...    "body": "This is a body of the issue.",
           ...    "title": "This is a title.",
           ...    "number": 666
           ... }''')
           >>> issue  = Issue.parse(issue_json, "somethingsomething")
           >>> issue.body
           'This is a body of the issue.'
           >>> issue.title
           'This is a title.'
           >>> issue.number
           666
           >>> len(issue.labels)
           1
           >>> issue.url
           'https://api.github.com/repos/somethingsomething'
           >>> issue.comments_url
           'https://api.github.com/repos/somethingsomething/comments'

           >>> issue_json = json.loads('''{
           ...    "url": "https://api.github.com/repos/somethingsomething",
           ...    "comment": "this is an invalid json"
           ... }''')
           >>> issue = Issue.parse(issue_json, "something")
           >>> issue is None
           True


        Args:
            json_response (json): GitHub API response encoded in a json object.
               It must contain a single object, not a list of objects. For details, refer to Issues_.
            repository (str): Name of the repository the issue belongs to, e.g. ``username/somerepo``.

        .. _Issues: https://developer.github.com/v3/issues/

        Returns:
            Issue: Issue instance if parsing succeeded, None otherwise.

        """
        url = json_response.get("url")
        labels = json_response.get("labels")
        comments_url = json_response.get("comments_url")
        body = json_response.get("body")
        title = json_response.get("title")
        number = json_response.get("number")

        if not url or not comments_url or not title or not number:
            return None

        if json_response.get("state") == "open":
            state_open = True
        else:
            state_open = False

        issue = Issue(url, comments_url, labels, state_open, title, body, number, repository)
        return issue


def get_config_dir():
    return appdirs.user_config_dir("gitbot", "melkamar")


def get_app_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def get_pkg_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__)))


def init_session(token, session=None):
    """
    Create an authorized session object for GitHub.

    Args:
        token(str): Authentication token for GitHub. See Tokens_.
        session(requests.Session, optional): A session object to be used, if supplied, this method simply
            sets the internal session object to the one passed in this parameter (instead of creating a new one).

    .. _Tokens: https://help.github.com/articles/creating-an-access-token-for-command-line-use/

    Returns: None, the session is set internally via a member variable.
    """
    global github_session

    if not session:
        github_session = requests.Session()
    else:
        github_session = session

    github_session.headers.update({'Authorization': 'token ' + token, 'User-Agent': 'Python'})


def init_rules(filename):
    try:
        init_rules_logic(filename)
    except FileNotFoundError as err:
        fn = os.path.join(get_config_dir(), "rules.cfg")
        logger.warn("Rules file {} not found. Will try file in user config dir: {}".format(filename, fn))
        try:
            init_rules_logic(fn)
            logger.warn("... user rules config file found. OK.")
        except FileNotFoundError as err:
            logger.error(
                "Rules file {} not found either. You need to supply it. "
                "Run script with \"generate\" command.".format(fn))
            exit(1)


def init_rules_logic(filename):
    """
    Initialize global rules store with rules defined in a file. This method does not handle file existence, permissions
    etc. That is the responsibility of its caller.

    Args:
        filename(str): Path to file containing the rules.

    Returns:
        None.

    """
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


def process_issues(token, repository, default_label="", skip_labelled=True, process_comments=True,
                   process_closed_issues=False, process_title=True, remove_current=False):
    """
    Main handling logic of app. Processes issues in a given repository with the given settings.
    Parameters correspond to command-line arguments.

    Args:
        token(str): GitHub authentication token. Refer to Issues_.
        repository(str): Name of the repository being processed. E.g. ``foobar/repo``
        default_label(str, optional): Label that should be applied to an issue if no rule fits. If empty or None,
            no default label is applied.
        skip_labelled(bool): If true, issues that are already labelled will be skipped.
        process_comments(bool): If true, comments on the issue will be processed as well. Otherwise, only body of the
            issue is.
        process_closed_issues(bool): If true, issues that are marked as closed will be processed as well as open ones.
        process_title(bool): If true, title of the issue will be processed as well as its body.
        remove_current(bool): If true, all current labels on issues will be removed and replaced by newly added ones.

    Returns:
        None.

    .. _Issues: https://developer.github.com/v3/issues/
    """
    init_session(token)

    if process_closed_issues:
        state_param = "all"
    else:
        state_param = "open"

    issues = fetch_issues(repository, state_param)

    for issue in issues:
        logger.debug("Issue: {}".format(issue))

        if skip_labelled and issue.has_labels():
            logger.info("  -> Skipping issue {} because it has labels and skip_labelled is True.".format(issue))
            continue

        process_issue(issue, default_label, process_comments, process_title, remove_current)


def apply_labels(issue, labels):
    """
    Apply given labels to an issue on GitHub.

    Args:
        issue(Issue): Issue object to which to apply labels.
        labels(:obj:`list` of :obj:`str`): List of labels to apply.

    Returns:
        None

    """

    if not labels:
        return

    patchurl = edit_issue_url.format(issue.reponame, issue.number)

    logger.info("Applying labels {} to issue {}. ".format(labels, issue))

    logger.debug("  Sending PATCH to {}. Data: {}".format(patchurl, labels))

    data = {'labels': labels}

    try:
        res = github_session.patch(patchurl, json=data, headers={"Content-Type": "text/plain"})
        res.raise_for_status()
    except requests.HTTPError:
        logger.error("A HTTP error occurred when updating an issue. Code: {}\nFull error: {}".format(res.status_code,
                                                                                                     res.content))


def process_issue(issue, default_label="", process_comments=True, process_title=True, remove_current=False,
                  predef_comments=None, predef_rules=None, dry_run=False):
    """
    Handle logic of rule matching and labelling of a given issue, including sending a request to GitHub.

    For details about parameters, see :func:`process_issues()`.

    .. testsetup::

       from gitbot.github_issues_bot import process_issue

    Usage example:
       - Create issue and expect a label to be assigned to it.
           >>> test_issue = Issue("<url>", "<url>",
           ...    [{'name':'labelA'}, {'name':'labelB'}], True, "Test issue",
           ...    "Test body. My cool string.", 42, "example/foo")
           >>> labels = process_issue(test_issue,
           ...    predef_rules=[Rule(r'cool', 'cool label')], predef_comments=['comment'], dry_run=True)
           >>> 'cool label' in labels
           True
           >>> sorted(labels)
           ['cool label', 'labelA', 'labelB']

       - Create issue and expect a label NOT to be assigned to it, only the original labels should stay.
           >>> test_issue = Issue("<url>", "<url>",
           ...    [{'name':'labelA'}, {'name':'labelB'}], True, "Test issue",
           ...    "Test body. My cool string.", 42, "example/foo")
           >>> labels = process_issue(test_issue,
           ...   predef_rules=[Rule(r'hot', 'hot label')], predef_comments=['comment'], dry_run=True)
           >>> 'hot label' in labels
           False
           >>> sorted(labels)
           ['labelA', 'labelB']

    Args:
        issue(Issue): Issue to be processed.
        default_label(str):
        process_comments(bool):
        process_title(bool):
        remove_current(bool):
        predef_comments(:obj:`list` of :obj:`str`, optional): If set, comments are not fetched from the issue, but instead the ones
            supplied through this parameter are used. Useful for testing, not much else.
        predef_rules(:obj:`list` of :obj:`Rule`, optional): If set, rules are not loaded from the rules file, but instead the ones
            supplied through this parameter are used. Useful for testing, not much else.
        dry_run(bool, optional): If true, issue is processed, but nothing is actually pushed to GitHub.

    Returns:
        :obj:`list` of :obj:`str`: Returns list of labels newly associated with the issue.
    """
    labels = []

    if predef_rules:
        rules_list = predef_rules
    else:
        rules_list = rules

    for rule in rules_list:
        logger.debug("  Checking rule {}".format(rule))
        new_label = rule.check_fits(issue.body)

        if not new_label and process_title:
            new_label = rule.check_fits(issue.title)

        # try to match anything beside comments first,
        # comments need to be fetched and that should be avoided if possible
        if not new_label and process_comments:
            if not predef_comments:
                comments = fetch_comments(issue)
            else:
                comments = predef_comments

            for comment in comments:
                new_label = rule.check_fits(comment)
                if new_label:
                    break

        if new_label:
            logger.debug("    -> rule matches.")
            labels.append(new_label)

    if default_label and not labels:
        logger.warning("No rule matches. Applying default label: {}".format(default_label))
        labels.append(default_label)

    labels_added = len(labels) > 0
    # Init data with the current labels
    data = {
        "labels": list(labels)
    }

    if not remove_current:
        for label in issue.labels:
            data['labels'].append(label['name'])
    else:
        logger.warn("Removing original labels from issue {} (Original labels: {})".format(issue, issue.labels))

    if not dry_run and labels_added:
        apply_labels(issue, labels)

    return data.get('labels')


def fetch_issues(repository, state, session=None):
    """
    Fetches all issues in a repository with the given state.
    :param repository:
    :param state:
    :return: List of Issue objects.

    Args:
        repository(str): Name of the repository to fetch.
        state(str): Issues in which states to fetch. Allowed string values: all, open, closed.
        session(:obj:`requests.Session`, optional): If supplied, use this session object instead of the internal.

    Returns:
        :obj:`list` of :obj:`Issue`: Returns list of Issue objects parsed from the given repository.

    """
    get_url = fetch_issues_url.format(repository, state)
    logger.info("Fetching issues: {}".format(get_url))

    try:
        if not session:
            response = github_session.get(get_url)
        else:
            response = session.get(get_url)
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


def fetch_comments(issue, session=None):
    """
    Fetches text of all comments of the given issue.

    Args:
        issue(Issue): Issue for which to fetch comments.
        session(:obj:`requests.Session`, optional): If supplied, use this session object instead of the internal.

    Returns:
        :obj:`list` of :obj:`str`: Returns list of strings - contents of comments.
    """
    try:
        if not session:
            response = github_session.get(issue.comments_url)
        else:
            response = session.get(issue.comments_url)
        response.raise_for_status()
        return [comment['body'] for comment in response.json()]
    except requests.HTTPError:
        logger.error(
            "A HTTP error occurred when fetching comments. Code: {}\nFull error: {}".format(response.status_code,
                                                                                            response.content))
        return []


def read_auth(filename, section, key):
    """
    Reads a key from a section in a configuration ini-formatted file.

    Args:
        filename (str): Name of the authentication file.
        section (str): Section to read from, i.e. [section] in the auth file.
        key (str): Particular key inside the given section to read.

    Returns:
        str: Value read from the file.
    """
    config = configparser.ConfigParser()
    try:
        config.read(filename)
        token = config[section][key]
        return token
    except KeyError:
        fn = os.path.join(get_config_dir(), "auth.cfg")
        logger.warn(
            "[{}]{} setting in file {} not found. Will try file in user config dir: {}".format(section, key, filename,
                                                                                               fn))
        try:
            filename = os.path.join(get_config_dir(), "auth.cfg")
            config.read(filename)
            token = config['auth']['gittoken']
            logger.warn("... user auth config file found. OK.")
            return token
        except KeyError:
            logger.error("[{}]{} setting in file {} not found either. You need to supply it. "
                         "Run script with \"generate\" command.".format(section, key, fn))
            exit(1)


def log_num_to_level(value):
    return {
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(value, logging.WARNING)


@click.group()
def main():
    pass


@main.command()
@click.argument('repositories', nargs=-1, required=True)
@click.option('-a', '--auth', default="auth.cfg", help="Authentication file. See auth.cfg.sample.")
@click.option('-v', '--verbose', count=True,
              help="Much verbosity. May be repeated multiple times. More v's, more info!")
@click.option('-r', '--rules-file', 'rules_file', default="rules.cfg", help="File containing tagging rules.")
@click.option('-i', '--interval', default=60, help="Interval of repository checking in seconds. Default is 60 seconds.")
@click.option('-d', '--default-label', 'default_label', default="",
              help="Label to apply to an issue if no other rule applies. If empty, no label is applied. Defaults to no label.")
@click.option('--process-title/--no-process-title', 'process_title', default=True,
              help="Should the title of the issue be matched against the rules as well? Defaults to true.")
@click.option('--comments/--no-comments', 'process_comments', default=True,
              help="Should comments be also matched against the rules? Defaults to true.")
@click.option('--closed-issues/--no-closed-issues', 'process_closed_issues', default=False,
              help="Should closed issues be still processed? Defaults to false.")
@click.option('--skip-labelled/--no-skip-labelled', 'skip_labelled', default=True,
              help="Should issues that are labelled already be skipped? Defaults to true.")
@click.option('--remove-current/--no-remove-current', 'remove_current', default=False,
              help="Should the current labels on an issue be removed if a rule matches? Defaults to false.")
def console(repositories, auth, verbose, rules_file, interval, default_label, skip_labelled, process_comments,
            process_closed_issues, process_title, remove_current):
    logger.level = log_num_to_level(verbose)
    while True:
        logger.warning(init_message.format(repositories, logger.level, auth, rules_file, interval,
                                           default_label,
                                           skip_labelled,
                                           process_comments, process_closed_issues, process_title,
                                           remove_current))

        init_rules(rules_file)
        token = read_auth(auth, "auth", "gittoken")

        for rule in rules:
            logger.debug(rule)

        for repository in repositories:
            process_issues(token, repository, default_label, skip_labelled, process_comments,
                           process_closed_issues,
                           process_title, remove_current)

        logger.info("Iteration done. Another will start in {} seconds.\n".format(interval))
        time.sleep(interval)


@main.command()
def web():
    """Running in web mode will automatically label all issues that are posted to the app at endpoint /callback.
    You will need the GitHub webhook secret set up both at GitHub and in the auth.cfg file for it to work."""
    from gitbot import web_listener
    web_listener.app.run(debug=True, host="0.0.0.0")
    # print("not")


auth_sample = """[auth]
gittoken=<your token>
hook_secret=<github hook secret>
"""

rules_sample = """#; Separate regex and assigned label by "=>".
#; Spaces in the regex section DO MATTER! "xyz=>abc" is NOT "xyz => abc"

bug\s+[^?]*=>bug
help=>help wanted
(how|what|why).*\?=>question
"""


@main.command()
def generate():
    """Generates config files necessary for the program to run."""
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)

    fn = os.path.join(config_dir, "auth.cfg.sample")
    if os.path.exists(fn):
        print("File {} already exists. If you want to create a new one, delete it and rerun this command.".format(fn))
    else:
        with open(fn, "w") as file:
            file.writelines(auth_sample)
        print("Created file {}. Edit it to your needs.".format(fn))

    fn = os.path.join(config_dir, "rules.cfg")
    if os.path.exists(fn):
        print("File {} already exists. If you want to create a new one, delete it and rerun this command.".format(fn))
    else:
        with open(fn, "w") as file:
            file.writelines(rules_sample)
        print("Created file {}. Edit it to your needs.".format(fn))


if __name__ == '__main__':
    main()
