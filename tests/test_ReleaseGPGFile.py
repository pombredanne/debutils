import pytest
from debutils._parsers.releasefile import ReleaseGPGFile

@pytest.fixture(scope="module")
def release_gpg():
    return ReleaseGPGFile("tests/testdata/Release.gpg")


class TestReleaseGPGFile:
    def test_parse(self, release_gpg):
        pass

    def test_print(self, release_gpg):
        pass