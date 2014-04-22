""" releasefile.py

file parsers for Release and Release.gpg
"""

import collections
import re
import time
import base64

from .fileloader import FileLoader
from ..util import bytes_to_int, int_to_bytes


class ReleaseFile(FileLoader):

    date_format = "%a, %d %b %Y %H:%M:%S UTC"

    def __init__(self, release):
        # ReleaseFile fields, in order
        self.origin = None
        self.label = None
        self.suite = None
        self.version = None
        self.codename = None
        self.date = None
        self.valid_until = None
        self.architectures = []
        self.components = []
        self.description = None
        # it is more natural to implement this part inverted from the actual file
        # a File key/value will look like this (each value is a normal dict)
        # +--------------------------------------------+--------------------------------+
        # | key                                        | value                          |
        # +--------------------------------------------+--------+-----------------------+
        # | file path relative to root/dists/distname/ | md5    | md5sum of file        |
        # +                                            +--------+-----------------------+
        # |                                            | sha1   | sha1sum of file       |
        # +                                            +--------+-----------------------+
        # |                                            | sha256 | sha256sum of file     |
        # +                                            +--------+-----------------------+
        # |                                            | size   | size of file in bytes |
        # +--------------------------------------------+--------+-----------------------+
        self.files = collections.OrderedDict()

        super(ReleaseFile, self).__init__(release)

    def parse(self):
        pos = 0
        md5s = False
        sha1s = False
        sha256s = False
        while pos < len(self.bytes):
            # find the next newline
            line_end = pos + self.bytes[pos:].index(b'\n')

            # read the next line
            if line_end != -1:
                line = self.bytes[pos:line_end].decode()

            # no newlines left, so use the rest of the file
            else:
                line = self.bytes[pos:].decode()

            # increment position by the length of the line
            # and skip the newline character
            pos += len(line) + 1

            # parse in file hash entries
            if re.match(r'^ ([0-9a-f]+)\s+([0-9]+) (.*)$', line):
                f = re.split(r'^ ([0-9a-f]+)\s+([0-9]+) (.*)$', line)[1:-1]

                if f[2] not in self.files.keys():
                    self.files[f[2]] = {
                        "size": 0,
                        "md5": "",
                        "sha1": "",
                        "sha256": "",
                    }

                self.files[f[2]]["size"] = int(f[1])

                if md5s:
                    self.files[f[2]]["md5"] = f[0]

                if sha1s:
                    self.files[f[2]]["sha1"] = f[0]

                if sha256s:
                    self.files[f[2]]["sha256"] = f[0]

                continue

            # parse fields
            f = re.split(r'^([A-Za-z1256\-]+): ?', line)[1:]

            # hash field starters
            # MD5Sum:
            if f[0] == "MD5Sum":
                md5s = True
                sha1s = sha256s = False
                continue

            # SHA1:
            elif f[0] == "SHA1":
                sha1s = True
                md5s = sha256s = False
                continue

            # SHA256:
            elif f[0] == "SHA256":
                sha256s = True
                md5s = sha1s = False
                continue

            # not a hash field starter at all
            # no continue here because it's a field that is parsed further down
            else:
                md5s = sha1s = sha256s = False

            # Origin: str
            if f[0] == "Origin":
                self.origin = f[1]
                continue

            # Label: str
            if f[0] == "Label":
                self.label = f[1]
                continue

            # Suite: str
            if f[0] == "Suite":
                self.suite = f[1]
                continue

            # Version: str
            if f[0] == "Version":
                self.version = f[1]
                continue

            # Codename: str
            if f[0] == "Codename":
                self.codename = f[1]
                continue

            # Date: strptime
            if f[0] == "Date":
                self.date = time.strptime(f[1], self.date_format)
                continue

            # Valid-Until: strptime
            if f[0] == "Valid-Until":
                self.valid_until = time.strptime(f[1], self.date_format)
                continue

            # Architectures: space delimited list
            if f[0] == "Architectures":
                self.architectures = f[1].split(" ")
                continue

            # Components: space delimited list
            if f[0] == "Components":
                self.components = f[1].split(" ")
                continue

            # Description: str
            if f[0] == "Description":
                self.description = f[1]
                continue


            # some other field
            raise NotImplementedError("Unexpected input: " + line)

    def sign(self):
        ##TODO: sign a Release file
        raise NotImplementedError()


class ReleaseGPGFile(FileLoader):
    gpg_sig_format = \
        r'^-----BEGIN PGP SIGNATURE-----$\n'\
        r'(.*)\n\n'\
        r'(.*)'\
        r'^(.*)\n'\
        r'^-----END PGP SIGNATURE-----$\n'

    crc24_init = 0xB704CE
    crc24_poly = 0x1864CFB

    def __init__(self, releasesig):
        self.headers = collections.OrderedDict()
        self.sig = None
        self.crc = None

        super(ReleaseGPGFile, self).__init__(releasesig)

    def parse(self):
        # parsing/decoding using the RFC 4880 section on "Forming ASCII Armor"
        # https://tools.ietf.org/html/rfc4880#section-6.2
        k = re.split(self.gpg_sig_format, self.bytes.decode(), flags=re.MULTILINE | re.DOTALL)[1:-1]

        # parse header field(s)
        h = [ h for h in re.split(r'^([^:]*): (.*)$\n?', k[0], flags=re.MULTILINE) if h != '' ]
        for key, val in [ (h[i], h[i+1]) for i in range(0, len(h), 2) ]:
            self.headers[key] = val

        ##TODO: dump fields in sig per RFC 4880
        self.sig = base64.b64decode(k[1].replace('\n', '').encode())
        self.crc = bytes_to_int(base64.b64decode(k[2].encode()))

        ## verify CRC
        if self.crc != self.crc24():
            raise Exception("Bad CRC")

    def crc24(self):
        # CRC24 computation, as described in the RFC 4880 section on Radix-64 Conversions
        #
        # The checksum is a 24-bit Cyclic Redundancy Check (CRC) converted to
        # four characters of radix-64 encoding by the same MIME base64
        # transformation, preceded by an equal sign (=).  The CRC is computed
        # by using the generator 0x864CFB and an initialization of 0xB704CE.
        # The accumulation is done on the data before it is converted to
        # radix-64, rather than on the converted data.
        if self.sig is None:
            return None

        crc = self.crc24_init
        sig = [ ord(i) for i in self.sig ] if type(self.sig) is str else self.sig
        for loc in range(0, len(self.sig)):
            crc ^= sig[loc] << 16

            for i in range(0, 8):
                crc <<= 1
                if crc & 0x1000000:
                    crc ^= self.crc24_poly

        return crc & 0xFFFFFF

    def __str__(self):
        headers = ""
        for key, val in self.headers.items():
            headers += "{key}: {val}\n".format(key=key, val=val)

        # base64-encode self.sig, then insert a newline every 64th character
        payload = base64.b64encode(self.sig).decode()
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
