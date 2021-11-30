.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin

static-check:
	echo "Running static checks in zato-web-admin"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

run-tests:
	echo "Running access checks in zato-web-admin"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/admin/access/test_*.py -s
