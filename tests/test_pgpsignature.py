import pytest
import pgpdump
from debutils.pgp.signature import PGPSignature

@pytest.fixture(scope="module",
                params=[
                    "tests/testdata/Release.gpg",
                    "http://us.archive.ubuntu.com/ubuntu/dists/precise/Release.gpg",
                    "http://http.debian.net/debian/dists/sid/Release.gpg"
                ])
def pgpsig(request):
    return (PGPSignature(request.param), request.param)


class TestPGPSignature:
    def test_parse(self, pgpsig):
        pgps = pgpsig[0]
        pgps_path = pgpsig[1]

        assert pgps.crc == pgps.crc24()

    def test_print(self, pgpsig, capsys):
        pgps = pgpsig[0]

        print(pgps)
        out, _ = capsys.readouterr()

        assert out == pgps.bytes.decode() + '\n'