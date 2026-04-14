
.PHONY: build test fuzzy flake8 static-check

MAKEFLAGS += --silent

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-server
Zato_Core_Dir=$(CURDIR)/src/zato_server_core
Zato_Fuzz_Timeout=$(or $(timeout),$(Zato_Fuzz_Test_Timeout),120)

FUZZ_TARGETS = \
	fuzz_format_access_line \
	fuzz_format_rest_line \
	fuzz_header_value_eq \
	fuzz_log_writer \
	fuzz_make_cid_public \
	fuzz_parse_content_length \
	fuzz_parse_status_code \
	fuzz_transform_header_key \
	fuzz_trim_ows

MUTANT_FILES = \
	-f src/http/io.rs \
	-f src/http/response.rs \
	-f src/http/request.rs \
	-f src/logging.rs

MUTANT_EXCLUDES = \
	'with_gevent_io|fd_read|fd_write_all|build_response|handle_http_request|get_cached_attrs|chrono_to_py_datetime|log_rest_summary|log_access|init_rest_log|init_access_log|init_writer'

test:
	echo "Running tests in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/test_sio_*.py -s
	$(Zato_Python_Dir)/py     $(CURDIR)/test/zato/commands_/test_*.py

fuzzy:
	echo "=== Running proptest in $(Zato_Package_Name) ==="
	. $$HOME/.cargo/env && cd $(Zato_Core_Dir) && cargo test
	echo "=== Running cargo-fuzz in $(Zato_Package_Name) ($(Zato_Fuzz_Timeout)s per target) ==="
	. $$HOME/.cargo/env && cd $(Zato_Core_Dir) && \
		for target in $(FUZZ_TARGETS); do \
			echo "  Fuzzing $$target ..."; \
			cargo +nightly fuzz run $$target -- -max_total_time=$(Zato_Fuzz_Timeout) 2>&1 | tail -1; \
		done
	echo "=== Running cargo-mutants in $(Zato_Package_Name) ==="
	. $$HOME/.cargo/env && cd $(Zato_Core_Dir) && cargo mutants --no-shuffle $(MUTANT_FILES) --exclude-re $(MUTANT_EXCLUDES)

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	$(MAKE) flake8
