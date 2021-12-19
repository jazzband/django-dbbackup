#!/usr/bin/env python

from pathlib import Path

from setuptools import setup, find_packages
import dbbackup


def get_requirements():
    return open('requirements.txt').read().splitlines()


def get_test_requirements():
    return open('requirements-tests.txt').read().splitlines()


project_dir = Path(__file__).parent


keywords = [
    'django', 'database', 'media', 'backup',
    'amazon', 's3' 'dropbox',
]

setup(
    name='django-dbbackup',
    version=dbbackup.__version__,
    description=dbbackup.__doc__,
    author=dbbackup.__author__,
    author_email=dbbackup.__email__,
    long_description=project_dir.joinpath("README.rst").read_text(encoding="utf-8"),
    python_requires=">=3.6",
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
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Database',
        'Topic :: System :: Archiving',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Archiving :: Compression'
    ],
)
