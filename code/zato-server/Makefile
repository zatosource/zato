
.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin
Zato_Package_Name=zato-server

pubsub-tests:
	echo "Running pub/sub tests in $(Zato_Package_Name)"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/pubsub/test_pubapi_rest.py -s
	$(PY_DIR)/py        $(CURDIR)/test/zato/pubsub/test_pubapi_services.py
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/pubsub/test_publish.py -s

wsx-tests:
	echo "Running WSX tests in $(Zato_Package_Name)"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/wsx/test_*.py -s

run-tests:
	echo "Running tests in $(Zato_Package_Name)"
	$(MAKE) pubsub-tests
	$(MAKE) wsx-tests
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/file_transfer/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/apispec/test_*.py -s
	$(PY_DIR)/py        $(CURDIR)/test/zato/commands_/test_*.py
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/pattern/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/rest/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/server_rpc/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/stats/test_*.py -s

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-server/src/zato/server

mypy-apispec:
	echo "Running mypy in $(Zato_Package_Name) / apispec"
	$(PY_DIR)/mypy --config-file=$(CURDIR)/../mypy.ini \
		$(CURDIR)/src/zato/server/apispec/

mypy-pubsub:
	echo "Running mypy in $(Zato_Package_Name) / pubsub"
	$(PY_DIR)/mypy --config-file=$(CURDIR)/../mypy.ini \
		$(CURDIR)/src/zato/server/pubsub/

pyright-apispec:
	$(PY_DIR)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/apispec/

pyright-pubsub:
	$(PY_DIR)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/__init__.py
	$(PY_DIR)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/model.py
	$(PY_DIR)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/task.py
	$(PY_DIR)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/sync.py

mypy:
	$(MAKE) mypy-apispec
	$(MAKE) mypy-pubsub

pyright:
	$(MAKE) pyright-apispec
	$(MAKE) pyright-pubsub

type-check:
	echo "Running type checks ($(Zato_Package_Name))"
	$(MAKE) mypy
	$(MAKE) pyright

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	$(MAKE) flake8
	$(MAKE) type-check
