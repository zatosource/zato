
.PHONY: static-check

run-tests:
	py $(CURDIR)/test/zato/test_enmasse.py
	py $(CURDIR)/test/zato/test_openapi.py
	py $(CURDIR)/test/zato/test_service_invoke.py

pylint:
	echo Running pylint in zato-cli
	$(CURDIR)/../bin/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-cli/src/zato/cli

static-check:
	echo "Running static checks in zato-cli"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
