
.PHONY: static-check

PY_DIR=$(CURDIR)/../bin

pylint:
	echo Running pylint in zato-broker
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-broker/src/zato/broker

static-check:
	echo "Running static checks in zato-broker"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
