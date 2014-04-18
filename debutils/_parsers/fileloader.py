""" fileloader.py

File-based metaclass to reduce duplicate code.
"""

import os.path

try:
    e = FileNotFoundError
except NameError:
    e = IOError


class FileLoader(object):
    def __init__(self, lfile):
        self.bytes = bytes()
        self.path = None

        # NoneType means we're creating a new file, probably in-memory
        if lfile is None:
            pass

        # str without NUL bytes means this is likely a file path
        # because in 2.x, bytes is str
        elif type(lfile) is str and '\x00' not in lfile:
            # does the file exist?
            if os.path.exists(lfile):

                self.path = os.path.realpath(lfile)

                with open(lfile, 'rb') as lf:
                    self.bytes = bytes(lf.read())

            # if the file does not exist, does the directory pointed to exist?
            elif os.path.isdir(os.path.dirname(lfile)):
                self.path = os.path.realpath(lfile)

            # if the file does not exist and its directory path does not exist,
            # you're gonna have a bad time
            else:
                raise e(lfile)

        # we have been passed a file-like object
        elif hasattr(lfile, "read"):
            self.bytes = bytes(lfile.read())

            # try to extract the path, too
            if hasattr(lfile, "name") and os.path.exists(os.path.realpath(lfile.name)):
                self.path = lfile.name

        # we have been passed the contents of a file that were read elsewhere
        else:
            self.bytes = bytes(lfile)


        # try to kick off the parser
        # this only works on properly implemented children of this type
        if self.bytes != bytes():
            try:
                self.parse()

            except NotImplementedError:
                pass

    def parse(self):
        raise NotImplementedError()