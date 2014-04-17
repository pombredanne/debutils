from distutils.core import setup
from pip.req import parse_requirements

import debutils._author

import os

# long_description is the contents of README.rst
with open('README.rst') as readme:
    long_desc = readme.read()

# requirements generators
reqs = parse_requirements('requirements.txt')
test_reqs = parse_requirements('requirements-test.txt')

##TODO: fill in blank fields
setup(
    name             = 'Debutils',
    version          = debutils._author.__version__,
    description      = 'Python library for doing things with Debian packages and repositories',
    long_description = long_desc,
    author           = debutils._author.__author__,
    license          = debutils._author.__license__,
    platform         = 'any',
    url              = "https://github.com/Commod0re/debutils",
    download_url     = "",

    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    keywords    = [],

    install_requires = [ str(ir.req) for ir in reqs ],

    packages = [
        "debutil"
    ],
)