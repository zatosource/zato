
.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin

run-tests:
	echo "Running unit-tests in zato-server"
	$(PY_DIR)/py $(CURDIR)/test/zato/file_transfer/test_*.py
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/apispec/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/pattern/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/pubsub/test_pubapi_rest.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/pubsub/test_pubapi_services.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/pubsub/test_publish.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/rest/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/server_rpc/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/stats/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/test_*.py -s

pylint:
	echo Running pylint in zato-server
	$(CURDIR)/../bin/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-server/src/zato/server

static-check:
	echo "Running static checks in zato-server"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

mypy-apispec:
	echo "Running mypy in zato-server / apispec"
	$(PY_DIR)/mypy --config-file=$(CURDIR)/../mypy.ini \
		$(CURDIR)/src/zato/server/apispec/

mypy-pubsub:
	echo "Running mypy in zato-server / pubsub"
	$(PY_DIR)/mypy --config-file=$(CURDIR)/../mypy.ini \
		$(CURDIR)/src/zato/server/pubsub/

pyright-apispec:
	pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/apispec/

pyright-pubsub:
	pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/__init__.py
	pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/model.py
	pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/task.py
	pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/sync.py

mypy:
	$(MAKE) mypy-apispec
	#$(MAKE) mypy-pubsub

pyright:
	$(MAKE) pyright-apispec
	#$(MAKE) pyright-pubsub

type-check:
	echo "Running type checks (zato-server)"
	$(MAKE) mypy
	$(MAKE) pyright
