.PHONY: build install clean server-build scheduler-build sio-build \
	server-clean scheduler-clean sio-clean \
	server-install scheduler-install sio-install \
	ruff qa-reqs-install unify \
	update cron-update stop-server restart-server restart-server-with-scheduler \
	stop-dashboard restart-dashboard

MAKEFLAGS += --silent

default: build

build: server-build scheduler-build sio-build

server-build:
	. $(HOME)/.cargo/env && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(CURDIR)/code/zato-server/src/zato_server_core/Cargo.toml

scheduler-build:
	. $(HOME)/.cargo/env && \
	VIRTUAL_ENV=$(CURDIR)/code PATH=$(CURDIR)/code/bin:$$PATH \
	$(CURDIR)/code/bin/maturin develop --release --manifest-path $(CURDIR)/code/zato-scheduler/src/zato_scheduler_core/Cargo.toml

sio-build:
	cd $(CURDIR)/code/zato-common && $(MAKE) build

install:
ifeq ($(strip $(PKG)),)
	$(CURDIR)/code/install.sh
else
	$(CURDIR)/code/support-linux/bin/uv pip install --upgrade --python $(CURDIR)/code/bin/python $(PKG)
endif

clean:
	$(CURDIR)/code/clean.sh

server-clean:
	rm -rf $(CURDIR)/code/zato-server/src/zato_server_core/target

scheduler-clean:
	rm -rf $(CURDIR)/code/zato-scheduler/src/zato_scheduler_core/target

sio-clean:
	rm -rf $(CURDIR)/code/zato-common/src/zato_sio/target

server-install: server-build

scheduler-install: scheduler-build

sio-install: sio-build

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
