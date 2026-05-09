.PHONY: help install install-deps clean \
	broker-install scheduler-install server-install sio-install health-install \
	broker-clean scheduler-clean server-clean sio-clean health-clean tests-clean \
	broker-build scheduler-build server-build sio-build health-build build \
	broker-rust-unit-tests broker-rust-unit-tests-sudo broker-uring-tests broker-uring-bpf-tests \
	broker-chaos-tests broker-backup-tests broker-perf-tests broker-perf-tests-collect-info \
	broker-fuzzy broker-alloy-tests \
	scheduler-rust-unit-tests scheduler-shim-tests scheduler-integration-tests scheduler-fuzzy \
	server-sio-tests server-marshall-tests server-config-store-tests server-commands-tests \
	server-connection-tests server-pattern-tests server-pubsub-unit-tests server-pubsub-tests server-mcp-live-tests server-fuzzy server-tests \
	rate-limiting-rust-unit-tests rate-limiting-python-unit-tests test-rate-limiting \
	enmasse-tests cli-odb-default-tests cli-tests \
	common-tests cy-tests distlock-tests web-admin-tests \
	health-hl7-tests health-fhir-tests \
	test-fast test-rust-unit test-integration test-pubsub test-chaos test-uring test-perf test-fuzzy test-formal \
	test-all test \
	ruff ruff-zato ruff-tests fix broker-ruff health-ruff broker-clippy health-clippy \
	pyright pyright-zato \
	audit audit-zato \
	licenses licenses-zato \
	deptry deptry-zato \
	vulture vulture-zato \
	sbom sbom-zato \
	python-lint \
	auth-tests auth-coverage-rust auth-coverage-python auth-mutation auth-miri test-auth-coverage test-rest test-rest-mutants \
	broker-tests-auth broker-tests-auth-mutants broker-tests-auth-fuzzy broker-tests-auth-proptest \
	format format-zato format-broker format-work-arena \
	clippy clippy-zato clippy-broker clippy-work-arena \
	dylint dylint-zato dylint-broker dylint-work-arena \
	deny deny-zato deny-broker deny-work-arena \
	vet vet-zato vet-broker vet-work-arena \
	geiger geiger-zato geiger-broker geiger-work-arena \
	work-arena-build work-arena-install work-arena-clean ensure-work-arena-built \
	work-arena-rust-unit-tests work-arena-perf-tests \
	rust-lint lint

MAKEFLAGS += --silent --no-print-directory

ifndef Zato_Projects_Root
$(error Zato_Projects_Root is not set in the environment)
endif

Zato_Base       := $(Zato_Projects_Root)/zatosource-zato/4.1
Zato_Broker     := $(Zato_Projects_Root)/private-zato-broker
Zato_Health     := $(Zato_Projects_Root)/private-zato-health
Zato_Work_Arena := $(Zato_Projects_Root)/private-zato-work-arena
Zato_Libs       := $(Zato_Base)/code/zato-libs

ZATO_SITE_PACKAGES := $(shell $(Zato_Base)/code/bin/python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])" 2>/dev/null)

CHAOS_PY = PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(ZATO_SITE_PACKAGES) tests/.venv/bin/python
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

# --only-exactly-once-delivery
#
# Run ONLY tests that enforce the exactly-once delivery contract.
# Every ChaosTestCase subclass carries @pytest.mark.exactly_once automatically.
# When this flag is active, any test WITHOUT that marker is skipped.

help:
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-32s %s\n", $$1, $$2}'

install-deps: ## Create local venv and install this repo's test dependencies.
	cd tests && uv venv .venv --clear
	cd tests && uv pip install -r requirements.txt

install: install-deps broker-install scheduler-install server-install sio-install health-install work-arena-install ## Full install across every component (deps + build).

broker-install: ## Install broker deps and build.
	$(MAKE) -C $(Zato_Broker) install

scheduler-install: ## Install/build the public scheduler Rust extension.
	$(MAKE) -C $(Zato_Base) scheduler-install

server-install: ## Install/build the public server Rust extension.
	$(MAKE) -C $(Zato_Base) server-install

sio-install: ## Install/build the public SIO Rust extension.
	$(MAKE) -C $(Zato_Base) sio-install

health-install: ## Install health deps and build.
	$(MAKE) -C $(Zato_Health) install

clean: tests-clean broker-clean scheduler-clean server-clean sio-clean health-clean work-arena-clean ## Wipe all build artifacts and venvs across every component.

tests-clean: ## Wipe this repo's venv and pytest caches.
	rm -rf tests/.venv
	find tests -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find tests -type d -name '.pytest_cache*' -exec rm -rf {} + 2>/dev/null || true

broker-clean: ## Clean broker build artifacts and zato-libs entry.
	$(MAKE) -C $(Zato_Broker) clean

scheduler-clean: ## Clean public scheduler Rust target dir.
	$(MAKE) -C $(Zato_Base) scheduler-clean

server-clean: ## Clean public server Rust target dir.
	$(MAKE) -C $(Zato_Base) server-clean

sio-clean: ## Clean public SIO Rust target dir.
	$(MAKE) -C $(Zato_Base) sio-clean

health-clean: ## Clean health build artifacts and zato-libs entries.
	$(MAKE) -C $(Zato_Health) clean

broker-build: ## Build the broker Rust extension and copy .so into zato-libs.
	$(MAKE) -C $(Zato_Broker) build

scheduler-build: ## Build the public scheduler Rust extension.
	$(MAKE) -C $(Zato_Base) scheduler-build

server-build: ## Build the public server Rust extension.
	$(MAKE) -C $(Zato_Base) server-build

sio-build: ## Build the public SIO Rust extension.
	$(MAKE) -C $(Zato_Base) sio-build

health-build: ## Build the healthcare Rust extensions and copy .so files into zato-libs.
	$(MAKE) -C $(Zato_Health) build

work-arena-build: ## Build the work arena Rust extension.
	. $(HOME)/.cargo/env && \
	VIRTUAL_ENV=$(Zato_Base)/code maturin develop --release --manifest-path $(Zato_Work_Arena)/Cargo.toml

work-arena-install: work-arena-build ## Install work arena (alias for build).

work-arena-clean: ## Clean work arena build artifacts.
	. $(HOME)/.cargo/env && cargo clean --manifest-path $(Zato_Work_Arena)/Cargo.toml

build: broker-build scheduler-build server-build sio-build health-build work-arena-build ## Build everything across all repos.

ensure-work-arena-built:
	@$(ZATO_PY) -c "import zato_work_arena_core" 2>/dev/null || \
		{ echo "--- Auto-building work-arena ---"; $(MAKE) work-arena-build; }

ensure-broker-built:
	@$(CHAOS_PY) -c "import zato_broker_core" 2>/dev/null || \
		{ echo "--- Auto-building broker ---"; $(MAKE) broker-build; }

ensure-sio-built:
	@$(ZATO_PY) -c "import zato_sio" 2>/dev/null || \
		{ echo "--- Auto-building sio ---"; $(MAKE) sio-build; }

ensure-scheduler-built:
	@$(ZATO_PY) -c "import zato_scheduler_core" 2>/dev/null || \
		{ echo "--- Auto-building scheduler ---"; $(MAKE) scheduler-build; }

broker-rust-unit-tests: ensure-broker-built ## Broker Rust unit tests (cargo test, includes crash + DLQ integration).
	. $(HOME)/.cargo/env && \
	cd $(Zato_Broker)/code/zato-broker/src/zato_broker_core && \
		RUST_BACKTRACE=1 cargo test -- --skip test_perf --nocapture $(PYTEST_ARGS)

broker-rust-unit-tests-sudo: ensure-broker-built ## Broker unit tests that require root (dm-flakey temp file leak, etc.).
	sudo -E PYTHONDONTWRITEBYTECODE=1 COLUMNS=$$(tput cols 2>/dev/null || echo 200) $(CHAOS_PY) -m pytest tests/src/zato-broker/chaos/test_tmp_file_leak.py -v -s -o cache_dir=tests/.pytest_cache_broker_sudo $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS); _rc=$$?; stty sane 2>/dev/null; exit $$_rc

broker-uring-tests: ensure-broker-built ## io_uring writer config and back-pressure tests.
	. $(HOME)/.cargo/env && \
	cd $(Zato_Broker)/code/zato-broker/src/zato_broker_core && \
		RUST_BACKTRACE=1 cargo test -- --nocapture \
			test_iouring_small_max_inflight_backpressure \
			test_iouring_diag_stats \
			test_iouring_set_max_inflight \
			test_iouring_set_max_inflight_clamps_to_half_ring \
			test_iouring_set_max_inflight_clamps_low \
			test_iouring_default_max_inflight \
			test_iouring_config_override_max_inflight \
			test_default_max_inflight_is_4096 \
			$(PYTEST_ARGS)

broker-uring-bpf-tests: ensure-broker-built ## io_uring back-pressure BPF tests. Requires root and bpftrace.
	sudo -E PYTHONDONTWRITEBYTECODE=1 COLUMNS=$$(tput cols 2>/dev/null || echo 200) $(CHAOS_PY) -m pytest tests/src/zato-broker/chaos/test_iouring_backpressure.py -v -s -o cache_dir=tests/.pytest_cache_broker $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS); _rc=$$?; stty sane 2>/dev/null; exit $$_rc

broker-chaos-tests: ensure-broker-built ## Broker chaos tests. Append fail-on-first / skip-passed / slow / only-exactly-once-delivery.
ifdef NOSUDO
	$(CHAOS_PY) -m pytest tests/src/zato-broker/chaos/ -v -s -o cache_dir=tests/.pytest_cache_broker -k "not needs_root" $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(SLOW) $(ONLY_EOD) $(PYTEST_ARGS); _rc=$$?; stty sane 2>/dev/null; exit $$_rc
else
	sudo -E PYTHONDONTWRITEBYTECODE=1 COLUMNS=$$(tput cols 2>/dev/null || echo 200) $(CHAOS_PY) -m pytest tests/src/zato-broker/chaos/ -v -s -o cache_dir=tests/.pytest_cache_broker $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(SLOW) $(ONLY_EOD) $(PYTEST_ARGS); _rc=$$?; stty sane 2>/dev/null; exit $$_rc
endif

broker-backup-tests: ensure-broker-built ## Broker backup/restore chaos tests. Append fail-on-first / skip-passed / slow / only-exactly-once-delivery.
ifdef NOSUDO
	$(CHAOS_PY) -m pytest tests/src/zato-broker/chaos/ -v -s -o cache_dir=tests/.pytest_cache_broker -k "backup" -k "not needs_root" $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(SLOW) $(ONLY_EOD) $(PYTEST_ARGS); _rc=$$?; stty sane 2>/dev/null; exit $$_rc
else
	sudo -E PYTHONDONTWRITEBYTECODE=1 COLUMNS=$$(tput cols 2>/dev/null || echo 200) $(CHAOS_PY) -m pytest tests/src/zato-broker/chaos/ -v -s -o cache_dir=tests/.pytest_cache_broker -k "backup" $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(SLOW) $(ONLY_EOD) $(PYTEST_ARGS); _rc=$$?; stty sane 2>/dev/null; exit $$_rc
endif

broker-perf-tests: ensure-broker-built ## Broker perf tests (cargo test perf + Python perf runner).
	$(MAKE) -C $(Zato_Broker) perf-tests scenario=$(scenario) coro=$(coro) fsync=$(fsync) topics=$(topics) clients=$(clients) subs=$(subs) pubs=$(pubs) msgsize=$(msgsize) shard-drain-flush-passes=$(shard-drain-flush-passes) PERF_ARGS="$(PERF_ARGS)"

broker-perf-tests-collect-info: ## Collect all diagnostic data from a running broker.
	$(MAKE) -C $(Zato_Broker) perf-tests-collect-info

broker-fuzzy: ensure-broker-built ## Broker proptest + cargo-fuzz + cargo-mutants.
	$(MAKE) -C $(Zato_Broker) fuzzy timeout=$(timeout)

broker-alloy-tests: ## Alloy formal model checks for exactly-once delivery (parallel).
	java -version >/dev/null 2>&1 || { echo "Java not found - install JDK 11+ to run Alloy checks"; exit 1; }
	test -f tests/src/zato-broker/alloy-tests/org.alloytools.alloy.dist.jar || { echo "Alloy jar not found in tests/src/zato-broker/alloy-tests/"; exit 1; }
	tests/.venv/bin/python -m pytest tests/src/zato-broker/alloy-tests/ -v -rsx --tb=long -o cache_dir=tests/.pytest_cache_alloy -n auto --dist loadgroup $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

ZATO_SCHEDULER_TESTS        = $(CURDIR)/tests/src/zato-scheduler/rust-unit-tests
ZATO_RATE_LIMITING_TESTS    = $(CURDIR)/tests/src/zato-rate-limiting/rust-unit-tests
ZATO_RATE_LIMITING_PY_TESTS = $(CURDIR)/tests/src/zato-rate-limiting/python-unit-tests
ZATO_WORK_ARENA_TESTS       = $(CURDIR)/tests/src/zato-work-arena/rust-unit-tests

work-arena-rust-unit-tests: ensure-work-arena-built ## Work arena Rust unit tests.
	. $(HOME)/.cargo/env && \
	cd $(ZATO_WORK_ARENA_TESTS) && cargo test -- --skip perf_ $(PYTEST_ARGS)

work-arena-perf-tests: ensure-work-arena-built ## Work arena performance tests.
	. $(HOME)/.cargo/env && \
	cd $(ZATO_WORK_ARENA_TESTS) && cargo test --release -- perf_ $(PYTEST_ARGS)

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
	$(ZATO_PY) -m pytest tests/src/zato-scheduler/test_scheduler_shim.py -v -s -o cache_dir=tests/.pytest_cache_scheduler_shim -W ignore::DeprecationWarning $(FAIL_FAST) $(SKIP_PASSED) $(PYTEST_ARGS)

scheduler-integration-tests: ensure-scheduler-built ## Scheduler Python integration tests.
	$(ZATO_PY) -m pytest tests/src/zato-scheduler/ -v -s -o cache_dir=tests/.pytest_cache_scheduler -W ignore::DeprecationWarning --ignore=tests/src/zato-scheduler/rust-unit-tests --ignore=tests/src/zato-scheduler/test_scheduler_shim.py $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST_CS) $(WITH_COVERAGE) $(PYTEST_ARGS)

scheduler-fuzzy: ## Scheduler proptest + cargo-fuzz.
	$(MAKE) -C $(Zato_Base) scheduler-tests timeout=$(timeout)

server-sio-tests: ensure-sio-built ## SIO unit tests (public src).
	$(ZATO_PY) -m pytest $(Zato_Base)/code/zato-server/test/zato/test_sio_eval.py -v -s -o cache_dir=tests/.pytest_cache_sio $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

server-marshall-tests: ## Marshall unit tests (public src).
	$(ZATO_PY) -m pytest $(Zato_Base)/code/zato-common/test/zato/common/marshall_/ -v -s -o cache_dir=tests/.pytest_cache_marshall $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

server-config-store-tests: ## ConfigStore integration tests (spins up a temp server).
	$(ZATO_PY) -m pytest tests/src/zato-server/config_store/ -v -s -o cache_dir=tests/.pytest_cache_config_store -W ignore::DeprecationWarning $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST_CS) $(WITH_COVERAGE) $(PYTEST_ARGS)

server-commands-tests: ## Server commands_ tests (public src).
	$(ZATO_PY) $(Zato_Base)/code/zato-server/test/zato/commands_/test_commands.py

server-connection-tests: ## Server connection tests (public src).
	$(ZATO_PY) -m pytest $(Zato_Base)/code/zato-server/test/zato/connection/ -v -s -o cache_dir=tests/.pytest_cache_connection $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

server-pattern-tests: ## Server pattern tests (public src).
	$(ZATO_PY) -m pytest $(Zato_Base)/code/zato-server/test/zato/pattern/ -v -s -o cache_dir=tests/.pytest_cache_pattern $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

server-pubsub-unit-tests: ## PubSub unit tests (private src, no server needed).
	$(ZATO_PY) -m unittest discover -s tests/src/zato-common/pubsub -p 'test_*.py' -v

server-pubsub-tests: ## PubSub REST integration tests (private src, starts a temp server via conftest.py).
	$(ZATO_PY) -m pytest tests/src/zato-server/pubsub_rest -v -s -o cache_dir=tests/.pytest_cache_pubsub $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

test-pubsub: server-pubsub-unit-tests server-pubsub-tests ## All PubSub tests: unit first, then REST integration.

server-mcp-live-tests: ## MCP live API integration tests (spins up a temp server).
	$(ZATO_PY) -m pytest tests/src/zato-server/mcp_live/ -v -s -o cache_dir=tests/.pytest_cache_mcp_live -W ignore::DeprecationWarning $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST_CS) $(WITH_COVERAGE) $(PYTEST_ARGS)

server-tests: ## Aggregate server-side test target running every server tests group.
	$(MAKE) -C $(Zato_Base)/code/zato-server test

server-fuzzy: ## Server proptest + cargo-fuzz.
	$(MAKE) -C $(Zato_Base)/code/zato-server fuzzy timeout=$(timeout)

enmasse-tests: ## Enmasse round-trip tests (public src).
	$(ZATO_PY) -m unittest discover -s $(Zato_Base)/code/zato-cli/test/zato/enmasse_ -p 'test_*.py' -v

cli-odb-default-tests: ## Verify quickstart defaults to SQLite ODB.
	$(ZATO_PY) -m pytest tests/src/zato-cli/test_odb_sqlite_default.py -v -s -o cache_dir=tests/.pytest_cache_cli_odb $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

cli-tests: ## All CLI tests (public per-component).
	$(MAKE) -C $(Zato_Base)/code/zato-cli test

common-tests: ## Common tests (public per-component).
	$(MAKE) -C $(Zato_Base)/code/zato-common test

cy-tests: ## Cython tests (public per-component).
	$(MAKE) -C $(Zato_Base)/code/zato-cy test

distlock-tests: ## Distlock tests (public per-component).
	$(MAKE) -C $(Zato_Base)/code/zato-distlock test

web-admin-tests: ## Web-admin tests (public per-component).
	$(MAKE) -C $(Zato_Base)/code/zato-web-admin test

health-hl7-tests: ## HL7v2 tests run inside the health repo.
	$(MAKE) -C $(Zato_Health) hl7-tests

health-fhir-tests: ## FHIR tests run inside the health repo.
	$(MAKE) -C $(Zato_Health) fhir-tests

test-fast: server-sio-tests server-marshall-tests scheduler-shim-tests ## Fastest: pure-Python unit tests.

test-rust-unit: broker-rust-unit-tests scheduler-rust-unit-tests rate-limiting-rust-unit-tests work-arena-rust-unit-tests ## Rust unit tests (cargo test).

test-integration: enmasse-tests scheduler-integration-tests test-pubsub cli-odb-default-tests server-config-store-tests server-mcp-live-tests ## Python integration tests.

test-chaos: broker-chaos-tests broker-backup-tests ## Broker chaos and backup tests.

test-uring: broker-uring-tests broker-uring-bpf-tests ## io_uring writer + BPF backpressure tests.

test-perf: broker-perf-tests ## Broker performance tests.

test-fuzzy: broker-fuzzy server-fuzzy scheduler-fuzzy ## Proptest + cargo-fuzz across all crates.

test-formal: broker-alloy-tests ## Alloy formal model checks.

test-all: test-fast test-rust-unit test-integration test-chaos test-uring test-perf test-fuzzy test-formal ## Everything, fastest first.

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

ZATO_CLIPPY_CONF := $(CURDIR)/tests/rust-lint
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
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_sio/Cargo.toml            -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   -- --check

format-broker: ## Check Rust formatting in the broker crate.
	. $(HOME)/.cargo/env && \
	cargo fmt --manifest-path $(Zato_Broker)/Cargo.toml -- --check

format-work-arena: ## Check Rust formatting in the work arena crate.
	. $(HOME)/.cargo/env && \
	cargo fmt --manifest-path $(Zato_Work_Arena)/Cargo.toml -- --check

format: format-zato format-broker format-work-arena ## Check Rust formatting everywhere.

clippy-zato: ## Clippy all public Rust crates.
	. $(HOME)/.cargo/env && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_sio/Cargo.toml            --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS)

clippy-broker: ## Clippy the broker crate.
	. $(HOME)/.cargo/env && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(Zato_Broker)/Cargo.toml --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS)

clippy-work-arena: ## Clippy the work arena crate.
	. $(HOME)/.cargo/env && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(Zato_Work_Arena)/Cargo.toml \
		--all-targets --all-features -- $(ZATO_CLIPPY_FLAGS)

clippy: clippy-zato clippy-broker clippy-work-arena ## Clippy everything.

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
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_sio/Cargo.toml            -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   -- --tests

dylint-broker: ## Dylint the broker crate.
	. $(HOME)/.cargo/env && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS_COMMON)" cargo dylint --all --manifest-path $(Zato_Broker)/Cargo.toml

dylint-work-arena: ## Dylint the work arena crate.
	. $(HOME)/.cargo/env && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(Zato_Work_Arena)/Cargo.toml

dylint: dylint-zato dylint-broker dylint-work-arena ## Dylint everything.

deny-zato: ## Dependency audit (advisories, licenses, bans) for public crates.
	. $(HOME)/.cargo/env && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    check --config $(CURDIR)/tests/rust-lint/deny.toml && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    check --config $(CURDIR)/tests/rust-lint/deny.toml && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml check --config $(CURDIR)/tests/rust-lint/deny.toml && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_sio/Cargo.toml            check --config $(CURDIR)/tests/rust-lint/deny.toml && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   check --config $(CURDIR)/tests/rust-lint/deny.toml

deny-broker: ## Dependency audit for the broker crate.
	. $(HOME)/.cargo/env && \
	cargo deny --manifest-path $(Zato_Broker)/Cargo.toml check --config $(CURDIR)/tests/rust-lint/deny-broker.toml

deny-work-arena: ## Dependency audit for the work arena crate.
	. $(HOME)/.cargo/env && \
	cargo deny --manifest-path $(Zato_Work_Arena)/Cargo.toml check --config $(CURDIR)/tests/rust-lint/deny-work-arena.toml

deny: deny-zato deny-broker deny-work-arena ## Dependency audit everywhere.

vet-zato: ## Supply-chain audit for public crates.
	. $(HOME)/.cargo/env && \
	cargo vet --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml --store-path $(CURDIR)/tests/rust-lint/supply-chain-zato

vet-broker: ## Supply-chain audit for the broker.
	. $(HOME)/.cargo/env && \
	cargo vet --manifest-path $(Zato_Broker)/Cargo.toml --store-path $(CURDIR)/tests/rust-lint/supply-chain-broker

vet-work-arena: ## Supply-chain audit for the work arena.
	. $(HOME)/.cargo/env && \
	cargo vet --manifest-path $(Zato_Work_Arena)/Cargo.toml --store-path $(CURDIR)/tests/rust-lint/supply-chain-work-arena

vet: vet-zato vet-broker vet-work-arena ## Supply-chain audit everywhere.

geiger-zato: ## Report unsafe usage in public crate dependency trees.
	. $(HOME)/.cargo/env && \
	cargo geiger --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml && \
	cargo geiger --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml && \
	cargo geiger --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml

geiger-broker: ## Report unsafe usage in the broker dependency tree.
	. $(HOME)/.cargo/env && \
	cargo geiger --manifest-path $(Zato_Broker)/Cargo.toml

geiger-work-arena: ## Report unsafe usage in the work arena dependency tree.
	. $(HOME)/.cargo/env && \
	cargo geiger --manifest-path $(Zato_Work_Arena)/Cargo.toml

geiger: geiger-zato geiger-broker geiger-work-arena ## Report unsafe usage everywhere.

rust-lint: format clippy dylint deny vet geiger ## Full Rust static analysis pipeline.

# ----------------------------------------------------------------------------
# Python lint infrastructure
#
# All lint config lives here (private repo). Public repos ship only
# format-time settings in ruff.toml (line-length, quote-style).
#
# Ruff --config points at our python-lint/ruff.toml.
# Pyright --project points at a generated pyrightconfig.json.
# Same pattern as the Rust side with CLIPPY_CONF_DIR.
# ----------------------------------------------------------------------------

ZATO_PYTHON_LINT := $(CURDIR)/tests/python-lint
ZATO_RUFF_CONF   := $(ZATO_PYTHON_LINT)/ruff.toml
ZATO_RUFF        := tests/.venv/bin/ruff
RUFF_FIX         := $(if $(filter fix,$(MAKECMDGOALS)),--fix,)
ZATO_PYRIGHT     := tests/.venv/bin/pyright
ZATO_PIP_LICENSES := tests/.venv/bin/pip-licenses
ZATO_DEPTRY      := tests/.venv/bin/deptry
ZATO_VULTURE     := tests/.venv/bin/vulture
ZATO_CYCLONEDX   := tests/.venv/bin/cyclonedx-py

ZATO_PYRIGHT_TEMPLATE := $(ZATO_PYTHON_LINT)/pyrightconfig.json.in
ZATO_PYRIGHT_JSON     := $(ZATO_PYTHON_LINT)/pyrightconfig.json

ZATO_LICENSES_ALLOW := Apache Software License;BSD License;MIT License;Python Software Foundation License;ISC License (ISCL);Mozilla Public License 2.0 (MPL 2.0)
ZATO_LICENSES_DENY  := GNU General Public License v3 (GPLv3);GNU General Public License v2 (GPLv2)

# Generate pyrightconfig.json from template.
# Pyright requires include/extraPaths to be relative to the config file's directory.
# We compute the relative path from python-lint/ to Zato_Base at Make time.
ZATO_PYRIGHT_REL := $(shell python3 -c "import os; print(os.path.relpath('$(Zato_Base)', '$(ZATO_PYTHON_LINT)'))")

$(ZATO_PYRIGHT_JSON): $(ZATO_PYRIGHT_TEMPLATE)
	sed 's|{{Zato_Base}}|$(ZATO_PYRIGHT_REL)|g' $< > $@

# -- Code quality: Ruff -------------------------------------------------------

ruff-zato: ## Ruff check all public Zato Python packages. Append FIX=1 for --fix.
	$(ZATO_RUFF) check $(RUFF_FIX) --config $(ZATO_RUFF_CONF) \
		$(Zato_Base)/code/zato-common/src \
		$(Zato_Base)/code/zato-server/src \
		$(Zato_Base)/code/zato-cli/src \
		$(Zato_Base)/code/zato-web-admin/src \
		$(Zato_Base)/code/zato-cy/src \
		$(Zato_Base)/code/zato-distlock/src

ruff-tests: ## Ruff check this repo's test sources. Append FIX=1 for --fix.
	$(ZATO_RUFF) check $(RUFF_FIX) --config $(ZATO_RUFF_CONF) $(CURDIR)/tests/src

ruff: ruff-zato ruff-tests ## Ruff check everything. Use "make ruff fix" for --fix.

fix: ruff ## Modifier target - triggers --fix when combined with ruff targets.

broker-ruff: ## Run ruff inside the broker repo.
	$(MAKE) -C $(Zato_Broker) ruff

health-ruff: ## Run ruff inside the health repo.
	$(MAKE) -C $(Zato_Health) ruff

# -- Code quality: Pyright -----------------------------------------------------

pyright-zato: $(ZATO_PYRIGHT_JSON) ## Pyright type-check all public Zato Python packages.
	$(ZATO_PYRIGHT) --project $(ZATO_PYRIGHT_JSON)

pyright: pyright-zato ## Pyright type-check everything.

# -- Supply chain: uv audit ----------------------------------------------------

audit-zato: ## Scan Zato dependencies for known vulnerabilities.
	cd $(Zato_Base)/code && uv audit

audit: audit-zato ## Vulnerability scan everything.

# -- Supply chain: pip-licenses ------------------------------------------------

licenses-zato: ## Verify all Zato dependencies use approved licenses.
	$(ZATO_PIP_LICENSES) \
		--allow-only="$(ZATO_LICENSES_ALLOW)" \
		--fail-on="$(ZATO_LICENSES_DENY)" \
		--with-urls --format=table

licenses: licenses-zato ## License compliance check everything.

# -- Dependency hygiene: deptry -------------------------------------------------

deptry-zato: ## Check dependency declarations match actual imports across all Zato packages.
	cd $(Zato_Base)/code/zato-common    && $(CURDIR)/$(ZATO_DEPTRY) . && \
	cd $(Zato_Base)/code/zato-server    && $(CURDIR)/$(ZATO_DEPTRY) . && \
	cd $(Zato_Base)/code/zato-cli       && $(CURDIR)/$(ZATO_DEPTRY) . && \
	cd $(Zato_Base)/code/zato-web-admin && $(CURDIR)/$(ZATO_DEPTRY) .

deptry: deptry-zato ## Dependency hygiene check everything.

# -- Dead code: Vulture ---------------------------------------------------------

vulture-zato: ## Find dead code across all Zato packages.
	$(ZATO_VULTURE) \
		$(Zato_Base)/code/zato-common/src \
		$(Zato_Base)/code/zato-server/src \
		$(Zato_Base)/code/zato-cli/src \
		$(Zato_Base)/code/zato-web-admin/src \
		$(ZATO_PYTHON_LINT)/vulture-whitelist.py \
		--min-confidence 80

vulture: vulture-zato ## Dead code detection everywhere.

# -- SBOM: CycloneDX -----------------------------------------------------------

sbom-zato: ## Generate SBOM for the Zato virtualenv.
	$(ZATO_CYCLONEDX) environment --of json -o $(ZATO_PYTHON_LINT)/sbom-zato.json $(Zato_Base)/code

sbom: sbom-zato ## Generate all SBOMs.

# -- Umbrella targets ----------------------------------------------------------

python-lint: ruff pyright audit licenses deptry vulture ## Full Python static analysis pipeline.

lint: rust-lint python-lint ## Full static analysis pipeline (Rust + Python).

broker-clippy: ## (Legacy) Run clippy inside the broker repo. Prefer clippy-broker.
	$(MAKE) clippy-broker

health-clippy: ## Run clippy inside the health repo.
	$(MAKE) -C $(Zato_Health) clippy

# ----------------------------------------------------------------------------
# Auth coverage gates
#
# Every target below runs against the authentication and authorization
# surface only:
#
#   Rust:   $(Zato_Broker)/code/zato-broker/src/zato_broker_core/src/auth/**
#   Python: zato.broker, zato.server.service.internal.security.basic_auth,
#           zato.server.service.internal.pubsub.permission,
#           zato.server.base.parallel
#
# `test-auth-coverage` is the umbrella target that aggregates
# everything. CI runs it; a non-zero exit fails the build.
# ----------------------------------------------------------------------------

ZATO_BROKER_CORE := $(Zato_Broker)/code/zato-broker/src/zato_broker_core
AUTH_TESTS_DIR   := $(CURDIR)/tests/src/zato-broker/auth_tests
AUTH_COVERAGE_DIR := $(CURDIR)/tests/.auth-coverage
AUTH_PROFRAW_DIR  := $(AUTH_COVERAGE_DIR)/profraw

auth-tests: ensure-broker-built ## Run the broker_only and server_broker auth pytest suites with coverage on.
	mkdir -p $(AUTH_COVERAGE_DIR) $(AUTH_PROFRAW_DIR)
	COVERAGE_FILE=$(AUTH_COVERAGE_DIR)/.coverage \
	COVERAGE_PROCESS_START=$(AUTH_TESTS_DIR)/.coveragerc \
	LLVM_PROFILE_FILE=$(AUTH_PROFRAW_DIR)/auth-%p-%m.profraw \
	$(CHAOS_PY) -m pytest $(AUTH_TESTS_DIR) -v -s \
		-o cache_dir=tests/.pytest_cache_auth $(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

auth-coverage-rust: ensure-broker-built ## cargo llvm-cov over src/auth/** with fail-under 100 per-function.
	. $(HOME)/.cargo/env && \
	cd $(ZATO_BROKER_CORE) && \
		cargo llvm-cov --lib --no-cfg-coverage \
			--include-files 'src/auth/**' \
			--fail-under-functions 100 \
			--fail-under-lines 100 \
			--fail-under-regions 100 \
			--summary-only

auth-coverage-python: auth-tests ## coverage.py with branch=True and fail_under=100 on auth Python files.
	cd $(AUTH_COVERAGE_DIR) && \
		$(CHAOS_PY) -m coverage combine && \
		$(CHAOS_PY) -m coverage report --rcfile=$(AUTH_TESTS_DIR)/.coveragerc

auth-mutation: ensure-broker-built ## cargo-mutants on src/auth/** with zero MISSED required.
	. $(HOME)/.cargo/env && \
	cd $(ZATO_BROKER_CORE) && \
		cargo mutants --in-place --no-shuffle --error-exit-code 1

auth-miri: ## cargo miri on src/auth/** unit tests; FFI-heavy crates are stubbed.
	. $(HOME)/.cargo/env && \
	cd $(ZATO_BROKER_CORE) && \
		MIRIFLAGS='-Zmiri-disable-isolation' \
		cargo +nightly miri test --lib auth::

test-auth-coverage: auth-coverage-rust auth-coverage-python auth-mutation ## Aggregate Rust + Python coverage + mutation gates. Fails on any miss.
	@echo '--- Auth coverage gate: PASS ---'

# ----------------------------------------------------------------------------
# Auth-only proptest, cargo-fuzz, cargo-mutants
#
# These targets stay in this repo (per the testing-lives-here convention)
# but delegate the actual cargo work to the broker crate at
# $(ZATO_BROKER_CORE). They scope every tool to src/auth/** only, so a
# normal dev loop does not pay for the rest of the broker surface.
#
# Override the per-fuzz-target wall-clock with `timeout=<seconds>`.
# Defaults to whatever the broker repo's own `Zato_Fuzz_Test_Timeout`
# resolves to (60s today).
# ----------------------------------------------------------------------------

AUTH_FUZZ_TARGETS = \
	fuzz_password_parse \
	fuzz_pattern_match \
	fuzz_topic_parse \
	fuzz_user_id_parse \
	fuzz_username_parse

AUTH_FUZZ_TOTAL   = $(or $(timeout),120)
AUTH_FUZZ_COUNT   = $(words $(AUTH_FUZZ_TARGETS))
AUTH_FUZZ_PER     = $(shell echo $$(( $(AUTH_FUZZ_TOTAL) / $(AUTH_FUZZ_COUNT) )))

broker-tests-auth-proptest: ensure-broker-built ## Run only the proptest-based auth unit tests under cargo test.
	. $(HOME)/.cargo/env && \
	cd $(ZATO_BROKER_CORE) && \
		RUST_BACKTRACE=1 cargo test --lib 'rust_unit_tests::auth_' -- --nocapture $(PYTEST_ARGS)

broker-tests-auth-fuzzy: ensure-broker-built ## libFuzzer (cargo +nightly fuzz) on every auth fuzz target. Total budget=$(AUTH_FUZZ_TOTAL)s, override with timeout=<seconds>.
	. $(HOME)/.cargo/env && \
	cd $(ZATO_BROKER_CORE) && \
		for target in $(AUTH_FUZZ_TARGETS); do \
			echo "--- fuzzing $$target for $(AUTH_FUZZ_PER)s ($(AUTH_FUZZ_TOTAL)s / $(AUTH_FUZZ_COUNT) targets) ---"; \
			cargo +nightly fuzz run $$target -- -max_total_time=$(AUTH_FUZZ_PER) || exit $$?; \
		done

broker-tests-auth-mutants: ensure-broker-built ## cargo-mutants on src/auth/** only; non-zero exit on any MISSED.
	. $(HOME)/.cargo/env && \
	cd $(ZATO_BROKER_CORE) && \
		cargo mutants --no-shuffle --error-exit-code 1 \
			-f 'src/auth/*.rs'

broker-tests-auth: broker-tests-auth-proptest broker-tests-auth-fuzzy broker-tests-auth-mutants ## All auth-only Rust gates: proptest + libFuzzer + cargo-mutants.
	@echo '--- broker-tests-auth: PASS ---'

# ----------------------------------------------------------------------------
# REST tests (excludes pubsub)
# ----------------------------------------------------------------------------

test-rest: ## REST unit tests (http_soap dispatch and auth). Excludes pubsub, enmasse, and config_store integration tests.
	$(ZATO_PY) -m pytest \
		tests/src/zato-server/http_soap/ \
		-v -s -o cache_dir=tests/.pytest_cache_rest -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(SKIP_PASSED) $(FROM_LAST) $(PYTEST_ARGS)

COSMIC_RAY := $(Zato_Base)/code/bin/cosmic-ray

test-rest-mutants: ## Mutation testing on channel.py dispatch methods (cosmic-ray).
	rm -f tests/.cr-session.sqlite
	$(COSMIC_RAY) init tests/cosmic-ray/channel.toml tests/.cr-session.sqlite
	$(COSMIC_RAY) baseline tests/cosmic-ray/channel.toml
	$(COSMIC_RAY) exec tests/cosmic-ray/channel.toml tests/.cr-session.sqlite
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
