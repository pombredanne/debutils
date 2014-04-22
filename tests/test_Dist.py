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
    # def test_verify_release(self, release_verify):
    #     with pytest.raises(NotImplementedError):
    #         ##TODO: write this test once sign_with is implemented
    #         release_verify.verify()
    #
    # def test_sign_release(self, release_sign):
    #     with pytest.raises(NotImplementedError):
    #         ##TODO: write this test once sign_with is implemented
    #         release_sign.sign_with(None)
