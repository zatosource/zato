
.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin
Zato_Package_Name=zato-web-admin

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-web-admin/src/zato/admin

run-tests:
	echo "Running access checks in $(Zato_Package_Name)"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/admin/access/test_login_logout.py -s --nologcapture
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/admin/access/test_pubsub.py -s --nologcapture
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/admin/access/test_index.py -s --nologcapture
	$(PY_DIR)/py $(CURDIR)/test/zato/admin/playwright_/test_*.py -s --nologcapture

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
