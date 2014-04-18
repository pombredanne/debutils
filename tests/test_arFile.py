import pytest

from debutils._parsers.arfile import ArFile


try:
    e = FileNotFoundError
except NameError:
    e = IOError

@pytest.fixture(scope="module",
                params=[
                    "tests/testdata/example_1.0-1_all.deb",
                    "tests/testdata/sym_example_1.0-1_all.deb",
                    open("tests/testdata/example_1.0-1_all.deb", 'rb'),
                    open("tests/testdata/example_1.0-1_all.deb", 'rb').read()
                ])
def ar(request):
    return ArFile(request.param)


class TestArFile:
    def test_errors(self):
        with pytest.raises(NotImplementedError):
            ArFile(None)

        with pytest.raises(e):
            ArFile("/this/path/does/not/exist")


    def test_ar(self, ar):
        assert list(ar.files.keys()) == ["debian-binary",
                                         "control.tar.gz",
                                         "data.tar.gz"]
