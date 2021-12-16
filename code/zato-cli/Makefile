
.PHONY: static-check

pylint:
	echo Running pylint in zato-cli
	$(CURDIR)/../bin/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-cli/src/zato/cli

static-check:
	echo "Running static checks in zato-cli"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
