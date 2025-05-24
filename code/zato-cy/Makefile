.PHONY: build
MAKEFLAGS += --silent

default: build

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-cy

build:
	$(Zato_Python_Dir)/py -m pip install --config-settings editable_mode=compat -e .

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
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/cy/reqresp/test_*.py -s

simpleio-tests:
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/cy/simpleio_/test_*.py -s

run-tests:
	echo "Running tests in $(Zato_Package_Name)"
	$(MAKE) reqresp-tests
	$(MAKE) simpleio-tests

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
