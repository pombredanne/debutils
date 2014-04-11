from distutils.core import setup
from pip.req import parse_requirements
import pydeb._author

# long_description is the contents of README.rst
with open('README.rst') as readme:
    long_desc = readme.read()

# requirements generators
reqs = parse_requirements('requirements.txt')
test_reqs = parse_requirements('requirements-test.txt')

##TODO: fill in blank fields
setup(
    name             = 'PyDeb',
    version          = pydeb._author.__version__,
    description      = 'Python library for doing things with Debian packages and repositories',
    long_description = long_desc,
    author           = pydeb._author.__author__,
    license          = pydeb._author.__license__,
    platform         = 'any',
    url              = "",
    download_url     = "",

    classifiers = [],
    keywords    = [],

    install_requires = [str(ir.req) for ir in reqs],

    packages = [],
)