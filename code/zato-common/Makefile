
.PHONY: test

PY_DIR=$(CURDIR)/../bin

run-tests:
	echo "Running unit-tests in zato-common"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/test_kv_data_api.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/test_util.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/marshall_/test_attach.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/marshall_/test_validation.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/marshall_/test_json_to_dataclass.py -s

pylint:
	echo Running pylint in zato-common
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-common/src/zato/common/

static-check:
	echo "Running static checks in zato-common"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

pyright:
	pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/common/pubsub.py

mypy:
	$(PY_DIR)/mypy --show-error-codes --ignore-missing-imports $(CURDIR)/src/zato/common/pubsub.py

type-check:
	echo "Running type checks (zato-common)"
	$(MAKE) mypy
	$(MAKE) pyright
