from setuptools import setup, find_packages
import shutil
import os

shutil.copy("README.md", "gitbot/")

with open("README.md") as file:
    long_description = file.read()

setup(
    name='gitbot',
    version='0.3.10',
    description='Automatically label GitHub issues based on regexp rules.',
    long_description=long_description,
    author='Martin Melka',
    author_email='melkamar@fit.cvut.cz',
    license='MIT',
    keywords='github,labeling,issues',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Bug Tracking'
    ],
    url='https://github.com/melkamar/gitbot',
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'gitbot = gitbot.github_issues_bot:main'
        ]
    },
    install_requires=['flask', 'click>=6', 'requests', 'appdirs', 'markdown', 'configparser']
)

os.remove("gitbot/README.md")
