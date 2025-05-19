
.PHONY: build
MAKEFLAGS += --silent

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-server

run-tests:
	echo "Running tests in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/test_sio_*.py -s
	$(Zato_Python_Dir)/py     $(CURDIR)/test/zato/commands_/test_*.py
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/rest/test_*.py -s

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	$(MAKE) flake8
