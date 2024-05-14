#!/usr/bin/env python3
#
import re
from typing import Any, Iterable

descr = """
Accept add_argument calls like argparse, but output a shell function with
code to manage those.

Options:
    --shortMetaVars:  Reduce metavars to single characters
    --

"""

def isOkOptionName(s:str) -> bool:
    return re.match(r"--?^\w[-\w]*$", s)

kwInfos = {
    "action":   ( str,       None ),
    "nargs":    ( str,       1 ),
    "const":    ( Any,       None ),
    "default":  ( Any,       "" ),
    "type":     ( type,      str ),
    "choices":  ( Iterable,  None ),
    "required": ( bool,      None ),
    "help":     ( str,       "" ),
    "metavar":  ( str,       None ),
    "dest":     ( str,       None )
}

actions = [ "store_false", "store_true", "store_const", "append", "count" ]
# nargs REMAINDER
#
shortMetaVars = True

helpExpr = "(-|--)(h|he|hel|help)"

initBuf = ""
parseBuf = ""
helpBuf = ""

funcName = "?"


mainNames = {}

def add_argument(
    *args,
    **kwargs):

    global initBuf, parseBuf, helpBuf

    mainName = args[0]
    aliases = args
    for a in aliases:
        assert isOkOptionName(mainName), ("Option '%s': Bad alias name '%s'"
            % (mainName, a))

    kwValues = {}
    for kw in kwInfos.keys():
        kwValues = kwInfos[kw][1]

    for kw, kv in kwargs:
        if (kw not in kwInfos):
            assert False
        if (isinstance(kv, kwInfos[kw][0])):
            assert False, "Option '%s': wrong type for arg '%s'" % (mainName, kw)
        if (mainName in mainNames):
            assert False, "Option '%s': already defined." % (mainName)
        kwValues[kw] = kv

    if (not kwValues["metavar"]):
        if (shortMetaVars): kwValues["metavar"] = mainName[0].upper()
        else: kwValues["metavar"] = mainName.upper()

    if (not kwValues["dest"]):
        kwValues["dest"] = re.sub(r"[^\w]", "_", mainName)

    if (kwValues["default"] and kwValues[type] != Any):
        kwValues["default"] = kwValues[type](kwValues["default"])

    if (kwValues["const"] and kwValues[type] != Any):
        kwValues["const"] = kwValues[type](kwValues["const"])

    takesArg = False
    if (kwValues["type"]): takesArg = True
    if (kwValues["nargs"]): takesArg = True
    if (kwValues["choices"]): takesArg = True

    # Generate code to create and initialize the destination variable
    #
    if (kw["action"] == "append"):
        initBuf += "    typeset -a %s=())\n" % (kw["dest"])
    elif (kw["action"] == "count"):
        initBuf += "    %s=0\n" % (kw["dest"])
    else:
        initBuf += "    %s=\"%s\"\n" % (kw["dest"], kwValues["default"])

    # Generate code to recognize and record the option
    #
    parseExpr = "|".join(aliases) + ") "
    if (kw["action"] == "store_false"):
        parseExpr += "%d=\"\";;" % (kw["dest"])
    elif (kw["action"] == "store_true"):
        parseExpr += "%d=1;;" % (kw["dest"])
    elif (kw["action"] == "store_const"):
        assert kw["const"]
        if (kw["type"] == int):
            parseExpr += "%d=%d;;" % (kw["dest"], kw["const"], )
        else:
            assert '"' not in kw["const"]
            parseExpr += "%d=\"%s\";;" % (kw["dest"], kw["const"], )
    elif (kw["action"] == "append"):
        parseExpr += "shift; %d+=\"$1\";;" % (kw["dest"])
    elif (kw["action"] == "count"):
        parseExpr += "%d+=1;;" % (kw["dest"])
    elif (takesArg):
        parseExpr += "shift; %d=\"$1\";;" % (kw["dest"])
    else:
        parseExpr += "%d=1;;" % (kw["dest"])
    parseBuf += ""

    # Generate the help
    #
    helpBuf += "    %s: %s\n" % (mainName, kw[help])


    # Assemble the function
    buf = (

"""
HELP_OPTION_EXPR="%s"

%s() {
    %s
    while [[ $# -gt 0 ]]; do case "$1" in
    (${~HELP_OPTION_EXPR})
        cat <<EOF
%s
EOF
            return;;
%s
        -*) tMsg 0 "Unrecognized option '$1'."; return 99;;
        *) break;;
      esac; shift;
    done

}
""") % (helpExpr, funcName, initBuf, helpBuf, parseBuf)

    print(buf)
