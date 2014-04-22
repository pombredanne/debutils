import pytest

from debutils.Repo import Dist


@pytest.fixture(scope="module",
                params=[
                    ("tests/testdata/Release", "tests/testdata/Release.gpg"),
                    ("http://us.archive.ubuntu.com/ubuntu/dists/precise/Release",
                     "http://us.archive.ubuntu.com/ubuntu/dists/precise/Release.gpg"),
                    ("http://http.debian.net/debian/dists/sid/Release",
                     "http://http.debian.net/debian/dists/sid/Release.gpg")
                ])
def release_verify(request):
    return Dist(request.param[0], request.param[1])

@pytest.fixture(scope="module")
def release_sign(request):
    return Dist("tests/testdata/Release")


class TestDist:
    pass
