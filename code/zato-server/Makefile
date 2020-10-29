
.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin

run-tests:
	$(PY_DIR)/py $(CURDIR)/test/zato/test_apispec_generator.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_apispec_open_api.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_apispec_docstring_service.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_apispec_docstring_sio.py
