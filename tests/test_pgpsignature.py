import pytest
from debutils.pgp.signature import PGPSignature

test_files = [
    "tests/testdata/Release.gpg",
    "http://us.archive.ubuntu.com/ubuntu/dists/precise/Release.gpg",
    "http://http.debian.net/debian/dists/sid/Release.gpg"
]


@pytest.fixture(scope="module", params=test_files)
def pgpsig(request):
    return PGPSignature(request.param)


@pytest.fixture(scope="module", params=test_files)
def pgpdump(request):
    import pgpdump
    import requests

    if "://" in request.param:
        raw = requests.get(request.param).content
    else:
        with open(request.param, 'rb') as r:
            raw = r.read()

    return pgpdump.AsciiData(raw)

class TestPGPSignature:
    def test_parse(self, pgpsig, pgpdump):
        ##TODO: compare pgpdump results to PGPSignature
        pass

    def test_crc24(self, pgpsig):
        assert pgpsig.crc == pgpsig.crc24()

    def test_print(self, pgpsig, capsys):
        print(pgpsig)
        out, _ = capsys.readouterr()

        assert out == pgpsig.bytes.decode() + '\n'