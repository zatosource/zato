TTF = dist/file-icons.ttf

all: clean unpack charmap

# Install dependencies
install:
	cpan Archive::Extract
	npm --global install ppjson
.PHONY: install

# Nuke untracked files
clean:
	rm -rf tmp
	rm -f $(TTF) charmap.html
.PHONY: clean

# Sort icons list
sort:
	head -n1 icons.tsv > icons.tsv~
	sort -dfik3 icons.tsv | grep -v ^\# >> icons.tsv~
	mv icons.tsv~ icons.tsv
.PHONY: sort

# Update character map
charmap:
	./bin/update-charmap.pl

# Generate an unstyled HTML version of character map
charmap-preview:
	@ if command 2>&1 >/dev/null -v cmark-gfm; then GFM="cmark-gfm"; \
	elif command 2>&1 >/dev/null -v gfm;       then GFM="gfm"; fi; \
	[ "$$GFM" ] || { echo 2>&1 "No CommonMark parser installed!"; exit 2; }; \
	"$$GFM" --unsafe charmap.md \
	| sed -e 's~https://raw.githubusercontent.com/file-icons/source/[^/]*/~~g' \
	| sed -e 's/\?sanitize=true//g' \
	> charmap.html

# Extract a downloaded IcoMoon folder
unpack:
	test -f file-icons-*.zip && mv "$$_" file-icons.zip
	./bin/unpack.pl file-icons.zip
	./bin/compress.pl $(TTF)
	chmod 0644 icomoon.json dist/*

# Clean up SVG source
svg: $(wildcard svg/*.svg)
	@./bin/clean-svg.pl $^
.PHONY: svg
