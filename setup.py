from setuptools import setup, find_packages
import dbbackup


def get_requirements():
    return open('requirements.txt').read().splitlines()


def get_test_requirements():
    return open('requirements-tests.txt').read().splitlines()


setup(
    name='django-dbbackup',
    version=dbbackup.__version__,
    description=dbbackup.__doc__,
    author=dbbackup.__author__,
    author_email=dbbackup.__email__,
    install_requires=get_requirements(),
    tests_require=get_test_requirements(),
    license='BSD',
    url='https://github.com/django-dbbackup/django-dbbackup',
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
