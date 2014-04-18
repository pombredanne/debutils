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