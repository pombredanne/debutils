import pytest
from debutils._parsers.releasefile import ReleaseFile, ReleaseGPGFile

@pytest.fixture(scope="module")
def release():
    return ReleaseFile("tests/testdata/Release")

@pytest.fixture(scope="module")
def release_gpg():
    return ReleaseGPGFile("tests/testdata/Release.gpg")


class TestReleaseGPGFile:
    def test_releasegpgfile(self, release_gpg):
        pass
