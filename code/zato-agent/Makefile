
.PHONY: static-check

static-check:
	echo "Running static checks in zato-agent"
	$(CURDIR)/../bin/flake8 --version 1>&2
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
