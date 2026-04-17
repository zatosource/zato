.PHONY: build install clean server-build scheduler-build sio-build \
	server-clean scheduler-clean sio-clean \
	server-install scheduler-install sio-install \
	static-check qa-reqs-install unify \
	update cron-update stop-server restart-server restart-server-with-scheduler \
	stop-dashboard restart-dashboard generate-enmasse run-producers run-consumers prometheus grafana

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

INSTALL_ARGS := $(filter-out install,$(MAKECMDGOALS))

install:
ifeq ($(strip $(INSTALL_ARGS)),)
	$(CURDIR)/code/install.sh
else
	$(CURDIR)/code/support-linux/bin/uv pip install --upgrade --python $(CURDIR)/code/bin/python $(INSTALL_ARGS)
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

unify:
	mkdir -p $(CURDIR)/code/lib/python3.12/site-packages/lib2to3/pgen2
	printf 'def detect_encoding(readline):\n    return ("utf-8", [])\n' > $(CURDIR)/code/lib/python3.12/site-packages/lib2to3/pgen2/tokenize.py
	touch $(CURDIR)/code/lib/python3.12/site-packages/lib2to3/__init__.py
	touch $(CURDIR)/code/lib/python3.12/site-packages/lib2to3/pgen2/__init__.py
	python3 $(CURDIR)/code/util/unify.py

static-check:
	cd $(CURDIR)/code/zato-cli       && $(MAKE) static-check
	cd $(CURDIR)/code/zato-client    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-common    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-distlock  && $(MAKE) static-check
	cd $(CURDIR)/code/zato-cy        && $(MAKE) static-check
	cd $(CURDIR)/code/zato-server    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-testing   && $(MAKE) static-check
	cd $(CURDIR)/code/zato-web-admin && $(MAKE) static-check
	echo "Static checks OK"

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

generate-enmasse:
	cd $(CURDIR)/code/zato-common && $(MAKE) generate-enmasse USERS=$(word 2,$(MAKECMDGOALS)) TOPICS_MULTIPLIER=$(word 3,$(MAKECMDGOALS))

run-producers:
	py code/zato-common/src/zato/common/pubsub/perftest/python_/app.py \
		--num-producers $(if $(word 2,$(MAKECMDGOALS)),$(word 2,$(MAKECMDGOALS)),1) \
		--reqs-per-producer $(if $(word 3,$(MAKECMDGOALS)),$(word 3,$(MAKECMDGOALS)),1) \
		--reqs-per-second $(if $(word 4,$(MAKECMDGOALS)),$(word 4,$(MAKECMDGOALS)),1.0) \
		--topics $(if $(word 5,$(MAKECMDGOALS)),$(word 5,$(MAKECMDGOALS)),3) \
		--burst-multiplier $(if $(word 6,$(MAKECMDGOALS)),$(word 6,$(MAKECMDGOALS)),10) \
		--burst-interval $(if $(word 7,$(MAKECMDGOALS)),$(word 7,$(MAKECMDGOALS)),60) \
		--burst-duration $(if $(word 8,$(MAKECMDGOALS)),$(word 8,$(MAKECMDGOALS)),10) \
		$(if $(word 9,$(MAKECMDGOALS)),--cpu-num $(word 9,$(MAKECMDGOALS)),) \
		$(if $(word 10,$(MAKECMDGOALS)),--use-new-requests,)

run-consumers:
	py code/zato-common/src/zato/common/pubsub/perftest/python_/app.py \
		--num-consumers $(if $(word 2,$(MAKECMDGOALS)),$(word 2,$(MAKECMDGOALS)),1) \
		--pull-interval $(if $(word 3,$(MAKECMDGOALS)),$(word 3,$(MAKECMDGOALS)),1.0) \
		--max-messages $(if $(word 4,$(MAKECMDGOALS)),$(word 4,$(MAKECMDGOALS)),100) \
		$(if $(word 5,$(MAKECMDGOALS)),--cpu-num $(word 5,$(MAKECMDGOALS)),) \
		$(if $(word 6,$(MAKECMDGOALS)),--use-new-requests,)

prometheus:
	prometheus --config.file=$(CURDIR)/code/zato-common/src/zato/common/pubsub/perftest/prometheus_/prometheus.yml

grafana:
	env GF_SECURITY_ADMIN_PASSWORD=$$Zato_Grafana_Password \
	Zato_Grafana_Base_Path=$(CURDIR)/code/zato-common/src/zato/common/pubsub/perftest/grafana_ \
	grafana-server \
		--homepath=/usr/share/grafana \
		--config=/dev/null \
		cfg:default.paths.data=/tmp/grafana-data \
		cfg:default.paths.logs=/tmp/grafana-logs \
		cfg:default.paths.plugins=/tmp/grafana-plugins \
		cfg:default.paths.provisioning=$(CURDIR)/code/zato-common/src/zato/common/pubsub/perftest/grafana_

json:
	@:

%:
	@:
