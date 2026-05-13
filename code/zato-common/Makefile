.PHONY: default build test clippy ruff
MAKEFLAGS += --silent

CRATE_DIR = $(CURDIR)/../zato-rust/zato_input_output
PY = $(CURDIR)/../bin/python
export VIRTUAL_ENV = $(CURDIR)/..

default: build

build:
	. $$HOME/.cargo/env && cd $(CRATE_DIR) && $(PY) -m maturin develop --release

test:
	@$(PY) -c "from zato import input_output" 2>/dev/null || \
		{ echo "I/O module not built yet, run 'make build' first"; exit 1; }
	. $$HOME/.cargo/env && cd $(CRATE_DIR) && cargo clippy -- -D warnings
	. $$HOME/.cargo/env && cd $(CRATE_DIR) && cargo test

clippy:
	. $$HOME/.cargo/env && cd $(CRATE_DIR) && cargo clippy -- -D warnings

ruff:
	$(CURDIR)/../bin/ruff check $(CURDIR)/
