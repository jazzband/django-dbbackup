#!/usr/bin/env python
import os
from setuptools import setup, find_packages
import dbbackup


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


def get_requirements():
    with open(os.path.join(ROOT_DIR, 'requirements.txt')) as fh:
        return fh.read().splitlines()


def get_test_requirements():
    with open(os.path.join(ROOT_DIR, 'requirements-tests.txt')) as fh:
        return fh.read().splitlines()


def get_long_description():
    with open(os.path.join(ROOT_DIR, 'README.rst')) as fh:
        return fh.read()


keywords = [
    'django', 'database', 'media', 'backup',
    'amazon', 's3' 'dropbox',
]

setup(
    name='django-dbbackup',
    version=dbbackup.__version__,
    description=dbbackup.__doc__,
    long_description=get_long_description(),
    author=dbbackup.__author__,
    author_email=dbbackup.__email__,
    install_requires=get_requirements(),
    tests_require=get_test_requirements(),
    license='BSD',
    url=dbbackup.__url__,
    keywords=keywords,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Database',
        'Topic :: System :: Archiving',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Archiving :: Compression'
    ],
)
