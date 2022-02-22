
.PHONY: static-check

PY_DIR=$(CURDIR)/../bin

pylint:
	echo Running pylint in zato-testing
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-testing/src/zato/testing

static-check:
	echo "Running static checks in zato-testing"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
