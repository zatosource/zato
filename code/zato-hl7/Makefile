
.PHONY: build
MAKEFLAGS += --silent

default: build

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-hl7

build:
	$(Zato_Python_Dir)/py $(CURDIR)/setup.py develop

dev-install:
	$(CURDIR)/../support-linux/bin/uv pip install --upgrade --python $(Zato_Python_Dir)/python -r $(CURDIR)/../qa-requirements.txt

clean:
	rm -rf $(CURDIR)/build
	find $(CURDIR) -type f -name '*.c' -delete
	find $(CURDIR) -type f -name '*.html' -delete
	find $(CURDIR) -type f -name '*.so' -delete
	find $(CURDIR) -name '*.egg-info' -exec rm -rf {} +

ruff:
	echo "Running ruff in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/ruff check --config $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/hl7/mllp/server.py

pyright:
	echo "Running pyright in $(Zato_Package_Name)"
	cd $(CURDIR)/.. && $(Zato_Python_Dir)/pyright $(CURDIR)/src/zato/hl7/mllp/server.py

hl7-tests:
	$(Zato_Python_Dir)/py -m pytest $(CURDIR)/test/zato/hl7/test_*.py -s -W ignore::DeprecationWarning
	cd $(CURDIR)/test/zato/hl7/mllp && $(Zato_Python_Dir)/py -m pytest test_*.py -s -W ignore::DeprecationWarning -p no:anyio

hl7-test:
	$(MAKE) ruff
	$(MAKE) pyright
	$(MAKE) hl7-tests
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

run-tests:
	$(MAKE) hl7-test
	$(MAKE) static-check
	echo
