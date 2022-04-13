
.PHONY: static-check

PY_DIR=$(CURDIR)/../bin
Zato_Package_Name=zato-distlock

run-tests:
	echo "Running tests in $(Zato_Package_Name)"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/distlock/test_*.py -s

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-distlock/src/zato/distlock

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
