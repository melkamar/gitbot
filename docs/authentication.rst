.. _authentication:

Authentication
==============

Authentication for Gitbot is defined in file ``auth.cfg``.

By default, it is located next to the gitbot package, but can be changed via a command line parameter or when
deploying as a WSGI app. When in doubt, run ``gitbot generate`` command.

File contents
-------------

Contents of the authentication file are:

- Section ``[auth]``
   - ``gittoken=<git token>``
      Auth token from GitHub allowing Gitbot to read and push issues to the repository. To get it, navigate to:
      ``Profile settings`` > ``Developer settings`` > ``Personal access tokens`` > ``Generate new token``.

      **Warning!** This will allow Gitbot to act on your behalf in the scope of the given token! I cannot be held
      responsible for any potential damage caused by the application (however unlikely they are).
   - ``hook_secret=<custom secret>``
      Your custom webhook secret. It is used to make sure notifications coming from GitHub to the webserver instance
      of Gitbot are actually from GitHub. Fill any string you wish here and do the same for all repositories that will
      be processed by Gitbot.