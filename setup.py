# setup.py
# encoding: utf-8

from setuptools import setup, find_packages

import newman

setup(
    name='newman',
    version=newman.get_version(),
    description='Simple utility for making command tools.  Inspired by rake.',
    author="Matt O'Donnell",
    author_email='matt@absolutod.com',
    packages=find_packages(),
    install_requires=[
        'docutils',
        'termcolor'
    ],
    entry_points={
        'console_scripts':[
            'newman = newman.core:main',
            ]
    },
    classifiers=[
        'Operating System :: POSIX',
        'Environment :: Console'
    ]
)