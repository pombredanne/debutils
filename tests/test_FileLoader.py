import pytest
from debutils._parsers.fileloader import FileLoader

import os.path

try:
    e = FileNotFoundError
except NameError:
    e = IOError


@pytest.fixture(scope="module",
                params=[
                    "http://www.dancewithgrenades.com/robots.txt",
                    "https://www.google.com/robots.txt"
                ])
def load_url(request):
    return FileLoader(request.param)


@pytest.fixture(scope="module",
                params=[
                    "tests/testdata/example_1.0-1_all.deb",
                    "tests/testdata/sym_example_1.0-1_all.deb",
                    open("tests/testdata/example_1.0-1_all.deb", 'rb'),
                ])
def load_local(request):
    return FileLoader(request.param)


class TestFileLoader:
    def test_load_none(self):
        loaded = FileLoader(None)

        assert loaded.bytes == b''
        assert loaded.path is None

    def test_load_url(self, load_url):
        assert load_url.bytes != b''
        assert load_url.path is None

    def test_load_local(self, load_local):
        assert load_local.bytes != b''
        assert load_local.path is not None
        assert len(load_local.bytes) == os.path.getsize(load_local.path)

    def test_load_newfile(self):
        newfile_path = os.path.realpath(os.path.dirname(".")) + "/newfile"
        loaded = FileLoader(newfile_path)

        assert loaded.bytes == b''
        assert loaded.path is not None
        assert loaded.path == newfile_path

    def test_load_invalid_path(self):
        with pytest.raises(e):
            FileLoader("/this/path/does/not/exist")

    def test_load_bytes(self):
        loaded = FileLoader(open("tests/testdata/example_1.0-1_all.deb", 'rb').read())

        assert loaded.bytes != b''
        assert loaded.path is None
        assert len(loaded.bytes) == os.path.getsize("tests/testdata/example_1.0-1_all.deb")