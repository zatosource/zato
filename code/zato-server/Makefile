
.PHONY: build

PY_DIR=$(CURDIR)/../bin

server-test:
	$(PY_DIR)/py $(CURDIR)/test/zato/test_apispec_generator.py && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_apispec_open_api.py  && \
	$(PY_DIR)/py $(CURDIR)/test/zato/test_apispec_sio_desc.py
