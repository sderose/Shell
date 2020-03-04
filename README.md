=Shell REPO=

A bunch of utilities to help with your shell environment.

On the whole, these are less polished than others, but may still prove
handy. These are mainly used on MacOSX and/or Linux. I've tried to avoid
*nix flavor differences, but some remain.

==Path stuff==

* _cleanpath -- Process $PATH to remove duplicates.

* addToPath -- Append a directory to $PATH as long as it exists, and is not
already there.

* checkPath -- Run through $PATH and report problems such as nonexistent
directories.

* identifyAllExecutables -- Ambitious but imperfect code to find everybody
along the PATH, not to mention aliases and shell functions. This can be
especially helpful for finding commands that show up in several places.


==Output formatting==

* echoToStderr (bash) -- Syntactic sugar / shorthand.

* hilite -- Find matches to one or more regexes (including some prepackaged sets),
and hilite them in one or more colors.

* makeGraphvizFromDirTree -- What it says.

* makeVue.py -- Vue is a handy drawing package; this will take a list of strings
and make a node for each one, placing them in a row (I think), to save time
vs. hand-creating a lot.

* spinner.py -- Spins a character by changing between slash, backslash, vertical bar,
and hyphen,

* unescapeURI -- Replace URI %xx codes.


==Processes==

* countShells.py -- Meh. Attempts to figure out how many shells are running.

* isrunning (bash) -- Test whether a given program is running.

* runIfNotRunning (bash) --


==MacOSX specific==

* macFilenameSort -- Try to sort files by name, the way MacOSX does (automatically
separating out numbers to compare numerically, vs. letters alphabetically).

* macSystemReportToHtml -- Seemed like a good idea once.

* macmore --

* maildir2mbox.py --


==Code-related==

* bash2perl -- Really old. Does a rough-cut conversion of bash syntax to Perl.
It knows about bracket conventions, if/else keywords and braces, common function
names, regexes, etc. But it's not a turnkey solution. It does a lot of the
mechanical editing, which saves a lot of time but is not nearly complete.

* perl2python -- A boatload of regexes to convert Perl code to Python. It's far
from perfect, but even getting most of the punctuation, keywords, and function
names mapped saves a lot of time.

* prettyPrintExpr -- Takes an expression with () [] {}, and display it in ways
that should make it easy to see what's going on. It prints three forms:

* the same string but with sub-parts colorized progressively by depth
* the same string with layers of lines over it showing the scopes of each
bracked subexpression
* an indented outline

* pyconflict --

* pythonpath.py --

* tracePythonPackage.py -- An attempt to automatically figure out where a Python
library is getting imported from. Not just the directory, but which package
manager (port, brew, pip, conda) installed it.


==Informational==

* duByUser -- Sum up disk usage under a directory, by specific users.

* listGroups --

* prenv (bash) -- prettier display of environment info.q

* showKeyCodes -- Lets you press keys and see what actually gets sent.

* showNumberInBases -- Show a number in multiple bases.

* showScale (Perl) -- Show a line like a rule for column numbers. You can even
have it overlay higher up in your terminal window, to more easily measure
a line up there.

* showShellVars --

* showTip -- Issue a random tip re. one of my utilities. I don't maintain this
any more.

============================

* allDates (bash) -- Try to retrieve and display all the dates associated
with a file.

* assign (bash) --

* checkSync --

* clean --

* commandsHelp.py --

* diaStart.sh --

* ecmd -- Broken. The idea is to find where a command is implemented, such as
by a script along PATH, or as an alias or shell function in .bash_profile or
similar, or whatever. Then, if it's not a binary, open your EDITOR on it.

* genKey.py --

* getDocumentTitle.py -- Extract the main title string from any of several file
types, including HTML, TXT, POD, and PDF.

* getPassPhrase.sh (sh) -- Use my 'randomRecords' to pick several random words
from /usr/share/dict/words, for example to make a password.
See [https://xkcd.com/936/] and [https://www.correcthorsebatterystaple.net/].

* gitdiffhook (bash) -- Used by git diff to invoke regular 'diff' with options.

* greprange --

* indente (Perl) -- Indent (pretty-print) a file, and open that copy in your EDITOR.
Especially useful for *ML if your editor won't indent it for you. I should add
a few more file types, like JSON.

* lastCommands.py -- This is meant to retrieve the last N shell commands, and
re-run them in the same order. But that's surprisingly hard to get exactly
right.

* openall --

* pressure -- Convert a pressure value in any of 25 units, to the equivalent in all
of those units.

* smoke (bash) -- Tries to run all the executable in a given directory -- easy
way to flush out badly broken/obsolete code.

* stdinToEditor --

* stdinToFirefox --

* timeDiff --

* whereFrom --

* whichBoot -- Check whether the machine was booted via UEFI or BIOS (mainly
useful in Linux).

