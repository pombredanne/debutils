""" debfile.py

Pythonic interface for accessing .deb files
"""

import tarfile
import collections
import time

from debutils.Deb.arfile import ArFile
from debutils.Deb.util import modestr


class DebView(collections.ItemsView):
    def __str__(self):
        s = ""
        for i in self:
            s += "{mode:10s} {uid}/{gid} {size:>9d} {date:16} {member}\n".format(
                mode=modestr(i[1]["mode"]),
                uid=i[1]["uname"],
                gid=i[1]["gname"],
                size=i[1]["size"],
                date=time.strftime("%Y-%m-%d %H:%M:%S", i[1]["mtime"]),
                member=i[0]
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


                self[ti.name] = member

    def items(self):
        return DebView(self)

    def __str__(self):
        s = ""
        for i in self.items():
            s += str(i) + "\n"
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

if __name__ == "__main__":
    example = DebFile("tests/testdata/example_1.0-1_all.deb")

    print("print(example.contents())")
    print(example.contents())
    print(type(example.contents()))
    print()

    print("for i in example.contents()")
    for i in example.contents():
        print(i)
        print(type(i))