.PHONY: build install clean default \
	server-build scheduler-build io-build common-core-build pg-wire-build queue-bridge-build mq-client \
	server-clean scheduler-clean io-clean common-core-clean pg-wire-clean queue-bridge-clean rust-target-prune \
	server-install scheduler-install io-install common-core-install pg-wire-install queue-bridge-install \
	health-install health-build health-clean \
	ruff pyright pyright-all test-lint test-static test-static-python test-static-rust test-static-js \
	qa-reqs-install rust-lint-tools-install unify \
	analytics update cron-update update-on-prem-gateway stop-server restart-server restart-server-with-scheduler \
	stop-dashboard restart-dashboard scheduler queue-bridge file-listener sftp api-portal api-portal-demo api-portal-tutorial b2b-portal mcp-demo \
	help install-deps install-fhir-converter \
	test-server test-server-fuzz test-rest test-rest-fuzz test-scheduler test-rate-limiting test-enmasse test-cli \
	test-pubsub test-pubsub-perf test-queue-delivery test-queue-delivery-rest test-queue-delivery-soap test-queue-delivery-fhir test-queue-delivery-mllp \
	test-queue-delivery-channel-rest test-queue-delivery-channel-soap \
	test-mcp test-bearer test-graphql test-grpc \
	test-edifact test-soap test-openapi test-api-portal-live \
	test-llm test-outconn-tls-local-docker \
	test-sql test-oracle-db test-mssql-db test-aws test-sdk test-microsoft-cloud test-salesforce test-discord \
	test-hl7 test-ccda test-documents hl7-scenario-hie hl7-scenario-registration hl7-scenario-lab hl7-scenarios test-ui \
	test-common test-distlock test-truncate test-message-filters test-safeguards test-request-response \
	test-audit-log test-audit-export test-alerting test-lets-encrypt test-destinations test-analytics test-demo-seed test-logging \
	test-ibm-mq test-kafka test-kafka-live test-mongodb test-es test-ftp test-sftp test-file-transfer test-rule-engine test-rule-engine-perf \
	test-fabric-live fabric-cleanup fabric-tutorial fabric-loading-tables fabric-lookup-tables fabric-looking-up-data \
	fabric-api-on-fabric-data fabric-scheduled-reports fabric-files fabric-sending-events fabric-receiving-events \
	fabric-reading-events fabric-notebook-results fabric-pipelines-and-reports fabric-local-systems \
	rule-engine-notify rule-engine-retention rule-engine-spike-alerts rule-engine-dashboard \
	test-all test-all-no-static test test-all-reset test-all-no-static-reset test-clean-test-all test-perf \
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

# Cargo retains the artifacts of every earlier feature set, dependency version and toolchain,
# so a target directory above this size in megabytes is removed before the next build.
ZATO_RUST_TARGET_MAX_MB ?= 3072

# IBM MQ redistributable client, needed by the queue bridge at runtime
MQ_CLIENT_DIR := $(CURDIR)/lib/mqm
MQ_CLIENT_URL := https://zato.io/mqclient-linux-x64.tar.gz
MQ_CLIENT_LIB := $(MQ_CLIENT_DIR)/lib64/libmqm_r.so

# Scalar bundle for the API portal - the version is pinned in package.json
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

build: common-core-build pg-wire-build server-build scheduler-build io-build queue-bridge-build
# build: ... fhir-rust-build  # FHIR commented out for now

server-build: rust-target-prune
	@echo ">>> Building server"
	$(LOAD_CARGO_ENV) && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_server_core/Cargo.toml

scheduler-build: rust-target-prune
	@echo ">>> Building scheduler"
	$(LOAD_CARGO_ENV) && \
	cargo build --release --manifest-path $(ZATO_RUST)/zato_scheduler_core/Cargo.toml --bin _zato_scheduler && \
	rm -f $(CURDIR)/code/bin/_zato_scheduler && \
	cp $(ZATO_RUST)/zato_scheduler_core/target/release/_zato_scheduler $(CURDIR)/code/bin/_zato_scheduler

io-build: rust-target-prune
	@echo ">>> Building I/O"
	$(LOAD_CARGO_ENV) && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_input_output/Cargo.toml

common-core-build: rust-target-prune
	@echo ">>> Building common-core"
	$(LOAD_CARGO_ENV) && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_common_core/Cargo.toml

pg-wire-build: rust-target-prune
	@echo ">>> Building pg-wire"
	$(LOAD_CARGO_ENV) && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_pg_wire/Cargo.toml

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

queue-bridge-build: rust-target-prune mq-client
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

sftp: ## Three development OpenSSH SFTP servers in containers on ports 33101-33103 for local file transfer work, each logging under its own label.
	$(CURDIR)/code/bin/py $(CURDIR)/code/zato-common/src/zato/common/sftp_dev/run.py

api-portal:
	$(ZATO_PY) -m zato.openapi.app.run

api-portal-demo: export Zato_API_Portal_Header_Title = Demo portal
api-portal-demo: ## Healthcare demo for the API portal - services, security definitions, groups and REST channels, then the portal itself.
	$(ZATO_PY) -m zato.openapi.portal.demo.install --server-dir $(Zato_Server_Dir) --zato $(CURDIR)/code/bin/zato
	echo "API portal: http://localhost:$(Zato_Port_API_Portal)"
	$(MAKE) api-portal

b2b-portal: ## A static mockup of the B2B portal, with sample data and no server behind it.
	echo "B2B portal: http://localhost:8186/"
	$(ZATO_PY) -m zato.common.b2b.portal.run

api-portal-tutorial: export Zato_API_Portal_Header_Title = Main tutorial
api-portal-tutorial: ## The main tutorial for the API portal - its service, connections, API key, REST channel and scheduler job, then the portal itself.
	$(ZATO_PY) -m zato.openapi.portal.demo.tutorial --server-dir $(Zato_Server_Dir)
	echo "API portal: http://localhost:$(Zato_Port_API_Portal)"
	$(MAKE) api-portal

# The container the MCP healthcare demo runs in and the host ports its Dashboard and its server are published on
Zato_MCP_Demo_Image          ?= ghcr.io/zatosource/zato-4.1:latest
Zato_MCP_Demo_Port_Dashboard ?= 8283
Zato_MCP_Demo_Port_Server    ?= 11323

mcp-demo: ## A Zato container with the MCP healthcare demo - the main tutorial, HL7 MLLP and FHIR, the healthcare analytics services, their SQLite databases and the MCP gateway exposing them.
	echo "Dashboard:   http://localhost:$(Zato_MCP_Demo_Port_Dashboard)/zato/demo-config/"
	echo "MCP gateway: http://localhost:$(Zato_MCP_Demo_Port_Server)/mcp/healthcare (Authorization: Bearer healthcare-demo)"
	docker run --rm --name zato-mcp-demo \
		-p $(Zato_MCP_Demo_Port_Dashboard):8183 \
		-p $(Zato_MCP_Demo_Port_Server):11223 \
		-e Zato_Demo_Config_Sets=tutorial,mcp \
		$(Zato_MCP_Demo_Image)

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
	cd ~/env/qs-1/ && Zato_Rule_Engine_Dashboard_DB_URL=$(Zato_Rule_Engine_Dashboard_DB_URL) \
		Zato_SSL_Dir=$(HAPROXY_DEV_DIR) Zato_Lets_Encrypt_HAProxy_Config=$(HAPROXY_DEV_DIR)/haproxy.cfg \
		zato start server1/ --fg --verbose

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

# Where the certificates, keys and CA certificates that outgoing connections read are kept
Zato_TLS_Material_Dir ?= /opt/hot-deploy/ssl

# Reports changed TLS material to the server, which refreshes the outgoing connections that read it
tls-material-listener:
	py $(CURDIR)/code/zato-common/src/zato/common/file_transfer/listener.py $(Zato_TLS_Material_Dir) --tls-material --observer $(Zato_File_Listener_Observer)

haproxy:
	@mkdir -p $(HAPROXY_DEV_DIR)
	@touch $(HOME)/env/qs-1/blocked-paths.txt
	@if [ -f $(HAPROXY_DEV_DIR)/zato.pem ]; then \
		cp $(HAPROXY_DEV_DIR)/zato.pem $(HAPROXY_DEV_DIR)/user.pem; \
	else \
		rm -f $(HAPROXY_DEV_DIR)/user.pem; \
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
	@if [ ! -f $(HAPROXY_DEV_DIR)/user.pem ]; then \
		cp $(HAPROXY_DEV_DIR)/auto.pem $(HAPROXY_DEV_DIR)/user.pem; \
	fi
	@sed \
		-e 's|/opt/zato/env/qs-1/blocked-paths.txt|$(HOME)/env/qs-1/blocked-paths.txt|g' \
		-e 's|bind 0.0.0.0:$${Zato_Port_MLLP}$$|&\n    bind 0.0.0.0:$${Zato_Port_MLLP_SSL} ssl crt $(HAPROXY_DEV_DIR)/user.pem|' \
		$(HAPROXY_CFG) > $(HAPROXY_DEV_DIR)/haproxy.cfg
	Zato_Port_Server=$(Zato_Port_Server) \
	Zato_Port_Dashboard=$(Zato_Port_Dashboard) \
	Zato_Port_API_Portal=$(Zato_Port_API_Portal) \
	Zato_Port_Load_Balancer=$(Zato_Port_Load_Balancer) \
	Zato_Port_MLLP=$(Zato_Port_MLLP) \
	Zato_Port_MLLP_SSL=$(Zato_Port_MLLP_SSL) \
	Zato_HL7_MLLP_Port=$(Zato_HL7_MLLP_Port) \
	Zato_Load_Balancer_Stats_Password=dev \
	Zato_Load_Balancer_Metrics_Password=dev \
	haproxy -W -d -f $(HAPROXY_DEV_DIR)/haproxy.cfg

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

install-fhir-converter: ## Build the C-CDA to FHIR converter from source and install it next to the Python binary.
	$(CURDIR)/../../zato-docker/build-scripts/08d-install-fhir-converter.sh $(CURDIR)/code/bin/fhir-converter

health-install: ## Install health deps and build.
	@if [ -z "$(Zato_Health)" ]; then echo "ERROR: Zato_Health_Root is not set"; exit 1; fi
	$(MAKE) -C $(Zato_Health) install

server-install: server-build

scheduler-install: scheduler-build

io-install: io-build

common-core-install: common-core-build

pg-wire-install: pg-wire-build

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

pg-wire-clean:
	rm -rf $(ZATO_RUST)/zato_pg_wire/target

queue-bridge-clean:
	rm -rf $(ZATO_RUST)/zato_queue_bridge/target

rust-target-prune: ## Remove every Rust target directory larger than ZATO_RUST_TARGET_MAX_MB.
	for target_dir in $(wildcard $(ZATO_RUST)/*/target $(ZATO_RUST)/*/fuzz/target); do \
		size_mb=$$(du -sm $$target_dir | cut -f1); \
		if [ $$size_mb -gt $(ZATO_RUST_TARGET_MAX_MB) ]; then \
			echo ">>> Removing $$target_dir ($$size_mb MB, limit $(ZATO_RUST_TARGET_MAX_MB) MB)"; \
			rm -rf $$target_dir; \
		fi; \
	done


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
	cd $(CURDIR)/code && PYRIGHT_PYTHON_IGNORE_WARNINGS=1 $(PYRIGHT) \
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

# Every first-party Python tree
Zato_Pyright_All_Paths := \
	zato-cli/src \
	zato-client/src \
	zato-common/src \
	zato-distlock/src \
	zato-openapi/src \
	zato-rule-engine-dashboard/src \
	zato-server/src \
	zato-testing/src \
	zato-web-admin/src \
	util/ \
	tests/python/

pyright-all:
	@echo "Running Python type checks on every first-party tree from $(CURDIR)/code"
	cd $(CURDIR)/code && PYRIGHT_PYTHON_IGNORE_WARNINGS=1 $(PYRIGHT) --project pyright-all.json $(Zato_Pyright_All_Paths)

test-lint: ## Static analysis only - no test is executed. The first stage of test-all.
	$(Zato_Log_Reset)
	$(MAKE) ruff pyright format clippy $(Zato_Log)

test-static-python: ## Every Python static check - ruff, and pyright over every first-party tree.
	$(Zato_Log_Reset)
	$(MAKE) ruff pyright-all $(Zato_Log)

test-static-rust: ## Every Rust static check - format, clippy, dylint, deny, vet and geiger.
	$(Zato_Log_Reset)
	$(MAKE) rust-lint $(Zato_Log)

test-static-js: ## Every JS static check - a node --check syntax pass over all first-party sources.
	$(Zato_Log_Reset)
	find $(CURDIR)/code/zato-web-admin/src/zato/admin/static/js \
		$(CURDIR)/code/zato-web-admin/src/zato/admin/static/message-viewer-src \
		$(CURDIR)/code/zato-rule-engine-dashboard/src \
		$(CURDIR)/code/tests/js \
		-name '*.js' -type f -not -path '*/node_modules/*' -print0 | xargs -0 -n1 node --check $(Zato_Log)

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

scalar-update: ## Re-download the Scalar bundle pinned in zato-openapi/package.json into the portal's static directory.
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

update-on-prem-gateway:
	/opt/zato/current/bin/py $(CURDIR)/code/zato-common/src/zato/common/util/on_prem_gateway.py

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
	$(Zato_Log_Reset)
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
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
# The CLI is driven through sh, which forks, so these tests need a process that gevent has not patched
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/commands_/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_server_commands -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
# The TLS material listener reads inotify events in an OS thread, which a gevent-patched process blocks
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/file_transfer/test_tls_material_listener.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_server_tls_material_listener -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

# fuzz_disabled
test-server-fuzz: ## Server property, fuzz and mutation tests.
#	$(Zato_Log_Reset)
#	$(MAKE) -C $(CURDIR)/code/zato-server fuzz timeout=$(timeout) $(Zato_Log)

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

# fuzz_disabled
test-rest-fuzz: ## REST mutation tests.
#	$(Zato_Log_Reset)
#	rm -f $(COSMIC_RAY_SESSION)
#	@echo ">>> cosmic-ray init - finding the mutants of $(notdir $(COSMIC_RAY_CONFIG))"
#	$(COSMIC_RAY) init $(COSMIC_RAY_CONFIG) $(COSMIC_RAY_SESSION) $(Zato_Log)
#	@echo ">>> cosmic-ray baseline - the suite once with nothing mutated"
#	$(COSMIC_RAY) baseline $(COSMIC_RAY_CONFIG) $(Zato_Log)
#	@echo ">>> cosmic-ray exec - the suite once per mutant, progress every 10s"
#	$(ZATO_PY) $(COSMIC_RAY_EXEC) $(COSMIC_RAY) $(COSMIC_RAY_CONFIG) $(COSMIC_RAY_SESSION) $(Zato_Log)
#	@$(ZATO_PY) -c "\
#	import sqlite3; \
#	conn = sqlite3.connect('$(COSMIC_RAY_SESSION)'); \
#	cur = conn.cursor(); \
#	cur.execute(\"SELECT test_outcome, COUNT(*) FROM work_results GROUP BY test_outcome\"); \
#	results = {r[0]: r[1] for r in cur.fetchall()}; \
#	killed = results.get('KILLED', 0); \
#	survived = results.get('SURVIVED', 0); \
#	total = killed + survived; \
#	print(f'Killed: {killed}/{total} ({killed/total*100:.1f}%)') if total else print('No results'); \
#	print(f'Survived: {survived}/{total}') if survived else None; \
#	" $(Zato_Log)

test-scheduler: ## All scheduler tests.
	$(Zato_Log_Reset)
	$(MAKE) scheduler-build $(Zato_Log)
	. $(HOME)/.cargo/env && cd $(ZATO_RUST)/zato_scheduler_core && cargo test $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-scheduler/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_scheduler -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-rate-limiting: rust-target-prune ## All rate limiting tests.
	$(Zato_Log_Reset)
	. $(HOME)/.cargo/env && cd $(ZATO_RUST)/zato_rate_limiting_core && cargo test $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-rate-limiting/python-unit-tests \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rate_limiting_py -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

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
		$(CURDIR)/code/tests/python/zato-common/pubsub_backend/test_store_sqlite.py \
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

test-queue-delivery-soap: ## Queue delivery of outgoing SOAP connections, live, on every pub/sub backend.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_soap/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_soap \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-fhir: ## Queue delivery of outgoing FHIR connections, live, on every pub/sub backend.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_fhir/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_fhir \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-mllp: ## Queue delivery of outgoing MLLP connections, live, on every pub/sub backend.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_mllp/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_mllp \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-channel-rest: ## The queue of REST channels - enmasse with a SQLite ODB, then live on every pub/sub backend.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_delivery_channel_rest.py \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_channel_rest/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_channel_rest \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-channel-soap: ## The queue of SOAP channels - enmasse with a SQLite ODB, then live on every pub/sub backend.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_delivery_channel_soap.py \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_channel_soap/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_channel_soap \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery: test-queue-delivery-rest test-queue-delivery-soap test-queue-delivery-fhir test-queue-delivery-mllp test-queue-delivery-channel-rest test-queue-delivery-channel-soap ## Queue delivery of every kind of outgoing connection and of REST and SOAP channels.

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

# discord_disabled - these enmasse suites run in test-discord only
Zato_Test_Enmasse_Disabled := \
	test_importer_enmasse_discord.py test_exporter_enmasse_discord.py

# Every enmasse suite lives here - the importers, the exporters and the round trips for
# every connection type. Targets for a given connection type do not carry enmasse tests
# of their own, discovery below already covers them and running them twice proves nothing.
test-enmasse: ## Enmasse tests - every importer, every exporter, the round trips and secret rotation against live services.
	$(Zato_Log_Reset)
	cd $(CURDIR)/code/zato-cli/test/zato/enmasse_ && $(ZATO_PY) -m unittest -v \
		$$(find . -name 'test_*.py' $(foreach name,$(Zato_Test_Enmasse_Disabled),! -name $(name)) | sort) $(Zato_Log)
# Secret rotation needs the live services switched on, which the discovery above leaves off
	Zato_Test_Live_SQL=1 Zato_Test_FTP=1 Zato_Test_SFTP=1 Zato_Test_SMB=1 Zato_Test_MongoDB=1 \
		$(ZATO_PY) -m unittest discover -s $(CURDIR)/code/zato-cli/test/zato/enmasse_ -p 'test_secret_rotation_live.py' -v $(Zato_Log)

test-enmasse-delete-live: ## Enmasse should_delete against a live server - every object created and deleted through the pickup directory.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_delete_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_enmasse_delete_live -o log_cli_level=WARNING \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-cli: ## CLI tests.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-cli/test_odb_sqlite_default.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_cli_odb \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	$(MAKE) -C $(CURDIR)/code/zato-cli test $(Zato_Log)

test-mcp: ## Every MCP test - the offline suites, the browser lifecycle, a real LLM and the local container.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mcp/ \
		$(CURDIR)/code/tests/python/zato-server/mcp_live/ \
		$(CURDIR)/code/tests/python/zato-common/safeguards/test_masking_config.py \
		$(CURDIR)/code/tests/python/zato-common/safeguards/test_masking.py \
		$(CURDIR)/code/tests/python/zato-dashboard/js_/test_mcp_wizard_masking_js.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mcp -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_mcp_masking_hooks.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_mcp_connection_lists.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_alerts_gateway_mcp.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/importers/test_importer_enmasse_mcp_gateway.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/exporters/test_exporter_enmasse_mcp_gateway.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mcp_enmasse -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_gateway_create.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_wizard.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_wizard_masking.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_wizard_hooks.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_wizard_oauth.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_wizard_oauth_live.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_gateway_groups_live.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_gateway_oauth_guard_live.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_gateway_channels_live.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_mcp_gateway_integrity.py \
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

test-bearer: ## Inbound and outgoing bearer token live tests, including private key JWT.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/security/ \
		$(CURDIR)/code/tests/python/zato-server/bearer_inbound_live/ \
		$(CURDIR)/code/tests/python/zato-server/bearer_outgoing_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_bearer -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_crud.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_private_key_jwt.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_groups.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_rest_channel.py \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_bearer_token_mcp_gateway.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_playwright -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-ccda: ## C-CDA to FHIR - the converter, the service facade, enmasse, a live server with C-CDA channels and the Dashboard form.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/hl7/ccda/ \
		$(CURDIR)/code/tests/python/zato-server/ccda/ \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_ccda_channel.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ccda -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/ccda_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ccda_live -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_hl7_rest_channel_ccda.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_playwright -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-documents: ## Documents in attachments, files and IHE XDM packages - the unpacker, the service input and a live server with the demo IMAP server.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/documents/ \
		$(CURDIR)/code/tests/python/zato-server/documents/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_documents -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/documents_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_documents_live -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-mcp-oauth: ## OAuth for MCP gateways - simulated clients signing in through Keycloak.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mcp_oauth_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mcp_oauth -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-audit-export: ## Audit log export to OpenTelemetry - the offline mapping and queue tests, the enmasse round trip of the payload flag, then a live server against a collector.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/audit_log/export/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_export -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_audit_export_payload.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_export_enmasse -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/audit_export_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_export_live -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-openapi: ## Offline OpenAPI tests - the type mapping of models and annotations, the generator, the portal's document, client and relay.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-openapi/generator/ \
		$(CURDIR)/code/tests/python/zato-openapi/portal_client/ \
		$(CURDIR)/code/tests/python/zato-server/api_portal/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_openapi -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-api-portal-live: ## API portal tests against a live server - the document after a start, after a restart and per channel method.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/api_portal_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_api_portal_live -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-graphql: ## GraphQL live tests.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/graphql_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_graphql -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-grpc: ## gRPC live tests.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/grpc_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_grpc -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-edifact: ## EDIFACT tests - fully offline, no external services needed.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/edifact/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_edifact -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-soap: ## SOAP messaging and channel tests - fully offline, no external services needed.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/soap/ \
		$(CURDIR)/code/tests/python/zato-server/http_soap/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_soap \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

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

test-outconn-tls-local-docker: ## Replaced client certificates of outgoing REST and SOAP connections in the local container.
	$(Zato_Log_Reset)
# Skips on its own when the local zato-4.1 container is not there
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/outconn_tls_local_docker/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_outconn_tls_local_docker -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-sql: ## Every SQL test - Redshift against a local protocol simulator, offline and through a live Zato server.
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
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/aws_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_aws_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

# ############################################################################
# Microsoft Fabric
# ############################################################################

FABRIC_LIVE = PYTHONPATH=$(CURDIR)/code/tests/python/zato-common/lib $(ZATO_PY) -m live_fabric

fabric-tutorial: ## Fabric capacity, app registration, workspace Clinic Analytics, lakehouse Operations with the sample tables, enmasse.yaml and fabric.ini.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) tutorial $(Zato_Log)

fabric-loading-tables: ## Fabric shared part and the sample tables of the Operations lakehouse.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) loading-tables $(Zato_Log)

fabric-lookup-tables: ## Fabric shared part and the sample tables of the Operations lakehouse.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) lookup-tables $(Zato_Log)

fabric-looking-up-data: ## Fabric shared part and the sample tables of the Operations lakehouse.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) looking-up-data $(Zato_Log)

fabric-api-on-fabric-data: ## Fabric shared part and the sample tables of the Operations lakehouse.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) api-on-fabric-data $(Zato_Log)

fabric-scheduled-reports: ## Fabric shared part and the sample tables of the Operations lakehouse.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) scheduled-reports $(Zato_Log)

fabric-files: ## Fabric shared part, the sample tables and the Files/incoming and Files/exports folders.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) files $(Zato_Log)

fabric-sending-events: ## Fabric shared part, eventhouse Operations Events and eventstream occupancy-events with its keys.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) sending-events $(Zato_Log)

fabric-receiving-events: ## Fabric shared part, eventhouse Operations Events and eventstream occupancy-events with its keys.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) receiving-events $(Zato_Log)

fabric-reading-events: ## Fabric shared part, eventhouse Operations Events and eventstream occupancy-events with its keys.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) reading-events $(Zato_Log)

fabric-notebook-results: ## Fabric shared part, the sample tables, notebook Reminder candidates and pipeline Reminders.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) notebook-results $(Zato_Log)

fabric-pipelines-and-reports: ## Fabric shared part, the sample tables, pipeline Nightly occupancy, semantic model and report Occupancy.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) pipelines-and-reports $(Zato_Log)

fabric-local-systems: ## Fabric shared part, the sample tables and the Copy pipeline Appointments from clinic.
	$(Zato_Log_Reset)
	$(FABRIC_LIVE) local-systems $(Zato_Log)

fabric-cleanup: ## Deletes the Fabric workspace with everything in it, the app registrations and ~/env/fabric-live/, suspends the capacity.
	$(FABRIC_LIVE) cleanup

Fabric_Chapters = fabric-tutorial fabric-loading-tables fabric-lookup-tables fabric-looking-up-data fabric-api-on-fabric-data \
	fabric-scheduled-reports fabric-files fabric-sending-events fabric-receiving-events fabric-reading-events \
	fabric-notebook-results fabric-pipelines-and-reports fabric-local-systems

test-fabric-live: $(Fabric_Chapters) ## Microsoft Fabric tests through a live Zato server against the real Clinic Analytics workspace, Kafka SASL PLAIN and OAUTHBEARER round trips through its eventstream included.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) \
	Zato_Test_Fabric_Live=1 \
	PYTHONPATH=$(CURDIR)/code/tests/python/zato-common/lib \
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/fabric_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_fabric_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-sdk: ## Connector SDK tests through a live Zato server against a suite-owned target server.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/sdk_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sdk_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-oracle-db: ## Outgoing Oracle DB connection tests against a live Oracle container, including a live Zato server, stored procedure calls, concurrent queries from greenlets and the SQL audit log.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/oracle_db_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_oracle_db_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/sql_outgoing_audit/test_sql_audit_oracle.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sql_audit_oracle -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-mssql-db: ## Outgoing MS SQL connection tests against a live MS SQL Developer container, including a live Zato server, queries, stored procedure calls and the SQL audit log.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mssql_db_live/ \
		$(CURDIR)/code/tests/python/zato-server/sql_outgoing_audit/test_sql_audit_mssql.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mssql_db_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-discord: ## Discord connection tests - the client against a simulated Discord, a live Zato server, the enmasse importer and exporter, and the Dashboard lifecycle.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/connection/chat/discord/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_discord_client -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/discord/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_discord_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-cli/test/zato/enmasse_/importers/test_importer_enmasse_discord.py \
		$(CURDIR)/code/zato-cli/test/zato/enmasse_/exporters/test_exporter_enmasse_discord.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_discord_enmasse -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_chat_discord_lifecycle.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_playwright -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-microsoft-cloud: ## Microsoft 365 connection tests through a live Zato server against a simulated Microsoft cloud.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/microsoft_cloud_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_microsoft_cloud_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

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
		--ignore=$(CURDIR)/code/tests/python/zato-common/mllp/fuzz \
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
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/ibm_mq/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ibm_mq \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-kafka: rust-target-prune ## Kafka unit tests - the Rust bridge and the enmasse round trips, no live servers.
	$(Zato_Log_Reset)
	. $(HOME)/.cargo/env && cd $(ZATO_RUST)/zato_queue_bridge && cargo test $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_kafka.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_kafka \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

# The three suites below each start their own queue bridge, whose HTTP API listens on one fixed port,
# which is why they run one after another and never side by side.
test-kafka-live: ## Kafka tests against live Kafka in Docker - one instance plain and TLS, the three-instance cluster and queue delivery on every pub/sub backend.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) Zato_Test_Kafka=1 $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/kafka/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_kafka_live \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) Zato_Test_Kafka=1 $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/kafka_cluster/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_kafka_cluster \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) Zato_Test_Kafka=1 $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_kafka/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_kafka \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-audit-log: ## Audit log tests against live SQLite, MySQL and PostgreSQL, plain and TLS, plus live Redis tests.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/redis_/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_redis \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/audit_log/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_log \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-alerting: ## Alerting engine tests - rules, actions, dedup, lifecycle and collectors, fully offline.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/alerting/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_alerting -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-lets-encrypt: ## Let's Encrypt tests - lego obtains and renews certificates from a local Pebble, zato.test must point to 127.0.0.1 in /etc/hosts.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/lets_encrypt/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_lets_encrypt -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-ftp: ## FTP and FTPS tests - the outconn, enmasse and scheduler suites against live FTP servers, plus the audit and delivery suites against stubs.
	$(Zato_Log_Reset)
	Zato_Test_FTP=1 ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/connection/test_outconn_ftp.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ftp -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_ftp_audit.py \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_streamed_transfers.py \
		$(CURDIR)/code/tests/python/zato-server/outgoing_delivery/test_file_delivery_handlers.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ftp_audit -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_scheduler/ \
		-k "FTP and not SFTP" \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ftp_scheduler -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-sftp: ## SFTP tests - the outconn and scheduler suites against live OpenSSH servers, plus the audit, listing and schedule suites against stubs.
	$(Zato_Log_Reset)
	Zato_Test_SFTP=1 ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/connection/test_outconn_sftp.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sftp -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_sftp_audit.py \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_sftp_listing.py \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_schedule_audit.py \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_schedule_encodings.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sftp_audit -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_scheduler/ \
		-k "SFTP" \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sftp_scheduler -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-file-transfer: test-sftp ## File transfer demo tests - the SFTP suites first, then the demo config set, the local SFTP, FTP, FTPS and SMB servers, a live server polling all of them, and the Dashboard card.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/demo_config/test_demo_config.py \
		$(CURDIR)/code/tests/python/zato-common/file_transfer_local_servers/ \
		$(CURDIR)/code/tests/python/zato-server/demo_file_transfer/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_demo_file_transfer -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/playwright_/test_demo_config.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_playwright -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-destinations: ## Channel destination tests - the destination list, payload overrides, delivery order, retries, the dispatchers, the per-hop trail and the Dashboard views, fully offline.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/destination/ \
		$(CURDIR)/code/tests/python/zato-server/destinations/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_destinations -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/destination_views/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_destination_views -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-demo-seed: ## Demo-data seeder tests - the seeded week of traffic, alerts and config history, fully offline.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/demo_seed/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_demo_seed -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

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
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/redis_service/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_redis_service \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-es: ## Elasticsearch connection tests against a live server, plain and TLS.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/es/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_es \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

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

test-analytics: ## Analytics rollup, view and baseline tests on SQLite, with the rollup reading audit logs held in SQLite, MySQL and PostgreSQL.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/analytics/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_analytics \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-logging: ## Logging live tests - log files, env-variable log levels, PII audit log.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/logging_/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_logging -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-common: ## Common library tests.
	$(Zato_Log_Reset)
	$(MAKE) -C $(CURDIR)/code/zato-common test $(Zato_Log)

test-distlock: ## Distlock tests.
	$(Zato_Log_Reset)
	$(MAKE) -C $(CURDIR)/code/zato-distlock test $(Zato_Log)

test-truncate: ## Truncation and graceful trimming tests with 100% branch coverage.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m coverage run --branch --source=zato.common.util.truncate \
		--data-file=$(CURDIR)/code/tests/.coverage_truncate -m pytest \
		$(CURDIR)/code/tests/python/zato-common/truncate/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_truncate -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m coverage report --data-file=$(CURDIR)/code/tests/.coverage_truncate --show-missing --fail-under=100 $(Zato_Log)

test-message-filters: ## Message filter and projection tests with 100% branch coverage.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m coverage run --branch --source=zato.common.util.message_filters \
		--data-file=$(CURDIR)/code/tests/.coverage_message_filters -m pytest \
		$(CURDIR)/code/tests/python/zato-common/message_filters/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_message_filters -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m coverage report --data-file=$(CURDIR)/code/tests/.coverage_message_filters --show-missing --fail-under=100 $(Zato_Log)

test-safeguards: ## Response safeguard tests with 100% branch coverage.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m coverage run --branch --source=zato.common.util.safeguards \
		--data-file=$(CURDIR)/code/tests/.coverage_safeguards -m pytest \
		$(CURDIR)/code/tests/python/zato-common/safeguards/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_safeguards -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m coverage report --data-file=$(CURDIR)/code/tests/.coverage_safeguards --show-missing --fail-under=100 $(Zato_Log)

test-request-response: ## Unified service I/O tests - messages, request.raw, request.input and response.payload.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/message/ \
		$(CURDIR)/code/tests/python/zato-server/service/test_request_raw.py \
		$(CURDIR)/code/tests/python/zato-server/service/test_request_input.py \
		$(CURDIR)/code/tests/python/zato-server/service/test_response_payload.py \
		$(CURDIR)/code/tests/python/zato-server/service/test_io_payload.py \
		$(CURDIR)/code/tests/python/zato-server/service/test_model_payload.py \
		$(CURDIR)/code/tests/python/zato-server/reqresp_payload/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_request_response -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

# Every test target, ordered from the cheapest to the most expensive.

# Static analysis, nothing is executed
Zato_Test_Static := test-lint

# Offline unit suites, no server, no container, no browser
Zato_Test_Offline := \
	test-message-filters test-demo-seed test-truncate test-safeguards \
	test-edifact test-alerting test-request-response test-destinations \
	test-soap test-openapi

# Rust toolchain suites and the database matrices
Zato_Test_Toolchain := \
	test-distlock test-common test-rate-limiting test-cli test-scheduler \
	test-audit-log test-analytics

# Suites needing a live server or an external service
# discord_disabled - test-discord
Zato_Test_Live := \
	test-mcp test-logging test-graphql test-grpc test-aws test-pubsub test-queue-delivery test-mongodb test-es \
	test-sql test-oracle-db test-mssql-db test-microsoft-cloud test-salesforce test-bearer \
	test-ibm-mq test-kafka test-sdk test-hl7 test-ccda test-documents test-llm test-rule-engine test-enmasse test-audit-export \
	test-api-portal-live test-file-transfer

# The whole browser and dashboard suite
# Zato_Test_Browser := test-ui

# Mutation and fuzzing, the longest of all
# fuzz_disabled - test-rest-fuzz test-server-fuzz
Zato_Test_Heavy := test-rest test-server

# Standalone performance suites, left out of test-all
Zato_Test_Perf := test-pubsub-perf test-rule-engine-perf

Zato_Test_Fuzz := test-rest-fuzz test-server-fuzz

Zato_Test_All := \
	$(Zato_Test_Static) $(Zato_Test_Offline) $(Zato_Test_Toolchain) \
	$(Zato_Test_Live) $(Zato_Test_Browser) $(Zato_Test_Heavy)

# Real functionality only - no static checks, no fuzzing and no mutation testing
Zato_Test_No_Static := $(filter-out $(Zato_Test_Static) $(Zato_Test_Fuzz),$(Zato_Test_All))

# Which target the run is currently on - written before the target starts, so a target that
# fails or is interrupted leaves its own name behind and the next run picks up from there.
# Removed once the list has been walked to the end. Each walk has its own file.
Zato_Test_Resume_File           := $(CURDIR)/code/tests/.test-all-resume
Zato_Test_No_Static_Resume_File := $(CURDIR)/code/tests/.test-all-no-static-resume

# Set to anything to ignore the resume file and walk the list from the beginning
RESTART ?=

# Walks the targets in $(1) in order, resuming from the one named in the resume file $(2).
# The whole walk is also written to /tmp/logs-<walk target>.txt, each target keeping its own log as well.
define Zato_Test_Walk
	@if [ -n "$(RESTART)" ]; then rm -f $(2); fi
	@$(Zato_Log_Reset)
	@resume=''; \
	if [ -f $(2) ]; then \
		resume=$$(cat $(2)); \
		echo ">>> Resuming from $$resume" | tee -a /tmp/logs-$@.txt; \
	fi; \
	for target in $(1); do \
		if [ -n "$$resume" ]; then \
			if [ "$$target" != "$$resume" ]; then continue; fi; \
			resume=''; \
		fi; \
		echo "$$target" > $(2); \
		$(MAKE) $$target 2>&1 | tee -a /tmp/logs-$@.txt || { \
			status=$$?; \
			echo ">>> $$target failed, its log is /tmp/logs-$$target.txt" | tee -a /tmp/logs-$@.txt; \
			exit $$status; \
		}; \
	done; \
	rm -f $(2)
endef

test-all: ## Everything, resuming from the target that last failed. RESTART=1 to start from scratch.
	$(call Zato_Test_Walk,$(Zato_Test_All),$(Zato_Test_Resume_File))

test-all-no-static: ## Everything except the static checks, fuzzing and mutation testing, resuming from the target that last failed. RESTART=1 to start from scratch.
	$(call Zato_Test_Walk,$(Zato_Test_No_Static),$(Zato_Test_No_Static_Resume_File))

test-all-reset: ## Forget where the last test-all stopped.
	rm -f $(Zato_Test_Resume_File)

test-all-no-static-reset: ## Forget where the last test-all-no-static stopped.
	rm -f $(Zato_Test_No_Static_Resume_File)

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
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_pg_wire/Cargo.toml        -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_input_output/Cargo.toml             -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   -- --check

format: format-zato ## Check Rust formatting everywhere.

clippy-zato: rust-target-prune ## Clippy all public Rust crates.
	. $(HOME)/.cargo/env && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_pg_wire/Cargo.toml        --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
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

dylint-zato: rust-target-prune ## Dylint all public Rust crates.
	. $(HOME)/.cargo/env && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_pg_wire/Cargo.toml        -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_input_output/Cargo.toml             -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   -- --tests

dylint: dylint-zato ## Dylint everything.

rust-deny-zato: ## Dependency audit (advisories, licenses, bans) for public crates.
	. $(HOME)/.cargo/env && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    --config $(CURDIR)/code/tests/rust/rust-lint/deny.toml check && \
	cargo deny --manifest-path $(ZATO_RUST_DIR)/zato_pg_wire/Cargo.toml        --config $(CURDIR)/code/tests/rust/rust-lint/deny.toml check && \
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
# The tolerated noise is also left out of what gets printed, together with geiger's
# "Failed to match (ignoring source)" lines, the files its own parser cannot read and
# the raw cargo artifact messages it echoes.
GEIGER_NOISE := ^Failed to match \(ignoring source\) package:|^Failed to parse file:|^WARNING: Dependency file was never scanned:|^WARNING: .*No metrics found|^error: Found [0-9]+ warnings$$|^\{"\$$message_type":"artifact",

geiger-zato: ## Report unsafe usage in public crate dependency trees.
	. $(HOME)/.cargo/env && \
	for crate in zato_common_core zato_pg_wire zato_server_core zato_scheduler_core; do \
		out=$$(cargo geiger --manifest-path $(ZATO_RUST_DIR)/$$crate/Cargo.toml 2>&1); \
		status=$$?; \
		echo "$$out" | grep -Ev '$(GEIGER_NOISE)'; \
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
Zato_Port_API_Portal ?= 8185
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
HL7_DEV_PORTAL_PORT   := 28185
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
	Zato_Port_API_Portal=$(HL7_DEV_PORTAL_PORT) \
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
