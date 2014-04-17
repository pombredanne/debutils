import pytest
from debutils.Deb.debfile import DebFile


@pytest.fixture(scope="module",
                params=["tests/testdata/example_1.0-1_all.deb",
                        open("tests/testdata/example_1.0-1_all.deb", 'rb'),
                        open("tests/testdata/example_1.0-1_all.deb", 'rb').read()])
def deb(request):
    return DebFile(request.param)


class TestDebFile:
    def test_load(self, deb):
        pass

    def test_contents(self, deb):
        assert len(deb.contents()) == 8

        c = [".", "./usr", "./usr/share", "./usr/share/doc", "./usr/share/doc/example",
             "./usr/share/doc/example/README.Debian", "./usr/share/doc/example/copyright",
             "./usr/share/doc/example/changelog.Debian.gz"
             ]
        for i, f in enumerate(deb.contents()):
            assert f["name"] == c[i]
