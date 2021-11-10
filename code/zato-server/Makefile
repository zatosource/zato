
.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin

run-tests:
	echo "Running unit-tests in zato-server"
	$(PY_DIR)/py $(CURDIR)/test/zato/file_transfer/test_*.py
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/apispec/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/apispec/test_dc_open_api.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/pattern/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/server_rpc/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/stats/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/test_*.py -s

static-check:
	echo "Running static checks in zato-server"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
