
.PHONY: build test fuzzy
MAKEFLAGS += --silent

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-server

test:
	echo "Running tests in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/test_sio_*.py -s
	$(Zato_Python_Dir)/py     $(CURDIR)/test/zato/commands_/test_*.py

fuzzy:
	echo "Running proptest in $(Zato_Package_Name)"
	. $$HOME/.cargo/env && cd $(CURDIR)/src/zato_server_core && cargo test
	echo "Running cargo-mutants in $(Zato_Package_Name)"
	. $$HOME/.cargo/env && cd $(CURDIR)/src/zato_server_core && cargo mutants --no-shuffle -f src/http/io.rs -f src/http/response.rs --exclude-re 'with_gevent_io|fd_read|fd_write_all|build_response'

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	$(MAKE) flake8
