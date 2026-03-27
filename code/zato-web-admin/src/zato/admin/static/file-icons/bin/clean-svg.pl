#!/usr/bin/env perl
use strict;
use warnings;
use autodie;
use v5.14;
use Getopt::Long qw(:config auto_abbrev);

my $help;
my $verbose;
GetOptions(
	"help|usage" => \$help,
	"verbose"    => \$verbose
) or die "Error parsing command-line arguments: $@\n";

say "clean-svg.pl: Performs rudimentary clean-up of SVG source code
Usage: $0 [svg-files...]" and exit if $help;


sub slurp {
	local $/ = undef;
	open(my $fh, shift);
	return join "", <$fh>;
}

for (@ARGV) {
	my $file = $_;
	$_ = (my $input = slurp $file);
	s/\r\n/\n/g;
	s/<g id="icomoon-ignore">\s*<\/g>//gmi;
	s/<g\s*>\s*<\/g>//gmi;
	s/\s+(id|viewBox|xml:space)="[^"]*"/ /gmi;
	s/<!DOCTYPE[^>]*>//gi;
	s/<\?xml.*?\?>//gi;
	s/<!--.*?-->//gm;
	s/ [xy]="0(?:px)?"//gi;
	s/ xmlns:xlink="[^"]*"//gi;
	s/ (?:fill|stroke)="#[A-Fa-f0-9]+"//gi;
	s/ style="enable-background:.*?;"//gmi;
	s/ enable-background\s*=\s*"[^"]*"//gmi;
	s/"\s+>/">/g;
	s/\x20{2,}/ /g;
	s/[\t\n]+//gm;
	
	# Only write back if something changed
	if($input ne (my $output = $_)){
		open my $fh, ">", $file;
		print $fh $output;
		close $fh;
	}
}
