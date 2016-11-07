How to use Gitbot
=================

Gitbot may be run in two ways:

- :ref:`console-usage`
   Runs as a console application, all issues are re-scanned and processed every couple of minutes (interval
   customizable). Easier to set up, no requirement on setting up GitHub (aside from credentials).
- :ref:`webapp-usage`
   Runs as a web application. GitHub repositories that should be processed need to be set up with :ref:`webhooks-label`.
   Application can either be run using embedded webserver, or deployed as s WSGi application.

.. _console-usage:

Console mode
------------
Gitbot in console mode is started as ``gitbot console [OPTIONS] REPOSITORIES...``, where:

- ``REPOSITORIES`` is whitespace-separated list of GitHub repositories to process, e.g. ``melkamar/gitbot foo/bar``.
   Gitbot must have sufficient permissions to read the repository and push labels. See :ref:`authentication`.
- ``OPTIONS`` are following:
   - ``-a, --auth TEXT``
      Authentication file. See auth.cfg.sample.
   - ``-v, --verbose``
      Much verbosity. May be repeated multiple
      times. More v's, more info!

   - ``-r, --rules-file TEXT``
      File containing tagging rules.
   - ``-i, --interval INTEGER``
      Interval of repository checking in seconds. Default is 60 seconds.
   - ``-d, --default-label TEXT``
      Label to apply to an issue if no other rule applies. If empty, no label is applied.
      Defaults to no label.
   - ``--process-title / --no-process-title``
      Should the title of the issue be matched against the rules as well? Defaults to true.
   - ``--comments / --no-comments``
      Should comments be also matched against the rules? Defaults to true.
   - ``--closed-issues / --no-closed-issues``
      Should closed issues be still processed? Defaults to false.
   - ``--skip-labelled / --no-skip-labelled``
      Should issues that are labelled already be skipped? Defaults to true.
   - ``--remove-current / --no-remove-current``
      Should the current labels on an issue be removed if a rule matches? Defaults to false.


.. _webapp-usage:

Web server mode
---------------
Babab


.. _webhooks-label:

Web hooks
*********

Something something