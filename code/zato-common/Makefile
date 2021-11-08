
.PHONY: test

PY_DIR=$(CURDIR)/../bin

run-tests:
	echo "Running unit-tests in zato-common"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/test_kv_data_api.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/test_util.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/marshall_/test_json_to_dataclass.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/marshall_/test_attach.py -s
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/common/marshall_/test_validation.py -s

static-check:
	echo "Running static checks in zato-common"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
