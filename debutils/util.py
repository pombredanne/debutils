""" util.py

utility functions for debutils.Deb
"""

def modestr(mode):
    """
    :param int mode: unix mode
    :return: string representation of the provided mode
    """

    mstr = ""
    chrs = ["r", "w", "x"]

    for x in range(0, 9):
        if mode & (256>>x):
            mstr += chrs[x%3]

        else:
            mstr += "-"

    return mstr

def bytes_to_int(b):
    n = 0
    for octet in bytearray(b):
        n += octet
        n <<= 8
    n >>= 8

    return n

def int_to_bytes(i):
    b = []
    while i > 0:
        b.insert(0, i & 0xFF)
        i >>= 8

    return bytes(b) if len(bytes(b)) == len(b) else ''.join([ chr(c) for c in b ])