# -*- coding: utf-8 -*-
import os.path
import re
import sys
from setuptools import setup
import blogofobe_blog


py_version = sys.version_info[:2]
PY3 = py_version[0] == 3
PY26 = py_version == (2, 6)
if PY3:
    if py_version < (3, 2):
        raise RuntimeError(
            'On Python 3, blogofobe requires Python 3.2 or better')
else:
    if py_version < (2, 6):
        raise RuntimeError(
            'On Python 2, blogofobe requires Python 2.6 or better')

description = blogofobe_blog.__dist__['pypi_description']
with open('README.rst', 'rt') as readme:
    long_description = readme.read()

dependencies = [
    'blogofobe',
    'six',
    ]
if PY26:
    dependencies.append('argparse')


def find_package_data(module, path):
    """Find all data files to include in the package.
    """
    files = []
    exclude = re.compile("\.pyc$|~$")
    for dirpath, dirnames, filenames in os.walk(os.path.join(module, path)):
        for filename in filenames:
            if not exclude.search(filename):
                files.append(
                    os.path.relpath(os.path.join(dirpath, filename), module))
    return {module: files}

classifiers = [
    'Programming Language :: Python :: {0}'.format(py_version)
    for py_version in ['2', '2.6', '2.7', '3', '3.2']]
classifiers.extend([
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: Implementation :: CPython',
    'Environment :: Console',
    'Natural Language :: English',
])

setup(
    name="blogofobe_blog",
    version=blogofobe_blog.__version__,
    description=blogofobe_blog.__dist__['pypi_description'],
    long_description=long_description,
    author=blogofobe_blog.__dist__["author"],
    author_email="wxl@polka.bike",
    url=blogofobe_blog.__dist__["url"],
    license="MIT",
    classifiers=classifiers,
    packages=["blogofobe_blog"],
    package_data=find_package_data("blogofobe_blog", "site_src"),
    include_package_data=True,
    install_requires=dependencies,
    zip_safe=False,
    entry_points={
        "blogofobe.plugins": ["blogofobe_blog = blogofobe_blog"]},
)
