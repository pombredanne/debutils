import pytest
from debutils.Deb.arfile import ArFile, ArchiveError

@pytest.fixture(scope="module",
                params=["tests/testdata/example_1.0-1_all.deb",
                open("tests/testdata/example_1.0-1_all.deb", 'rb'),
                open("tests/testdata/example_1.0-1_all.deb", 'rb').read()])
def ar(request):
    return ArFile(request.param)


class TestArFile:
    def test_errors(self):
        with pytest.raises(ArchiveError):
            ArFile(None)

        try:
            # only works in Python 3.3+
            with pytest.raises(FileNotFoundError):
                ArFile("/this/path/does/not/exist")

        except NameError:
            # on Python <=3.2, this should raise an IOError
            with pytest.raises(IOError):
                ArFile("/this/path/does/not/exist")

    def test_ar(self, ar):
        assert list(ar.files.keys()) == ["debian-binary", "control.tar.gz", "data.tar.gz"]
