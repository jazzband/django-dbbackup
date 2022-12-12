#!/usr/bin/env python

from pathlib import Path

from setuptools import find_packages, setup

root_dir = Path(__file__).parent
src_dir = root_dir / "dbbackup"
with (src_dir / "VERSION").open() as f:
    version = f.read().strip()


def get_requirements():
    with (root_dir / "requirements.txt").open() as f:
        return f.read().splitlines()


def get_test_requirements():
    with (root_dir / "requirements" / "tests.txt").open() as f:
        return f.read().splitlines()


setup(
    name="django-dbbackup",
    version=version,
    description="Management commands to help backup and restore a project database and media.",
    author="Archmonger",
    author_email="archiethemonger@gmail.com",
    long_description=(root_dir / "README.rst").read_text(encoding="utf-8"),
    python_requires=">=3.7",
    install_requires=get_requirements(),
    tests_require=get_test_requirements(),
    include_package_data=True,
    zip_safe=False,
    license="BSD",
    url="https://github.com/jazzband/django-dbbackup",
    keywords=[
        "django",
        "database",
        "media",
        "backup",
        "amazon",
        "s3",
        "dropbox",
    ],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Environment :: Console",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Database",
        "Topic :: System :: Archiving",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Archiving :: Compression",
    ],
)
