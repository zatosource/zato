
.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin

run-tests:
	$(PY_DIR)/py $(CURDIR)/test/zato/file_transfer/test_ftp.py

static-check:
	echo "Running static checks in zato-server"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
