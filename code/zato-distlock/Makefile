
.PHONY: static-check

PY_DIR=$(CURDIR)/../bin

run-tests:
	echo "Running unit-tests in zato-distlock"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/distlock/test_*.py -s

static-check:
	echo "Running static checks in zato-distlock"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
