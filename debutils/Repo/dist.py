""" release.py

Generate and sign Release files
"""

from .._parsers.releasefile import ReleaseFile, ReleaseSignature


class Dist:
    def __init__(self, rfile=None, sigfile=None):
        self.release = ReleaseFile(rfile)
        self.sig = ReleaseGPGFile(sigfile)

    ##TODO: this doesn't belong here - move it to ReleaseSignature
    # def verify(self):
    #     if None in [self.release, self.sig]:
    #         raise ReleaseError("Release.verify requires both a Release and a Release signature")
    #
    #     ##TODO: implement verify
    #     # prepare to hash
    #     hash = self.sig.dump.packets()[0].hash_algorithm
    #     if hash in hashlib.algorithms_available:
    #         h = hashlib.new(hash)
    #     else:
    #         raise Exception(hash)
    #
    #     # hash the data body first
    #     h.update(self.release.bytes)
    #     ##TODO: hash the signature payload from the version through the end of the hashed subpacket data
    #     ##TODO: hash the signature packet version
    #     ##TODO: hash the length of the hashed data up to this point as a four-octet big-endian integer
    #     ##TODO: run the final hash through the signature algorithm
    #
    #     alg = self.sig.dump.packets()[0].pub_algorithm
    #
    #     raise NotImplementedError()

    # def sign_with(self, secret_key):
    #     ##TODO: implement sign_with
    #     raise NotImplementedError()