.PHONY: test

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-common

rules-tests:
	$(Zato_Python_Dir)/pytest test/zato/common/rules -v -W ignore::DeprecationWarning

rules-perf-tests:
	cd $(CURDIR) && PYTHONPATH=$(CURDIR)/.. python test/zato/common/rules/test_perf.py

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
