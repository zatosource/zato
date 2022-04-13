
.PHONY: static-check

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-broker

pylint:
	echo Running pylint in zato-broker
	$(Zato_Python_Dir)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-broker/src/zato/broker

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
