from setuptools import setup, find_packages

setup(
    name='gitbot',
    version='0.3.3',
    description='Automatically label GitHub issues based on regexp rules.',
    author='Martin Melka',
    author_email='melkamar@fit.cvut.cz',
    license='MIT',
    url='https://github.com/melkamar/gitbot',
    include_package_data=True,
    # package_data={'gitbot': ['README.md']},
    # data_files=[("", ["README.md", ]),
    #             ("gitbot/static/css", [
    #                 "static/css/bootstrap.css",
    #                 "static/css/bootstrap.min.css",
    #             ]),
    #             ("gitbot/templates", [
    #                 "templates/about.html"])],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gitbot = gitbot.github_issues_bot:main'
        ]
    },
    install_requires=['flask', 'click>=6', 'requests', 'appdirs', 'markdown', ]
)
