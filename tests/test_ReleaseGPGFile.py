import pytest
from debutils._parsers.releasefile import ReleaseGPGFile

@pytest.fixture(scope="module",
                params=[
                    "tests/testdata/Release.gpg",
                    "http://us.archive.ubuntu.com/ubuntu/dists/precise/Release.gpg",
                    "http://http.debian.net/debian/dists/sid/Release.gpg"
                ])
def release_gpg(request):
    return ReleaseGPGFile(request.param)


class TestReleaseGPGFile:
    def test_parse(self, release_gpg):
        assert release_gpg.crc == release_gpg.crc24()

    def test_print(self, release_gpg, capsys):
        print(release_gpg)
        out, _ = capsys.readouterr()

        assert out == release_gpg.bytes.decode() + '\n'