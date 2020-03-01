#!/usr/bin/perl -w
#
# addPath: add a path item to a given variable, delimited by colons, if
#    not already there. Warn if it doesn't exist as a directory.
#
# By Steven J. DeRose.
#
use strict;

=pod

B<OBSOLETE>

See Python version I<addToPath>.

=head1 Usage

    PATH=`addToPath.pl PATH [path-to-add]`

Adds the given path to the end of any path variable (shown as PATH, but
CDPATH, CLASSPATH, MANPATH, etc. can be substituted).
Will not add if it's already there.

=head1 Warning

    You need to do it with `` as shown, because the script can't change the
    actual variable directly for the shell it's called from.

=head1 History

=over

=item * Option to add at start instead of end

=item * 2020-02-11: Ported to Python and improved.
This Perl version now obsolete, and dedicated to the Public Domain.

=back

=cut

###############################################################################
#
if (!$ARGV[1] || $ARGV[0] =~ m/^-+h/) {
    system "perldoc $0";
    exit;
}

my $var = $ARGV[0];
my $dir = $ARGV[1];

if ($ARGV[1] eq "") {
	die "Must specify env variable to extend, and path to add.\n";
}

my $oldvar = $ENV{$var};

if (-d $dir == 0) {
	warn "\n'$dir' is not a directory, not added to \$$var.\n";
	exit;
}

if (":$var:" =~ /:$dir:/) {
	exit; # already there
}

$var = "$oldvar:$dir";
print "$var";

exit;
