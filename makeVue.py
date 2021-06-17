#!/usr/bin/env python
#
# makeVue.py: Create a Vue document with many boxes.
#
from __future__ import print_function
import sys, os, argparse
import re
import time

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY3:
    def unichr(n): return chr(n)

from alogging import ALogger
lg = ALogger(1)


__metadata__ = {
    'title'        : "makeVue.py",
    'description'  : "Create a Vue document with many boxes.",
    'rightsHolder' : "Steven J. DeRose",
    'creator'      : "http://viaf.org/viaf/50334488",
    'type'         : "http://purl.org/dc/dcmitype/Software",
    'language'     : "Python 3.7",
    'created'      : "2016-02-08",
    'modified'     : "2020-03-04",
    'publisher'    : "http://github.com/sderose",
    'license'      : "https://creativecommons.org/licenses/by-sa/3.0/"
}
__version__ = __metadata__['modified']

descr="""
=Description=

Turn a text file (one item per line),
into a Vue document with a box for each line of the input text, or make
nodes and arcs.

The input format is somewhat like graphviz, but more trivial:

* each line can contain one or more node names/labels (optionally quoted)

* if there's more than one label, separate them with '>' (change with --arrow).
Each arrow will generate an arc.

* within a label, '\n' causes a line-break in the node text.

* lines may optionally be terminated with a semicolon.

* before all that, a line can have []-enclosed modifiers (which so far are
discarded).


=Related Commands=

C<dot>, C<Vue>.

=Known bugs and Limitations=

For the moment, the boxes are just placed in a long horizontal row, on the
assumption you will arrange them how you want in Vue.

Would be nicer to read something like GraphViz format, will names
to create nodes, and relationships to create arcs.

Box size and text length get no special treatment; size should at least be
an option, and text should be wrappable.

Reverse-engineered from sample output from Vue. So any number of features
are not supported.

Vue's output puts a long comment ''before'' the XML declaration, which is
not valid. The comment warns not to remove it.

=Vue syntax notes=

Each object gets assigned a URI (at tufts.edu), with a GUID or similar on the
end. This programs uses the same domain and path, but int(time.time()) in hex
for the GUID-like part.

Colors always seem to be in #RRGGBB form.

arrowState is 3 for both ends,....

Arrows have point1, point2, ID1, and ID2 sub-elements; not sure why.


=History=

* 2016-02-08: Written by Steven J. DeRose.
* 2017-01-25: Add canvas, box, and gutter geometry options. Wraps
into rows if there are many boxes.
* 2-18-10-25: Recover from spare, fix. Rows.


=To do=

* Do something with the [] prefixes. At least:
    strokeColor, strokeWidth, strokeStyle
    textColor, textSize, font
    fillColor
    shape


=Rights=

Copyright 2016 by Steven J. DeRose.
This work is licensed under a Creative Commons
Attribution-Share Alike 3.0 Unported License. For further information on
this license, see http://creativecommons.org/licenses/by-sa/3.0/.

For the most recent version, see [http://www.derose.net/steve/utilities] or
[http://github.com/sderose].


=Options=
"""

# Don't know what names Vue uses, list made from just looking at menu.
shapes = [
    'rect',
    'roundRect',
    'diamond',
    'ellipse',
    'hexagon',
    'octagon',
    'triangle-up',
    'triangle-down',
    'triangle-left',
    'triangle-right',
]

strokeStyles = [
]

arrowStates = {
    3:    "both ends",
}


##############################################################################
#
def makeVueTop(path):
    fname = os.path.basename(path)
    vueTop = ""
    if (args.force):  # Not WF XML, but Vue makes/accepts it for its own files.
        vueTop += """<!-- Tufts VUE 3.3.0 concept-map (CSSuses.vue) 2016-02-08 -->
<!-- Tufts VUE: http://vue.tufts.edu/ -->
<!-- Do Not Remove: VUE mapping @version(1.1) jar:file:/Applications/VUE.app/Contents/Resources/Java/VUE.jar!/tufts/vue/resources/lw_mapping_1_1.xml -->
<!-- Do Not Remove: Saved date Mon Feb 08 14:22:21 EST 2016 by sderose on platform Mac OS X 10.10.5 in JVM 1.6.0_65-b14-466.1-11M4716 -->
<!-- Do Not Remove: Saving version @(#)VUE: built October 8 2015 at 1658 by tomadm on Linux 2.6.32-504.23.4.el6.x86_64 i386 JVM 1.7.0_21-b11(bits=32) -->
"""
    vueTop += """<?xml version="1.0"?>
<LW-MAP xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="none" ID="0" label="%s"
    created="1454959179093"
    x="0.0" y="0.0" width="1.4E-45" height="1.4E-45"
    strokeWidth="0.0" autoSized="false">
    <resource referenceCreated="1454959342008"
        spec="%s" type="1" xsi:type="URLResource">
        <title>%s</title>
        <property key="File" value="%s"/>
    </resource>"""
    vueTop = vueTop % (fname, path, fname, path)
    vueTop += colorSet(fill="#FFFFFF", stroke="#404040", text="#000000",
        font="SansSerif-plain-14") + makeURI()
    return(vueTop)

def makeNode(someID, label, x, y, w, h, shape):
    """Generate a single node.
    """
    idp = someID
    if (args.fixids): idp = "A_%d" % (someID)
    ch = """
    <child ID="%s"
        label="%s"
        layerID="1" created="%020x"
        x="%s" y="%s" width="%s" height="%s"
        strokeWidth="1.0" autoSized="false" xsi:type="node">""" % (
        idp, label, int(time.time()), x, y, w, h)

    ch += colorSet() + makeURI() + makeShape(shape)
    ch += "\t</child>"
    return(ch)

def makeArc(someID, _label, fromID, toID):
    """Generate a single arc.
    Does it go by node IDs or by point1/point2?
    """
    arc = ("""
    <child ID="%s" layerID="13" created="%020x"
        x="118.0" y="49.0" width="24.0" height="4.0"
        strokeWidth="%d" strokeStyle="%d" autoSized="false" controlCount="0"
        arrowState="%d" xsi:type="link">
    """ % (someID, time.time(), args.strokeWidth, args.strokeStyle, 1))
    arc += (
        colorSet(fill="", stroke="#33A8F5", text="#404040", font="Arial-plain-11") +
        makeURI())
    arc += """
        <point1 x="120.0" y="51.0"/>
        <point2 x="140.0" y="51.0"/>
        <ID1 xsi:type="node">%s</ID1>
        <ID2 xsi:type="node">%s</ID2>
    </child>
    """ % (fromID, toID)

def makeLayer():
    """Uh, what?
    """
    layer = """
    <layer ID="1" label="Layer 1" created="1454959179100" x="0.0"
        y="0.0" width="1.4E-45" height="1.4E-45" strokeWidth="0.0" autoSized="false">
        """ + makeURI() + """
    </layer>

    <userZoom>1.0</userZoom>
    <userOrigin x="-14.0" y="-14.0"/>
    <presentationBackground>#202020</presentationBackground>
    """
    return(layer)

def makePathwayList(path):
    """Just coopied from a sample.
    """
    pwl="""
    <PathwayList currentPathway="0" revealerIndex="-1">
        <pathway ID="0" label="Untitled Pathway" created="1454959179092"
            x="0.0" y="0.0" width="1.4E-45" height="1.4E-45"
            strokeWidth="0.0" autoSized="false" currentIndex="-1" open="true">
            <strokeColor>#B3993333</strokeColor>
            <textColor>#000000</textColor>
            <font>SansSerif-plain-14</font>
            <URIString>http://vue.tufts.edu/rdf/resource/c255b1c6c0a8010a1de9c46dd4905e59</URIString>

            <masterSlide ID="2" created="1454959179119" x="0.0" y="0.0"
                width="800.0" height="600.0" locked="true"
                strokeWidth="0.0" autoSized="false">
                <fillColor>#000000</fillColor>
                <strokeColor>#404040</strokeColor>
                <textColor>#000000</textColor>
                <font>SansSerif-plain-14</font>
                <URIString>http://vue.tufts.edu/rdf/resource/c255b1c7c0a8010a1de9c46d37587304</URIString>

                <titleStyle ID="3" label="Header"
                    created="1454959179188" x="341.0" y="175.0"
                    width="118.0" height="50.0" strokeWidth="0.0"
                    autoSized="true" isStyle="true" xsi:type="node">
                    <strokeColor>#404040</strokeColor>
                    <textColor>#FFFFFF</textColor>
                    <font>Gill Sans-plain-36</font>
                    <URIString>http://vue.tufts.edu/rdf/resource/c255b1c8c0a8010a1de9c46d39b76f9f</URIString>
                    <shape xsi:type="rectangle"/>
                </titleStyle>

                <textStyle ID="4" label="Slide Text"
                    created="1454959179189" x="349.5" y="282.5"
                    width="101.0" height="35.0" strokeWidth="0.0"
                    autoSized="true" isStyle="true" xsi:type="node">
                    <strokeColor>#404040</strokeColor>
                    <textColor>#FFFFFF</textColor>
                    <font>Gill Sans-plain-22</font>
                    <URIString>http://vue.tufts.edu/rdf/resource/c255b1cac0a8010a1de9c46da5936797</URIString>
                    <shape xsi:type="rectangle"/>
                </textStyle>

                <linkStyle ID="5" label="Links" created="1454959179191"
                    x="375.5" y="385.0" width="49.0" height="30.0"
                    strokeWidth="0.0" autoSized="true" isStyle="true" xsi:type="node">
                    <strokeColor>#404040</strokeColor>
                    <textColor>#B3BFE3</textColor>
                    <font>Gill Sans-plain-18</font>
                    <URIString>http://vue.tufts.edu/rdf/resource/c255b1cbc0a8010a1de9c46d6406926a</URIString>
                    <shape xsi:type="rectangle"/>
                </linkStyle>

            </masterSlide>
        </pathway>
    </PathwayList>
    <date>2016-02-08</date>
    <modelVersion>6</modelVersion>
    """
    pwl += """<saveLocation>%s</saveLocation>
    <saveFile>%s</saveFile>
</LW-MAP>
""" % (os.path.dirname(path), path)
    return(pwl)

def colorSet(fill=None, stroke=None, text=None, font=None):
    if (fill is None):   fill = args.fillColor
    if (stroke is None): stroke = args.strokeColor
    if (text is None):   text = args.textColor
    if (font is None):   font = args.font
    return("""
        <fillColor>%s</fillColor>
        <strokeColor>%s</strokeColor>
        <textColor>%s</textColor>
        <font>%s</font>\n""" % (fill, stroke, text, font))

def makeURI():
    return("        <URIString>" +
        ("http://vue.tufts.edu/rdf/resource/%020x" % int(time.time())) +
        "</URIString>\n")

def makeShape(shape="roundRect"):
    return("""\t\t<shape arcwidth="20.0" archeight="20.0" xsi:type="%s"/>\n""" %
        (shape))


###############################################################################
# Main
#
def processOptions():
    try:
        from BlockFormatter import BlockFormatter
        parser = argparse.ArgumentParser(
            description=descr, formatter_class=BlockFormatter)
    except ImportError:
        parser = argparse.ArgumentParser(description=descr)

    parser.add_argument(
        "--arrow",            type=str, default=">",
        help='String to separate nodes/labels in input file lines.')
    parser.add_argument("--boxwidth",     metavar="W", type=int, default=20,
        help='Width of boxes.')
    parser.add_argument("--boxheight",    metavar="H", type=int, default=20,
        help='Height of boxes.')
    parser.add_argument(
        "--fillColor",        type=str, default="#A6A6A6", metavar="RGB",
        help='#RRGGBB')
    parser.add_argument(
        "--fixids",           action='store_true',
        help='Make IDs be not just numbers..')
    parser.add_argument(
        "--font",             type=str, default="Arial-plain-12",
        help='')
    parser.add_argument(
        "--force", "-f",      action='store_true',
        help='Include non-well-formed Vue header comment.')
    parser.add_argument(
        "--idstart",          type=int, default=1,
        help='Value to use for first generated ID.')
    parser.add_argument(
        "--iencoding",        type=str, metavar='E', default="utf-8",
        help='Character set for input files. Default: utf-8.')
    parser.add_argument(
        "--oencoding",        type=str, metavar='E',
        help='Use this character set for output files.')
    parser.add_argument(
        "--quiet", "-q",      action='store_true',
        help='Suppress most messages.')
    parser.add_argument(
        "--shape",            type=str, choices=shapes, default="roundRect",
        help='Shape to use for boxes')
    parser.add_argument(
        "--strokeColor",      type=str, default="#FFFFFF", metavar="RGB",
        help='#RRGGBB')
    parser.add_argument(
        "--strokeStyle",      type=int, default=1, metavar="S",
        help='')
    parser.add_argument(
        "--strokeWith",       type=int, default=1, metavar="W",
        help='')
    parser.add_argument(
        "--textColor",        type=str, default="#000000", metavar="RGB",
        help='#RRGGBB')
    parser.add_argument(
        "--unicode",          action='store_const',  dest='iencoding',
        const='utf8', help='Assume utf-8 for input files.')
    parser.add_argument(
        "--verbose", "-v",    action='count',       default=0,
        help='Add more messages (repeatable).')
    parser.add_argument(
        "--version", action='version', version=__version__,
        help='Display version information, then exit.')

    parser.add_argument(
        "--left", type=int, default=20,
        help='Left side of area to draw in.')
    parser.add_argument(
        "--top", type=int, default=20,
        help='Top side of area to draw in.')
    parser.add_argument(
        "--width", type=int, default=500,
        help='Width of area to draw in.')
    parser.add_argument(
        "--height", type=int, default=500,
        help='Height of area to draw in.')

    parser.add_argument("--gutterwidth",  metavar="W", type=int, default=20,
        help='Width of gutters between boxes.')
    parser.add_argument("--gutterheight", metavar="H", type=int, default=20,
        help='Height of inter-row spacing.')

    parser.add_argument(
        'files',             type=str,
        nargs=argparse.REMAINDER,
        help='Path(s) to input file(s)')

    args0 = parser.parse_args()
    return(args0)


args = processOptions()

if (len(args.files) == 0):
    lg.error("No files specified....")
    sys.exit()

nodeIndex = {}        # label: (id, x, y, w, h, shape)

curID = args.idstart
x0 = args.left
y0 = args.top

print(makeVueTop(args.files[0]))
recnum = 0
for label0 in (open(args.files[0],'r').readlines()):
    recnum += 1
    label0 = label0.strip(".,:; \t\n\r\f")
    bkt = re.sub(r'^\s*\[[^\]]*\]\s*', '', label0)  # Modifiers a la graphviz
    parts = re.split(r'\s+'+args.arrow+r'\s*', label0)

    for i, part in enumerate(parts):
        part = part.strip()
        part = re.sub(r'\\n', '&#xa0;', part)
        if (len(part)>1 and part[0]==part[-1] and
            part[0] in '"\''): part = part[1:-2]
        if (part in nodeIndex):
            lg.eMsg("Duplicate node label0 '%s' at record %d." % (part, recnum))
        nodeIndex[part] =  ( curID, x0, y0, args.boxwidth, args.boxheight, args.shape )
        print(makeNode(curID, part, x0, y0, args.boxwidth, args.boxheight, args.shape))
        curID += 1
        # Move to next box position
        x0 += args.boxwidth + args.gutterwidth
        if (x0 > args.left + args.width):
            y0 += args.boxheight + args.gutterheight
            x0 = args.left

    for i, part in enumerate(parts):
        if (i==0): continue
        # FIX: Look up node IDs in nodeIndex.
        print(makeArc(curID, "", curID+1, curID+2))
        curID += 1

print(makeLayer())
print(makePathwayList(args.files[0]))

if (not args.quiet):
    lg.vMsg(0,"Done.")
    lg.showStats()
