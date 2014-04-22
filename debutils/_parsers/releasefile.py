""" releasefile.py

file parsers for Release and Release.gpg
"""

import collections
import re
import time

from .fileloader import FileLoader
from .pgp import PGPSignature


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


class ReleaseSignature(PGPSignature):
    pass
    ##TODO: differentiate this from PGPSignature somehow
