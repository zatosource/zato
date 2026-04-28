.PHONY: build install clean server-build scheduler-build sio-build common-core-build queue-bridge-build \
	server-clean scheduler-clean sio-clean common-core-clean queue-bridge-clean \
	server-install scheduler-install sio-install common-core-install queue-bridge-install \
	ruff qa-reqs-install unify \
	update cron-update stop-server restart-server restart-server-with-scheduler \
	stop-dashboard restart-dashboard scheduler

MAKEFLAGS += --silent

ZATO_RUST := $(CURDIR)/code/zato-rust

default: build

build: common-core-build server-build scheduler-build sio-build queue-bridge-build

server-build:
	. $(HOME)/.cargo/env && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_server_core/Cargo.toml

scheduler-build:
	. $(HOME)/.cargo/env && \
	cargo build --release --manifest-path $(ZATO_RUST)/zato_scheduler_core/Cargo.toml --bin _zato_scheduler && \
	cp $(ZATO_RUST)/zato_scheduler_core/target/release/_zato_scheduler $(CURDIR)/code/bin/_zato_scheduler

scheduler:
	$(CURDIR)/code/bin/_zato_scheduler

sio-build:
	. $(HOME)/.cargo/env && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_sio/Cargo.toml

common-core-build:
	. $(HOME)/.cargo/env && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_common_core/Cargo.toml

queue-bridge-build:
	. $(HOME)/.cargo/env && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(ZATO_RUST)/zato_queue_bridge/Cargo.toml

install:
	@if [ "$(filter-out install,$(MAKECMDGOALS))" = "" ]; then \
		$(CURDIR)/code/install.sh; \
	else \
		$(CURDIR)/code/support-linux/bin/uv pip install --upgrade --python $(CURDIR)/code/bin/python $(filter-out install,$(MAKECMDGOALS)); \
	fi

%:
	@:

clean:
	$(CURDIR)/code/clean.sh

server-clean:
	rm -rf $(ZATO_RUST)/zato_server_core/target

scheduler-clean:
	rm -rf $(ZATO_RUST)/zato_scheduler_core/target

sio-clean:
	rm -rf $(ZATO_RUST)/zato_sio/target

common-core-clean:
	rm -rf $(ZATO_RUST)/zato_common_core/target

queue-bridge-clean:
	rm -rf $(ZATO_RUST)/zato_queue_bridge/target

server-install: server-build

scheduler-install: scheduler-build

sio-install: sio-build

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
