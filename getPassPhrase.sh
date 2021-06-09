#!/bin/sh
#
# Written 2015-12-31 by Steven J. DeRose. CCLI Attribution-Sharealike 3.0.
#
if [[ "$1" == "-h" ]]; then
    echo "$0: Grab some random words from system dictionary."
    exit
fi

if ! [ "$PASSPHRASE_WORDS" ]; then
    PASSPHRASE_WORDS=4
fi
if ! [ "$PASSPHRASE_DICT" ]; then
    PASSPHRASE_DICT="/usr/share/dict/words"
fi
if ! [ -r "$PASSPHRASE_DICT" ]; then
    echo "$0: Can't find dictionary at '$PASSPHRASE_DICT'."
    exit
fi

PP=`randomRecords -q -n $PASSPHRASE_WORDS $PASSPHRASE_DICT`
echo $PP
