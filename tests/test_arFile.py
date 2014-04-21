import pytest

from debutils._parsers.arfile import ArFile

@pytest.fixture(scope="module")
def ar(request):
    return ArFile("tests/testdata/example_1.0-1_all.deb")


class TestArFile:
    def test_errors(self):
        with pytest.raises(NotImplementedError):
            ArFile(None)

    def test_ar(self, ar):
        assert list(ar.files.keys()) == ["debian-binary",
                                         "control.tar.gz",
                                         "data.tar.gz"]
