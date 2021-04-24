
.PHONY: static-check

PY_DIR=$(CURDIR)/../bin

static-check:
	echo "Running static checks in zato-testing"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

run-tests:
	echo "Running unit-tests in zato-testing"
	$(PY_DIR)/py $(CURDIR)/test/zato/test_*.py -v
