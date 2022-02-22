
.PHONY: static-check

PY_DIR=$(CURDIR)/../bin

run-tests:
	py $(CURDIR)/test/zato/test_enmasse.py
	py $(CURDIR)/test/zato/test_openapi.py
	py $(CURDIR)/test/zato/test_service_invoke.py

pylint:
	echo Running pylint in zato-cli
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-cli/src/zato/cli

static-check:
	echo "Running static checks in zato-cli"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
