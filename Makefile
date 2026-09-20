.PHONY: build install clean default \
	server-build scheduler-build io-build common-core-build queue-bridge-build mq-client \
	server-clean scheduler-clean io-clean common-core-clean queue-bridge-clean \
	server-install scheduler-install io-install common-core-install queue-bridge-install \
	health-install health-build health-clean \
	ruff pyright test-lint test-static test-static-python test-static-rust test-static-js \
	qa-reqs-install rust-lint-tools-install unify \
	analytics update cron-update stop-server restart-server restart-server-with-scheduler \
	stop-dashboard restart-dashboard scheduler queue-bridge file-listener openapi-console \
	help install-deps \
	test-server test-server-fuzz test-rest test-rest-fuzz test-scheduler test-rate-limiting test-enmasse test-cli \
	test-pubsub test-pubsub-perf test-queue-delivery test-queue-delivery-rest \
	test-mcp test-bearer test-graphql test-grpc \
	test-as2 test-as4 test-edifact test-x12 test-soap \
	test-llm \
	test-sql test-oracle-db test-mssql-db test-aws test-sdk test-microsoft-cloud test-salesforce \
	test-hl7 hl7-scenario-hie hl7-scenario-registration hl7-scenario-lab hl7-scenarios test-ui \
	test-common test-distlock test-truncate test-message-filters test-safeguards test-request-response \
	test-audit-log test-alerting test-destinations test-analytics test-demo-seed test-logging \
	test-ibm-mq test-kafka test-mongodb test-es test-ftp test-rule-engine test-rule-engine-perf \
	rule-engine-notify rule-engine-retention rule-engine-spike-alerts rule-engine-dashboard \
	test-all test test-all-reset test-clean-test-all test-perf \
	health-ruff health-clippy \
	format format-zato \
	clippy clippy-zato \
	dylint dylint-zato \
	rust-deny rust-deny-zato \
	vet vet-zato \
	geiger geiger-zato \
	rust-lint lint \
	hl7-haproxy hl7-backend-mllp hl7-backend-rest hl7-send-message \
	quickstart dashboard server listener haproxy dev sbom scalar-update themes css

SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c
MAKEFLAGS += --silent --no-print-directory

CARGO_ENV := $(HOME)/.cargo/env
LOAD_CARGO_ENV := if [ -f $(CARGO_ENV) ]; then . $(CARGO_ENV); fi

ZATO_RUST := $(CURDIR)/code/zato-rust

# IBM MQ redistributable client, needed by the queue bridge at runtime
MQ_CLIENT_DIR := $(CURDIR)/lib/mqm
MQ_CLIENT_URL := https://zato.io/mqclient-linux-x64.tar.gz
MQ_CLIENT_LIB := $(MQ_CLIENT_DIR)/lib64/libmqm_r.so

# Scalar bundle for the OpenAPI console - the version is pinned in package.json
SCALAR_PACKAGE_JSON := $(CURDIR)/code/zato-openapi/package.json
SCALAR_BUNDLE := $(CURDIR)/code/zato-openapi/src/zato/openapi/app/static/scalar/scalar.standalone.js

SITE_PACKAGES := $(shell $(CURDIR)/code/bin/python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])" 2>/dev/null)

ZATO_PY := $(CURDIR)/code/bin/python

# The venv linters qa-reqs-install provides, pinned in code/qa-requirements.txt
RUFF := $(CURDIR)/code/bin/ruff
PYRIGHT := $(CURDIR)/code/bin/pyright

TS := ts '%Y-%m-%d %H:%M:%S'

# What a test target's recipe lines end with - the output timestamped on the console and
# appended to /tmp/logs-<target name>.txt, which Zato_Log_Reset on the first line truncates.
# Written as a line suffix rather than a wrapper target so that a target stays one target.
Zato_Log       = 2>&1 | $(TS) | tee -a /tmp/logs-$@.txt
Zato_Log_Reset = rm -f /tmp/logs-$@.txt

Zato_Test_Python := $(ZATO_PY)
include $(CURDIR)/code/tests/check.mk

# ----------------------------------------------------------------------------
# Zato_Health_Root - needed by health, test, and lint targets only.
# Existing build/install/clean/restart targets work without it.
# ----------------------------------------------------------------------------

Zato_Health := $(Zato_Health_Root)
Zato_Libs   := $(CURDIR)/code/zato-libs

FAIL_ON_FIRST   ?=
SKIP_PASSED_F   ?=
FROM_LAST_F     ?=
SLOW_F          ?=
WITH_COVERAGE_F ?=
ONLY_EOD_F      ?=
PERF_TIER       ?=
HEAVY           ?=
JSON            ?=

FAIL_FAST     := $(if $(FAIL_ON_FIRST),-x,)
SKIP_PASSED   := $(if $(SKIP_PASSED_F),--ff,)
FROM_LAST     := $(if $(FROM_LAST_F),--lf,)
FROM_LAST_CS  := $(if $(FROM_LAST_F),--ff,)
SLOW          := $(if $(SLOW_F),--slow,)
WITH_COVERAGE := $(if $(WITH_COVERAGE_F),--with-coverage,)
ONLY_EOD      := $(if $(ONLY_EOD_F),--only-exactly-once-delivery,)
PERF_ARGS     := $(if $(HEAVY),heavy,) $(if $(JSON),json,) $(PERF_TIER)

# ############################################################################
# Build targets
# ############################################################################

default: dev

build: common-core-build server-build scheduler-build io-build queue-bridge-build
# build: ... fhir-rust-build  # FHIR commented out for now

server-build:
	@echo ">>> Building server"
	$(LOAD_CARGO_ENV) && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_server_core/Cargo.toml

scheduler-build:
	@echo ">>> Building scheduler"
	$(LOAD_CARGO_ENV) && \
	cargo build --release --manifest-path $(ZATO_RUST)/zato_scheduler_core/Cargo.toml --bin _zato_scheduler && \
	rm -f $(CURDIR)/code/bin/_zato_scheduler && \
	cp $(ZATO_RUST)/zato_scheduler_core/target/release/_zato_scheduler $(CURDIR)/code/bin/_zato_scheduler

io-build:
	@echo ">>> Building I/O"
	$(LOAD_CARGO_ENV) && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_input_output/Cargo.toml

common-core-build:
	@echo ">>> Building common-core"
	$(LOAD_CARGO_ENV) && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_common_core/Cargo.toml

mq-client:
	@if [ ! -f $(MQ_CLIENT_LIB) ]; then \
		echo ">>> Downloading IBM MQ client from $(MQ_CLIENT_URL) to $(MQ_CLIENT_DIR)"; \
		if ! ( \
			mkdir -p $(MQ_CLIENT_DIR) && \
			retry_all_errors="$$(curl --help all 2>/dev/null | awk '/--retry-all-errors/{print $$1; exit}')" && \
			curl -fL --http1.1 --retry 2 --retry-delay 1 $$retry_all_errors $(MQ_CLIENT_URL) -o $(MQ_CLIENT_DIR)/mqclient.tar.gz && \
			tar -xzf $(MQ_CLIENT_DIR)/mqclient.tar.gz -C $(MQ_CLIENT_DIR) && \
			rm $(MQ_CLIENT_DIR)/mqclient.tar.gz \
		); then \
			rm -f $(MQ_CLIENT_DIR)/mqclient.tar.gz; \
			echo ">>> WARNING: IBM MQ client download failed"; \
		fi; \
	fi

queue-bridge-build: mq-client
	@echo ">>> Building queue-bridge"
	$(LOAD_CARGO_ENV) && \
	MQ_HOME=$(MQ_CLIENT_DIR) \
	cargo build --release --manifest-path $(ZATO_RUST)/zato_queue_bridge/Cargo.toml --bin _zato_queue_bridge && \
	rm -f $(CURDIR)/code/bin/_zato_queue_bridge && \
	cp $(ZATO_RUST)/zato_queue_bridge/target/release/_zato_queue_bridge $(CURDIR)/code/bin/_zato_queue_bridge

fhir-rust-build:
	@echo ">>> Building FHIR Rust extension"
	@if [ -z "$(Zato_Health)" ]; then echo "ERROR: Zato_Health_Root is not set"; exit 1; fi
	$(MAKE) -C $(Zato_Health) fhir-rust-build

fhir-rust-clean:
	@if [ -z "$(Zato_Health)" ]; then echo "ERROR: Zato_Health_Root is not set"; exit 1; fi
	rm -rf $(Zato_Health)/rust/target

health-build: ## Build the healthcare Rust extensions and copy .so files into zato-libs.
	@if [ -z "$(Zato_Health)" ]; then echo "ERROR: Zato_Health_Root is not set"; exit 1; fi
	$(MAKE) -C $(Zato_Health) build



# ############################################################################
# Run targets
# ############################################################################

queue-bridge:
	@if [ -f $(MQ_CLIENT_LIB) ]; then \
		Zato_MQ_Client_Lib=$(MQ_CLIENT_LIB) $(CURDIR)/code/bin/_zato_queue_bridge; \
	else \
		$(CURDIR)/code/bin/_zato_queue_bridge; \
	fi

file-listener:
	$(CURDIR)/code/bin/py $(CURDIR)/code/zato-common/src/zato/common/file_transfer/listener.py

openapi-console:
	$(ZATO_PY) -m zato.openapi.app.run

# ############################################################################
# Quickstart dev targets
# ############################################################################

quickstart:
	Zato_Metrics_Password=$(Zato_Metrics_Password) zato quickstart ~/env/qs-1 --force --password=$(Zato_Password) --verbose

dashboard:
	clear
	cd ~/env/qs-1/ && zato start web-admin/ --fg --verbose

# The database the rule engine dashboard and the server share - the server runs
# the rules and logs decisions there, the dashboard reads and edits everything
Zato_Rule_Engine_Dashboard_DB_URL ?= sqlite:///$(HOME)/env/qs-1/zato-rule-engine-dashboard.db

server:
	clear
	cd ~/env/qs-1/ && Zato_Rule_Engine_Dashboard_DB_URL=$(Zato_Rule_Engine_Dashboard_DB_URL) zato start server1/ --fg --verbose

# The password the admin account is created with on the first start against a new database,
# the same one the rest of the environment uses
Zato_Rule_Engine_Dashboard_Admin_Password ?= $(Zato_Password)

rule-engine-dashboard:
	clear
	Zato_Rule_Engine_Dashboard_DB_URL=$(Zato_Rule_Engine_Dashboard_DB_URL) \
		Zato_Rule_Engine_Dashboard_Admin_Password=$(Zato_Rule_Engine_Dashboard_Admin_Password) \
		$(ZATO_PY) -m zato.rule_engine_dashboard.app.run

scheduler:
	clear
	cd ~/env/qs-1/ && zato start scheduler/ --fg --verbose

Zato_Server_Dir ?= $(HOME)/env/qs-1/server1

# Which file-watching method the listener uses - Kubernetes needs polling
# because ConfigMap updates arrive as symlink swaps that inotify does not report
Zato_File_Listener_Observer ?= inotify

listener:
	py $(CURDIR)/code/zato-common/src/zato/common/file_transfer/listener.py $(Zato_Server_Dir)/pickup/incoming/services/ --observer $(Zato_File_Listener_Observer)

# The name the Docker image's entrypoint invokes
file-pickup-listener: listener

haproxy:
	@mkdir -p $(HAPROXY_DEV_DIR)
	@touch $(HOME)/env/qs-1/blocked-paths.txt
	@if [ -f $(HAPROXY_DEV_DIR)/zato.pem ]; then \
		cp $(HAPROXY_DEV_DIR)/zato.pem $(HAPROXY_DEV_DIR)/user.pem; \
	fi
	@if [ "$(Zato_SSL_Key_Algorithm)" = "rsa" ]; then \
		openssl genrsa -out $(HAPROXY_DEV_DIR)/auto.key $(Zato_SSL_Key_Size); \
	else \
		openssl ecparam -genkey -name secp384r1 -out $(HAPROXY_DEV_DIR)/auto.key; \
	fi
	@openssl req -new -key $(HAPROXY_DEV_DIR)/auto.key -out $(HAPROXY_DEV_DIR)/auto.csr \
		-subj "$(Zato_SSL_Subject)" \
		-addext "$(Zato_SSL_Subject_Alt_Name)"
	@openssl x509 -req -days $(Zato_SSL_Cert_Days) -in $(HAPROXY_DEV_DIR)/auto.csr \
		-signkey $(HAPROXY_DEV_DIR)/auto.key -out $(HAPROXY_DEV_DIR)/auto.crt -copy_extensions copy
	@cat $(HAPROXY_DEV_DIR)/auto.crt $(HAPROXY_DEV_DIR)/auto.key > $(HAPROXY_DEV_DIR)/auto.pem
	@rm -f $(HAPROXY_DEV_DIR)/auto.key $(HAPROXY_DEV_DIR)/auto.csr $(HAPROXY_DEV_DIR)/auto.crt
	@pem_file=auto.pem; \
	if [ -f $(HAPROXY_DEV_DIR)/user.pem ]; then pem_file=user.pem; fi; \
	sed \
		-e 's|/opt/zato/env/qs-1/blocked-paths.txt|$(HOME)/env/qs-1/blocked-paths.txt|g' \
		-e 's|bind 0.0.0.0:$${Zato_Port_MLLP}$$|&\n    bind 0.0.0.0:$${Zato_Port_MLLP_SSL} ssl crt $(HAPROXY_DEV_DIR)/'"$$pem_file"'|' \
		$(HAPROXY_CFG) > $(HAPROXY_DEV_DIR)/haproxy.cfg
	Zato_Port_Server=$(Zato_Port_Server) \
	Zato_Port_Dashboard=$(Zato_Port_Dashboard) \
	Zato_Port_OpenAPI_Console=$(Zato_Port_OpenAPI_Console) \
	Zato_Port_Load_Balancer=$(Zato_Port_Load_Balancer) \
	Zato_Port_MLLP=$(Zato_Port_MLLP) \
	Zato_Port_MLLP_SSL=$(Zato_Port_MLLP_SSL) \
	Zato_HL7_MLLP_Port=$(Zato_HL7_MLLP_Port) \
	Zato_Load_Balancer_Stats_Password=dev \
	Zato_Load_Balancer_Metrics_Password=dev \
	haproxy -d -f $(HAPROXY_DEV_DIR)/haproxy.cfg

dev:
	$$Zato_Dev_Prefix -t dashboard -- bash -c 'make -C $(CURDIR) dashboard; exec bash -i'
	$$Zato_Dev_Prefix -t server -- bash -c 'make -C $(CURDIR) server; exec bash -i'
	$$Zato_Dev_Prefix -t scheduler -- bash -c 'make -C $(CURDIR) scheduler; exec bash -i'
	$$Zato_Dev_Prefix -t listener -- bash -c 'make -C $(CURDIR) listener; exec bash -i'
	$(MAKE) haproxy

# ############################################################################
# Install targets
# ############################################################################

install:
	@if [ -z "$(MAKEOVERRIDES)" ]; then \
		$(CURDIR)/code/install.sh; \
	else \
		$(CURDIR)/code/support-linux/bin/uv pip install --upgrade --python $(CURDIR)/code/bin/python $(MAKEOVERRIDES); \
	fi

install-deps: ## Create local venv and install test dependencies.
	cd $(CURDIR)/code/tests && uv venv .venv --clear
	cd $(CURDIR)/code/tests && uv pip install -r requirements.txt

health-install: ## Install health deps and build.
	@if [ -z "$(Zato_Health)" ]; then echo "ERROR: Zato_Health_Root is not set"; exit 1; fi
	$(MAKE) -C $(Zato_Health) install

server-install: server-build

scheduler-install: scheduler-build

io-install: io-build

common-core-install: common-core-build

queue-bridge-install: queue-bridge-build

# ############################################################################
# Clean targets
# ############################################################################

clean:
	$(CURDIR)/code/clean.sh

server-clean:
	rm -rf $(ZATO_RUST)/zato_server_core/target

scheduler-clean:
	rm -rf $(ZATO_RUST)/zato_scheduler_core/target

io-clean:
	rm -rf $(ZATO_RUST)/zato_input_output/target

common-core-clean:
	rm -rf $(ZATO_RUST)/zato_common_core/target

queue-bridge-clean:
	rm -rf $(ZATO_RUST)/zato_queue_bridge/target


health-clean: ## Clean health build artifacts and zato-libs entries.
	@if [ -z "$(Zato_Health)" ]; then echo "ERROR: Zato_Health_Root is not set"; exit 1; fi
	$(MAKE) -C $(Zato_Health) clean

# ############################################################################
# QA and tooling
# ############################################################################

qa-reqs-install: rust-lint-tools-install
	$(CURDIR)/code/support-linux/bin/uv pip install --python $(ZATO_PY) -r $(CURDIR)/code/qa-requirements.txt
# The runtime pins come last so anything the QA install had to move is put back
	$(CURDIR)/code/support-linux/bin/uv pip install --python $(ZATO_PY) -r $(CURDIR)/code/requirements.txt
	cp -r $(CURDIR)/code/patches/. $(SITE_PACKAGES)/
	$(ZATO_PY) -m playwright install chromium
	sudo snap install k6

rust-lint-tools-install: ## Install the cargo subcommands the Rust lint pipeline needs - dylint, deny, vet and geiger.
	$(LOAD_CARGO_ENV) && cargo install dylint-link cargo-deny cargo-vet
# These two need --locked - their newest dependency versions want a newer rustc than the toolchain ships
	$(LOAD_CARGO_ENV) && cargo install --locked cargo-dylint cargo-geiger

unify:
	mkdir -p $(SITE_PACKAGES)/lib2to3/pgen2
	printf 'def detect_encoding(readline):\n    return ("utf-8", [])\n' > $(SITE_PACKAGES)/lib2to3/pgen2/tokenize.py
	touch $(SITE_PACKAGES)/lib2to3/__init__.py
	touch $(SITE_PACKAGES)/lib2to3/pgen2/__init__.py
	python3 $(CURDIR)/code/util/unify.py

ruff:
	$(RUFF) check $(CURDIR)/code

pyright:
	@echo "Running every configured Python type check from $(CURDIR)/code"
	cd $(CURDIR)/code && $(PYRIGHT) \
		zato-common/src/zato/hl7v2/ \
		zato-common/src/zato/common/hl7/fhir/fields.py \
		zato-common/src/zato/common/pubsub/outgoing.py \
		zato-common/src/zato/common/pubsub/sql/ \
		zato-common/src/zato/common/rule_engine/jobs/ \
		zato-common/src/zato/common/rule_engine/notify/ \
		zato-common/src/zato/common/test/config_pubsub_outgoing.py \
		zato-common/src/zato/common/test/rabbitmq_.py \
		zato-server/src/zato/server/connection/outgoing_delivery/ \
		zato-server/src/zato/server/base/config_manager/outgoing_queues.py \
		zato-server/src/zato/server/generic/api/outconn_hl7_fhir.py \
		zato-server/src/zato/server/service/internal/pubsub/outgoing.py \
		tests/python/

test-lint: ruff pyright format clippy ## Static analysis only - no test is executed. The first stage of test-all.

test-static-python: ruff pyright ## Every Python static check - ruff and pyright.

test-static-rust: rust-lint ## Every Rust static check - format, clippy, dylint, deny, vet and geiger.

test-static-js: ## Every JS static check - a node --check syntax pass over all first-party sources.
	find $(CURDIR)/code/zato-web-admin/src/zato/admin/static/js \
		$(CURDIR)/code/zato-web-admin/src/zato/admin/static/message-viewer-src \
		$(CURDIR)/code/zato-rule-engine-dashboard/src \
		$(CURDIR)/code/tests/js \
		-name '*.js' -type f -not -path '*/node_modules/*' -print0 | xargs -0 -n1 node --check

test-static: test-static-python test-static-rust test-static-js ## Every static check there is - Python, Rust and JS. Nothing is executed.

CYCLONEDX_BOM_VERSION := 7.3.0

sbom: ## Generate a CycloneDX SBOM of the Python environment.
	@echo ">>> Generating CycloneDX SBOM (cyclonedx-bom $(CYCLONEDX_BOM_VERSION))"
	mkdir -p $(CURDIR)/sbom
	$(CURDIR)/code/support-linux/bin/uvx --from cyclonedx-bom==$(CYCLONEDX_BOM_VERSION) cyclonedx-py environment \
		$(CURDIR)/code/bin/python \
		--output-format json \
		--spec-version 1.6 \
		--mc-type application \
		--output-file $(CURDIR)/sbom/zato.cdx.json
# Locally installed packages carry file:// distribution URLs that expose build machine paths
	@$(CURDIR)/code/bin/python -c "\
	import json; \
	path = '$(CURDIR)/sbom/zato.cdx.json'; \
	sbom = json.load(open(path)); \
	strip = lambda item: item | {'externalReferences': [elem for elem in item['externalReferences'] if not elem['url'].startswith('file://')]}; \
	sbom['components'] = [strip(item) if 'externalReferences' in item else item for item in sbom['components']]; \
	json.dump(sbom, open(path, 'w'), indent=2); \
	components = sbom['components']; \
	suffix = 'component' if len(components) == 1 else 'components'; \
	print(f'>>> Wrote {path} ({len(components)} {suffix})'); \
	"

scalar-update: ## Re-download the Scalar bundle pinned in zato-openapi/package.json into the console's static directory.
	version=$$($(ZATO_PY) -c "import json; print(json.load(open('$(SCALAR_PACKAGE_JSON)'))['dependencies']['@scalar/api-reference'])") && \
	echo ">>> Downloading @scalar/api-reference@$$version" && \
	curl -fL https://cdn.jsdelivr.net/npm/@scalar/api-reference@$$version/dist/browser/standalone.min.js -o $(SCALAR_BUNDLE) && \
	echo ">>> Wrote $(SCALAR_BUNDLE)"

themes: ## Regenerate the webapp UI kit's theme css files, themes-index.js and themes.html from the sources in themes-in/.
	$(ZATO_PY) -m zato.common.webapp.ui.themes
# The generated theme files are css like any other, so prettier has the last word on their shape
	$(MAKE) css

# Where the rule engine's css lives - the dashboard's own screens and the webapp UI kit
# they are built on. Files are discovered under these roots rather than listed, so a new
# stylesheet is formatted the moment it is added, and anything under a vendor directory
# is left exactly as it was shipped.
CSS_ROOTS := \
	$(CURDIR)/code/zato-rule-engine-dashboard/src/zato/rule_engine_dashboard/app/static \
	$(CURDIR)/code/zato-common/src/zato/common/webapp/ui/static

PRETTIER_VERSION := 3.6.2
PRETTIER_CONFIG  := $(CURDIR)/code/.prettierrc

css: ## Format every rule engine css file with prettier - the dashboard's screens and the webapp UI kit, vendored files untouched.
	files=$$(find $(CSS_ROOTS) -type d -name vendor -prune -o -type f -name '*.css' -print | sort); \
	if [ -z "$$files" ]; then echo "No css found under $(CSS_ROOTS)"; exit 1; fi; \
	npx --yes prettier@$(PRETTIER_VERSION) --config $(PRETTIER_CONFIG) --write $$files

help:
	grep -hE '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-32s %s\n", $$1, $$2}'

# ############################################################################
# Server management
# ############################################################################

update:
	py $(CURDIR)/code/zato-common/src/zato/common/util/updates_cli.py

cron-update:
	/opt/zato/current/bin/py $(CURDIR)/code/zato-common/src/zato/common/util/updates_cron.py

analytics: ## Aggregate new audit log events into the analytics store.
	$(CURDIR)/code/bin/zato analytics rollup --verbose

rule-engine-notify: ## Rule engine notification dispatcher - a resident loop running advisory suites and delivering to Slack and Teams.
	$(ZATO_PY) -m zato.common.rule_engine.jobs.notify $(Zato_Rule_Engine_Job_Args)

rule-engine-retention: ## Rule engine retention sweep - one pass deleting decisions past the retention window.
	$(ZATO_PY) -m zato.common.rule_engine.jobs.retention $(Zato_Rule_Engine_Job_Args)

rule-engine-spike-alerts: ## Rule engine spike sweep - one pass comparing the current hour's decisions against the typical rate.
	$(ZATO_PY) -m zato.common.rule_engine.jobs.spikes $(Zato_Rule_Engine_Job_Args)

stop-server:
	py $(CURDIR)/code/zato-common/src/zato/common/util/component_cli.py stop-server

restart-server-with-scheduler:
	py $(CURDIR)/code/zato-common/src/zato/common/util/component_cli.py restart-server

restart-server:
	py $(CURDIR)/code/zato-common/src/zato/common/util/component_cli.py restart-server

stop-dashboard:
	py $(CURDIR)/code/zato-common/src/zato/common/util/component_cli.py stop-dashboard

restart-dashboard:
	py $(CURDIR)/code/zato-common/src/zato/common/util/component_cli.py restart-dashboard

# ############################################################################
# Test targets
# ############################################################################

COSMIC_RAY         := $(CURDIR)/code/bin/cosmic-ray
COSMIC_RAY_CONFIG  := $(CURDIR)/code/tests/rust/cosmic-ray/channel.toml
COSMIC_RAY_SESSION := $(CURDIR)/code/tests/.cr-session.sqlite

# cosmic-ray exec writes its results into the session and prints nothing, so it is
# run through a wrapper that reports how far it has got while it works
COSMIC_RAY_EXEC := $(CURDIR)/code/tests/rust/cosmic-ray/exec_with_progress.py

test-server: ## Server unit and integration tests.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-common/test/zato/common/marshall_/ \
		$(CURDIR)/code/tests/python/zato-server/marshall/ \
		$(CURDIR)/code/tests/python/zato-server/config_store/ \
		$(CURDIR)/code/tests/python/zato-server/service/ \
		$(CURDIR)/code/tests/python/zato-server/hot_deploy/ \
		$(CURDIR)/code/tests/python/zato-server/django_plugin/ \
		$(CURDIR)/code/zato-server/test/zato/connection/ \
		$(CURDIR)/code/zato-server/test/zato/pattern/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_server -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)
# The CLI is driven through sh, which forks, so these tests need a process that gevent has not patched
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/commands_/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_server_commands -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-server-fuzz: ## Server property, fuzz and mutation tests.
	$(Zato_Log_Reset)
	$(MAKE) -C $(CURDIR)/code/zato-server fuzz timeout=$(timeout) $(Zato_Log)

test-rest: ## REST channel and outgoing audit log tests.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/http_soap/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rest -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/rest_outgoing_audit/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rest_outgoing_audit -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-rest-fuzz: ## REST mutation tests.
	$(Zato_Log_Reset)
	rm -f $(COSMIC_RAY_SESSION)
	@echo ">>> cosmic-ray init - finding the mutants of $(notdir $(COSMIC_RAY_CONFIG))"
	$(COSMIC_RAY) init $(COSMIC_RAY_CONFIG) $(COSMIC_RAY_SESSION) $(Zato_Log)
	@echo ">>> cosmic-ray baseline - the suite once with nothing mutated"
	$(COSMIC_RAY) baseline $(COSMIC_RAY_CONFIG) $(Zato_Log)
	@echo ">>> cosmic-ray exec - the suite once per mutant, progress every 10s"
	$(ZATO_PY) $(COSMIC_RAY_EXEC) $(COSMIC_RAY) $(COSMIC_RAY_CONFIG) $(COSMIC_RAY_SESSION) $(Zato_Log)
	@$(ZATO_PY) -c "\
	import sqlite3; \
	conn = sqlite3.connect('$(COSMIC_RAY_SESSION)'); \
	cur = conn.cursor(); \
	cur.execute(\"SELECT test_outcome, COUNT(*) FROM work_results GROUP BY test_outcome\"); \
	results = {r[0]: r[1] for r in cur.fetchall()}; \
	killed = results.get('KILLED', 0); \
	survived = results.get('SURVIVED', 0); \
	total = killed + survived; \
	print(f'Killed: {killed}/{total} ({killed/total*100:.1f}%)') if total else print('No results'); \
	print(f'Survived: {survived}/{total}') if survived else None; \
	" $(Zato_Log)

test-scheduler: ## All scheduler tests.
	$(MAKE) scheduler-build
	. $(HOME)/.cargo/env && cd $(ZATO_RUST)/zato_scheduler_core && cargo test $(PYTEST_ARGS)
	$(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-scheduler/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_scheduler -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-rate-limiting: ## All rate limiting tests.
	. $(HOME)/.cargo/env && cd $(ZATO_RUST)/zato_rate_limiting_core && cargo test $(PYTEST_ARGS)
	$(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-rate-limiting/python-unit-tests \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rate_limiting_py -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-pubsub: ## Every pub/sub functional test - core, SQL, AMQP and outgoing delivery.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/pubsub/ \
		$(CURDIR)/code/tests/python/zato-common/rabbitmq_/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_service/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_push/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_cleanup/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_clear_queue/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_clear_queue_combined/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_clear_queue_concurrent/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_clear_queue_push/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_ack_atomicity/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_cli/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_endpoint_delete/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_new_sub/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_sec_delete/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_sec_edit/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_sub_edit/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_sub_delete/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_sub_delete_mismatch/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_subscribe_atomic/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_perm_edit/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_topic_delete/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_topic_delete_atomic/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_topic_rename/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_topic_rename_atomic/ \
		$(CURDIR)/code/tests/python/zato-server/pubsub_unsub_atomic/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/config_store/test_pubsub_topic.py \
		$(CURDIR)/code/tests/python/zato-server/config_store/test_pubsub_subscription.py \
		$(CURDIR)/code/tests/python/zato-server/config_store/test_pubsub_permission.py \
		$(CURDIR)/code/tests/python/zato-server/config_store/test_pubsub_permission_revoke.py \
		$(CURDIR)/code/tests/python/zato-server/service/test_service_publish.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_config_store -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
		$(CURDIR)/code/tests/python/zato-common/pubsub_backend/test_pubsub_backend_sqlite.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_backend \
		-W "ignore:This process:DeprecationWarning" \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
		$(CURDIR)/code/tests/python/zato-common/pubsub/test_outgoing.py \
		$(CURDIR)/code/tests/python/zato-common/pubsub_outgoing/ \
		$(CURDIR)/code/tests/python/zato-server/outgoing_delivery/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_outgoing \
		-W "ignore:This process:DeprecationWarning" \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/pubsub_outgoing/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_outgoing_live \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
		$(CURDIR)/code/tests/python/zato-common/pubsub_backend_amqp/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_backend_amqp \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-rest: ## Queue delivery of outgoing REST connections, live, on every pub/sub backend.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_rest/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_rest \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery: test-queue-delivery-rest ## Queue delivery of every kind of outgoing connection.

test-pubsub-perf: ## Every pub/sub performance test - SQL, AMQP, system-level load and mass recovery.
	$(Zato_Log_Reset)
	basetemp="$${TMPDIR:-/tmp}/zato-pubsub-backend-perf-$$USER"; \
	trap 'rm -rf "$$basetemp"' EXIT INT TERM; \
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
		$(CURDIR)/code/tests/python/zato-common/pubsub_backend_perf/test_pubsub_backend_perf_sqlite.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_backend_perf \
		-o log_cli=false \
		-W "ignore:This process:DeprecationWarning" \
		--basetemp="$$basetemp" \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/pubsub_system_perf/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_system_perf \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
		$(CURDIR)/code/tests/python/zato-common/pubsub_backend_amqp_perf/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_backend_amqp_perf \
		-o log_cli=false \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	basetemp="$${TMPDIR:-/tmp}/zato-pubsub-backend-perf-$$USER"; \
	trap 'rm -rf "$$basetemp"' EXIT INT TERM; \
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
		$(CURDIR)/code/tests/python/zato-common/pubsub_backend_perf/test_pubsub_backend_perf_mass_sqlite.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_backend_perf \
		-o log_cli=false \
		-W "ignore:This process:DeprecationWarning" \
		--basetemp="$$basetemp" \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

# Every enmasse suite lives here - the importers, the exporters and the round trips for
# every connection type. Targets for a given connection type do not carry enmasse tests
# of their own, discovery below already covers them and running them twice proves nothing.
test-enmasse: ## Enmasse tests - every importer, every exporter, the round trips and secret rotation against live services.
	$(ZATO_PY) -m unittest discover -s $(CURDIR)/code/zato-cli/test/zato/enmasse_ -p 'test_*.py' -v
# Secret rotation needs the live services switched on, which the discovery above leaves off
	Zato_Test_Live_SQL=1 Zato_Test_FTP=1 Zato_Test_SFTP=1 Zato_Test_SMB=1 Zato_Test_MongoDB=1 \
		$(ZATO_PY) -m unittest discover -s $(CURDIR)/code/zato-cli/test/zato/enmasse_ -p 'test_secret_rotation_live.py' -v

test-cli: ## CLI tests.
	$(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-cli/test_odb_sqlite_default.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_cli_odb \
		$(FAIL_FAST) $(PYTEST_ARGS)
	$(MAKE) -C $(CURDIR)/code/zato-cli test

test-mcp: ## Every MCP test - the offline suites, the browser lifecycle, a real LLM and the local container.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mcp/ \
		$(CURDIR)/code/tests/python/zato-server/mcp_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mcp -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_gateway_create.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_wizard.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_response_controls.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_audit_log.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_mcp_gateway.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_playwright -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mcp_llm_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mcp_llm -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
# Skips on its own when the local zato-4.1 container is not there
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mcp_local_docker/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mcp_local_docker -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

llm-console: ## Browser console for the local LLM - starts Ollama, the model and Open WebUI.
	$(ZATO_PY) -u $(CURDIR)/code/tests/python/zato-server/mcp_llm_live/console.py

test-bearer: ## Inbound bearer token live tests.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/security/ \
		$(CURDIR)/code/tests/python/zato-server/bearer_inbound_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_bearer -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_crud.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_groups.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_rest_channel.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_mcp_gateway.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_playwright -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-graphql: ## GraphQL live tests.
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/graphql_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_graphql -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-grpc: ## gRPC live tests.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/grpc_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_grpc -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-as2: ## Every AS2 test - offline messaging, live interop and the browser lifecycle.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/as2/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_as2 -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/as2_interop/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_as2_interop -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/as2_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_as2_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-as4: ## AS4 messaging tests - fully offline, no external services needed.
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/as4/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_as4 -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-edifact: ## EDIFACT tests - fully offline, no external services needed.
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/edifact/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_edifact -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-x12: ## X12 tests - fully offline, no external services needed.
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/x12/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_x12 -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-soap: ## SOAP messaging and channel tests - fully offline, no external services needed.
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/soap/ \
		$(CURDIR)/code/tests/python/zato-server/http_soap/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_soap \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-llm: ## Every outgoing LLM test - the offline simulator, browser lifecycle, real Ollama and local container.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/llm/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_llm -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_llm_outconn_end_to_end.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_playwright -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/llm_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_llm_live -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
# Skips on its own when the local zato-4.1 container is not there
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/llm_local_docker/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_llm_local_docker -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-sql: ## Every SQL test - Snowflake and Redshift against local protocol simulators, offline and through a live Zato server.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/sql_cloud/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sql_cloud -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/sql_cloud_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sql_cloud_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-aws: ## AWS connection tests through a live Zato server against a simulated AWS environment.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/aws_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_aws_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-sdk: ## Connector SDK tests through a live Zato server against a suite-owned target server.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/sdk_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sdk_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-oracle-db: ## Outgoing Oracle DB connection tests against a live Oracle container, including a live Zato server, stored procedure calls, concurrent queries from greenlets and the SQL audit log.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/oracle_db_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_oracle_db_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/sql_outgoing_audit/test_sql_audit_oracle.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sql_audit_oracle -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-mssql-db: ## Outgoing MS SQL connection tests against a live MS SQL Developer container, including a live Zato server, queries, stored procedure calls and the SQL audit log.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mssql_db_live/ \
		$(CURDIR)/code/tests/python/zato-server/sql_outgoing_audit/test_sql_audit_mssql.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mssql_db_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-microsoft-cloud: ## Microsoft 365 connection tests through a live Zato server against a simulated Microsoft cloud.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/microsoft_cloud_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_microsoft_cloud_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-salesforce: ## Salesforce connection tests - a live Zato server against a simulated instance, and the Dashboard lifecycle.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/salesforce_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_salesforce_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_cloud_salesforce_lifecycle.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_playwright -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-hl7: ## Every HL7 test - parsing, FHIR, MLLP channels, outgoing connections, other languages and volume.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/mllp/ \
		$(CURDIR)/code/tests/python/zato-common/hl7_audit/ \
		$(CURDIR)/code/tests/python/zato-common/hl7_feed/ \
		$(CURDIR)/code/tests/python/zato-common/channel_state/ \
		$(CURDIR)/code/tests/python/zato-common/alerting/ \
		$(CURDIR)/code/tests/python/zato-common/destination/ \
		$(CURDIR)/code/tests/python/zato-server/destinations/ \
		$(CURDIR)/code/tests/python/zato-common/demo_seed/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7 -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/mllp_channels/ \
		$(CURDIR)/code/tests/python/zato-server/mllp_integration/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_mllp_channels -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mllp_languages/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_mllp_languages -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) \
	Zato_Test_HL7_Outconn_Third_Party=1 \
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mllp_outconn_third_party/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_mllp_outconns -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) \
	Zato_Test_HL7_Languages=1 \
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mllp_languages/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_languages -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) \
	Zato_Test_HL7_Volume=1 \
	Zato_Audit_Log_Flush_Max_Size=200 \
	Zato_Audit_Log_Flush_Max_Wait_Ms=500 \
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mllp_integration/test_volume.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_volume -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/hl7_fhir/ \
		$(CURDIR)/code/tests/python/zato-common/fhir_display/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_fhir -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-ui: ## Every dashboard test - the UI kit, the rule engine screens, the audit log, the whole Playwright suite and the web-admin access checks.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/webapp_ui/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_webapp_ui \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	cd $(CURDIR)/code/tests/js/zato-rule-engine-dashboard && npm install --no-audit --no-fund $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-rule-engine-dashboard/ui/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_dashboard_ui \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) $(CURDIR)/code/tests/python/zato-common/audit_log/run_matrix.py $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_playwright \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log); \
	status=$$?; \
	if [ $$status -eq 3 ]; then \
		echo "pytest exited with code 3 (internal error) - the test run itself broke, this is not an ordinary test failure, look for INTERNALERROR lines above"; \
	fi; \
	exit $$status
	$(MAKE) -C $(CURDIR)/code/zato-web-admin test $(Zato_Log)

test-ibm-mq: ## IBM MQ queue bridge tests against a live queue manager, plain and TLS.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/ibm_mq/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ibm_mq \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-kafka: ## Kafka end-to-end tests against a live broker in Docker, driven through the Dashboard.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_kafka_end_to_end.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_kafka \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-audit-log: ## Audit log tests against live SQLite, MySQL and PostgreSQL, plain and TLS, plus live Redis tests.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/redis_/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_redis \
		$(FAIL_FAST) $(PYTEST_ARGS)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/audit_log/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_log \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-alerting: ## Alerting engine tests - rules, actions, dedup, lifecycle and collectors, fully offline.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/alerting/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_alerting -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-ftp: ## FTP and FTPS tests - the outconn, enmasse and scheduler suites against live FTP servers, plus the audit and delivery suites against stubs.
	Zato_Test_FTP=1 ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/connection/test_outconn_ftp.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ftp -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_ftp_audit.py \
		$(CURDIR)/code/tests/python/zato-server/outgoing_delivery/test_file_delivery_handlers.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ftp_audit -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_scheduler/ \
		-k "FTP and not SFTP" \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ftp_scheduler -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-destinations: ## Channel destination tests - the destination list, payload overrides, delivery order, retries, the dispatchers, the per-hop trail and the Dashboard views, fully offline.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/destination/ \
		$(CURDIR)/code/tests/python/zato-server/destinations/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_destinations -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/destination_views/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_destination_views -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-demo-seed: ## Demo-data seeder tests - the seeded week of traffic, alerts and config history, fully offline.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/demo_seed/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_demo_seed -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-mongodb: ## Every MongoDB test - live plain and TLS servers plus the in-process simulator.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mongodb/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mongodb \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mongodb_simulated/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mongodb_simulated \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-redis-service: ## Redis tests for the self.redis service API against a local redis-server process, started by the tests.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/redis_service/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_redis_service \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-es: ## Elasticsearch connection tests against a live server, plain and TLS.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/es/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_es \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-rule-engine: ## Rule engine tests - grammar, matching, SQL, dashboard views and jobs.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-common/test/zato/common/rule_engine/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rule_engine \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/rule_engine_sql/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rule_engine_sql \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-rule-engine-dashboard/rule_views/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rule_views \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/rule_engine_jobs/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rule_engine_jobs \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-rule-engine-perf: ## Rule engine SQL backend performance tests.
	$(Zato_Log_Reset)
	basetemp="$${TMPDIR:-/tmp}/zato-rule-engine-perf-$$USER"; \
	trap 'rm -rf "$$basetemp"' EXIT INT TERM; \
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/rule_engine_perf/test_rule_engine_perf_sqlite.py \
		$(CURDIR)/code/tests/python/zato-common/rule_engine_perf/test_rule_engine_perf_mysql.py \
		$(CURDIR)/code/tests/python/zato-common/rule_engine_perf/test_rule_engine_perf_mysql_ssl.py \
		$(CURDIR)/code/tests/python/zato-common/rule_engine_perf/test_rule_engine_perf_postgresql.py \
		$(CURDIR)/code/tests/python/zato-common/rule_engine_perf/test_rule_engine_perf_postgresql_ssl.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rule_engine_perf \
		-o log_cli=false \
		--basetemp="$$basetemp" \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-analytics: ## Analytics rollup, view and baseline tests against live SQLite, MySQL and PostgreSQL, plain and TLS.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/analytics/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_analytics \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-logging: ## Logging live tests - log files, env-variable log levels, PII audit log.
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/logging_/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_logging -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

test-common: ## Common library tests.
	$(MAKE) -C $(CURDIR)/code/zato-common test

test-distlock: ## Distlock tests.
	$(MAKE) -C $(CURDIR)/code/zato-distlock test

test-truncate: ## Truncation and graceful trimming tests with 100% branch coverage.
	$(ZATO_PY) -m coverage run --branch --source=zato.common.util.truncate \
		--data-file=$(CURDIR)/code/tests/.coverage_truncate -m pytest \
		$(CURDIR)/code/tests/python/zato-common/truncate/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_truncate -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)
	$(ZATO_PY) -m coverage report --data-file=$(CURDIR)/code/tests/.coverage_truncate --show-missing --fail-under=100

test-message-filters: ## Message filter and projection tests with 100% branch coverage.
	$(ZATO_PY) -m coverage run --branch --source=zato.common.util.message_filters \
		--data-file=$(CURDIR)/code/tests/.coverage_message_filters -m pytest \
		$(CURDIR)/code/tests/python/zato-common/message_filters/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_message_filters -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)
	$(ZATO_PY) -m coverage report --data-file=$(CURDIR)/code/tests/.coverage_message_filters --show-missing --fail-under=100

test-safeguards: ## Response safeguard tests with 100% branch coverage.
	$(ZATO_PY) -m coverage run --branch --source=zato.common.util.safeguards \
		--data-file=$(CURDIR)/code/tests/.coverage_safeguards -m pytest \
		$(CURDIR)/code/tests/python/zato-common/safeguards/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_safeguards -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)
	$(ZATO_PY) -m coverage report --data-file=$(CURDIR)/code/tests/.coverage_safeguards --show-missing --fail-under=100

test-request-response: ## Unified service I/O tests - messages, request.raw, request.input and response.payload.
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/message/ \
		$(CURDIR)/code/tests/python/zato-server/service/test_request_raw.py \
		$(CURDIR)/code/tests/python/zato-server/service/test_request_input.py \
		$(CURDIR)/code/tests/python/zato-server/service/test_response_payload.py \
		$(CURDIR)/code/tests/python/zato-server/service/test_io_payload.py \
		$(CURDIR)/code/tests/python/zato-server/service/test_model_payload.py \
		$(CURDIR)/code/tests/python/zato-server/reqresp_payload/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_request_response -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS)

# Every test target, ordered from the cheapest to the most expensive.

# Static analysis, nothing is executed
Zato_Test_Static := test-lint

# Offline unit suites, no server, no container, no browser
# test-as4
Zato_Test_Offline := \
	test-message-filters test-demo-seed test-truncate test-safeguards \
	test-edifact test-alerting test-x12 test-request-response test-destinations \
	test-soap

# Rust toolchain suites and the database matrices
Zato_Test_Toolchain := \
	test-distlock test-common test-rate-limiting test-cli test-scheduler \
	test-audit-log test-analytics

# Suites needing a live server or an external service
# test-as2
Zato_Test_Live := \
	test-mcp test-logging test-graphql test-grpc test-aws test-pubsub test-queue-delivery test-mongodb test-es \
	test-sql test-oracle-db test-mssql-db test-microsoft-cloud test-salesforce test-bearer \
	test-ibm-mq test-kafka test-sdk test-hl7 test-llm test-rule-engine test-enmasse

# The whole browser and dashboard suite
# Zato_Test_Browser := test-ui

# Mutation and fuzzing, the longest of all
Zato_Test_Heavy := test-rest test-server test-rest-fuzz test-server-fuzz

# Standalone performance suites, left out of test-all
Zato_Test_Perf := test-pubsub-perf test-rule-engine-perf

Zato_Test_All := \
	$(Zato_Test_Static) $(Zato_Test_Offline) $(Zato_Test_Toolchain) \
	$(Zato_Test_Live) $(Zato_Test_Browser) $(Zato_Test_Heavy)

# Which target the run is currently on - written before the target starts, so a target that
# fails or is interrupted leaves its own name behind and the next run picks up from there.
# Removed once the list has been walked to the end.
Zato_Test_Resume_File := $(CURDIR)/code/tests/.test-all-resume

# Set to anything to ignore the resume file and walk the list from the beginning
RESTART ?=

test-all: ## Everything, resuming from the target that last failed. RESTART=1 to start from scratch.
	@if [ -n "$(RESTART)" ]; then rm -f $(Zato_Test_Resume_File); fi
	@resume=''; \
	if [ -f $(Zato_Test_Resume_File) ]; then \
		resume=$$(cat $(Zato_Test_Resume_File)); \
		echo ">>> Resuming from $$resume"; \
	fi; \
	for target in $(Zato_Test_All); do \
		if [ -n "$$resume" ]; then \
			if [ "$$target" != "$$resume" ]; then continue; fi; \
			resume=''; \
		fi; \
		echo "$$target" > $(Zato_Test_Resume_File); \
		$(MAKE) $$target || exit $$?; \
	done; \
	rm -f $(Zato_Test_Resume_File)

test-all-reset: ## Forget where the last test-all stopped.
	rm -f $(Zato_Test_Resume_File)

test-clean-test-all: ## Run test-all from a clean state instead of resuming a previous run.
	$(MAKE) RESTART=1 test-all

test-perf: $(Zato_Test_Perf) ## Every performance suite - not part of test-all.

test: test-all ## Alias for test-all.

# ############################################################################
# Rust lint infrastructure
#
# All lint config lives here (private repo). Public crates ship only
# unsafe_code = "forbid" and overflow-checks = true.
#
# CLIPPY_CONF_DIR points clippy at our clippy.toml.
# ZATO_CLIPPY_FLAGS passes -W/-D/-A lint levels via the -- separator.
# Same pattern as the Linux kernel and TiKV.
# ############################################################################

ZATO_CLIPPY_CONF := $(CURDIR)/code/tests/rust/rust-lint
ZATO_RUST_DIR    := $(CURDIR)/code/zato-rust

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

rust-deny-zato: ## Dependency audit (advisories, licenses, bans) for public crates.
	. $(HOME)/.cargo/env && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    --config $(CURDIR)/code/tests/rust/rust-lint/deny.toml check && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    --config $(CURDIR)/code/tests/rust/rust-lint/deny.toml check && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml --config $(CURDIR)/code/tests/rust/rust-lint/deny.toml check && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_input_output/Cargo.toml             --config $(CURDIR)/code/tests/rust/rust-lint/deny.toml check && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   --config $(CURDIR)/code/tests/rust/rust-lint/deny.toml check

rust-deny: rust-deny-zato ## Dependency audit everywhere.

vet-zato: ## Supply-chain audit for public crates.
	. $(HOME)/.cargo/env && \
	cargo vet --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml --store-path $(CURDIR)/code/tests/rust/rust-lint/supply-chain-zato

vet: vet-zato ## Supply-chain audit everywhere.

# geiger turns any warning into a failing exit, and its scan-coverage warnings are noise -
# "never scanned" fires for files embedded through include_str! (pyo3's guide .md, icu's
# .rs.data blobs) and, nondeterministically, for source files it did scan on the previous
# run, so neither it nor "No metrics found" can gate the pipeline. Both are tolerated below,
# the unsafe usage table stays the deliverable, and a run that fails for any other reason -
# a compile error, a crash - still fails the target. No grep -q anywhere - with pipefail
# a -q grep that quits early kills the pipe upstream and flips the pipeline's status.
geiger-zato: ## Report unsafe usage in public crate dependency trees.
	. $(HOME)/.cargo/env && \
	for crate in zato_common_core zato_server_core zato_scheduler_core; do \
		out=$$(cargo geiger --manifest-path $(ZATO_RUST_DIR)/$$crate/Cargo.toml 2>&1); \
		status=$$?; \
		echo "$$out"; \
		if [ $$status -ne 0 ]; then \
			errline=$$(echo "$$out" | grep -E '^error: Found [0-9]+ warnings$$'); \
			if [ -z "$$errline" ]; then exit $$status; fi; \
			bad=$$(echo "$$out" | grep '^WARNING:' | grep -Ev 'was never scanned:|No metrics found'); \
			if [ -n "$$bad" ]; then printf 'Real geiger findings:\n%s\n' "$$bad"; exit $$status; fi; \
		fi; \
	done

geiger: geiger-zato ## Report unsafe usage everywhere.

rust-lint: format clippy dylint rust-deny vet geiger ## Full Rust static analysis pipeline.

health-ruff: ## Run ruff inside the health repo.
	@if [ -z "$(Zato_Health)" ]; then echo "ERROR: Zato_Health_Root is not set"; exit 1; fi
	$(MAKE) -C $(Zato_Health) ruff

lint: rust-lint ## Full static analysis pipeline.

health-clippy: ## Run clippy inside the health repo.
	@if [ -z "$(Zato_Health)" ]; then echo "ERROR: Zato_Health_Root is not set"; exit 1; fi
	$(MAKE) -C $(Zato_Health) clippy

# ############################################################################
# HL7 dev targets - launch HAProxy and test backends for manual testing
# ############################################################################

HAPROXY_CFG     := $(CURDIR)/code/zato-common/src/zato/common/pubsub/server/haproxy.cfg
HAPROXY_DEV_DIR := /tmp/zato-haproxy-dev

# The configuration file the container ships with reads every port from the environment,
# so a dev run supplies the same values the image's own defaults use
Zato_Port_Server ?= 17010
Zato_Port_Dashboard ?= 8183
Zato_Port_OpenAPI_Console ?= 8185
Zato_Port_Load_Balancer ?= 11223
Zato_Port_MLLP ?= 11553
Zato_Port_MLLP_SSL ?= 11554

# The same variables and defaults the containers read, per /docs/admin/security/ssl
Zato_SSL_Subject ?= /C=US/ST=State/L=City/O=Organization/CN=localhost
Zato_SSL_Subject_Alt_Name ?= subjectAltName=DNS:localhost,IP:127.0.0.1
Zato_SSL_Cert_Days ?= 3650
Zato_SSL_Key_Algorithm ?= ecdsa
Zato_SSL_Key_Size ?= 4096

# Where the server's own MLLP listener sits on loopback, which is what the MLLP backend points at
Zato_HL7_MLLP_Port ?= 31312

MLLP_TESTS            := $(CURDIR)/code/tests/python/zato-common/mllp
HL7_DEV_DIR           := /tmp/zato-hl7-dev
HL7_DEV_FRONTEND_PORT := 21223
HL7_DEV_HTTP_LB_PORT  := 21225
HL7_DEV_REST_PORT     := 27010
HL7_DEV_MLLP_PORT     := 21312
HL7_DEV_DASH_PORT     := 28183
HL7_DEV_CONSOLE_PORT  := 28185
HL7_DEV_STATS_PORT    := 28404

hl7-haproxy: ## Start HAProxy in full debug mode on dev ports.
	@echo ">>> Starting HAProxy in debug mode (frontend=$(HL7_DEV_FRONTEND_PORT), REST=$(HL7_DEV_REST_PORT), MLLP=$(HL7_DEV_MLLP_PORT))"
	@mkdir -p $(HL7_DEV_DIR)
	@touch $(HL7_DEV_DIR)/blocked-paths.txt
	@sed \
		-e 's|/opt/zato/env/qs-1/blocked-paths.txt|$(HL7_DEV_DIR)/blocked-paths.txt|g' \
		-e 's|0.0.0.0:|127.0.0.1:|g' \
		-e 's|127.0.0.1:11225|127.0.0.1:$(HL7_DEV_HTTP_LB_PORT)|g' \
		-e 's|127.0.0.1:8182|127.0.0.1:$(HL7_DEV_DASH_PORT)|g' \
		-e 's|\*:8404|127.0.0.1:$(HL7_DEV_STATS_PORT)|g' \
		$(HAPROXY_CFG) > $(HL7_DEV_DIR)/haproxy.cfg
	Zato_Port_Server=$(HL7_DEV_REST_PORT) \
	Zato_Port_Dashboard=$(HL7_DEV_DASH_PORT) \
	Zato_Port_OpenAPI_Console=$(HL7_DEV_CONSOLE_PORT) \
	Zato_Port_Load_Balancer=$(HL7_DEV_FRONTEND_PORT) \
	Zato_Port_MLLP=$(HL7_DEV_MLLP_PORT) \
	Zato_Load_Balancer_Stats_Password=dev \
	Zato_Load_Balancer_Metrics_Password=dev \
	haproxy -d -f $(HL7_DEV_DIR)/haproxy.cfg

hl7-backend-mllp: ## Start the MLLP echo backend on dev port.
	@echo ">>> Starting MLLP echo backend on port $(HL7_DEV_MLLP_PORT)"
	$(ZATO_PY) $(MLLP_TESTS)/mllp_test_server.py --callback-mode echo --log-messages --port $(HL7_DEV_MLLP_PORT)

hl7-backend-rest: ## Start the HTTP echo backend on dev port.
	@echo ">>> Starting HTTP echo backend on port $(HL7_DEV_REST_PORT)"
	$(ZATO_PY) $(MLLP_TESTS)/rest_echo_server.py --port $(HL7_DEV_REST_PORT) --log

hl7-send-message: ## Send the wellness HL7v2 message to the dev HAProxy frontend via MLLP.
	@echo ">>> Sending wellness HL7v2 message to 127.0.0.1:$(HL7_DEV_FRONTEND_PORT)"
	cd $(MLLP_TESTS) && $(ZATO_PY) mllp_send_message.py --port $(HL7_DEV_FRONTEND_PORT)

# ----------------------------------------------------------------------------
# Live HL7 systems - real clinical systems in containers, started standalone
# on fixed ports. Every target is one call of the live_hl7 command and needs
# Zato_Password exported.
# ----------------------------------------------------------------------------

HL7_LIVE_PYTHONPATH := $(CURDIR)/code/tests/python/zato-common/lib:$(CURDIR)/code/zato-common/src
HL7_LIVE_RUN = Zato_Health_Root=$(Zato_Health) PYTHONPATH=$(HL7_LIVE_PYTHONPATH) $(ZATO_PY) -m live_hl7.cli
HL7_LIVE_SYSTEMS := dcm4che_tools dcm4chee openelis openemr openhim openmrs oscar sftp

# .PHONY expands its prerequisites where it stands, so the generated targets are declared here, after the lists they come from
.PHONY: $(addprefix hl7-,$(filter-out dcm4che_tools,$(HL7_LIVE_SYSTEMS))) \
	$(addprefix hl7-start-,$(HL7_LIVE_SYSTEMS)) $(addprefix hl7-stop-,$(HL7_LIVE_SYSTEMS)) \
	$(addprefix hl7-logs-,$(HL7_LIVE_SYSTEMS)) $(addprefix hl7-describe-,$(HL7_LIVE_SYSTEMS))

hl7-dcm4chee: ## Bring the dcm4chee archive up standalone, stopping what runs of it first.
	$(HL7_LIVE_RUN) start dcm4chee --follow

hl7-openelis: ## Bring OpenELIS up standalone, stopping what runs of it first.
	$(HL7_LIVE_RUN) start openelis --follow

hl7-openemr: ## Bring OpenEMR up standalone, stopping what runs of it first.
	$(HL7_LIVE_RUN) start openemr --follow

hl7-openhim: ## Bring OpenHIM up standalone, stopping what runs of it first.
	$(HL7_LIVE_RUN) start openhim --follow

hl7-openmrs: ## Bring OpenMRS up standalone, stopping what runs of it first.
	$(HL7_LIVE_RUN) start openmrs --follow

hl7-oscar: ## Bring OSCAR up standalone, stopping what runs of it first.
	$(HL7_LIVE_RUN) start oscar --follow

hl7-sftp: ## Bring the SFTP server up standalone, stopping what runs of it first.
	$(HL7_LIVE_RUN) start sftp --follow

$(addprefix hl7-start-,$(HL7_LIVE_SYSTEMS)): hl7-start-%:
	$(HL7_LIVE_RUN) start $*

$(addprefix hl7-stop-,$(HL7_LIVE_SYSTEMS)): hl7-stop-%:
	$(HL7_LIVE_RUN) stop $*

$(addprefix hl7-logs-,$(HL7_LIVE_SYSTEMS)): hl7-logs-%:
	$(HL7_LIVE_RUN) logs $*

$(addprefix hl7-describe-,$(HL7_LIVE_SYSTEMS)): hl7-describe-%:
	$(HL7_LIVE_RUN) describe $*

# ----------------------------------------------------------------------------
# Live HL7 scenario suites - each drives the real systems of one clinical
# scenario in their containers against a throwaway Zato environment.
# ----------------------------------------------------------------------------

hl7-scenario-hie: ## The health information exchange scenario - facility, interoperability layer, shared record and client registry, live.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) \
	Zato_Test_HL7_HIE=1 \
	Zato_Health_Root=$(Zato_Health) \
	PYTHONPATH=$(HL7_LIVE_PYTHONPATH) \
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/hl7_hie/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_hie -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

hl7-scenario-registration: ## The registration scenario - the ADT feed, orders and identity between the integration engine, a PACS and a department, live.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) \
	Zato_Test_HL7_Registration=1 \
	Zato_Health_Root=$(Zato_Health) \
	PYTHONPATH=$(HL7_LIVE_PYTHONPATH) \
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/hl7_registration/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_registration -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

hl7-scenario-lab: ## The laboratory scenario - the LIS orders on an analyzer and takes its results through the middleware, live.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) \
	Zato_Test_HL7_Lab=1 \
	Zato_Health_Root=$(Zato_Health) \
	PYTHONPATH=$(HL7_LIVE_PYTHONPATH) \
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/hl7_lab/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_lab -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

hl7-scenarios: hl7-scenario-hie hl7-scenario-registration hl7-scenario-lab ## Every live clinical scenario, one after another.
