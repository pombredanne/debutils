""" signature.py

PGP Signature parsing
"""
import base64
import collections
import re
import hashlib

from .._parsers.fileloader import FileLoader
from .util import bytes_to_int, int_to_bytes

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
# ...
#
# ...
#
# ...
#
# Once the data body is hashed, then a trailer is hashed.
# (...) A V4 signature hashes the packet body
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

class PGPSignature(FileLoader):
    pgp_signature_ascii_format = \
        r'^-----BEGIN PGP SIGNATURE-----$\n'\
        r'(.*)\n\n'\
        r'(.*)'\
        r'^(.{3})\n'\
        r'^-----END PGP SIGNATURE-----$\n'

    crc24_init = 0xB704CE
    crc24_poly = 0x1864CFB

    def __init__(self, sigf):
        self.ascii_headers = collections.OrderedDict()
        self.signature_packet = None
        self.crc = None

        ##TODO: handle creating a new signature
        super(PGPSignature, self).__init__(sigf)

    ##TODO: fully parse PGP signature packet
    def parse(self):
        # parsing/decoding using the RFC 4880 section on "Forming ASCII Armor"
        # https://tools.ietf.org/html/rfc4880#section-6.2
        k = re.split(self.pgp_signature_ascii_format, self.bytes.decode(), flags=re.MULTILINE | re.DOTALL)[1:-1]

        # parse header field(s)
        h = [ h for h in re.split(r'^([^:]*): (.*)$\n?', k[0], flags=re.MULTILINE) if h != '' ]
        for key, val in [ (h[i], h[i+1]) for i in range(0, len(h), 2) ]:
            self.ascii_headers[key] = val

        self.signature_packet = base64.b64decode(k[1].replace('\n', '').encode())
        self.crc = bytes_to_int(base64.b64decode(k[2].encode()))

        # verify CRC
        if self.crc != self.crc24():
            raise Exception("Bad CRC")

        ##TODO: dump fields in signature_packet per RFC 4880, without using pgpdump

    ##TODO: add signature generation function
    ##TODO: add signature verification function

    def crc24(self):
        # CRC24 computation, as described in the RFC 4880 section on Radix-64 Conversions
        #
        # The checksum is a 24-bit Cyclic Redundancy Check (CRC) converted to
        # four characters of radix-64 encoding by the same MIME base64
        # transformation, preceded by an equal sign (=).  The CRC is computed
        # by using the generator 0x864CFB and an initialization of 0xB704CE.
        # The accumulation is done on the data before it is converted to
        # radix-64, rather than on the converted data.
        if self.signature_packet is None:
            return None

        crc = self.crc24_init
        sig = [ ord(i) for i in self.signature_packet ] if type(self.signature_packet) is str else self.signature_packet

        for loc in range(0, len(self.signature_packet)):
            crc ^= sig[loc] << 16

            for i in range(0, 8):
                crc <<= 1
                if crc & 0x1000000:
                    crc ^= self.crc24_poly

        return crc & 0xFFFFFF

    def __str__(self):
        headers = ""
        for key, val in self.ascii_headers.items():
            headers += "{key}: {val}\n".format(key=key, val=val)

        # base64-encode self.signature_packet, then insert a newline every 64th character
        payload = base64.b64encode(self.signature_packet).decode()
        payload = '\n'.join(payload[i:i+64] for i in range(0, len(payload), 64))

        return \
            "-----BEGIN PGP SIGNATURE-----\n"\
            "{headers}\n"\
            "{sig}\n"\
            "={crc}\n"\
            "-----END PGP SIGNATURE-----\n".format(
                headers=headers,
                sig=payload,
                crc=base64.b64encode(int_to_bytes(self.crc)).decode(),
            )