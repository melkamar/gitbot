from setuptools import setup, find_packages

setup(
    name='gitbot',
    version='0.3',
    description='Finds Czech holiday for given year.',
    author='Ondřej Caletka',
    author_email='ondrej@caletka.cz',
    maintainer='Martin Melka',
    maintainer_email='melkamar@fit.cvut.cz',
    license='MIT',
    url='https://github.com/melkamar/gitbot',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gitbot = gitbot.github_issues_bot:main'
        ]
    },
    install_requires=['flask', 'click>=6', 'requests']
)
