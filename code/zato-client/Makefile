
.PHONY: test

default: upload
PY_DIR=$(CURDIR)/../bin

upload2: PYTHON_BIN = python2
upload3: PYTHON_BIN = python3

upload:
	$(MAKE) upload2
	$(MAKE) upload3

clean:
	rm -rf $(CURDIR)/dist/ && rm -rf $(CURDIR)/build

twine:
	twine upload $(CURDIR)/dist/*

upload2 upload3:
	$(MAKE) clean
	$(PYTHON_BIN) setup.py clean && $(PYTHON_BIN) setup.py bdist_wheel
	$(MAKE) twine

pylint:
	echo Running pylint in zato-client
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-client/src/zato/client

static-check:
	echo "Running static checks in zato-client"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
