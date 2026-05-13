.PHONY: build install clean server-build scheduler-build io-build common-core-build queue-bridge-build \
	server-clean scheduler-clean io-clean common-core-clean queue-bridge-clean \
	server-install scheduler-install io-install common-core-install queue-bridge-install \
	ruff pyright qa-reqs-install unify \
	update cron-update stop-server restart-server restart-server-with-scheduler \
	stop-dashboard restart-dashboard scheduler queue-bridge file-listener

MAKEFLAGS += --silent

CARGO_ENV := $(HOME)/.cargo/env
LOAD_CARGO_ENV := if [ -f $(CARGO_ENV) ]; then . $(CARGO_ENV); fi

ZATO_RUST := $(CURDIR)/code/zato-rust
ZATO_HEALTH_RS := $(CURDIR)/code/zato-common/src/zato

default: build

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

scheduler:
	$(CURDIR)/code/bin/_zato_scheduler

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

queue-bridge-build:
	@echo ">>> Building queue-bridge"
	$(LOAD_CARGO_ENV) && \
	cargo build --release --manifest-path $(ZATO_RUST)/zato_queue_bridge/Cargo.toml --bin _zato_queue_bridge && \
	rm -f $(CURDIR)/code/bin/_zato_queue_bridge && \
	cp $(ZATO_RUST)/zato_queue_bridge/target/release/_zato_queue_bridge $(CURDIR)/code/bin/_zato_queue_bridge

# FHIR commented out for now
#fhir-rust-build:
#	@echo ">>> Building FHIR Rust extension"
#	$(LOAD_CARGO_ENV) && \
#	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
#	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_HEALTH_RS)/fhir_r4_0_1_core/Cargo.toml

# FHIR commented out for now
#fhir-rust-clean:
#	rm -rf $(ZATO_HEALTH_RS)/fhir_r4_0_1_core/target

queue-bridge:
	$(CURDIR)/code/bin/_zato_queue_bridge

file-listener:
	$(CURDIR)/code/bin/py $(CURDIR)/code/zato-common/src/zato/common/file_transfer/listener.py

install:
	@if [ -z "$(MAKEOVERRIDES)" ]; then \
		$(CURDIR)/code/install.sh; \
	else \
		$(CURDIR)/code/support-linux/bin/uv pip install --upgrade --python $(CURDIR)/code/bin/python $(MAKEOVERRIDES); \
	fi

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

server-install: server-build

scheduler-install: scheduler-build

io-install: io-build

common-core-install: common-core-build

queue-bridge-install: queue-bridge-build

qa-reqs-install:
	$(CURDIR)/code/support-linux/bin/uv pip install --upgrade --python $(CURDIR)/code/bin/python -r $(CURDIR)/code/qa-requirements.txt
	npx --yes playwright install chromium
	mkdir -p $(CURDIR)/code/eggs/requests/ || true
	cp -v $(CURDIR)/code/patches/requests/* $(CURDIR)/code/eggs/requests/
	sudo snap install k6

SITE_PACKAGES := $(shell $(CURDIR)/code/bin/python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])" 2>/dev/null)

unify:
	mkdir -p $(SITE_PACKAGES)/lib2to3/pgen2
	printf 'def detect_encoding(readline):\n    return ("utf-8", [])\n' > $(SITE_PACKAGES)/lib2to3/pgen2/tokenize.py
	touch $(SITE_PACKAGES)/lib2to3/__init__.py
	touch $(SITE_PACKAGES)/lib2to3/pgen2/__init__.py
	python3 $(CURDIR)/code/util/unify.py

ruff:
	$(CURDIR)/code/bin/ruff check $(CURDIR)/code

pyright:
	@echo "Running pyright from $(CURDIR)/code on zato-common/src/zato/hl7v2/ tests/python/"
	cd $(CURDIR)/code && pyright zato-common/src/zato/hl7v2/ tests/python/

update:
	py $(CURDIR)/code/zato-common/src/zato/common/util/updates_cli.py

cron-update:
	/opt/zato/current/bin/py $(CURDIR)/code/zato-common/src/zato/common/util/updates_cron.py

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
