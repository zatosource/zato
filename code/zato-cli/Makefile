
.PHONY: static-check

PY_DIR=$(CURDIR)/../bin
Zato_Package_Name=zato-cli

run-tests:
	$(PY_DIR)/py $(CURDIR)/test/zato/test_enmasse.py
	$(PY_DIR)/py $(CURDIR)/test/zato/test_openapi.py
	$(PY_DIR)/py $(CURDIR)/test/zato/test_service_invoke.py

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-cli/src/zato/cli

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
