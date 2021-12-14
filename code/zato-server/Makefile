
.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin

run-tests:
	echo "Running unit-tests in zato-server"
	$(PY_DIR)/py $(CURDIR)/test/zato/file_transfer/test_*.py
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/apispec/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/pattern/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/server_rpc/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/stats/test_*.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/test_*.py -s

static-check:
	echo "Running static checks in zato-server"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

pyright:
	pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/__init__.py
	pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/model.py
	#pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/task.py

mypy:
	$(PY_DIR)/mypy --show-error-codes --ignore-missing-imports $(CURDIR)/src/zato/server/pubsub/__init__.py
	$(PY_DIR)/mypy --show-error-codes --ignore-missing-imports $(CURDIR)/src/zato/server/pubsub/model.py
	$(PY_DIR)/mypy --show-error-codes --ignore-missing-imports $(CURDIR)/src/zato/server/pubsub/task.py

type-check:
	echo "Running type checks in zato-server pubsub"
	$(MAKE) mypy
	$(MAKE) pyright