import pytest
import re

from debutils._parsers.debfile import DebFile


@pytest.fixture(scope="module")
def deb():
    return DebFile("tests/testdata/example_1.0-1_all.deb")


@pytest.fixture(scope="module")
def deb_contents():
    contents = []
    with open("tests/testdata/dpkg_contents_example_1.0-1_all", 'r') as d:
        for line in d.readlines():
            f = re.split(r'[\-ldrwxsS]{10} [a-z0-9]+/[a-z0-9]+\s+[0-9]+ [0-9\-]+ [0-9:]+ (.*)\n', line)

            member = f[1][:-1] if f[1][-1:] == "/" else f[1]
            member = member.split(" ->")[0] if "->" in member else member

            contents.append(member)

    return contents


@pytest.fixture(scope="module")
def dpkg_contents():
    import os.path

    # compare directly against the output of `dpkg --contents`
    if os.path.isfile("/usr/bin/dpkg"):
        import subprocess
        o =  subprocess.check_output(["/usr/bin/dpkg", "--contents", "tests/testdata/example_1.0-1_all.deb"]).decode("ascii")

    # no dpkg; use the backup file
    else:
        with open("tests/testdata/dpkg_contents_example_1.0-1_all", 'r') as d:
            o = d.read()

    return o + '\n'


class TestDebFile:
    def test_load(self, deb):
        pass

    def test_contents(self, deb, deb_contents):
        contents = list(deb_contents)
        assert len(deb.contents()) == len(contents)

        for i, f in enumerate(deb.contents()):
            assert f["name"] == contents[i]

    def test_print_contents(self, deb, dpkg_contents, capsys):
        print(deb.contents())
        out, _ = capsys.readouterr()

        assert out == dpkg_contents


