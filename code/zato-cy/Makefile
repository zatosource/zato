
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

simpleio:
	$(MAKE) build

simpleio-test:
	$(MAKE) build
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/cy/simpleio_/test_empty_keys.py -s
