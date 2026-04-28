.PHONY: default build test clippy ruff
MAKEFLAGS += --silent

CRATE_DIR = $(CURDIR)/../zato-rust/zato_sio
PY = $(CURDIR)/../bin/python
export VIRTUAL_ENV = $(CURDIR)/..

default: build

build:
	. $$HOME/.cargo/env && cd $(CRATE_DIR) && $(PY) -m maturin develop --release

test:
	@$(PY) -c "import zato_sio" 2>/dev/null || \
		{ echo "SIO not built yet, run 'make build' first"; exit 1; }
	. $$HOME/.cargo/env && cd $(CRATE_DIR) && cargo clippy -- -D warnings
	. $$HOME/.cargo/env && cd $(CRATE_DIR) && cargo test

clippy:
	. $$HOME/.cargo/env && cd $(CRATE_DIR) && cargo clippy -- -D warnings

ruff:
	$(CURDIR)/../bin/ruff check $(CURDIR)/
