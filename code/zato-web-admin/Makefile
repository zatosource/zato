.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin

pylint:
	echo Running pylint in zato-web-admin
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-web-admin/src/zato/admin

static-check:
	echo "Running static checks in zato-web-admin"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

run-tests:
	echo "Running access checks in zato-web-admin"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/admin/access/test_login_logout.py -s --nologcapture
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/admin/access/test_pubsub.py -s --nologcapture
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/admin/access/test_index.py -s --nologcapture
	$(PY_DIR)/py $(CURDIR)/test/zato/admin/playwright_/test_*.py -s --nologcapture
