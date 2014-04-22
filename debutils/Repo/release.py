""" release.py

Generate and sign Release files
"""

from .._parsers.releasefile import ReleaseFile, ReleaseGPGFile


class ReleaseError(Exception):
    pass


class Release:
    def __init__(self, rfile=None, sigfile=None):
        self.release = ReleaseFile(rfile)
        self.sig = ReleaseGPGFile(sigfile)

    def verify(self):
        if None in [self.release, self.sig]:
            raise ReleaseError("Release.verify requires both a Release and a Release signature")

        raise NotImplementedError()

    def sign_with(self, secret_key):
        ##TODO: implement sign_with
        raise NotImplementedError()