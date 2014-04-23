""" packet.py

"""
import math
import collections
from enum import IntEnum
from datetime import datetime

from . import PGPError
from .util import bytes_to_int


class PacketField(object):
    def __init__(self, packet):
        self.raw = bytes()

        self.parse(packet)

    def parse(self, packet):
        """
        :param packet: raw packet bytes
        """
        raise NotImplementedError

    def build(self):
        """
        construct self.raw from the fields given
        """
        raise NotImplementedError


class Packet(object):
    def __init__(self, packet):
        self.raw = packet
        self.header = Header(packet)

        # parse the packet
        # signature packet
        if self.header.tag.tag == Tag.Tag.Signature:
            self.packet = Signature(packet[len(self.header.raw):])


class SubPacket(PacketField):
    class Type(IntEnum):
        ##TODO: parse more of these
        CreationTime = 0x02
        ExpirationTime = 0x03
        Issuer = 0x10

        def __str__(self):
            return str(self.name)

    def __init__(self, packet):
        self.length = 0
        self.type = 0
        self.payload = bytes()

        super(SubPacket, self).__init__(packet)

    def parse(self, packet):
        self.length = bytes_to_int(packet[0:1])
        self.raw = packet[0:self.length + 1]
        self.type = SubPacket.Type(bytes_to_int(self.raw[1:2]))

        if self.type == SubPacket.Type.CreationTime:
            self.payload = datetime.utcfromtimestamp(bytes_to_int(self.raw[2:]))

        elif self.type == SubPacket.Type.Issuer:
            # python 2.7
            if type(self.raw) is str:
                self.payload = ''.join('{:02x}'.format(ord(c)) for c in self.raw[2:]).upper().encode()
            # python 3.x
            else:
                self.payload = ''.join('{:02x}'.format(c) for c in self.raw[2:]).upper().encode()

        else:
            self.payload = self.raw[2:]


class Signature(PacketField):
    class Version(IntEnum):
        ##TODO: parse v3 packets
        v4 = 4

    class Type(IntEnum):
        ##TODO: add more items to Type list
        BinaryDocument = 0x00

    class KeyAlgo(IntEnum):
        RSAEncryptOrSign = 0x01
        RSAEncrypt = 0x02
        RSASign = 0x03
        ##TODO: bother with Elgamel?
        DSA = 0x11

    class HashAlgo(IntEnum):
        MD5 = 0x01
        SHA1 = 0x02
        RIPEMD160 = 0x03
        SHA256 = 0x08
        SHA384 = 0x09
        SHA512 = 0x0A
        SHA224 = 0x0B

        def __str__(self):
            return str(self.name)

    def __init__(self, packet):
        self.version = 0
        self.type = -1
        self.key_algorithm = 0
        self.hash_algorithm = 0
        self.hashed_subpackets = {"length": 0, "packets": collections.OrderedDict()}
        self.unhashed_subpackets = {"length": 0, "packets": collections.OrderedDict()}
        self.hash2 = None
        self.signature_ints = collections.OrderedDict()

        super(Signature, self).__init__(packet)

    def parse(self, packet):
        self.raw = packet
        self.version = Signature.Version(bytes_to_int(self.raw[0:1]))
        self.type = Signature.Type(bytes_to_int(self.raw[1:2]))
        self.key_algorithm = Signature.KeyAlgo(bytes_to_int(self.raw[2:3]))
        self.hash_algorithm = Signature.HashAlgo(bytes_to_int(self.raw[3:4]))

        # hashed subpackets
        self.hashed_subpackets["length"] = bytes_to_int(self.raw[4:6])
        pos = 6
        end = pos + self.hashed_subpackets["length"]
        while pos < end:
            sp = SubPacket(self.raw[pos:end])
            self.hashed_subpackets["packets"][str(sp.type)] = sp
            pos += len(sp.raw)

        # unhashed subpackets
        self.unhashed_subpackets["length"] = bytes_to_int(self.raw[pos:pos+2])
        pos += 2
        end = pos + self.unhashed_subpackets["length"]
        while pos < end:
            sp = SubPacket(self.raw[pos:end])
            self.unhashed_subpackets["packets"][str(sp.type)] = sp
            pos += len(sp.raw)

        self.hash2 = self.raw[pos:pos + 2]
        pos += 2

        # algorithm-specific integer(s)
        while pos < len(self.raw):
            k = len(list(self.signature_ints.keys()))
            self.signature_ints[k] = {}

            self.signature_ints[k]["length"] = bytes_to_int(self.raw[pos])
            pos += 1

            self.signature_ints[k]["int"] = bytes_to_int(self.raw[pos:pos + self.signature_ints[k]["length"]])
            pos += self.signature_ints[k]["length"]

    def get_creation_time(self):
        if "CreationTime" not in self.hashed_subpackets["packets"].keys():
            raise KeyError()

        return self.hashed_subpackets["packets"]["CreationTime"]

    def get_key_id(self):
        if "Issuer" not in self.unhashed_subpackets["packets"].keys():
            raise KeyError()

        return self.unhashed_subpackets["packets"]["Issuer"]


class Header(PacketField):
    class Format(IntEnum):
        old = 0
        new = 1

    def __init__(self, packet):
        self.tag = None
        self.length = 0

        super(Header, self).__init__(packet)

    def parse(self, packet):
        """
        There are two formats for headers

        old style
        ---------

        Old style headers can be 1, 2, 3, or 6 octets long and are composed of a Tag and a Length.
        If the header length is 1 octet (length_type == 3), then there is no Length field.

        new style
        ---------

        New style headers can be 2, 3, or 6 octets long and are also composed of a Tag and a Length.

        :param packet: raw packet bytes
        """
        self.tag = Tag(packet)

        # determine the header length including the Tag
        # old style packet header
        if self.tag.format == Header.Format.old:
            if self.tag.length_type == 0:
                self.raw = packet[:2]

            elif self.tag.length_type == 1:
                self.raw = packet[:3]

            elif self.tag.length_type == 2:
                self.raw = packet[:6]

            else:
                self.raw = packet[0]

        # new style packet header
        else:
            self.raw = packet[:2]

            if bytes_to_int(self.raw[1:]) > 191:
                self.raw = packet[:3]

            if bytes_to_int(self.raw[1:] > 8383):
                self.raw = packet[:6]

        # if the length is provided, parse it
        if len(self.raw) > 1:
            self.length = bytes_to_int(self.raw[1:])


class Tag(PacketField):
    class Tag(IntEnum):
        Invalid = 0
        Signature = 2

    def __init__(self, packet):
        self.always_1 = 0
        self.format = 0
        self.tag = 0
        self.length_type = 0

        super(Tag, self).__init__(packet)

    def parse(self, packet):
        """
        The packet tag is the first byte
        comprising of the following fields

        +-------------+----------+---------------+---+---+---+---+----------+----------+
        | byte        | 1                                                              |
        +-------------+----------+---------------+---+---+---+---+----------+----------+
        | bit         | 7        | 6             | 5 | 4 | 3 | 2 | 1        | 0        |
        +-------------+----------+---------------+---+---+---+---+----------+----------+
        | old-style   | always 1 | packet format | packet tag    | length type         |
        | description |          | 0 = old-style |               | 0 = 1 octet         |
        |             |          | 1 = new-style |               | 1 = 2 octets        |
        |             |          |               |               | 2 = 5 octets        |
        |             |          |               |               | 3 = no length field |
        +-------------+          +               +---------------+---------------------+
        | new-style   |          |               | packet tag                          |
        | description |          |               |                                     |
        +-------------+----------+---------------+-------------------------------------+
        :param packet: raw packet bytes
        """

        self.raw = bytes_to_int(packet[0:1])

        self.always_1 = self.raw >> 7
        if self.always_1 != 1:
            raise PGPError("Malformed tag!")

        self.format = Header.Format((self.raw >> 6) & 1)

        # old style
        if self.format == Header.Format.old:
            self.tag = Tag.Tag((self.raw >> 2) & 0xF)
            self.length_type = self.raw & 0x3

        # new style
        else:
            self.tag = Tag.Tag(self.raw & 0x3F)

        if self.tag == Tag.Tag.Invalid:
            raise PGPError("Invalid tag!")