import pytest
from debutils._parsers.releasefile import ReleaseFile

@pytest.fixture(scope="module",
                params=[
                    "tests/testdata/Release",
                    "http://us.archive.ubuntu.com/ubuntu/dists/precise/Release",
                ])
def release(request):
    return ReleaseFile(request.param)


class TestReleaseFile:
    def test_parse(self, release):
        import time
        import collections
        import re

        try:
            t = [str, unicode]
        except NameError:
            t = [str]

        # check fields
        assert type(release.origin) in t
        assert release.origin == "Ubuntu"

        assert type(release.label) in t
        assert release.label == "Ubuntu"

        assert type(release.suite) in t
        assert release.suite == "precise"

        assert type(release.version) in t
        assert release.version == "12.04"

        assert type(release.codename) in t
        assert release.codename == "precise"

        # don't check the date since we're downloading one from the internet now
        assert type(release.date) is time.struct_time
        
        assert type(release.architectures) is list
        assert len(release.architectures) == 5
        assert release.architectures == ["amd64", "armel", "armhf", "i386", "powerpc"]

        assert type(release.components) is list
        assert len(release.components) == 4
        assert release.components == ["main", "restricted", "universe", "multiverse"]

        assert type(release.description) in t
        assert release.description == "Ubuntu Precise 12.04"

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