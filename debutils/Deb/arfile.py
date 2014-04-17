""" arfile.py

Read `ar` archive format
"""

import collections
import struct
import io


class ArchiveError(Exception):
    pass


class ArFile:
    """
    Read GNU ar archives.

    Ar format
    =========

    Ar files have a global header, and then a file segment for each file within the archive.
    There is no compression at the Ar level.

    The following format is deduced from ar.h


    Global Header
    -------------
    magic string "<!arch>\n"

    File Segments
    -------------

    struct ar_hdr
    ====== ====== ========================================== =============
    Offset Length Name                                       Format
    ------ ------ ------------------------------------------ -------------
    0      16     Member file name; sometimes '/' terminated ASCII
    16     12     file date, seconds since epoch             ASCII decimal
    28     6      owner UID                                  ASCII decimal
    34     6      owner GID                                  ASCII decimal
    40     8      File mode                                  ASCII octal
    48     10     File size in bytes                         ASCII Decimal
    58     2      File magic; characters 0x96 0x0A           ASCII
    ====== ====== ========================================== =============

    .. note::

        All fields are defined as character arrays of the given length.

    .. note::

        Unused bytes in each header field are set to character 0x20

    .. note::

        Following the header is a 2-byte-aligned glob of the size described in the header.
        If the data ends at an odd byte offset, it is padded with 0x0A

    .. todo::

        Cannot yet write files; only read

    """

    ar_magic = bytearray([ord('!'), ord('<'), ord('a'), ord('r'), ord('c'), ord('h'), ord('>'), 0x0A])
    ar_fmagic = bytearray([0x60, 0x0A])
    ar_fpad = bytearray([0x0A])

    # struct format for struct.unpack
    ar_struct = "16s"   # char ar_name[16]
    ar_struct += "12s"  # char ar_date[12]
    ar_struct += "6s"   # char ar_uid[6]
    ar_struct += "6s"   # char ar_gid[6]
    ar_struct += "8s"   # char ar_mode[8]
    ar_struct += "10s"  # char ar_size[10]
    ar_struct += "2s"   # char ar_fmag[2]

    def __init__(self, arfile):
        """
        :param arfile: file path, file handle, or byte array of contents
        """

        # add instance data members
        self.files = collections.OrderedDict()
        self.bytes = bytearray()

        if type(arfile) is str:
            # file path; open the file and store the contents in self.bytes
            with open(arfile, 'rb') as ar:
                self.bytes = ar.read()

        if hasattr(arfile, "read"):
            self.bytes = arfile.read()

        if type(arfile) in [bytes, bytearray]:
            # file contents; just store it in self.bytes
            self.bytes = bytearray(arfile)

        self.decode()

    def decode(self):
        # check the global header
        if self.bytes[:8] != self.ar_magic:
            raise ArchiveError("Not an AR archive")

        # now loop through and populate self.files
        pos = 8

        while pos < len(self.bytes):
            unpacked = struct.unpack(self.ar_struct, self.bytes[pos:(pos + 60)])
            pos += 60

            member = {}
            member["name"] = unpacked[0].decode('utf-8').strip()  # ascii
            member["date"] = int(unpacked[1])     # decimal
            member["uid"] = int(unpacked[2])    # decimal
            member["gid"] = int(unpacked[3])      # decimal
            member["mode"] = int(unpacked[4], 8)  # octal
            member["size"] = int(unpacked[5])     # decimal
            member["fmag"] = unpacked[6]          # bytes
            member["data"] = io.BytesIO(self.bytes[pos:(pos + member["size"])])
            pos += member["size"]

            # if the data was padded, skip the pad as well
            if member["size"] % 2:
                pos += 1

            self.files[member["name"]] = member

        # now erase self.bytes so we don't have the whole thing stored twice
        del self.bytes

    def __iter__(self):
        for f in self.files:
            yield f

