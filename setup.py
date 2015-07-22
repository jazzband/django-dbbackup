import os
from setuptools import setup, find_packages

from dbbackup import VERSION


def get_path(fname):
    return os.path.join(os.path.dirname(__file__), fname)


def get_requirements():
    return open('requirements.txt').read().splitlines()


setup(
    name='django-dbbackup',
    version=VERSION,
    description='Management commands to help backup and restore a project database to AmazonS3, Dropbox or local disk.',
    author='Michael Shepanski',
    author_email='mjs7231@gmail.com',
    install_requires=get_requirements(),
    license='BSD',
    url='https://github.com/mjs7231/django-dbbackup',
    keywords=['django', 'dropbox', 'database', 'backup', 'amazon', 's3'],
    packages=find_packages(exclude=['tests.runtests.main']),
    test_suite='tests.runtests.main',
    classifiers=[
        'Environment :: Web Environment',
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
