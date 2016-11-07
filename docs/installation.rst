Gitbot installation
===================

pip
---

To download and install Gitbot as an executable script, run ``pip install gitbot``. Handy for console usage or quick
testing.

To install as a WSGi web application, run ``pip download gitbot`` instead. This will download the package without installing
it and you may set up your WSGi server to use the files inside the package. See :ref:`webapp-usage` for more info.

GitHub
------

You may download and install Gitbot from sources. To do that, run ``git clone https://github.com/melkamar/gitbot.git``.
Sources will be downloaded in your current working directory. Inside that directory you then may run:

- ``python setup.py test`` to run tests.
- ``python setup.py install`` to install the package, including creating an executable script.