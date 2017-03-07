.. _rules-file:

Labelling rules
===============

Rules for issue labelling by Gitbot is defined in file ``rules.cfg``.

By default, it is located next to the gitbot package, but can be changed via a command line parameter or when
deploying as a WSGI app. When in doubt, run ``gitbot generate`` command.

Rules' function
---------------

Rules for Gitbot map a regular expression pattern to a label. Simply put, each issue is scanned and matched against
the given rules. If any regexp pattern matches the issue, it is labelled with the given label. Issue is considered to
match a rule if the rule pattern matches its title or body. (Or optionally its comments, as defined by app parameters,
see :ref:`console-usage`.)

Rules' format
-------------

Rules are specified one-per-line in the following format::

   [pattern]=>[label]

For example, following pattern would assign ``generic`` label to all issues::

   .*=>generic

*Note*: Spaces matter in rules definitions. Following rule::

   hell => devil

Will NOT match issue with contents of ``hello world``, but it will match contents of ``this is hell``.

Lines starting with ``#;`` are considered comments and will be ignored by the rules processor.



