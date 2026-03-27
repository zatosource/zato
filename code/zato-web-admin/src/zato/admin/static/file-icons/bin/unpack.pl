#!/usr/bin/env perl
use strict;
use warnings;
use autodie;
use v5.14;
use utf8;
$| = 1;

use warnings qw< FATAL utf8 >;
use open     qw< :std :utf8 >;

use Archive::Extract;
use File::Basename qw< basename >;
use File::Path qw< rmtree >;
use File::Copy;
use File::Spec::Functions qw< :ALL >;


# Take first argument as logical path to downloaded archive
my $zip = shift;
die "Usage: $0 /path/to/file-icons.zip\n" unless $zip;

$zip = Archive::Extract->new(archive => Cwd::abs_path(rel2abs $zip)) or die $@;

# Switch to project directory and start extracting files
chdir Cwd::abs_path(rel2abs("../..", "$0"));

# Extract archive
rmtree "tmp";
$zip->extract(to => "tmp") or die $@;

move "tmp/fonts/file-icons.svg", "dist";
move "tmp/fonts/file-icons.ttf", "dist";
say "Fonts extracted";

# Fix that bullshit tabstop width I hate
`ppjson -wt tmp/selection.json`;
move "tmp/selection.json", "icomoon.json";
