""" key.py

"""

from .._parsers.fileloader import FileLoader


class PGPKeyCollection(object):
    def __init__(self):
        ##TODO: load/parse PGP keys from ASCII armored files
        ##TODO: load/parse PGP keys from binary files
        ##TODO: load/parse PGP keys from GPG keyrings
        pass

    ##TODO: context management magic
    def __enter__(self):
        pass

    def __exit__(self):
        pass


class PGPKey:
    pass
