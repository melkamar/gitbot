# GitHub issues bot

## Description

Will label issues on GitHub based on the issues' title, contents and/or comments. Labelling is determined by
a set of regular expression rules.

### Operation modes
There are two ways of running the bot:
* **Console** - actively polls GitHub for new issues and based on given options labels them. Run as `github_issues_bot.py console (...)`
* **Web app** - passively listens for GitHub's webhooks informing about new or changed issues. May be run from command line as `github_issues_bot.py web`
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
