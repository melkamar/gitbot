# Python task 1 - GitHub issues bot

## Quick oneliner
`python ./github-issues-bot.py -i 30 -d default-tag --no-comments --no-process-title melkamar/mi-pyt-test-issues`  
Will process only body of the issue report. Any further comments nor the title of the issue will not be matched against rules.

## Rules
Rules are located in file `rules.cfg`. Any other file needs to be passed as a command line option.  
The format for rules is `regexp=>desired label`.

## Detailed parameters
```
Usage: github-issues-bot.py [OPTIONS] [REPOSITORIES]...

  REPOSITORIES - Names of the repositories to process, e.g. melkamar/mi-
  pyt-1. Accepts whitespace-separated list.

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
  --skip-labelled / --no-skip-labelled
                                  Should issues that are labelled already be
                                  skipped? Defaults to true.
  --comments / --no-comments      Should comments be also matched against the
                                  rules? Defaults to true.
  --closed-issues / --no-closed-issues
                                  Should closed issues be still processed?
                                  Defaults to false.
  --process-title / --no-process-title
                                  Should the title of the issue be matched
                                  against the rules as well? Defaults to true.
  --remove-current / --no-remove-current
                                  Should the current labels on an issue be
                                  removed if a rule matches? Defaults to
                                  false.
  --help                          Show this message and exit.
  ```
