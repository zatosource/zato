
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

rate-limit:
	$(MAKE) build

simpleio:
	$(MAKE) build

reqresp-tests:
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/cy/reqresp/test_*.py -s

simpleio-tests:
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/cy/simpleio_/test_*.py -s

run-tests:
	echo "Running unit-tests in zato-cy"
	$(MAKE) reqresp-tests
	$(MAKE) simpleio-tests
	echo

static-check:
	echo "Running static checks in zato-cy"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
