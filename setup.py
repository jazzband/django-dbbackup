import os
from distutils.core import setup

from dbbackup import VERSION

def get_path(fname):
    return os.path.join(os.path.dirname(__file__), fname)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

packages = []
package_dir = "dbbackup"
for dirpath, dirnames, filenames in os.walk(package_dir):
    # ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    if "__init__.py" in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)

try:
    import pypandoc
    long_description = pypandoc.convert(get_path('README.md'), 'rst')
    long_description = long_description.split(
        '<!---Illegal PyPi RST data -->')[0]
    f = open(get_path('README.rst'), 'w')
    f.write(long_description)
    f.close()
except (IOError, ImportError):
    # No long description... but nevermind, it's only for PyPi uploads.
    long_description = ""


def get_requirements():
    requirements = []
    try:
        import importlib  # @UnusedImport
    except ImportError:
        requirements.append('importlib')
    try:
        import pysftp  # @UnusedImport
    except ImportError:
        requirements.append('pysftp')

    return requirements


setup(
    name='django-dbbackup',
    version=VERSION,
    description='Management commands to help backup and restore a project database to AmazonS3, Dropbox or local disk.',
    long_description=read('README.md'),
    author='Michael Shepanski',
    author_email='mjs7231@gmail.com',
    install_requires=get_requirements(),
    license='BSD',
    url='https://github.com/mjs7231/django-dbbackup',
    keywords=['django', 'dropbox', 'database', 'backup', 'amazon', 's3'],
    packages=packages
)
