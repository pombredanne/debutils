""" debfile.py

Pythonic interface for accessing .deb files
"""

import tarfile
import arfile
import io

class DebMetadata:
    def __init__(self, debcontrol):
        self.t = tarfile.open(fileobj=debcontrol, mode='r|gz')
        self.files = self.t.getmembers()


class DebContents:
    def __init__(self, debcontents):
        self.t = tarfile.open(fileobj=debcontents, mode='r|gz')
        self.files = self.t.getmembers()


class DebFile:
    """
    Read Debian binary package files
    """
    def __init__(self, debfile):
        """
        :param debfile: file path, file handle, or byte array contents of a .deb file
        """
        self._ar = arfile.ArFile(debfile)
        self.control = DebMetadata(io.BytesIO(self._ar.files["control.tar.gz"]["data"]))
        self.data = DebContents(io.BytesIO(self._ar.files["data.tar.gz"]["data"]))

if __name__ == "__main__":
    kiosk = DebFile("/Users/magreene/Dev/kiosk/packages/final/kiosk_3.05_all.deb")
    kiosk_panel_timer = DebFile("/Users/magreene/Dev/kiosk/packages/final/kiosk-panel-timer_3.04-2_i386.deb")
    print("")
