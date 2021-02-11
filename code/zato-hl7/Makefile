
.PHONY: build
MAKEFLAGS += --silent

default: build
PY_DIR=$(CURDIR)/../bin

build:
	py $(CURDIR)/setup.py develop

clean:
	rm -rf $(CURDIR)/build
	find $(CURDIR) -type f -name '*.c' -delete
	find $(CURDIR) -type f -name '*.html' -delete
	find $(CURDIR) -type f -name '*.so' -delete
	find $(CURDIR) -name '*.egg-info' -exec rm -rf {} +

hl7-tests:
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/hl7/test_*.py -s

run-tests:
	$(MAKE) hl7-tests
	$(MAKE) static-check
	echo

static-check:
	echo "Running static checks in zato-hl7"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
