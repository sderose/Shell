#!/bin/bash
#
# appendGitConfig.sh: Append user name/email to $1/.git/config.
# 2021-04-10: Written by Steven J. DeRose.
#
UNAME="Steven J. DeRose"
UMAIL="sderose@acm.org"

if ! [ -d "$1" ]; then
    echo "No directory at '$1'."
    exit
fi
TGT="$1/.git/config"
if ! [ -f "$TGT" ]; then
    echo "No file at '$TGT'."
    exit
fi
if $(grep -q "$UNAME" "$TGT"); then
    echo "Line for '$UNAME' already in $TGT."
    exit
fi

####### Here's the data to append:
#
DAT=`cat <<EOF
[diff]
    tool = meld
[difftool]
    prompt = false
[user]
    name = $UNAME
    email = $UMAIL
EOF
`
echo "$DAT" >>$TGT
