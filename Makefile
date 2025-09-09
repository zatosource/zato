.PHONY: build
MAKEFLAGS += --silent

default: run-tests
PY_DIR=$(CURDIR)/../bin

static-check:
	cd $(CURDIR)/code/zato-broker    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-cli       && $(MAKE) static-check
	cd $(CURDIR)/code/zato-client    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-common    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-distlock  && $(MAKE) static-check
	cd $(CURDIR)/code/zato-cy        && $(MAKE) static-check
	cd $(CURDIR)/code/zato-scheduler && $(MAKE) static-check
	cd $(CURDIR)/code/zato-server    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-testing   && $(MAKE) static-check
	cd $(CURDIR)/code/zato-web-admin && $(MAKE) static-check
	echo "Static checks OK"

type-check:
	cd $(CURDIR)/code/zato-common && $(MAKE) type-check
	cd $(CURDIR)/code/zato-server && $(MAKE) type-check
	echo "Type checks OK"

web-admin-tests:
	cd $(CURDIR)/code/zato-web-admin && PYTHONWARNINGS='ignore:X509Extension support in pyOpenSSL is deprecated.:DeprecationWarning' make run-tests

common-tests:
	cd $(CURDIR)/code/zato-common && make run-tests

pubsub-tests:
	cd $(CURDIR)/code/zato-common && Zato_Has_Debug=0 make pubsub-tests

server-tests:
	cd $(CURDIR)/code/zato-server && PYTHONWARNINGS=ignore make run-tests

cy-tests:
	cd $(CURDIR)/code/zato-cy && make PYTHONWARNINGS='ignore:X509Extension support in pyOpenSSL is deprecated.:DeprecationWarning' run-tests

cli-tests:
	cd $(CURDIR)/code/zato-cli && make run-tests

openapi:
	py -m zato.openapi.generator.cli $(filter-out $@,$(MAKECMDGOALS))

openapi-server-run:
	py $(CURDIR)/code/zato-openapi/src/zato/openapi/app/run.py

%:
	@:

install-qa-reqs:
	$(CURDIR)/code/bin/pip install --upgrade -r $(CURDIR)/code/qa-requirements.txt
	npx playwright install
	mkdir -p $(CURDIR)/code/eggs/requests/ || true
	cp -v $(CURDIR)/code/patches/requests/* $(CURDIR)/code/eggs/requests/
	sudo snap install k6

run-tests:
#	$(MAKE) web-admin-tests
	$(MAKE) common-tests
#	$(MAKE) server-tests
	$(MAKE) cli-tests
#	$(MAKE) cy-tests

all-tests:
	$(MAKE) run-tests

unify:
	mkdir -p $(CURDIR)/code/lib/python3.12/site-packages/lib2to3/pgen2
	printf 'def detect_encoding(readline):\n    return ("utf-8", [])\n' > $(CURDIR)/code/lib/python3.12/site-packages/lib2to3/pgen2/tokenize.py
	touch $(CURDIR)/code/lib/python3.12/site-packages/lib2to3/__init__.py
	touch $(CURDIR)/code/lib/python3.12/site-packages/lib2to3/pgen2/__init__.py
	python3 $(CURDIR)/code/util/unify.py

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
	grafana-server \
		--homepath=/usr/share/grafana \
		--config=/dev/null \
		cfg:default.paths.data=/tmp/grafana-data \
		cfg:default.paths.logs=/tmp/grafana-logs \
		cfg:default.paths.plugins=/tmp/grafana-plugins \
		cfg:default.paths.provisioning=$(CURDIR)/code/zato-common/src/zato/common/pubsub/perftest/grafana_
