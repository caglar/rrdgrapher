import rrdtool
import tempfile
import sys
import re
import shutil
from random import randint as rint

DAY = 86400
YEAR = 365 * DAY
IMGFORMAT = "PNG"

class RNDColorPallete:
    @staticmethod
    def getRndColorPallete(noOfColors):
        colorPallete = []
        r, g, b = rint(0,255), rint(0,255), rint(0,255)
        for i in range(noOfColors):
            dr = (rint(0,107))
            dg = (rint(0,107))
            db = (rint(0,107))
            r, g, b = (r + dr) % 255, (g + dg) % 255, (b + db) % 255
            colorPallete.append("#%02x%02x%02x" % (r, g, b))
        return colorPallete

class RRDGrapher:
    _RRDFile = ""
    _PNGPath = ""
    def __init__(self, rrdPath="", pngPath=""):
        self._RRDFile = rrdPath
        self._PNGPath = pngPath

    def getDSNames(self):
        dsNames = []
        info = rrdtool.info(self._RRDFile)
        p = re.compile("\[(.+)\]", re.IGNORECASE)

        for key in info.iterkeys():
            key = key.strip()
            if key.startswith("DS") or key.startswith('ds'):
                dsName = p.search(key).group()[1:-1].strip()
                r = filter(lambda ds: ds == dsName, dsNames)
                if not r:
                    dsNames.append(dsName)
        return dsNames

    def getRRDBegin(self, width=540, height=100):
        return [self._PNGPath,
                '--lazy',
                '--rigid',
                '--slope-mode',
                '--alt-autoscale-max',
                '--imgformat', 'PNG',
                '--width', str(width),
                '--height', str(height),
                ]

    def graphRRD(self, width=540, height=100):
        rrdParams = self.getRRDBegin( width, height)
        dsNames = self.getDSNames()
        colorPallete = RNDColorPallete.getRndColorPallete(len(dsNames))
        for i in range(len(dsNames)):
            rrdParams.append('DEF:' + dsNames[i]+'=' + self._RRDFile + ':' + dsNames[i] + ':AVERAGE')
            rrdParams.append('AREA:' + dsNames[i]+colorPallete[i] + ':' + dsNames[i])
        rrdtool.graph(rrdParams)

if __name__== "__main__":
    fd,path = tempfile.mkstemp('.png')
    rrdfile = ""

    if (sys.argv) > 1:
        rrdfile = sys.argv[1]
    else:
        print "Please enter the rrd file's directory."
        raise
    rrdgrapher = RRDGrapher(rrdfile, path)
    rrdgrapher.graphRRD()
    newpath = rrdfile.rstrip("rrd") + "png"
    shutil.move(path, newpath)
    print "RRD file's png is created at the " + newpath
    print "Note: You can ignore the libpng READ Error"
