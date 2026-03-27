#!/usr/bin/env perl
use strict;
use warnings;
use autodie;
use v5.14;
use utf8;
$| = 1;

use warnings qw< FATAL utf8 >;
use open     qw< :std :utf8 >;
use Carp     qw< confess >;

use File::Spec::Functions qw< :ALL >;
use File::Basename;
use Cwd;

END { close STDOUT }
local $SIG{__DIE__} = sub {
	confess "Uncaught exception: @_" unless $^S;
};

# Switch to project directory, resolving possible symlinks
chdir Cwd::abs_path(rel2abs("../..", "$0"));

# Paths to files being read/written to
my $svgfont_path = File::Spec->rel2abs("dist/file-icons.svg");
my $charmap_path = File::Spec->rel2abs("charmap.md");


# Slurp character map
my $charmap = do {{
	local $/ = undef;
	open(my $fh, $charmap_path);
	join "", <$fh>
}};

# Grab which codepoints are already listed
my %codepoints = ();
my %table_rows = ();
while($charmap =~ m/<tbody.+?<a name="([^"]+)".+<code>\\([0-9A-Fa-f]+)<\/code>.+<\/tbody>/ig){
	$codepoints{$2} = $1;
	$table_rows{$1} = $&;
}

my $url = "https://raw.githubusercontent.com/file-icons/source/master/svg/%3\$s.svg?sanitize=true";
(my $row = <<HTML) =~ s/&\Kamp;|\h*<!--.*?-->|[\r\n\t]+//g;
<tbody>
	<tr>
		<!-- Thumbnail + Permalink -->
		<td align="center">
			<a name="%4\$s" href="${url}">
				<img src="${url}" height="34" valign="bottom" hspace="3" alt="&amp;#x%2\$s;"/>
			</a>
		</td>
		
		<!-- Human-readable name -->
		<td>
			<b>%4\$s</b>
		</td>
		
		<td>
			<a name="%2\$s"></a> <!-- Anchor for hotlinking -->
			<code>\\%2\$s</code> <!-- Codepoint/escape sequence -->
		</td>
	</tr>
</tbody>
HTML


# Keep capitalisation used by existing SVG files
sub id { local $_ = shift; s/\W*(\w+)\W*/\L$1/g; return $_; }
my %svgFiles = map {(id($_), $_) if s!^svg/|\.svg$!!ig} glob "svg/*";

# Pick up newly-defined characters from SVG font
@ARGV = ($svgfont_path);
while(<>){
	if(/^\s*<glyph\s+unicode="&#x([0-9A-Fa-f]+);?"\s+glyph-name="([^"]+)"/){
		my $code = uc $1;
		my $name = ucfirst($2 =~ tr/-/ /r);

		# Avoid clobbering existing rows that might've been edited by user
		unless($codepoints{$code}){
			my $file = $svgFiles{id($name)} || $name;
			$file =~ s/\s+/-/g;
			$codepoints{$code} = $name;
			$table_rows{$name} = sprintf $row, $name, $code, $file, do {{
				$_ = $file;
				s/[- ](Old|Alt|New)\s*(\d*)$/, \u$1 $2/i;
				s/\s$//; $_
			}};
		}
	}
}


# Alphabetise and update table
my @sorted = sort {lc $a cmp lc $b} keys %table_rows;
my $updated = join "\n", map {$table_rows{$_}} @sorted;
$updated =~ s/^/\t/gm;
$charmap =~ s/\s*<tbody.+(<\/table>)/\n$updated\n$1/sgmi;

# Write back to file
open(my $fh, ">", $charmap_path);
print $fh $charmap;
