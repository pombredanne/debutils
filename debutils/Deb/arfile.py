""" arfile.py

Read `ar` archive format
"""

import collections
import struct


class ArchiveError(Exception):
    pass


class ArFile:
    """ class ArFile

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

        Unused bytes in each field are set to character 0x20

    .. note::

        Following the header is a 2-byte-aligned glob of the size described in the header.
        If the data ends at an odd byte offset, it is padded with 0x0A

    .. todo::

        Cannot yet write files; only read

    """

    class ArMembers(collections.UserDict):
        """ ArMembers

        Simple data storage class with nice dot notation access for members.
        """
        # struct format for struct.unpack
        ar_struct = "16s"   # char ar_name[16]
        ar_struct += "12s"  # char ar_date[12]
        ar_struct += "6s"   # char ar_uid[6]
        ar_struct += "6s"   # char ar_gid[6]
        ar_struct += "8s"   # char ar_mode[8]
        ar_struct += "10s"  # char ar_size[10]
        ar_struct += "2s"   # char ar_fmag[2]

        def __init__(self):
            super(ArFile.ArMembers, self).__init__()
            self.order = []

        def unpack_into(self, packed_bytes):
            """
            :param packed_bytes: bytearray of struct ar_hdr to unpack
            """
            unpacked = struct.unpack(self.ar_struct, packed_bytes)
            member = {
                "name": unpacked[0],          # ascii
                "date": int(unpacked[1]),     # decimal
                "uid": int(unpacked[2]),      # decimal
                "gid": int(unpacked[3]),      # decimal
                "mode": int(unpacked[4], 8),  # octal
                "size": int(unpacked[5]),     # decimal
                "fmag": unpacked[6],          # ascii
                "data": None,                 # bytes
            }
            self.order += member["name"]
            self.data[member["name"]] = member

        def last(self):
            """
            :return: the name of the most recently added Member item
            :raises KeyError: if no members yet exist
            """
            if len(self.order) == 0:
                raise KeyError("No keys exist")

            return self.order[-1]

        def add_bytes(self, name=None, contents=None):
            """
            :param str name: Member name to add bytes to
            :param bytearray contents: Contents of file to add to this member
            :raises KeyError:
                if there are no entries stored yet
                if `name` is not None and the key `name` does not yet exist
            """
            if len(self.data) == 0:
                raise KeyError("No keys exist")

            if name is not None and name not in self.order:
                raise KeyError("Key {key} does not exist".format(key=name))

            if name is None:
                name = self.last()

            self.data[name]["data"] = contents

    ar_magic = bytearray([ord('!'), ord('<'), ord('a'), ord('r'), ord('c'), ord('h'), ord('>'), 0x0A])
    ar_fmagic = bytearray([0x60, 0x0A])
    ar_fpad = bytearray([0x0A])

    def __init__(self, arfile):
        """
        :param arfile: file path or byte array of contents
        """

        # add instance data members
        self.files = ArFile.ArMembers()

        if type(arfile) is str:
            # file path; open the file and store the contents in self.bytes
            with open(arfile, 'rb') as ar:
                self.bytes = ar.read()

        if type(arfile) is bytearray:
            # file contents; just store it in self.bytes
            self.bytes = arfile

        self.decode()

    def decode(self):
        # check the global header
        if self.bytes[:8] != self.ar_magic:
            raise ArchiveError("Not an AR archive")

        # now loop through and populate self.files
        pos = 0

        while pos < len(self.bytes):
            self.files.unpack_into(self.bytes[pos:(pos + 60)])
            pos += 60

            name = self.files.last()
            size = self.files[name]["size"]

            # now pull over the file bytes
            self.files.add_bytes(contents=self.bytes[pos:(pos + size)])
            pos += size

            # if the data was padded, skip the pad as well
            if size % 2:
                pos += 1

        # now erase self.bytes so we don't have the whole thing stored twice
        del self.bytes

    def __iter__(self):
        for f in self.files:
            yield f
