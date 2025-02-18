
.PHONY: static-check

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-distlock

run-tests:
	echo "Running tests in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/distlock/test_*.py -s

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(Zato_Python_Dir)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-distlock/src/zato/distlock

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
