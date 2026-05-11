.PHONY: help install install-deps clean \
	scheduler-install server-install io-install health-install \
	scheduler-clean server-clean io-clean health-clean tests-clean \
	scheduler-build server-build io-build health-build build \
	scheduler-rust-unit-tests scheduler-shim-tests scheduler-integration-tests scheduler-fuzzy \
	server-io-tests server-marshall-tests server-config-store-tests server-commands-tests \
	server-connection-tests server-pattern-tests server-pubsub-unit-tests server-pubsub-tests server-mcp-live-tests server-fuzzy server-tests \
	rate-limiting-rust-unit-tests rate-limiting-python-unit-tests test-rate-limiting \
	enmasse-tests cli-odb-default-tests cli-tests \
	common-tests distlock-tests web-admin-tests \
	health-hl7-tests health-fhir-tests \
	test-fast test-rust-unit test-integration test-pubsub test-fuzzy \
	test-all test \
	health-ruff health-clippy \
	test-rest test-rest-mutants \
	format format-zato \
	clippy clippy-zato \
	dylint dylint-zato \
	deny deny-zato \
	vet vet-zato \
	geiger geiger-zato \
	rust-lint lint

MAKEFLAGS += --silent --no-print-directory

ifndef Zato_Projects_Root
$(error Zato_Projects_Root is not set in the environment)
endif

Zato_Base       := $(Zato_Projects_Root)/zatosource-zato/4.1
Zato_Health     := $(Zato_Projects_Root)/private-zato-health
Zato_Libs       := $(Zato_Base)/code/zato-libs

ZATO_SITE_PACKAGES := $(shell $(Zato_Base)/code/bin/python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])" 2>/dev/null)

ZATO_PY  = $(Zato_Base)/code/bin/python

FAIL_ON_FIRST  ?=
SKIP_PASSED_F  ?=
FROM_LAST_F    ?=
SLOW_F         ?=
WITH_COVERAGE_F ?=
ONLY_EOD_F     ?=
PERF_TIER      ?=
HEAVY          ?=
JSON           ?=

FAIL_FAST     := $(if $(FAIL_ON_FIRST),-x,)
SKIP_PASSED   := $(if $(SKIP_PASSED_F),--ff,)
FROM_LAST     := $(if $(FROM_LAST_F),--lf,)
FROM_LAST_CS  := $(if $(FROM_LAST_F),--ff,)
SLOW          := $(if $(SLOW_F),--slow,)
WITH_COVERAGE := $(if $(WITH_COVERAGE_F),--with-coverage,)
ONLY_EOD      := $(if $(ONLY_EOD_F),--only-exactly-once-delivery,)
PERF_ARGS     := $(if $(HEAVY),heavy,) $(if $(JSON),json,) $(PERF_TIER)

help:
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-32s %s\n", $$1, $$2}'

install-deps: ## Create local venv and install this repo's test dependencies.
	cd tests && uv venv .venv --clear
	cd tests && uv pip install -r requirements.txt

install: install-deps scheduler-install server-install io-install health-install ## Full install across every component (deps + build).

scheduler-install: ## Install/build the public scheduler Rust extension.
	$(MAKE) -C $(Zato_Base) scheduler-install

server-install: ## Install/build the public server Rust extension.
	$(MAKE) -C $(Zato_Base) server-install

io-install: ## Install/build the public I/O Rust extension.
	$(MAKE) -C $(Zato_Base) io-install

health-install: ## Install health deps and build.
	$(MAKE) -C $(Zato_Health) install

clean: tests-clean scheduler-clean server-clean io-clean health-clean ## Wipe all build artifacts and venvs across every component.

tests-clean: ## Wipe this repo's venv and pytest caches.
	rm -rf tests/.venv
	find tests -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find tests -type d -name '.pytest_cache*' -exec rm -rf {} + 2>/dev/null || true

scheduler-clean: ## Clean public scheduler Rust target dir.
	$(MAKE) -C $(Zato_Base) scheduler-clean

server-clean: ## Clean public server Rust target dir.
	$(MAKE) -C $(Zato_Base) server-clean

io-clean: ## Clean public I/O Rust target dir.
	$(MAKE) -C $(Zato_Base) io-clean

health-clean: ## Clean health build artifacts and zato-libs entries.
	$(MAKE) -C $(Zato_Health) clean

scheduler-build: ## Build the public scheduler Rust extension.
	$(MAKE) -C $(Zato_Base) scheduler-build

server-build: ## Build the public server Rust extension.
	$(MAKE) -C $(Zato_Base) server-build

io-build: ## Build the public I/O Rust extension.
	$(MAKE) -C $(Zato_Base) io-build

health-build: ## Build the healthcare Rust extensions and copy .so files into zato-libs.
	$(MAKE) -C $(Zato_Health) build

fhir-rust-build: ## Build the FHIR Rust extension (delegates to top-level Makefile).
	$(MAKE) -C $(Zato_Base) fhir-rust-build

build: scheduler-build server-build io-build health-build ## Build everything across all repos.

ensure-io-built:
	@$(ZATO_PY) -c "from zato import input_output" 2>/dev/null || \
		{ echo "--- Auto-building I/O ---"; $(MAKE) io-build; }

ensure-scheduler-built:
	@$(ZATO_PY) -c "import zato_scheduler_core" 2>/dev/null || \
		{ echo "--- Auto-building scheduler ---"; $(MAKE) scheduler-build; }

ZATO_SCHEDULER_TESTS        = $(CURDIR)/tests/python/zato-scheduler/rust-unit-tests
ZATO_RATE_LIMITING_TESTS    = $(CURDIR)/tests/python/zato-rate-limiting/rust-unit-tests
ZATO_RATE_LIMITING_PY_TESTS = $(CURDIR)/tests/python/zato-rate-limiting/python-unit-tests

scheduler-rust-unit-tests: ensure-scheduler-built ## Scheduler Rust unit tests.
	. $(HOME)/.cargo/env && \
	cd $(ZATO_SCHEDULER_TESTS) && cargo test $(PYTEST_ARGS)

rate-limiting-rust-unit-tests: ## Rate limiting Rust unit tests (token bucket, proptest).
	. $(HOME)/.cargo/env && \
	cd $(ZATO_RATE_LIMITING_TESTS) && cargo test $(PYTEST_ARGS)

rate-limiting-python-unit-tests: ## Rate limiting Python unit tests (token bucket, fixed window).
	$(ZATO_PY) -m pytest $(ZATO_RATE_LIMITING_PY_TESTS) -v -s -o cache_dir=tests/.pytest_cache_rate_limiting_py $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

test-rate-limiting: rate-limiting-rust-unit-tests rate-limiting-python-unit-tests ## All rate limiting tests.

scheduler-shim-tests: ensure-scheduler-built ## Scheduler Python shim tests.
	$(ZATO_PY) -m pytest tests/python/zato-scheduler/test_scheduler_shim.py -v -s -o cache_dir=tests/.pytest_cache_scheduler_shim -W ignore::DeprecationWarning $(FAIL_FAST) $(SKIP_PASSED) $(PYTEST_ARGS)

scheduler-integration-tests: ensure-scheduler-built ## Scheduler Python integration tests.
	$(ZATO_PY) -m pytest tests/python/zato-scheduler/ -v -s -o cache_dir=tests/.pytest_cache_scheduler -W ignore::DeprecationWarning --ignore=tests/python/zato-scheduler/rust-unit-tests --ignore=tests/python/zato-scheduler/test_scheduler_shim.py $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST_CS) $(WITH_COVERAGE) $(PYTEST_ARGS)

scheduler-fuzzy: ## Scheduler proptest + cargo-fuzz.
	$(MAKE) -C $(Zato_Base) scheduler-tests timeout=$(timeout)

server-io-tests: ensure-io-built ## I/O unit tests (public src).
	$(ZATO_PY) -m pytest $(Zato_Base)/code/zato-server/test/zato/test_io_eval.py -v -s -o cache_dir=tests/.pytest_cache_io $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

server-marshall-tests: ## Marshall unit tests (public src).
	$(ZATO_PY) -m pytest $(Zato_Base)/code/zato-common/test/zato/common/marshall_/ -v -s -o cache_dir=tests/.pytest_cache_marshall $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

server-config-store-tests: ## ConfigStore integration tests (spins up a temp server).
	$(ZATO_PY) -m pytest tests/python/zato-server/config_store/ -v -s -o cache_dir=tests/.pytest_cache_config_store -W ignore::DeprecationWarning $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST_CS) $(WITH_COVERAGE) $(PYTEST_ARGS)

server-commands-tests: ## Server commands_ tests (public src).
	$(ZATO_PY) $(Zato_Base)/code/zato-server/test/zato/commands_/test_commands.py

server-connection-tests: ## Server connection tests (public src).
	$(ZATO_PY) -m pytest $(Zato_Base)/code/zato-server/test/zato/connection/ -v -s -o cache_dir=tests/.pytest_cache_connection $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

server-pattern-tests: ## Server pattern tests (public src).
	$(ZATO_PY) -m pytest $(Zato_Base)/code/zato-server/test/zato/pattern/ -v -s -o cache_dir=tests/.pytest_cache_pattern $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

server-pubsub-unit-tests: ## PubSub unit tests (private src, no server needed).
	$(ZATO_PY) -m unittest discover -s tests/python/zato-common/pubsub -p 'test_*.py' -v

server-pubsub-tests: ## PubSub REST integration tests (private src, starts a temp server via conftest.py).
	$(ZATO_PY) -m pytest tests/python/zato-server/pubsub_rest -v -s -o cache_dir=tests/.pytest_cache_pubsub $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

test-pubsub: server-pubsub-unit-tests server-pubsub-tests ## All PubSub tests: unit first, then REST integration.

server-mcp-live-tests: ## MCP live API integration tests (spins up a temp server).
	$(ZATO_PY) -m pytest tests/python/zato-server/mcp_live/ -v -s -o cache_dir=tests/.pytest_cache_mcp_live -W ignore::DeprecationWarning $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST_CS) $(WITH_COVERAGE) $(PYTEST_ARGS)

server-tests: ## Aggregate server-side test target running every server tests group.
	$(MAKE) -C $(Zato_Base)/code/zato-server test

server-fuzzy: ## Server proptest + cargo-fuzz.
	$(MAKE) -C $(Zato_Base)/code/zato-server fuzzy timeout=$(timeout)

enmasse-tests: ## Enmasse round-trip tests (public src).
	$(ZATO_PY) -m unittest discover -s $(Zato_Base)/code/zato-cli/test/zato/enmasse_ -p 'test_*.py' -v

cli-odb-default-tests: ## Verify quickstart defaults to SQLite ODB.
	$(ZATO_PY) -m pytest tests/python/zato-cli/test_odb_sqlite_default.py -v -s -o cache_dir=tests/.pytest_cache_cli_odb $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

cli-tests: ## All CLI tests (public per-component).
	$(MAKE) -C $(Zato_Base)/code/zato-cli test

common-tests: ## Common tests (public per-component).
	$(MAKE) -C $(Zato_Base)/code/zato-common test

distlock-tests: ## Distlock tests (public per-component).
	$(MAKE) -C $(Zato_Base)/code/zato-distlock test

web-admin-tests: ## Web-admin tests (public per-component).
	$(MAKE) -C $(Zato_Base)/code/zato-web-admin test

health-hl7-tests: ## HL7v2 tests run inside the health repo.
	$(MAKE) -C $(Zato_Health) hl7-tests

health-fhir-tests: ## FHIR tests run inside the health repo.
	$(MAKE) -C $(Zato_Health) fhir-tests

test-fast: server-io-tests server-marshall-tests scheduler-shim-tests ## Fastest: pure-Python unit tests.

test-rust-unit: scheduler-rust-unit-tests rate-limiting-rust-unit-tests ## Rust unit tests (cargo test).

test-integration: enmasse-tests scheduler-integration-tests test-pubsub cli-odb-default-tests server-config-store-tests server-mcp-live-tests ## Python integration tests.

test-fuzzy: server-fuzzy scheduler-fuzzy ## Proptest + cargo-fuzz across all crates.

test-all: test-fast test-rust-unit test-integration test-fuzzy ## Everything, fastest first.

test: test-all ## Alias for test-all.

# ----------------------------------------------------------------------------
# Rust lint infrastructure
#
# All lint config lives here (private repo). Public crates ship only
# unsafe_code = "forbid" and overflow-checks = true.
#
# CLIPPY_CONF_DIR points clippy at our clippy.toml.
# ZATO_CLIPPY_FLAGS passes -W/-D/-A lint levels via the -- separator.
# Same pattern as the Linux kernel and TiKV.
# ----------------------------------------------------------------------------

ZATO_CLIPPY_CONF := $(CURDIR)/tests/rust/rust-lint
ZATO_RUST_DIR    := $(Zato_Base)/code/zato-rust

ZATO_CLIPPY_FLAGS := \
	-W unused \
	-W future-incompatible \
	-W nonstandard-style \
	-W rust-2018-idioms \
	-W rust-2021-compatibility \
	-W let-underscore \
	-A let_underscore_drop \
	-W missing-docs \
	-D unsafe-code \
	-W clippy::pedantic \
	-W clippy::nursery \
	-W clippy::cargo \
	-D clippy::unwrap_used \
	-D clippy::expect_used \
	-D clippy::unwrap_in_result \
	-D clippy::panic \
	-D clippy::todo \
	-D clippy::unimplemented \
	-D clippy::unreachable \
	-D clippy::indexing_slicing \
	-A clippy::let_underscore_must_use \
	-D clippy::mem_forget \
	-D clippy::dbg_macro \
	-D clippy::min_ident_chars \
	-D clippy::allow_attributes_without_reason \
	-W clippy::as_conversions \
	-W clippy::clone_on_ref_ptr \
	-W clippy::map_err_ignore \
	-W clippy::print_stdout \
	-W clippy::print_stderr \
	-W clippy::single_char_lifetime_names \
	-W clippy::missing_docs_in_private_items \
	-W clippy::undocumented_unsafe_blocks \
	-A clippy::module_name_repetitions \
	-A clippy::missing_errors_doc \
	-A clippy::missing_panics_doc \
	-A clippy::similar_names \
	-A clippy::too_many_lines \
	-A clippy::must_use_candidate \
	-A clippy::multiple_crate_versions \
	-D warnings

CLIPPY_CMD = . $(HOME)/.cargo/env && CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) \
	cargo clippy --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS)

format-zato: ## Check Rust formatting across all public crates.
	. $(HOME)/.cargo/env && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_input_output/Cargo.toml             -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   -- --check

format: format-zato ## Check Rust formatting everywhere.

clippy-zato: ## Clippy all public Rust crates.
	. $(HOME)/.cargo/env && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_input_output/Cargo.toml             --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS)

clippy: clippy-zato ## Clippy everything.

DYLINT_GIT  := https://github.com/trailofbits/dylint
DYLINT_TAG  := v5.0.0
DYLINT_LIBS := --git $(DYLINT_GIT) --tag $(DYLINT_TAG) --pattern examples/general

ZATO_DYLINT_FLAGS_COMMON := \
	-D non-local-effect-before-error-return \
	-D crate-wide-allow \
	-D await-holding-span-guard \
	-D basic-dead-store \
	-D incorrect-matches-operation \
	-D wrong-serialize-struct-arg \
	-D abs-home-path

ZATO_DYLINT_FLAGS := -A non-thread-safe-call-in-test $(ZATO_DYLINT_FLAGS_COMMON)

dylint-zato: ## Dylint all public Rust crates.
	. $(HOME)/.cargo/env && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_input_output/Cargo.toml             -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   -- --tests

dylint: dylint-zato ## Dylint everything.

deny-zato: ## Dependency audit (advisories, licenses, bans) for public crates.
	. $(HOME)/.cargo/env && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    check --config $(CURDIR)/tests/rust/rust-lint/deny.toml && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    check --config $(CURDIR)/tests/rust/rust-lint/deny.toml && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml check --config $(CURDIR)/tests/rust/rust-lint/deny.toml && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_input_output/Cargo.toml             check --config $(CURDIR)/tests/rust/rust-lint/deny.toml && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   check --config $(CURDIR)/tests/rust/rust-lint/deny.toml

deny: deny-zato ## Dependency audit everywhere.

vet-zato: ## Supply-chain audit for public crates.
	. $(HOME)/.cargo/env && \
	cargo vet --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml --store-path $(CURDIR)/tests/rust/rust-lint/supply-chain-zato

vet: vet-zato ## Supply-chain audit everywhere.

geiger-zato: ## Report unsafe usage in public crate dependency trees.
	. $(HOME)/.cargo/env && \
	cargo geiger --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml && \
	cargo geiger --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml && \
	cargo geiger --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml

geiger: geiger-zato ## Report unsafe usage everywhere.

rust-lint: format clippy dylint deny vet geiger ## Full Rust static analysis pipeline.

health-ruff: ## Run ruff inside the health repo.
	$(MAKE) -C $(Zato_Health) ruff

lint: rust-lint ## Full static analysis pipeline.

health-clippy: ## Run clippy inside the health repo.
	$(MAKE) -C $(Zato_Health) clippy

# ----------------------------------------------------------------------------
# REST tests (excludes pubsub)
# ----------------------------------------------------------------------------

test-rest: ## REST unit tests (http_soap dispatch and auth). Excludes pubsub, enmasse, and config_store integration tests.
	$(ZATO_PY) -m pytest \
		tests/python/zato-server/http_soap/ \
		-v -s -o cache_dir=tests/.pytest_cache_rest -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

COSMIC_RAY := $(Zato_Base)/code/bin/cosmic-ray

test-rest-mutants: ## Mutation testing on channel.py dispatch methods (cosmic-ray).
	rm -f tests/.cr-session.sqlite
	$(COSMIC_RAY) init tests/rust/cosmic-ray/channel.toml tests/.cr-session.sqlite
	$(COSMIC_RAY) baseline tests/rust/cosmic-ray/channel.toml
	$(COSMIC_RAY) exec tests/rust/cosmic-ray/channel.toml tests/.cr-session.sqlite
	@$(ZATO_PY) -c "\
	import sqlite3; \
	conn = sqlite3.connect('tests/.cr-session.sqlite'); \
	cur = conn.cursor(); \
	cur.execute(\"SELECT test_outcome, COUNT(*) FROM work_results GROUP BY test_outcome\"); \
	results = {r[0]: r[1] for r in cur.fetchall()}; \
	killed = results.get('KILLED', 0); \
	survived = results.get('SURVIVED', 0); \
	total = killed + survived; \
	print(f'Killed: {killed}/{total} ({killed/total*100:.1f}%)') if total else print('No results'); \
	print(f'Survived: {survived}/{total}') if survived else None; \
	"
