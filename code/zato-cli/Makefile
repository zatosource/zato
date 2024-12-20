
.PHONY: static-check

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-cli

run-tests:
	$(Zato_Python_Dir)/pytests $(CURDIR)/test/zato/enmasse_/test_*.py -s
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_openapi.py
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/test_service_invoke.py

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(Zato_Python_Dir)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-cli/src/zato/cli

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
