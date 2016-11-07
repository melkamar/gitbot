How to use Gitbot
=================

Gitbot may be run in two ways:

- :ref:`console-usage`
   Runs as a console application, all issues are re-scanned and processed every couple of minutes (interval
   customizable). Easier to set up, no requirement on setting up GitHub (aside from credentials).
- :ref:`webapp-usage`
   Runs as a web application. GitHub repositories that should be processed need to be set up with :ref:`webhooks-label`.
   Application can either be run using embedded webserver, or deployed as s WSGi application.

Labels that will be applied to issues are defined in a rules file (see :ref:`rules-file`).

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

Web server mode may be run from console with embedded server, or as a WSGI app. Both are described at the end of
this section.

In order to have web server Gitbot working, the following is necessary:

- Publicly accessible (routable) server.
- Correctly set up authentication token and webhook secret (see :ref:`authentication`).
- Web hook set up for a repository for which the token has sufficient permissions (see :ref:`webhooks-label`).

Running with embedded server
****************************

Embedded Gitbot server is started using ``gitbot web``. Unlike console mode, it is not currently possible to configure
issue processing options.

Running as WSGI application
***************************

To run Gitbot through a WSGI server, the following config is used::

   import sys
   path = '/path/to/script/folder'
   if path not in sys.path:
       sys.path.append(path)

   from web_listener import app as application

.. _webhooks-label:

GitHub web hooks
----------------

In order to use Gitbot as a passive web server, GitHub needs to notify it via a HTTP POST every time an issue is
created or edited. To do that, go to your GitHub repository and navigate to Settings > Webhooks > Add webhook, and fill
in the following information:

- Payload URL
   URL where the notification should be sent. Should be ``<gitbot-address>/callback``, e.g.
   ``https://example.com/callback``.
- Content type
   ``application/json`` is what we want.
- Secret
   Enter the same string you set up in the authentication file (see :ref:`authentication` for more details).
- Which events will trigger this webhook?
   Choose ``Let me select individual events`` > ``Issues``.

GitHub will now send a notification every time an issue is created or edited and Gitbot will react to it. Neat.