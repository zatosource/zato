
.PHONY: static-check

pylint:
	echo Running pylint in zato-zmq
	$(CURDIR)/../bin/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-zmq/src/zato/zmq_

static-check:
	echo "Running static checks in zato-zmq"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
