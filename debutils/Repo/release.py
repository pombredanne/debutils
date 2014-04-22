""" release.py

Generate and sign Release files
"""

from .._parsers.releasefile import ReleaseFile, ReleaseGPGFile


class ReleaseError(Exception):
    pass

# from the Computing Signatures section of RFC 4880 (http://tools.ietf.org/html/rfc4880#section-5.2.4)
#
# All signatures are formed by producing a hash over the signature
# data, and then using the resulting hash in the signature algorithm.
#
# For binary document signatures (type 0x00), the document data is
# hashed directly.  For text document signatures (type 0x01), the
# document is canonicalized by converting line endings to <CR><LF>,
# and the resulting data is hashed.
#
# When a signature is made over a key, the hash data starts with the
# octet 0x99, followed by a two-octet length of the key, and then body
# of the key packet.  (Note that this is an old-style packet header for
# a key packet with two-octet length.)  A subkey binding signature
# (type 0x18) or primary key binding signature (type 0x19) then hashes
# the subkey using the same format as the main key (also using 0x99 as
# the first octet).  Key revocation signatures (types 0x20 and 0x28)
# hash only the key being revoked.
#
# A certification signature (type 0x10 through 0x13) hashes the User
# ID being bound to the key into the hash context after the above
# data.  A V3 certification hashes the contents of the User ID or
# attribute packet packet, without any header.  A V4 certification
# hashes the constant 0xB4 for User ID certifications or the constant
# 0xD1 for User Attribute certifications, followed by a four-octet
# number giving the length of the User ID or User Attribute data, and
# then the User ID or User Attribute data.
#
# When a signature is made over a Signature packet (type 0x50), the
# hash data starts with the octet 0x88, followed by the four-octet
# length of the signature, and then the body of the Signature packet.
# (Note that this is an old-style packet header for a Signature packet
# with the length-of-length set to zero.)  The unhashed subpacket data
# of the Signature packet being hashed is not included in the hash, and
# the unhashed subpacket data length value is set to zero.
#
# Once the data body is hashed, then a trailer is hashed.  A V3
# signature hashes five octets of the packet body, starting from the
# signature type field.  This data is the signature type, followed by
# the four-octet signature time.  A V4 signature hashes the packet body
# starting from its first field, the version number, through the end
# of the hashed subpacket data.  Thus, the fields hashed are the
# signature version, the signature type, the public-key algorithm, the
# hash algorithm, the hashed subpacket length, and the hashed
# subpacket body.
#
# V4 signatures also hash in a final trailer of six octets: the
# version of the Signature packet, i.e., 0x04; 0xFF; and a four-octet,
# big-endian number that is the length of the hashed data from the
# Signature packet (note that this number does not include these final
# six octets).
#
# After all this has been hashed in a single hash context, the
# resulting hash field is used in the signature algorithm and placed
# at the end of the Signature packet.


class Release:
    def __init__(self, rfile=None, sigfile=None):
        self.release = ReleaseFile(rfile)
        self.sig = ReleaseGPGFile(sigfile)

    def verify(self):
        if None in [self.release, self.sig]:
            raise ReleaseError("Release.verify requires both a Release and a Release signature")
        ##TODO: implement verify

        raise NotImplementedError()

    def sign_with(self, secret_key):
        ##TODO: implement sign_with
        raise NotImplementedError()