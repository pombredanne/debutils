""" debfile.py

Pythonic interface for accessing .deb files
"""

import tarfile
import collections
import time

from .._parsers.arfile import ArFile
from ..util import modestr


class DebView(collections.ItemsView):
    date_format = "%Y-%m-%d %H:%M"

    def __str__(self):
        s = ""
        for i in self:
            mode = "-"
            member = i["name"]

            if i["type"] == tarfile.DIRTYPE:
                mode = "d"
                member += "/"

            if i["type"] in [tarfile.SYMTYPE, tarfile.LNKTYPE]:
                mode = "l"
                member += " -> " + i["linkto"]

            mode += modestr(i["mode"])

            s += "{mode:10s} {uid}/{gid} {size:>9d} {date:16} {member}\n".format(
                mode=mode,
                uid=i["uname"],
                gid=i["gname"],
                size=i["size"],
                date=time.strftime(self.date_format, i["mtime"]),
                member=member
            )
        return s

    def __iter__(self):
        for key in self._mapping:
            yield self._mapping[key]


class MetaDeb(collections.OrderedDict):
    def __init__(self, debtar):
        super(MetaDeb, self).__init__()

        with tarfile.open(fileobj=debtar, mode='r:gz') as tar:
            for ti in tar:
                member = {}
                member["name"] = ti.name
                member["size"] = ti.size
                member["mtime"] = time.localtime(ti.mtime)
                member["mode"] = ti.mode
                member["type"] = ti.type
                member["uid"] = ti.uid
                member["gid"] = ti.gid
                member["uname"] = ti.uname
                member["gname"] = ti.gname
                if ti.issym() or ti.islnk():
                    member["linkto"] = ti.linkname


                self[ti.name] = member

    def items(self):
        return DebView(self)

    def __str__(self):
        s = ""
        for i in self.items():
            s += str(i)
        return s


class DebMetadata(MetaDeb):
    def __init__(self, debcontrol):
        super(DebMetadata, self).__init__(debcontrol)

        debcontrol.seek(0)
        with tarfile.open(fileobj=debcontrol, mode='r:gz') as tar:
            for cfile in self.keys():
                file = tar.extractfile(cfile)

                if file is not None:
                    self[cfile]["contents"] = file.read()


class DebContents(MetaDeb):
    def __init__(self, debcontents):
        super(DebContents, self).__init__(debcontents)


class DebFile:
    """
    Read Debian binary package files
    """
    def __init__(self, debfile):
        """
        :param debfile: file path, file handle, or byte array contents of a .deb file
        """
        self._ar = ArFile(debfile)

        self._control = DebMetadata(self._ar.files["control.tar.gz"]["data"])
        self._contents = DebContents(self._ar.files["data.tar.gz"]["data"])
        pass

    def contents(self):
        return self._contents.items()
