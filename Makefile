.PHONY: build install clean default \
	server-build ipc-build scheduler-build ha-node-build io-build common-core-build pg-wire-build queue-bridge-build mq-client \
	server-clean ipc-clean scheduler-clean io-clean common-core-clean pg-wire-clean queue-bridge-clean rust-target-prune \
	server-install ipc-install scheduler-install ha-node-install io-install common-core-install pg-wire-install queue-bridge-install \
	health-install health-build health-clean \
	ruff pyright pyright-all test-lint test-static test-static-python test-static-rust test-static-js \
	qa-reqs-install rust-lint-tools-install unify \
	analytics update cron-update update-on-prem-gateway stop-server restart-server restart-server-with-scheduler \
	stop-dashboard restart-dashboard scheduler queue-bridge on-prem-gateway on-prem-gateway-hub file-listener sftp api-portal api-portal-demo api-portal-tutorial b2b-portal mcp-demo \
	help install-deps install-fhir-converter \
	test-server test-server-fuzz test-rest test-rest-fuzz test-rest-outgoing test-rest-redirects test-rest-perf test-rest-channel test-rest-channel-perf test-scheduler test-scheduler-failover \
	test-ha test-ha-core test-ha-pubsub-subscription-in-process test-ha-push-delivery test-ha-pubsub-subscription \
	test-ha-postgresql-local test-ha-power-loss test-ha-pubsub-subscription-ui test-ha-postgresql \
	test-ha-postgresql-kubernetes test-ha-postgresql-soak \
	test-soak test-soak-pubsub test-soak-scheduler-failover \
	test-arbiter \
	test-rate-limiting test-enmasse test-cli \
	test-pubsub test-pubsub-perf test-pubsub-perf-latency test-pubsub-exactly-once test-sql-conformance test-sql-conformance-fast test-sql-conformance-static test-pubsub-encoding test-pubsub-encoding-rust test-perf-rules test-queue-delivery test-queue-delivery-rest test-queue-delivery-soap test-queue-delivery-fhir test-queue-delivery-mllp \
	test-queue-delivery-channel-rest test-queue-delivery-channel-soap \
	test-mcp test-bearer test-graphql test-grpc \
	test-edifact test-soap test-openapi test-api-portal-live \
	test-llm test-outconn-tls-local-docker \
	test-sql test-oracle-db test-mssql-db test-aws test-sdk test-microsoft-cloud test-salesforce test-discord \
	test-hl7 test-ccda test-documents hl7-scenario-hie hl7-scenario-registration hl7-scenario-lab hl7-scenarios test-ui \
	test-common test-distlock test-truncate test-message-filters test-safeguards test-request-response \
	test-audit-log test-audit-export test-alerting test-lets-encrypt test-destinations test-analytics test-demo-seed test-logging \
	test-ibm-mq test-kafka test-kafka-live test-mongodb test-es test-ftp test-sftp test-file-transfer test-smb test-smb-ui test-smb-windows-build \
	test-rule-engine test-hot-deployment \
	test-fabric-live fabric-cleanup fabric-tutorial fabric-loading-tables fabric-lookup-tables fabric-looking-up-data \
	fabric-api-on-fabric-data fabric-scheduled-reports fabric-files fabric-sending-events fabric-receiving-events \
	fabric-reading-events fabric-notebook-results fabric-pipelines-and-reports fabric-local-systems \
	test-all test-all-no-static test test-all-reset test-all-no-static-reset test-clear-test-all test-clear test-perf \
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

# The shell of each recipe line, and the resuming of each goal, are set in code/tests/check.mk, included below

MAKEFLAGS += --silent --no-print-directory

CARGO_ENV := $(HOME)/.cargo/env
LOAD_CARGO_ENV := if [ -f $(CARGO_ENV) ]; then . $(CARGO_ENV); fi

ZATO_RUST := $(CURDIR)/code/zato-rust

# The target directory that all the crates share. It must match build.target-dir in .cargo/config.toml.
ZATO_RUST_TARGET := $(ZATO_RUST)/target

# Cargo retains the artifacts of every earlier feature set, dependency version and toolchain,
# so a target directory above this size in megabytes is removed before the next build.
ZATO_RUST_TARGET_MAX_MB ?= 6144

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

# What a test target's recipe lines end with - the output timestamped on the console and
# appended to /tmp/logs-<target name>.txt, which Zato_Log_Reset on the first line truncates.
# Each line is prefixed by the number of errors and warnings seen so far in the run of the target,
# in red and yellow on a terminal. The first Ctrl+C reaches the tests while the output of their teardown is still
# written to the console and the log, and the second Ctrl+C stops the writing at once.
# Written as a line suffix rather than a wrapper target so that a target stays one target.
# Zato_Log_Reset also records the start of the target in /tmp/zato-test-failures.txt, so that the failures
# recorded after it are known to come from that run.
Zato_Log       = 2>&1 | $(ZATO_PY) $(CURDIR)/code/tests/log_counter.py /tmp/logs-$@.txt
Zato_Log_Reset = rm -f /tmp/logs-$@.txt /tmp/logs-$@.txt.counts; echo ">>> ZATO TEST TARGET STARTED $$(date '+%Y-%m-%d %H:%M:%S') $@" >> /tmp/zato-test-failures.txt

Zato_Test_Python := $(ZATO_PY)
include $(CURDIR)/code/tests/check.mk

# ----------------------------------------------------------------------------
# Zato_Health_Root - needed by health, test, and lint targets only.
# Existing build/install/clean/restart targets work without it.
# ----------------------------------------------------------------------------

Zato_Health := $(Zato_Health_Root)
Zato_Libs   := $(CURDIR)/code/zato-libs

SKIP_PASSED_F   ?=
FROM_LAST_F     ?=
SLOW_F          ?=
WITH_COVERAGE_F ?=
ONLY_EOD_F      ?=
PERF_TIER       ?=
HEAVY           ?=
JSON            ?=

FAIL_FAST     := -x
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

build: common-core-build pg-wire-build server-build ipc-build scheduler-build ha-node-build io-build queue-bridge-build
# build: ... fhir-rust-build  # FHIR commented out for now

server-build: rust-target-prune
	@echo ">>> Building server"
	$(LOAD_CARGO_ENV) && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_server_core/Cargo.toml

ipc-build: rust-target-prune
	@echo ">>> Building the shared memory region of the server"
	$(LOAD_CARGO_ENV) && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_ipc_core/Cargo.toml

scheduler-build: rust-target-prune
	@echo ">>> Building scheduler"
	$(LOAD_CARGO_ENV) && \
	cargo build --release --manifest-path $(ZATO_RUST)/zato_scheduler_core/Cargo.toml --bin _zato_scheduler && \
	rm -f $(CURDIR)/code/bin/_zato_scheduler && \
	cp $(ZATO_RUST_TARGET)/release/_zato_scheduler $(CURDIR)/code/bin/_zato_scheduler

ha-node-build: rust-target-prune
	@echo ">>> Building the active-standby node"
	$(LOAD_CARGO_ENV) && \
	cargo build --release --manifest-path $(ZATO_RUST)/zato_ha_core/Cargo.toml --bin _zato_ha_node && \
	rm -f $(CURDIR)/code/bin/_zato_ha_node && \
	cp $(ZATO_RUST_TARGET)/release/_zato_ha_node $(CURDIR)/code/bin/_zato_ha_node

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
	cp $(ZATO_RUST_TARGET)/release/_zato_queue_bridge $(CURDIR)/code/bin/_zato_queue_bridge

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

on-prem-gateway: ## The on-prem gateway built and run from the source tree in Zato_On_Prem_Gateway_Root, enrolled with the hub on this machine.
	token=$$($(ZATO_PY) -m zato.server.on_prem_gateway_local --server-dir $(Zato_Server_Dir)) && \
		$(MAKE) -C $(Zato_On_Prem_Gateway_Root) run Token=$$token

# Without a load balancer, the address in an enrollment token has the port of the hub
on-prem-gateway-hub: ## The on-prem gateway hub built and run from the source tree in Zato_On_Prem_Gateway_Root.
	$(MAKE) -C $(Zato_On_Prem_Gateway_Root) hub

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

mcp-demo: ## A Zato container with the MCP healthcare demo - the main tutorial, HL7 MLLP and FHIR, the healthcare analytics services with their databases and the MCP gateway exposing them.
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

server:
	clear
	cd ~/env/qs-1/ && Zato_SSL_Dir=$(HAPROXY_DEV_DIR) Zato_Lets_Encrypt_HAProxy_Config=$(HAPROXY_DEV_DIR)/haproxy.cfg \
		zato start server1/ --fg --verbose

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
	$$Zato_Dev_Prefix -t on-prem-gateway-hub -- bash -c 'make -C $(CURDIR) on-prem-gateway-hub; exec bash -i'
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

ipc-install: ipc-build

scheduler-install: scheduler-build

ha-node-install: ha-node-build

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
	$(LOAD_CARGO_ENV) && cargo clean --manifest-path $(ZATO_RUST)/zato_server_core/Cargo.toml -p zato_server_core

ipc-clean:
	$(LOAD_CARGO_ENV) && cargo clean --manifest-path $(ZATO_RUST)/zato_ipc_core/Cargo.toml -p zato_ipc_core

scheduler-clean:
	$(LOAD_CARGO_ENV) && cargo clean --manifest-path $(ZATO_RUST)/zato_scheduler_core/Cargo.toml -p zato_scheduler_core

io-clean:
	$(LOAD_CARGO_ENV) && cargo clean --manifest-path $(ZATO_RUST)/zato_input_output/Cargo.toml -p zato_input_output

common-core-clean:
	$(LOAD_CARGO_ENV) && cargo clean --manifest-path $(ZATO_RUST)/zato_common_core/Cargo.toml -p zato_common_core

pg-wire-clean:
	$(LOAD_CARGO_ENV) && cargo clean --manifest-path $(ZATO_RUST)/zato_pg_wire/Cargo.toml -p zato_pg_wire

queue-bridge-clean:
	$(LOAD_CARGO_ENV) && cargo clean --manifest-path $(ZATO_RUST)/zato_queue_bridge/Cargo.toml -p zato_queue_bridge

rust-target-prune: ## Remove the shared Rust target directory when it is larger than ZATO_RUST_TARGET_MAX_MB.
	for target_dir in $(wildcard $(ZATO_RUST_TARGET)); do \
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
		zato-common/src/zato/common/test/config_pubsub_outgoing.py \
		zato-common/src/zato/common/test/rabbitmq_.py \
		zato-server/src/zato/server/connection/outgoing_delivery/ \
		zato-server/src/zato/server/base/config_manager/outgoing_queues.py \
		zato-server/src/zato/server/generic/api/outconn_hl7_fhir.py \
		zato-server/src/zato/server/service/internal/pubsub/outgoing.py \
		tests/python/

# Pyright worker count and Node.js heap limit - the default heap of about 4 GB forces repeated type cache evictions over this many files
Zato_Pyright_Threads := 8
Zato_Pyright_Heap_MB := 16384

# Every first-party Python tree
Zato_Pyright_All_Paths := \
	zato-cli/src \
	zato-client/src \
	zato-common/src \
	zato-distlock/src \
	zato-openapi/src \
	zato-server/src \
	zato-testing/src \
	zato-web-admin/src \
	util/ \
	tests/python/

pyright-all:
	@echo "Running Python type checks on every first-party tree from $(CURDIR)/code"
	cd $(CURDIR)/code && NODE_OPTIONS=--max-old-space-size=$(Zato_Pyright_Heap_MB) PYRIGHT_PYTHON_IGNORE_WARNINGS=1 $(PYRIGHT) --project pyright-all.json --threads $(Zato_Pyright_Threads) $(Zato_Pyright_All_Paths)

test-lint: ## Static analysis only - nothing of the product is executed. The first stage of test-all.
	$(Zato_Log_Reset)
	$(MAKE) ruff pyright format clippy $(Zato_Log)
	$(foreach target,$(Zato_Static_Linked_Targets),$(MAKE) $(target) $(Zato_Log) &&) true

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

# Where the rule engine's css lives - the webapp UI kit and the rule engine screens built on it.
# Files are discovered under this root rather than listed, so a new stylesheet is formatted
# the moment it is added, and anything under a vendor directory is left exactly as it was shipped.
CSS_ROOTS := \
	$(CURDIR)/code/zato-common/src/zato/common/webapp/ui/static

PRETTIER_VERSION := 3.6.2
PRETTIER_CONFIG  := $(CURDIR)/code/.prettierrc

css: ## Format every rule engine css file with prettier - the webapp UI kit and the rule engine screens, vendored files untouched.
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
		$(CURDIR)/code/tests/python/zato-server/django_plugin/ \
		$(CURDIR)/code/zato-server/test/zato/connection/ \
		$(CURDIR)/code/zato-server/test/zato/pattern/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_server -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
# The CLI is driven through sh, which forks, so these tests need a process that gevent has not patched
	ZATO_TEST_BASE_DIR=$(CURDIR) $(Zato_Test_Failure_Reports_Env) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/commands_/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_server_commands -W ignore::DeprecationWarning \
		$(Zato_Test_Failure_Reports) $(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
# The TLS material listener reads inotify events in an OS thread, which a gevent-patched process blocks
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/file_transfer/test_tls_material_listener.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_server_tls_material_listener -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-hot-deployment: ## Hot deployment - the import graph offline, then a live server with its pickup listener and its importers redeployed.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/import_graph/ \
		$(CURDIR)/code/tests/python/zato-server/hot_deploy/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hot_deployment -W ignore::DeprecationWarning \
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

test-rest-outgoing: ## Outgoing REST invocation tests, in-process and through a running server.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
		$(CURDIR)/code/tests/python/zato-server/rest_outgoing_invocation/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rest_outgoing_invocation -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
		$(CURDIR)/code/tests/python/zato-server/rest_outgoing_invocation_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rest_outgoing_invocation_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-rest-redirects: ## Pub/sub push redirects - the network scopes in Rust, the redirect policy, the follow loop against local endpoints and the delivery through a running server.
	$(Zato_Log_Reset)
	$(LOAD_CARGO_ENV) && cargo test --manifest-path $(ZATO_RUST)/zato_server_core/Cargo.toml --lib outgoing::scope $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/pubsub_push_redirect/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_push_redirect -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
		$(CURDIR)/code/tests/python/zato-server/pubsub_push_redirect_wire/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_push_redirect_wire -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/pubsub_push_redirect_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_push_redirect_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-rest-perf: ## Outgoing REST invocations measured as server CPU time per invocation.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/rest_outgoing_perf/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rest_outgoing_perf -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-rest-channel: ## REST and SOAP channel invocation tests through a running server.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/rest_channel_invocation/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rest_channel_invocation -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-rest-channel-perf: ## REST and SOAP channels measured as server CPU time per request.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/rest_channel_perf/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rest_channel_perf -W ignore::DeprecationWarning \
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
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/scheduler_run_state/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_scheduler_run_state -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-scheduler-failover: ## Active-passive scheduler failover tests on PostgreSQL and PostgreSQL with TLS.
	$(Zato_Log_Reset)
	$(MAKE) scheduler-build $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-server/scheduler_failover/ $(Zato_Test_Without_Soak) \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_scheduler_failover -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

# The HA targets in the order test-ha runs them, from the shortest to the longest, with the targets of the linked
# repositories after the suites of this repository and the soak tests last, and the target test-ha is currently on.
Zato_Test_HA = \
	test-ha-pubsub-subscription-in-process test-ha-push-delivery test-ha-pubsub-subscription \
	test-ha-postgresql-local test-ha-core test-ha-power-loss test-ha-pubsub-subscription-ui \
	test-ha-postgresql test-ha-postgresql-kubernetes $(Zato_HA_Linked_Targets) test-ha-postgresql-soak
Zato_Test_HA_Resume_File := $(CURDIR)/code/tests/.test-ha-resume

# The directory of each HA suite.
Zato_Test_HA_Server_Dir                := $(CURDIR)/code/tests/python/zato-server
Zato_Test_HA_Dir_power-loss            := $(CURDIR)/code/tests/python/zato-common/reliability/power_loss
Zato_Test_HA_Dir_postgresql-local      := $(Zato_Test_HA_Server_Dir)/ha_postgresql_local
Zato_Test_HA_Dir_push-delivery         := $(Zato_Test_HA_Server_Dir)/ha_push_delivery
Zato_Test_HA_Dir_pubsub-subscription   := $(Zato_Test_HA_Server_Dir)/ha_pubsub_subscription
Zato_Test_HA_Dir_postgresql            := $(Zato_Test_HA_Server_Dir)/ha_postgresql
Zato_Test_HA_Dir_postgresql-kubernetes := $(Zato_Test_HA_Server_Dir)/ha_postgresql_kubernetes

# The modules of each HA suite in the order they run, from the shortest to the longest. Every module of a suite
# is listed, and a suite with a module that is not listed refuses to run.
Zato_Test_HA_Modules_power-loss := \
	test_harness.py test_audit_archive.py test_postgresql_server.py

Zato_Test_HA_Modules_postgresql-local := \
	test_server_start.py test_warm_start.py test_takeover_wait.py test_server_liveness.py test_ping_under_load.py

Zato_Test_HA_Modules_push-delivery := \
	test_outgoing_audit.py test_publication_commit.py test_batch_commit.py

Zato_Test_HA_Modules_pubsub-subscription := \
	test_restart_rows.py test_reload_write_failure.py test_worker_kill.py \
	test_network_faults.py test_lock_timeout_postgresql.py

Zato_Test_HA_Modules_postgresql := \
	test_shared_split_brain.py test_shared_outage.py test_shared_partition.py test_shared_functional.py \
	test_shared_takeover.py test_shared_database_failover.py test_reliability.py test_shared_long_runs.py

Zato_Test_HA_Modules_postgresql-kubernetes := \
	test_manifest_rollout.py test_manifest_synchronous_standby.py test_shared_kube_pods.py test_shared_kube_local_postgresql.py \
	test_shared_kube_failover.py test_shared_kube_server_faults.py test_shared_kube_postgresql.py test_shared_kube_nodes.py \
	test_shared_kube_rollout.py test_shared_kube_path_delay.py test_shared_kube_database_outage.py

# The in-process suite of governed subscription rows and the Playwright suite of the same.
Zato_Test_HA_Dir_pubsub-subscription-in-process := $(Zato_Test_HA_Server_Dir)/pubsub_subscription_list
Zato_Test_HA_Dir_pubsub-subscription-ui          := $(CURDIR)/code/tests/python/zato-dashboard/playwright_pubsub_subscription
Zato_Test_HA_Dir_pubsub-subscription-flags      := $(Zato_Test_HA_Server_Dir)/pubsub_subscription_flags
Zato_Test_FSFault_Source := $(CURDIR)/code/tests/python/zato-common/pubsub_faults/native/fsfault.c
Zato_Test_FSFault_Dir    := /tmp/zato-test-fsfault
Zato_Test_FSFault_Library := $(Zato_Test_FSFault_Dir)/fsfault.so

# The pytest option that resumes each suite from the test that failed or was interrupted, or starts it over under RESTART.
Zato_Test_HA_Stepwise = $(if $(RESTART),--sw-reset,--sw)

# Runs the pytest arguments $(2) of the HA suite $(1) with the cache directory of the suite.
Zato_Test_HA_Pytest = \
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest $(2) \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ha_$(subst -,_,$(1)) -W ignore::DeprecationWarning \
		$(Zato_Test_HA_Stepwise) $(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

# Runs the modules of the HA suite $(1) in their order without their soak tests, which the soak targets run
# after every other HA target, resuming from the test that failed or was interrupted.
define Zato_Test_HA_Suite
	$(Zato_Log_Reset)
	@for module in $(Zato_Test_HA_Dir_$(1))/test_*.py; do \
		case " $(Zato_Test_HA_Modules_$(1)) " in \
			*" $$(basename $$module) "*) ;; \
			*) echo ">>> $$module is not in Zato_Test_HA_Modules_$(1)" $(Zato_Log); exit 1;; \
		esac; \
	done
	$(MAKE) ha-node-build $(Zato_Log)
	$(MAKE) scheduler-build $(Zato_Log)
	$(call Zato_Test_HA_Pytest,$(1),$(addprefix $(Zato_Test_HA_Dir_$(1))/,$(Zato_Test_HA_Modules_$(1))) $(Zato_Test_Without_Soak))
endef

# Runs the soak tests of the HA suite $(1), resuming from the test that failed or was interrupted.
define Zato_Test_HA_Soak
	$(Zato_Log_Reset)
	$(MAKE) ha-node-build $(Zato_Log)
	$(MAKE) scheduler-build $(Zato_Log)
	$(call Zato_Test_HA_Pytest,$(1)-soak,$(Zato_Test_HA_Dir_$(1))/ $(Zato_Test_Soak_Only))
endef

test-ha: ## Active-standby pair under the lease referee - every HA target from the shortest to the longest, the soak tests last, resuming from the target that last failed or was interrupted. RESTART=1 to start from scratch.
	$(MAKE) test-sql-conformance-fast
	$(call Zato_Test_Walk,$(Zato_Test_HA),$(Zato_Test_HA_Resume_File))

test-ha-core: rust-target-prune ## The Rust tests of the active-standby node - the role, the lease and the probe of the Zato database.
	$(Zato_Log_Reset)
	$(LOAD_CARGO_ENV) && cargo test --manifest-path $(ZATO_RUST)/zato_ha_core/Cargo.toml $(PYTEST_ARGS) $(Zato_Log)

test-ha-postgresql-local: ## The takeover of the Zato database and the start of a server under a node's generation, on a local PostgreSQL 19 with a synchronous standby, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	$(call Zato_Test_HA_Suite,postgresql-local)

test-ha-power-loss: ## Loss of power to a single server on PostgreSQL, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	$(call Zato_Test_HA_Suite,power-loss)

test-ha-push-delivery: ## The commit of the concluded messages of a push delivery batch and of the audit events of the outgoing calls of its subscriber when the server is killed, the subscription is edited or the server is stopped during the batch, and the publications of its subscriber, stored and logged only with the commit of the batch and refused a message ID of a different message, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	$(call Zato_Test_HA_Suite,push-delivery)

Zato_Test_FSFault_Control := $(Zato_Test_FSFault_Dir)/control

# Builds fsfault.so and writes its control file with no fault in it.
define Zato_Test_FSFault_Build
	mkdir -p $(Zato_Test_FSFault_Dir)
	gcc -O2 -Wall -Wextra -shared -fPIC -o $(Zato_Test_FSFault_Library) $(Zato_Test_FSFault_Source) -ldl -lpthread
	printf 'prefix=\n' > $(Zato_Test_FSFault_Control)
endef

# The variables under which a process, and every process it starts, loads fsfault.so and reads its control file.
Zato_Test_FSFault_Env = LD_PRELOAD=$(Zato_Test_FSFault_Library) ZATO_FSFAULT_CONTROL=$(Zato_Test_FSFault_Control)

test-ha-pubsub-subscription-in-process: ## Governed subscription rows of the configuration database on a server assembled in-process, on PostgreSQL, with fsfault.so loaded, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	$(Zato_Log_Reset)
	$(Zato_Test_FSFault_Build)
	$(MAKE) common-core-build $(Zato_Log)
	$(LOAD_CARGO_ENV) && cargo test --manifest-path $(ZATO_RUST)/zato_common_core/Cargo.toml --lib pubsub_subscription_list $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/importers/test_importer_enmasse_pubsub_subscription_flags.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/exporters/test_exporter_enmasse_pubsub_subscription_flags.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ha_pubsub_subscription_enmasse_flags \
		-W ignore::DeprecationWarning $(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	for mode in postgresql; do \
		$(Zato_Test_FSFault_Env) Zato_Test_PubSub_DB_Mode=$$mode ZATO_TEST_BASE_DIR=$(CURDIR) \
		$(ZATO_PY) -m gevent.monkey --module pytest \
			$(Zato_Test_HA_Dir_pubsub-subscription-in-process)/ \
			-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ha_pubsub_subscription_in_process_$$mode \
			-W ignore::DeprecationWarning $(Zato_Test_HA_Stepwise) $(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log) || exit $$?; \
	done

test-ha-pubsub-subscription: ## Governed subscription rows of the configuration database on a live server, on PostgreSQL, with lock, process and network faults, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	$(Zato_Log_Reset)
	$(Zato_Test_FSFault_Build)
	@for module in $(Zato_Test_HA_Dir_pubsub-subscription)/test_*.py; do \
		case " $(Zato_Test_HA_Modules_pubsub-subscription) " in \
			*" $$(basename $$module) "*) ;; \
			*) echo ">>> $$module is not in Zato_Test_HA_Modules_pubsub-subscription" $(Zato_Log); exit 1;; \
		esac; \
	done
	$(MAKE) common-core-build $(Zato_Log)
	$(MAKE) ha-node-build $(Zato_Log)
	$(MAKE) scheduler-build $(Zato_Log)
	for mode in postgresql; do \
		$(Zato_Test_FSFault_Env) Zato_Test_PubSub_DB_Mode=$$mode $(call Zato_Test_HA_Pytest,pubsub-subscription-$(subst -,_,$$mode),$(addprefix $(Zato_Test_HA_Dir_pubsub-subscription)/,$(Zato_Test_HA_Modules_pubsub-subscription)) $(Zato_Test_Without_Soak)) || exit $$?; \
	done

test-ha-pubsub-subscription-ui: ## Governed subscription rows of the configuration database in Dashboard, on PostgreSQL, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	$(Zato_Log_Reset)
	$(Zato_Test_FSFault_Build)
	$(MAKE) common-core-build $(Zato_Log)
	for mode in postgresql; do \
		$(Zato_Test_FSFault_Env) Zato_Test_PubSub_DB_Mode=$$mode ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
			$(Zato_Test_HA_Dir_pubsub-subscription-ui)/ \
			-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ha_pubsub_subscription_ui_$$mode \
			-o log_cli_level=WARNING -W ignore::DeprecationWarning $(Zato_Test_HA_Stepwise) $(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log) || exit $$?; \
	done

test-ha-postgresql: ## Active-standby pair on PostgreSQL without its soak tests, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	$(call Zato_Test_HA_Suite,postgresql)

test-ha-postgresql-kubernetes: ## Active-standby pair on PostgreSQL in Kubernetes, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	$(call Zato_Test_HA_Suite,postgresql-kubernetes)

test-ha-postgresql-soak: ## The soak tests of the active-standby pair on PostgreSQL, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	$(call Zato_Test_HA_Soak,postgresql)

# The unit tests of the arbiter, the config process, the control channel and the region that the worker
# and the config process of the server share.
Zato_Test_Arbiter_Unit := \
	zato-common/log_rotation zato-common/process_queue \
	zato-server/arbiter zato-server/config_process zato-server/control zato-server/outgoing_region

test-arbiter: ## The arbiter, the config process, the control channel and the region of the worker and the config process.
	$(Zato_Log_Reset)
	$(MAKE) ipc-build $(Zato_Log)
	$(LOAD_CARGO_ENV) && cargo test --manifest-path $(ZATO_RUST)/zato_ipc_core/Cargo.toml $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest $(addprefix $(CURDIR)/code/tests/python/,$(addsuffix /,$(Zato_Test_Arbiter_Unit))) \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_arbiter_unit -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-rate-limiting: rust-target-prune ## All rate limiting tests.
	$(Zato_Log_Reset)
	. $(HOME)/.cargo/env && cd $(ZATO_RUST)/zato_rate_limiting_core && cargo test $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-rate-limiting/python-unit-tests \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rate_limiting_py -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

# The managed PostgreSQL profiles and the databases of the stability suites that test-pubsub runs.
Zato_Test_PubSub_Managed_Modes   := postgresql-rds postgresql-azure
Zato_Test_PubSub_Stability_Modes := postgresql

# The marker expressions that run a suite without its soak tests and then its soak tests alone, after every other suite
# of the target.
Zato_Test_Without_Soak_Marker := not perftest and not soak
Zato_Test_Soak_Only_Marker    := not perftest and soak
Zato_Test_Without_Soak        := -m '$(Zato_Test_Without_Soak_Marker)'
Zato_Test_Soak_Only           := -m '$(Zato_Test_Soak_Only_Marker)'

# The resolver library that the managed profiles require, in a directory of its own, which the server containers mount.
Zato_Test_Resolver_Source  := $(CURDIR)/code/zato-common/src/zato/common/test/native/resolver.c
Zato_Test_Resolver_Dir     := /tmp/zato-test-resolver
Zato_Test_Resolver_Library := $(Zato_Test_Resolver_Dir)/resolver.so

# The runners of the suites of test-pubsub - a plain pytest process and a pytest process patched by gevent before pytest
# loads its plugins, some of which import ssl.
Zato_Test_PubSub_Plain          := -m pytest -W ignore::DeprecationWarning
Zato_Test_PubSub_Gevent         := -m gevent.monkey --module pytest -W ignore::DeprecationWarning
Zato_Test_PubSub_Gevent_Process := -m gevent.monkey --module pytest -W "ignore:This process:DeprecationWarning"

Zato_Test_Step_Runner_pubsub-core := $(Zato_Test_PubSub_Plain)
Zato_Test_Step_Tests_pubsub-core  := \
	$(CURDIR)/code/tests/python/zato-common/pubsub/ \
	$(CURDIR)/code/tests/python/zato-server/pubsub_service/ \
	$(CURDIR)/code/tests/python/zato-server/pubsub_service_subscriber/ \
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
	$(CURDIR)/code/tests/python/zato-server/pubsub_publish_retry/ \
	$(CURDIR)/code/tests/python/zato-common/pubsub_payload_cache/

Zato_Test_Step_Runner_pubsub-encoding := $(Zato_Test_PubSub_Plain)
Zato_Test_Step_Tests_pubsub-encoding  := \
	$(CURDIR)/code/tests/python/zato-common/pubsub_encoding/ \
	$(CURDIR)/code/tests/python/zato-server/pubsub_push_encoding/

Zato_Test_Step_Runner_pubsub-failover := $(Zato_Test_PubSub_Plain)
Zato_Test_Step_Tests_pubsub-failover  := $(CURDIR)/code/tests/python/zato-server/pubsub_failover/

Zato_Test_Step_Runner_pubsub-replication := $(Zato_Test_PubSub_Gevent)
Zato_Test_Step_Tests_pubsub-replication  := $(CURDIR)/code/tests/python/zato-common/pubsub_replication/

# The faults apply to a PostgreSQL container.
Zato_Test_Step_Env_pubsub-faults    := Zato_Test_PubSub_DB_Mode=postgresql
Zato_Test_Step_Runner_pubsub-faults := $(Zato_Test_PubSub_Gevent)
Zato_Test_Step_Tests_pubsub-faults  := $(CURDIR)/code/tests/python/zato-common/pubsub_faults/ $(Zato_Test_Without_Soak)

# The managed suites run on the managed profile $(1), with the resolver library preloaded.
define Zato_Test_PubSub_Managed_Step
Zato_Test_Step_Env_pubsub-managed-$(1)    := LD_PRELOAD=$(Zato_Test_Resolver_Library) Zato_Test_PubSub_DB_Mode=$(1)
Zato_Test_Step_Runner_pubsub-managed-$(1) := $(Zato_Test_PubSub_Gevent)
Zato_Test_Step_Tests_pubsub-managed-$(1)  := $(CURDIR)/code/tests/python/zato-common/pubsub_managed/
endef

# The stability suites and the suites of the subscription flags run on the pub/sub database $(1).
define Zato_Test_PubSub_Stability_Step
Zato_Test_Step_Env_pubsub-stability-$(1)              := Zato_Test_PubSub_DB_Mode=$(1)
Zato_Test_Step_Runner_pubsub-stability-$(1)           := $(Zato_Test_PubSub_Gevent)
Zato_Test_Step_Tests_pubsub-stability-$(1)            := $(CURDIR)/code/tests/python/zato-server/pubsub_stability/ $(Zato_Test_Without_Soak)
Zato_Test_Step_Env_pubsub-subscription-flags-$(1)     := Zato_Test_PubSub_DB_Mode=$(1)
Zato_Test_Step_Runner_pubsub-subscription-flags-$(1)  := $(Zato_Test_PubSub_Gevent)
Zato_Test_Step_Tests_pubsub-subscription-flags-$(1)   := $(Zato_Test_HA_Dir_pubsub-subscription-flags)/ $(Zato_Test_Without_Soak)
endef

$(foreach mode,$(Zato_Test_PubSub_Managed_Modes),$(eval $(call Zato_Test_PubSub_Managed_Step,$(mode))))
$(foreach mode,$(Zato_Test_PubSub_Stability_Modes),$(eval $(call Zato_Test_PubSub_Stability_Step,$(mode))))

Zato_Test_Step_Runner_pubsub-config-store := $(Zato_Test_PubSub_Plain)
Zato_Test_Step_Tests_pubsub-config-store  := \
	$(CURDIR)/code/tests/python/zato-server/config_store/test_pubsub_topic.py \
	$(CURDIR)/code/tests/python/zato-server/config_store/test_pubsub_subscription.py \
	$(CURDIR)/code/tests/python/zato-server/config_store/test_pubsub_permission.py \
	$(CURDIR)/code/tests/python/zato-server/config_store/test_pubsub_permission_revoke.py \
	$(CURDIR)/code/tests/python/zato-server/service/test_service_publish.py

Zato_Test_Step_Runner_pubsub-backend := $(Zato_Test_PubSub_Gevent_Process)
Zato_Test_Step_Tests_pubsub-backend  := \
	$(CURDIR)/code/tests/python/zato-common/pubsub_backend/test_pubsub_backend_postgresql.py \
	$(CURDIR)/code/tests/python/zato-common/pubsub_backend/test_store_postgresql.py \
	$(CURDIR)/code/tests/python/zato-common/pubsub_backend/test_generation_postgresql.py \
	$(CURDIR)/code/tests/python/zato-common/pubsub_backend/test_clock.py

Zato_Test_Step_Runner_pubsub-outgoing := $(Zato_Test_PubSub_Gevent_Process)
Zato_Test_Step_Tests_pubsub-outgoing  := \
	$(CURDIR)/code/tests/python/zato-common/pubsub/test_outgoing.py \
	$(CURDIR)/code/tests/python/zato-common/pubsub_outgoing/ \
	$(CURDIR)/code/tests/python/zato-server/outgoing_delivery/

Zato_Test_Step_Runner_pubsub-outgoing-live := $(Zato_Test_PubSub_Plain)
Zato_Test_Step_Tests_pubsub-outgoing-live  := $(CURDIR)/code/tests/python/zato-server/pubsub_outgoing/

# The steps of test-pubsub in the order they run, the step of exactly-once delivery, which runs its own walk, last,
# and the step that the target is currently on.
Zato_Test_PubSub_Steps := sql-conformance-static sql-conformance-engines \
	pubsub-core pubsub-encoding pubsub-failover pubsub-replication pubsub-faults \
	$(foreach mode,$(Zato_Test_PubSub_Managed_Modes),pubsub-managed-$(mode)) \
	$(foreach mode,$(Zato_Test_PubSub_Stability_Modes),pubsub-stability-$(mode)) \
	$(foreach mode,$(Zato_Test_PubSub_Stability_Modes),pubsub-subscription-flags-$(mode)) \
	pubsub-config-store pubsub-backend pubsub-outgoing pubsub-outgoing-live
Zato_Test_PubSub_Exactly_Once_Step := pubsub-exactly-once
Zato_Test_PubSub_Resume_File       := $(CURDIR)/code/tests/.test-pubsub-resume

test-pubsub: ## Every pub/sub functional test - core, SQL and outgoing delivery, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	@if [ -n "$(RESTART)" ]; then rm -f $(Zato_Test_PubSub_Resume_File); fi
	$(Zato_Log_Reset)
	mkdir -p $(Zato_Test_Resolver_Dir)
	gcc -shared -fPIC -o $(Zato_Test_Resolver_Library) $(Zato_Test_Resolver_Source) -ldl -lresolv
	$(MAKE) test-pubsub-encoding-rust
	@resume=''; \
	if [ -f $(Zato_Test_PubSub_Resume_File) ]; then \
		resume=$$(cat $(Zato_Test_PubSub_Resume_File)); \
		echo ">>> Resuming from $$resume" $(Zato_Log); \
	fi; \
	$(foreach step,$(Zato_Test_PubSub_Steps),$(call Zato_Test_Step,$(step),$(Zato_Test_PubSub_Resume_File))) \
	echo "$(Zato_Test_PubSub_Exactly_Once_Step)" > $(Zato_Test_PubSub_Resume_File); \
	$(MAKE) test-pubsub-exactly-once $(Zato_Log) || exit $$?; \
	rm -f $(Zato_Test_PubSub_Resume_File)

# The soak tests of every suite outside HA, which test-soak runs after every other target of test-all,
# while test-ha runs the soak tests of HA after every other HA target.
Zato_Test_Soak             := test-soak-pubsub test-soak-scheduler-failover
Zato_Test_Soak_Resume_File := $(CURDIR)/code/tests/.test-soak-resume

test-soak-pubsub: ## The pub/sub soak tests - the stability suite on every database mode.
	$(Zato_Log_Reset)
	for mode in $(Zato_Test_PubSub_Stability_Modes); do \
		Zato_Test_PubSub_DB_Mode=$$mode ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m gevent.monkey --module pytest \
			$(CURDIR)/code/tests/python/zato-server/pubsub_stability/ $(Zato_Test_Soak_Only) \
			-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_stability_soak_$$mode -W ignore::DeprecationWarning \
			$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log) || exit $$?; \
	done

test-soak-scheduler-failover: ## The soak test of the active-passive scheduler failover.
	$(Zato_Log_Reset)
	$(MAKE) scheduler-build $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-server/scheduler_failover/ $(Zato_Test_Soak_Only) \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_scheduler_failover_soak -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-soak: ## Every soak test, resuming from the target that last failed. RESTART=1 to start from scratch.
	$(call Zato_Test_Walk,$(Zato_Test_Soak),$(Zato_Test_Soak_Resume_File))

test-queue-delivery-rest: ## Queue delivery of outgoing REST connections - enmasse with a PostgreSQL ODB, then live.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_delivery_outgoing_rest.py \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_rest/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_rest \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-soap: ## Queue delivery of outgoing SOAP connections - enmasse with a PostgreSQL ODB, then live.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_delivery_outgoing_soap.py \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_soap/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_soap \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-fhir: ## Queue delivery of outgoing FHIR connections - enmasse with a PostgreSQL ODB, then live.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_delivery_outgoing_fhir.py \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_fhir/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_fhir \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-mllp: ## Queue delivery of outgoing MLLP connections - enmasse with a PostgreSQL ODB, then live.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_delivery_outgoing_mllp.py \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_mllp/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_mllp \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-channel-rest: ## The queue of REST channels - enmasse with a PostgreSQL ODB, the importer and the exporter of the delivery keys of REST and SOAP channels included, then live.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/importers/test_importer_enmasse_channel_delivery.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/exporters/test_exporter_enmasse_channel_delivery.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_delivery_channel_rest.py \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_channel_rest/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_channel_rest \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery-channel-soap: ## The queue of SOAP channels - enmasse with a PostgreSQL ODB, then live.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_delivery_channel_soap.py \
		$(CURDIR)/code/tests/python/zato-server/queue_delivery_channel_soap/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_queue_delivery_channel_soap \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-queue-delivery: test-queue-delivery-rest test-queue-delivery-soap test-queue-delivery-fhir test-queue-delivery-mllp test-queue-delivery-channel-rest test-queue-delivery-channel-soap ## Queue delivery of every kind of outgoing connection and of REST and SOAP channels.

# The live performance suite of pub/sub, run against a server on each pub/sub database in turn.
Zato_Test_PubSub_Perf_Dir         := $(CURDIR)/code/tests/python/zato-server/pubsub_perf
Zato_Test_PubSub_Perf_Tests       := $(Zato_Test_PubSub_Perf_Dir)/test_capacity.py $(Zato_Test_PubSub_Perf_Dir)/test_concurrency.py
Zato_Test_PubSub_Perf_Steps       := postgresql
Zato_Test_PubSub_Perf_Resume_File := $(CURDIR)/code/tests/.test-pubsub-perf-resume
Zato_Test_PubSub_Perf_Stepwise     = $(if $(RESTART),--sw-reset,--sw)

# Runs the suite on the pub/sub database $(1), unless the walk is still looking for the step it resumes from.
Zato_Test_PubSub_Perf_Step = \
	if [ -z "$$resume" ] || [ "$$resume" = "$(1)" ]; then \
		resume=''; \
		echo "$(1)" > $(Zato_Test_PubSub_Perf_Resume_File); \
		echo ">>> $(1)" $(Zato_Log); \
		Zato_Test_PubSub_DB_Mode=$(1) ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest -W ignore::DeprecationWarning \
			$(Zato_Test_PubSub_Perf_Tests) -v -s --tb=short \
			-o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_perf_$(1) \
			$(Zato_Test_PubSub_Perf_Stepwise) $(PYTEST_ARGS) $(Zato_Log) || exit $$?; \
	fi;

test-pubsub-perf: ## Pub/sub performance through a live server - concurrent publishers and subscribers, each subscriber with its own subscription, with exactly-once delivery, worker kills and rising concurrency, on PostgreSQL, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	@if [ -n "$(RESTART)" ]; then rm -f $(Zato_Test_PubSub_Perf_Resume_File); fi
	$(Zato_Log_Reset)
	@resume=''; \
	if [ -f $(Zato_Test_PubSub_Perf_Resume_File) ]; then \
		resume=$$(cat $(Zato_Test_PubSub_Perf_Resume_File)); \
		echo ">>> Resuming from $$resume" $(Zato_Log); \
	fi; \
	$(foreach step,$(Zato_Test_PubSub_Perf_Steps),$(call Zato_Test_PubSub_Perf_Step,$(step))) \
	rm -f $(Zato_Test_PubSub_Perf_Resume_File)

# The round-trip times of a network within one availability zone and across zones of a managed database, in milliseconds
Zato_Test_PubSub_Perf_Round_Trips := 0.5 1.0 2.0

test-pubsub-perf-latency: ## Pub/sub capacity through a live server on PostgreSQL, with each round-trip time of a managed database added to the network of the database container.
	$(Zato_Log_Reset)
	for round_trip in $(Zato_Test_PubSub_Perf_Round_Trips); do \
		Zato_Test_PubSub_DB_Mode=postgresql Zato_Test_PubSub_DB_Round_Trip_Ms=$$round_trip ZATO_TEST_BASE_DIR=$(CURDIR) \
		$(ZATO_PY) -m pytest -W ignore::DeprecationWarning \
			$(Zato_Test_PubSub_Perf_Dir)/test_capacity.py -v -s --tb=short \
			-o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_perf_latency \
			$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log) || exit $$?; \
	done

# The live suites of exactly-once delivery.
Zato_Test_Exactly_Once_Dir      := $(CURDIR)/code/tests/python/zato-server/pubsub_exactly_once
Zato_Test_Exactly_Once_Takeover := $(CURDIR)/code/tests/python/zato-server/pubsub_exactly_once_takeover

# The tests of each group and the pytest invocation that runs them.
Zato_Test_Exactly_Once_Gevent := -m gevent.monkey --module pytest -W "ignore:This process:DeprecationWarning"
Zato_Test_Exactly_Once_Live   := -m pytest -W ignore::DeprecationWarning

Zato_Test_Exactly_Once_Tests_backend  := $(CURDIR)/code/tests/python/zato-common/pubsub_backend/exactly_once/
Zato_Test_Exactly_Once_Tests_relay    := $(Zato_Test_Exactly_Once_Dir)/test_relay.py $(Zato_Test_Exactly_Once_Dir)/test_idempotency.py
Zato_Test_Exactly_Once_Tests_pull     := $(Zato_Test_Exactly_Once_Dir)/test_pull.py $(Zato_Test_Exactly_Once_Dir)/test_pull_response.py
Zato_Test_Exactly_Once_Tests_crash    := $(Zato_Test_Exactly_Once_Dir)/test_crash.py
Zato_Test_Exactly_Once_Tests_takeover := $(Zato_Test_Exactly_Once_Takeover)/
Zato_Test_Exactly_Once_Tests_traffic  := $(Zato_Test_Exactly_Once_Dir)/test_traffic.py

Zato_Test_Exactly_Once_Runner_backend  := $(Zato_Test_Exactly_Once_Gevent)
Zato_Test_Exactly_Once_Runner_relay    := $(Zato_Test_Exactly_Once_Live)
Zato_Test_Exactly_Once_Runner_pull     := $(Zato_Test_Exactly_Once_Live)
Zato_Test_Exactly_Once_Runner_crash    := $(Zato_Test_Exactly_Once_Live)
Zato_Test_Exactly_Once_Runner_takeover := $(Zato_Test_Exactly_Once_Live)
Zato_Test_Exactly_Once_Runner_traffic  := $(Zato_Test_Exactly_Once_Live)

# The steps in the order they run, each a group of tests on one pub/sub database, the step that the target is currently on,
# and the pytest option that resumes each step from the test that failed or was interrupted, or starts it over under RESTART.
Zato_Test_Exactly_Once_Steps := backend \
	$(foreach group,relay pull crash,$(foreach mode,postgresql,$(group):$(mode))) \
	takeover:postgresql \
	$(foreach mode,postgresql,traffic:$(mode))
Zato_Test_Exactly_Once_Resume_File := $(CURDIR)/code/tests/.test-pubsub-exactly-once-resume
Zato_Test_Exactly_Once_Stepwise     = $(if $(RESTART),--sw-reset,--sw)

# Runs the group $(2) on the pub/sub database $(3) as the step $(1), unless the walk is still looking for the step it resumes from.
Zato_Test_Exactly_Once_Run = \
	if [ -z "$$resume" ] || [ "$$resume" = "$(1)" ]; then \
		resume=''; \
		echo "$(1)" > $(Zato_Test_Exactly_Once_Resume_File); \
		echo ">>> $(1)" $(Zato_Log); \
		$(if $(3),Zato_Test_PubSub_DB_Mode=$(3)) ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) $(Zato_Test_Exactly_Once_Runner_$(2)) \
			$(Zato_Test_Exactly_Once_Tests_$(2)) -v -s --tb=short \
			-o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pubsub_exactly_once_$(subst :,_,$(1)) \
			$(Zato_Test_Exactly_Once_Stepwise) $(PYTEST_ARGS) $(Zato_Log) || exit $$?; \
	fi;

Zato_Test_Exactly_Once_Step = $(call Zato_Test_Exactly_Once_Run,$(1),$(word 1,$(subst :, ,$(1))),$(word 2,$(subst :, ,$(1))))

test-pubsub-exactly-once: ## Exactly-once delivery of pub/sub - the backend, a single server without and with faults, pull clients, takeovers and steady traffic, on PostgreSQL, resuming from the test that last failed or was interrupted. RESTART=1 to start from scratch.
	@if [ -n "$(RESTART)" ]; then rm -f $(Zato_Test_Exactly_Once_Resume_File); fi
	$(Zato_Log_Reset)
	$(MAKE) ha-node-build $(Zato_Log)
	$(MAKE) scheduler-build $(Zato_Log)
	@resume=''; \
	if [ -f $(Zato_Test_Exactly_Once_Resume_File) ]; then \
		resume=$$(cat $(Zato_Test_Exactly_Once_Resume_File)); \
		echo ">>> Resuming from $$resume" $(Zato_Log); \
	fi; \
	$(foreach step,$(Zato_Test_Exactly_Once_Steps),$(call Zato_Test_Exactly_Once_Step,$(step))) \
	rm -f $(Zato_Test_Exactly_Once_Resume_File)

# The suites of SQL conformance - the static scans, the settings of every engine and the acknowledgment of each write.
Zato_Test_SQL_Conformance_Dir := $(CURDIR)/code/tests/python/zato-common/sql_conformance

Zato_Test_Step_Plain  := -m pytest -W ignore::DeprecationWarning
Zato_Test_Step_Gevent := -m gevent.monkey --module pytest -W "ignore:This process:DeprecationWarning"

Zato_Test_Step_Tests_sql-conformance-static    := $(Zato_Test_SQL_Conformance_Dir)/static/ \
	$(CURDIR)/code/tests/python/zato-server/ha_postgresql_kubernetes/test_manifest_synchronous_standby.py
Zato_Test_Step_Tests_sql-conformance-engines   := $(Zato_Test_SQL_Conformance_Dir)/engines/
Zato_Test_Step_Tests_sql-conformance-writers   := $(Zato_Test_SQL_Conformance_Dir)/writers/

Zato_Test_Step_Runner_sql-conformance-static  := $(Zato_Test_Step_Plain)
Zato_Test_Step_Runner_sql-conformance-engines := $(Zato_Test_Step_Plain)
Zato_Test_Step_Runner_sql-conformance-writers := $(Zato_Test_Step_Gevent)

# The steps of each target in the order they run, the step that each target is currently on, and the pytest option
# that resumes each step from the test that failed or was interrupted, or starts it over under RESTART.
Zato_Test_SQL_Conformance_Steps       := sql-conformance-static sql-conformance-engines sql-conformance-writers
Zato_Test_SQL_Conformance_Fast_Steps  := sql-conformance-static sql-conformance-engines
Zato_Test_SQL_Conformance_Resume_File := $(CURDIR)/code/tests/.test-sql-conformance-resume
Zato_Test_Step_Stepwise                = $(if $(RESTART),--sw-reset,--sw)

# Runs the step $(1) without resuming, for the targets that run a step before their own suites.
Zato_Test_Step_Run_Once = \
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) $(Zato_Test_Step_Runner_$(1)) $(Zato_Test_Step_Tests_$(1)) \
		-v -s --tb=short -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_$(subst -,_,$(1)) \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log) || exit $$?;

# Runs the step $(1) of the walk with the resume file $(2), unless the walk is still looking for the step it resumes from,
# with the environment variables of the step, if it defines any.
Zato_Test_Step = \
	if [ -z "$$resume" ] || [ "$$resume" = "$(1)" ]; then \
		resume=''; \
		echo "$(1)" > $(2); \
		echo ">>> $(1)" $(Zato_Log); \
		$(Zato_Test_Step_Env_$(1)) ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) $(Zato_Test_Step_Runner_$(1)) $(Zato_Test_Step_Tests_$(1)) \
			-v -s --tb=short -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_$(subst -,_,$(1)) \
			$(Zato_Test_Step_Stepwise) $(PYTEST_ARGS) $(Zato_Log) || exit $$?; \
	fi;

# Walks the steps $(1) in order, resuming from the step named in the resume file $(2).
define Zato_Test_Step_Walk
	@if [ -n "$(RESTART)" ]; then rm -f $(2); fi
	$(Zato_Log_Reset)
	$(MAKE) ha-node-build $(Zato_Log)
	$(MAKE) scheduler-build $(Zato_Log)
	@resume=''; \
	if [ -f $(2) ]; then \
		resume=$$(cat $(2)); \
		echo ">>> Resuming from $$resume" $(Zato_Log); \
	fi; \
	$(foreach step,$(1),$(call Zato_Test_Step,$(step),$(2))) \
	rm -f $(2)
endef

# The targets of the repositories linked to this installation, which each makefile in links/ may extend - test-ha runs
# its own before the soak tests of HA, and test-lint and test-perf each run theirs after their own suites.
Zato_HA_Linked_Targets     :=
Zato_Static_Linked_Targets :=
Zato_Perf_Linked_Targets   :=

test-sql-conformance: ## SQL conformance - static scans, engine settings and write acknowledgments, resuming from the step that last failed or was interrupted. RESTART=1 to start from scratch.
	$(call Zato_Test_Step_Walk,$(Zato_Test_SQL_Conformance_Steps),$(Zato_Test_SQL_Conformance_Resume_File))

test-sql-conformance-fast: ## The static scans and the engine settings of SQL conformance, which test-pubsub and test-ha run first, test-pubsub as steps of its own walk.
	$(Zato_Log_Reset)
	@$(foreach step,$(Zato_Test_SQL_Conformance_Fast_Steps),$(call Zato_Test_Step_Run_Once,$(step)))

test-sql-conformance-static: ## The static scans of SQL conformance.
	$(Zato_Log_Reset)
	@$(call Zato_Test_Step_Run_Once,sql-conformance-static)

test-pubsub-encoding-rust: ## The Rust unit tests of the split push envelope encoder and of the vectored writes of the outgoing HTTP transport.
	$(Zato_Log_Reset)
	$(LOAD_CARGO_ENV) && cargo test --manifest-path $(ZATO_RUST)/zato_common_core/Cargo.toml --lib json $(Zato_Log)
	$(LOAD_CARGO_ENV) && cargo test --manifest-path $(ZATO_RUST)/zato_server_core/Cargo.toml --lib outgoing $(Zato_Log)

test-pubsub-encoding: ## Push payload encoding once per message - the Rust unit tests, the Python unit tests and the live tests of broadcast, edit, retry and the vectored transport, which test-pubsub runs as a step of its own.
	$(Zato_Log_Reset)
	$(MAKE) test-pubsub-encoding-rust
	@$(call Zato_Test_Step_Run_Once,pubsub-encoding)

test-perf-rules: ## The settings gate of performance figures and the scan of every performance suite.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-common/perf_rules/ \
		-v -s --tb=short -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_perf_rules -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

# The directory of the enmasse suites of zato-cli, which their modules import env_helper from
Zato_Test_Enmasse_Dir := $(CURDIR)/code/zato-cli/test/zato/enmasse_

# discord_disabled - these enmasse suites run in test-discord only
Zato_Test_Enmasse_Disabled := \
	test_importer_enmasse_discord.py test_exporter_enmasse_discord.py

# Every enmasse suite lives here - the importers, the exporters and the round trips for
# every connection type. Targets for a given connection type do not carry enmasse tests
# of their own, discovery below already covers them and running them twice proves nothing.
test-enmasse: ## Enmasse tests - every importer, every exporter, the file writer, is_active and should_delete on a PostgreSQL ODB, the round trips and secret rotation against live services.
	$(Zato_Log_Reset)
	cd $(Zato_Test_Enmasse_Dir) && $(Zato_Test_Failure_Reports_Env) $(ZATO_PY) -m pytest \
		$$(find . -name 'test_*.py' $(foreach name,$(Zato_Test_Enmasse_Disabled),! -name $(name)) | sort) \
		-v -s -x -o pythonpath=$(Zato_Test_Enmasse_Dir) -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_enmasse_cli \
		-W ignore::DeprecationWarning $(Zato_Test_Failure_Reports) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_file_writer.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_is_active.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_should_delete.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/importers/test_importer_enmasse_sql_extra.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_enmasse -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
# Secret rotation needs the live services switched on, which the discovery above leaves off
	Zato_Test_Live_SQL=1 Zato_Test_FTP=1 Zato_Test_SFTP=1 Zato_Test_SMB=1 Zato_Test_MongoDB=1 \
		$(Zato_Test_Failure_Reports_Env) $(ZATO_PY) -m pytest $(Zato_Test_Enmasse_Dir)/test_secret_rotation_live.py \
		-v -s -x -o pythonpath=$(Zato_Test_Enmasse_Dir) -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_enmasse_secret \
		-W ignore::DeprecationWarning $(Zato_Test_Failure_Reports) $(PYTEST_ARGS) $(Zato_Log)

test-enmasse-delete-live: ## Enmasse should_delete against a live server - every object created and deleted through the pickup directory.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_delete_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_enmasse_delete_live -o log_cli_level=WARNING \
		-W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-cli: ## CLI tests.
	$(Zato_Log_Reset)
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

test-outconn-tls-local-docker: ## Replaced client certificates of outgoing REST and SOAP connections in a container that the suite starts with the image's entrypoint.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/outconn_tls_local_docker/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_outconn_tls_local_docker -o log_cli_level=WARNING -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)

test-sql: ## Every SQL test - Redshift against a local protocol simulator, offline and through a live Zato server, and the SQL audit log of outgoing MySQL and PostgreSQL connections against live containers and of outgoing SQLite connections.
	$(Zato_Log_Reset)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/sql_cloud/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sql_cloud -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/sql_cloud_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sql_cloud_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/sql_outgoing_audit/test_sql_audit_sqlite.py \
		$(CURDIR)/code/tests/python/zato-server/sql_outgoing_audit/test_sql_audit_postgresql.py \
		$(CURDIR)/code/tests/python/zato-server/sql_outgoing_audit/test_sql_audit_mysql.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sql_audit -W ignore::DeprecationWarning \
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

test-oracle-db: ## Outgoing Oracle DB connection tests against a live Oracle container, including a live Zato server, stored procedure calls, concurrent queries from greenlets, the SQL audit log, and the facility synchronization project on a live Zato server with its scheduler, with faults injected at each step of a run.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/oracle_db_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_oracle_db_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/sql_outgoing_audit/test_sql_audit_oracle.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sql_audit_oracle -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/facility_sync_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_facility_sync_live -W ignore::DeprecationWarning \
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
	ZATO_TEST_BASE_DIR=$(CURDIR) $(Zato_Test_Failure_Reports_Env) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/connection/chat/discord/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_discord_client -W ignore::DeprecationWarning \
		$(Zato_Test_Failure_Reports) $(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/discord/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_discord_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) \
		$(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(Zato_Test_Failure_Reports_Env) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-cli/test/zato/enmasse_/importers/test_importer_enmasse_discord.py \
		$(CURDIR)/code/zato-cli/test/zato/enmasse_/exporters/test_exporter_enmasse_discord.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_discord_enmasse -W ignore::DeprecationWarning \
		$(Zato_Test_Failure_Reports) $(FAIL_FAST) $(PYTEST_ARGS) \
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
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/email_microsoft_365_smtp/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_email_microsoft_365_smtp -W ignore::DeprecationWarning \
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

test-hl7: ## Every HL7 test - parsing, FHIR, MLLP channels, outgoing connections, the enmasse import and export of MLLP and FHIR connections, the Dashboard views of MLLP channels, other languages and volume.
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
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/importers/test_importer_enmasse_channel_mllp.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/importers/test_importer_enmasse_outgoing_fhir.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/exporters/test_exporter_enmasse_channel_mllp.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/exporters/test_exporter_enmasse_outgoing_fhir.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_channel_mllp.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_outgoing_fhir.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_outgoing_mllp.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_tls_outgoing_mllp.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_enmasse -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
# The wizard's views configure Django in their conftest and run in a pytest process of their own
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/mllp_wizard_views/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_mllp_wizard_views -W ignore::DeprecationWarning \
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
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/mllp_integration/test_volume.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_volume -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	$(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/hl7_fhir/ \
		$(CURDIR)/code/tests/python/zato-common/fhir_display/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_hl7_fhir -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-ui: ## Every dashboard test - the UI kit, the sign-in of Dashboard users, the audit log, the URL configuration, the alerts tab, the headers of the middleware client, the whole Playwright suite and the web-admin access checks.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/webapp_ui/ \
		$(CURDIR)/code/tests/python/zato-common/webapp_auth/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_webapp_ui \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
# Each of these suites configures Django in its conftest with settings of its own and runs in a pytest process of its own
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/audit_log_views/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_log_views -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/urls_config/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_urls_config -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/alerts_tab/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_alerts_tab -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-dashboard/middleware_client/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_middleware_client -W ignore::DeprecationWarning \
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
test-kafka-live: ## Kafka tests against live Kafka in Docker - one instance plain and TLS, the three-instance cluster and queue delivery.
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

test-audit-log: ## Audit log tests against live PostgreSQL, plain and TLS, plus live Redis tests.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/redis_/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_redis \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/audit_log/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_log \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
# Each of these suites patches gevent in its conftest and runs in a pytest process of its own
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/audit_log_read/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_log_read -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/audit_log_write/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_log_write -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/email_imap_audit/ \
		$(CURDIR)/code/tests/python/zato-server/email_smtp_audit/ \
		$(CURDIR)/code/tests/python/zato-server/fhir_outgoing_audit/ \
		$(CURDIR)/code/tests/python/zato-server/http_channel_audit/ \
		$(CURDIR)/code/tests/python/zato-server/scheduler_audit/ \
		$(CURDIR)/code/tests/python/zato-server/service_audit/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_audit_log_reprocess -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-alerting: ## Alerting engine tests - rules, actions, dedup, lifecycle, collectors and the alert configuration of objects, the enmasse import and export of alert configuration, the alerts of generic and HTTP connections on a PostgreSQL configuration database, and the alert explanations, offline and through a live server with an LLM in a container.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/alerting/ \
		$(CURDIR)/code/tests/python/zato-common/alerting_explain/ \
		$(CURDIR)/code/tests/python/zato-common/alerting_object_config/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_alerting -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-cli/alerting_enmasse/ \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/importers/test_importer_enmasse_alerts.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/exporters/test_exporter_enmasse_alerts.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_alerts_channel_mllp.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_alerts_channel_soap.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_alerts_outgoing_fhir.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_alerts_outgoing_llm.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_alerts_outgoing_mllp.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_alerts_outgoing_rest.py \
		$(CURDIR)/code/tests/python/zato-cli/enmasse_/test_enmasse_alerts_outgoing_soap.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_alerting_enmasse -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/generic_alerts/ \
		$(CURDIR)/code/tests/python/zato-server/http_soap_alerts/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_connection_alerts -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/alert_explanation/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_alert_explanation -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/alert_explanation_live/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_alert_explanation_live -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-lets-encrypt: ## Let's Encrypt tests - lego obtains and renews certificates from a local Pebble, zato.test must point to 127.0.0.1 in /etc/hosts.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/lets_encrypt/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_lets_encrypt -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-ftp: ## FTP and FTPS tests - the outconn, enmasse and scheduler suites against live FTP servers, plus the audit and delivery suites against stubs.
	$(Zato_Log_Reset)
	Zato_Test_FTP=1 ZATO_TEST_BASE_DIR=$(CURDIR) $(Zato_Test_Failure_Reports_Env) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/connection/test_outconn_ftp.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_ftp -W ignore::DeprecationWarning \
		$(Zato_Test_Failure_Reports) $(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
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
	Zato_Test_SFTP=1 ZATO_TEST_BASE_DIR=$(CURDIR) $(Zato_Test_Failure_Reports_Env) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-server/test/zato/connection/test_outconn_sftp.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_sftp -W ignore::DeprecationWarning \
		$(Zato_Test_Failure_Reports) $(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
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

Zato_SMB_Windows_CLI   = PYTHONPATH=$(CURDIR)/code/tests/python/zato-common/lib $(ZATO_PY) -u -m live_windows.cli
Zato_SMB_Windows_Tests = $(CURDIR)/code/tests/python/zato-server/smb_windows_live
Zato_SMB_Windows_Shards = PYTHONPATH=$(CURDIR)/code/tests/python/zato-common/lib $(ZATO_PY) -u -m live_windows.shards

test-smb-windows-build: ## Windows Server 2025, 2022 and 2019 guests and a Japanese Windows Server 2025 guest for the live SMB tests - builds the prepared disks and the ready states that are missing or out of date.
	$(Zato_SMB_Windows_CLI) build

# The tests of test-smb-ui, and the directory under which the server of each shard keeps its databases,
# on a drive whose syncs keep pace with the audit writes of the servers of every shard.
Zato_Test_SMB_UI_Tests    := $(CURDIR)/code/tests/python/zato-dashboard/playwright_/smb_windows_ui
Zato_Test_SMB_UI_Disk_Dir ?= $(HOME)/files/zato-test

test-smb-ui: ## Live SMB tests through the Dashboard against Windows Server 2025, 2022 and 2019 guests and a Japanese Windows Server 2025 guest - the tests are divided into shards, set by Zato_Test_SMB_Shards, that run at the same time, each with a server, a Dashboard and guests of its own resumed from their ready states, and each creating the connections, the schedules and the job of its guests through the Dashboard.
	$(Zato_Log_Reset)
	Zato_Test_SMB_Windows=1 Zato_Test_Disk_Dir=$(Zato_Test_SMB_UI_Disk_Dir) ZATO_TEST_BASE_DIR=$(CURDIR) $(Zato_SMB_Windows_Shards) \
		$(Zato_Test_SMB_UI_Tests) \
		-x -v -s -p no:cacheprovider -o log_cli_level=WARNING -o faulthandler_timeout=120 -W ignore::DeprecationWarning \
		$(PYTEST_ARGS) $(Zato_Log)

test-smb: ## Live SMB tests against Windows Server 2025, 2022 and 2019 guests and a Japanese Windows Server 2025 guest - the offline checks, the audit, store and reprocess suites against stubs, the file exchange flows, reliability, the Dashboard and failover, in that order.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/live_windows_offline/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_smb_windows_offline -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_smb_audit.py \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_file_transfer_audit.py \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_store_data_types.py \
		$(CURDIR)/code/tests/python/zato-server/file_transfer_audit/test_reprocess.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_smb_audit -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	trap '$(Zato_SMB_Windows_CLI) stop' EXIT; \
	$(Zato_SMB_Windows_CLI) start $(Zato_Log) && \
	Zato_Test_SMB_Windows=1 ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(Zato_SMB_Windows_Tests)/test_connectivity.py \
		$(Zato_SMB_Windows_Tests)/test_exchange_hub.py \
		$(Zato_SMB_Windows_Tests)/test_write_modes.py \
		$(Zato_SMB_Windows_Tests)/test_documents.py \
		$(Zato_SMB_Windows_Tests)/test_labels.py \
		$(Zato_SMB_Windows_Tests)/test_landing.py \
		$(Zato_SMB_Windows_Tests)/test_bidirectional.py \
		$(Zato_SMB_Windows_Tests)/test_reliability.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_smb_windows -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log) && \
	$(MAKE) test-smb-ui $(Zato_Log) && \
	Zato_Test_SMB_Windows=1 ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(Zato_SMB_Windows_Tests)/test_failover.py \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_smb_windows_failover -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-file-transfer: test-sftp test-smb ## File transfer demo tests - the SFTP suites first, then the demo config set, the local SFTP, FTP, FTPS and SMB servers, a live server polling all of them, and the Dashboard card.
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

test-rule-engine: ## Rule engine tests - grammar, matching, the SQL store, invocation and the API portal.
	$(Zato_Log_Reset)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(Zato_Test_Failure_Reports_Env) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/zato-common/test/zato/common/rule_engine/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rule_engine \
		$(Zato_Test_Failure_Reports) $(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/rule_engine_sql/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rule_engine_sql \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/rule_engine_webapi/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_rule_engine_webapi \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

test-analytics: ## Analytics rollup, view and baseline tests on PostgreSQL, with the rollup reading audit logs held in PostgreSQL.
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
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-common/common_db/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_common_db -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-common/reservation/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_reservation \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-common/database_env/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_database_env \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest $(CURDIR)/code/tests/python/zato-common/local_postgresql/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_local_postgresql \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)
# The suite of the PostgreSQL driver patches gevent in its conftest and runs in a pytest process of its own
	ZATO_TEST_BASE_DIR=$(CURDIR) $(ZATO_PY) -m pytest \
		$(CURDIR)/code/tests/python/zato-common/pg8000_wire/ \
		-v -s -o cache_dir=$(CURDIR)/code/tests/.pytest_cache_pg8000_wire -W ignore::DeprecationWarning \
		$(FAIL_FAST) $(PYTEST_ARGS) $(Zato_Log)

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
	test-audit-log test-analytics test-arbiter

# Suites needing a live server or an external service
# discord_disabled - test-discord
Zato_Test_Live := \
	test-mcp test-logging test-graphql test-grpc test-aws test-pubsub test-queue-delivery test-mongodb test-es \
	test-sql test-oracle-db test-mssql-db test-microsoft-cloud test-salesforce test-bearer \
	test-ibm-mq test-kafka test-sdk test-hl7 test-ccda test-documents test-llm test-rule-engine test-enmasse test-audit-export \
	test-api-portal-live test-file-transfer test-perf-rules test-hot-deployment

# The whole browser and dashboard suite
# Zato_Test_Browser := test-ui

# Mutation and fuzzing, the longest of all
# fuzz_disabled - test-rest-fuzz test-server-fuzz
Zato_Test_Heavy := test-rest test-server

# Standalone performance suites, left out of test-all
Zato_Test_Perf := test-pubsub-perf test-pubsub-perf-latency

Zato_Test_Fuzz := test-rest-fuzz test-server-fuzz

Zato_Test_All := \
	$(Zato_Test_Static) $(Zato_Test_Offline) $(Zato_Test_Toolchain) \
	$(Zato_Test_Live) test-sql-conformance test-ha $(Zato_Test_Browser) $(Zato_Test_Heavy) test-soak

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

test-clear-test-all: ## Run test-all from a clear state instead of resuming a previous run.
	$(MAKE) RESTART=1 test-all

test-clear: ## Forget where every test target stopped, so that each next run starts from the beginning.
	rm -f $(CURDIR)/code/tests/.test-*-resume
	rm -rf $(CURDIR)/code/tests/.pytest_cache_*

test-perf: $(Zato_Test_Perf) ## Every performance suite - not part of test-all.
	$(foreach target,$(Zato_Perf_Linked_Targets),$(MAKE) $(target) &&) true

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
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_ha_core/Cargo.toml        -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_input_output/Cargo.toml             -- --check && \
	cargo fmt --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   -- --check

format: format-zato ## Check Rust formatting everywhere.

clippy-zato: rust-target-prune ## Clippy all public Rust crates.
	. $(HOME)/.cargo/env && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_common_core/Cargo.toml    --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_pg_wire/Cargo.toml        --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_server_core/Cargo.toml    --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_ipc_core/Cargo.toml       --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
	CLIPPY_CONF_DIR=$(ZATO_CLIPPY_CONF) cargo clippy --manifest-path $(ZATO_RUST_DIR)/zato_ha_core/Cargo.toml        --all-targets --all-features -- $(ZATO_CLIPPY_FLAGS) && \
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
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_ipc_core/Cargo.toml       -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_scheduler_core/Cargo.toml -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_ha_core/Cargo.toml        -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_input_output/Cargo.toml             -- --tests && \
	DYLINT_RUSTFLAGS="$(ZATO_DYLINT_FLAGS)" cargo dylint $(DYLINT_LIBS) --manifest-path $(ZATO_RUST_DIR)/zato_queue_bridge/Cargo.toml   -- --tests

dylint: dylint-zato ## Dylint everything.

# Every Cargo manifest of the product crates, their fuzz crates and the Rust test crates. The list is discovered
# at invocation time, so a crate added to the repository is audited without being registered here.
ZATO_DENY_CONF       := $(CURDIR)/code/tests/rust/rust-lint/deny.toml
ZATO_RUST_MANIFESTS   = $(shell find $(ZATO_RUST_DIR) $(CURDIR)/code/tests/rust -name Cargo.toml -not -path '*/target/*' | sort)

rust-deny-zato: ## Dependency audit - advisories, licenses, bans and sources - of every Rust manifest in the repository.
	. $(HOME)/.cargo/env && \
	failed=""; \
	for manifest in $(ZATO_RUST_MANIFESTS); do \
		echo ">>> cargo deny $$manifest"; \
		cargo deny --manifest-path $$manifest --config $(ZATO_DENY_CONF) check || failed="$$failed $$manifest"; \
	done; \
	if [ -n "$$failed" ]; then printf 'cargo deny failed for:%s\n' "$$failed"; exit 1; fi

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
	for crate in zato_common_core zato_pg_wire zato_server_core zato_scheduler_core zato_ha_core; do \
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

# ----------------------------------------------------------------------------
# The targets of the repositories linked to this installation, one makefile for each in links/.
include $(wildcard $(CURDIR)/links/*.mk)
