import pytest
from debutils._parsers.releasefile import ReleaseFile

@pytest.fixture(scope="module",
                params=[
                    "tests/testdata/Release",
                    "http://us.archive.ubuntu.com/ubuntu/dists/precise/Release",
                    "http://http.debian.net/debian/dists/sid/Release",
                ])
def release(request):
    return ReleaseFile(request.param)


class TestReleaseFile:
    def test_parse(self, release):
        import time
        import collections
        import re

        try:
            t = [str, unicode, None]
        except NameError:
            t = [str, type(None)]

        # check fields - these fields are not necessarily mandatory
        assert type(release.origin) in t
        assert type(release.label) in t
        assert type(release.suite) in t
        assert type(release.version) in t
        assert type(release.codename) in t
        assert type(release.description) in t

        # these fields are also optional
        assert type(release.date) in [time.struct_time, type(None)]
        assert type(release.date) in [time.struct_time, type(None)]

        # these fields are not optional
        assert type(release.architectures) is list
        assert len(release.architectures) > 0
        assert type(release.components) is list
        assert len(release.components) > 0

        # and files are important
        assert type(release.files) is collections.OrderedDict
        assert len(list(release.files.keys())) > 0

        for rfile in release.files.keys():
            assert type(release.files[rfile]) is dict
            assert len(release.files[rfile]) == 4

            assert "md5" in list(release.files[rfile].keys())
            assert type(release.files[rfile]["md5"]) in t
            assert len(release.files[rfile]["md5"]) == 32
            assert re.match('^[a-f0-9]{32}$', release.files[rfile]["md5"])

            assert "sha1" in list(release.files[rfile].keys())
            assert type(release.files[rfile]["sha1"]) in t
            assert len(release.files[rfile]["sha1"]) == 40
            assert re.match('^[a-f0-9]{40}$', release.files[rfile]["sha1"])

            assert "sha256" in list(release.files[rfile].keys())
            assert type(release.files[rfile]["sha256"]) in t
            assert len(release.files[rfile]["sha256"]) == 64
            assert re.match('^[a-f0-9]{64}$', release.files[rfile]["sha256"])

            assert "size" in list(release.files[rfile].keys())
            assert type(release.files[rfile]["size"]) is int
            assert release.files[rfile]["size"] >= 0