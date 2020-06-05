
.PHONY: build

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

rate-limit-tests:
	$(MAKE) build
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/cy/rate_limit/*.py -s

simpleio-tests:
	$(MAKE) build
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/cy/simpleio_/*.py -s

run-tests:
	# No tests to run for now
	echo
