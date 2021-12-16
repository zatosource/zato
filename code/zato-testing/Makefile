
.PHONY: static-check

pylint:
	echo Running pylint in zato-testing
	$(CURDIR)/../bin/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-testing/src/zato/testing

static-check:
	echo "Running static checks in zato-testing"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
