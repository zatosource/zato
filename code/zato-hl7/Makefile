
.PHONY: build
MAKEFLAGS += --silent

default: build

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-hl7

build:
	$(Zato_Python_Dir)/py $(CURDIR)/setup.py develop

clean:
	rm -rf $(CURDIR)/build
	find $(CURDIR) -type f -name '*.c' -delete
	find $(CURDIR) -type f -name '*.html' -delete
	find $(CURDIR) -type f -name '*.so' -delete
	find $(CURDIR) -name '*.egg-info' -exec rm -rf {} +

hl7-tests:
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/hl7/test_*.py -s

run-tests:
	$(MAKE) hl7-tests
	$(MAKE) static-check
	echo

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(Zato_Python_Dir)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-hl7/src/zato/hl7

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
