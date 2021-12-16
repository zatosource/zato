
.PHONY: static-check

pylint:
	echo Running pylint in zato-broker
	$(CURDIR)/../bin/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-broker/src/zato/broker

static-check:
	echo "Running static checks in zato-broker"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
