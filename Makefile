
.PHONY: build
MAKEFLAGS += --silent

default: run-tests
PY_DIR=$(CURDIR)/../bin

common-tests:
	cd $(CURDIR)/code/zato-common && make run-tests

cy-tests:
	cd $(CURDIR)/code/zato-cy && make run-tests

server-tests:
	cd $(CURDIR)/code/zato-server && make run-tests

cli-tests:
	cd $(CURDIR)/code/zato-cli && make run-tests

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

type-check-pubsub:
	cd $(CURDIR)/code/zato-server && $(MAKE) pyright-pubsub
	echo "Type checks OK"

web-admin-tests:
	cd $(CURDIR)/code/zato-web-admin && make run-tests

scheduler-tests:
	cd $(CURDIR)/code/zato-scheduler && make run-tests

rules-tests:
	cd $(CURDIR)/code/zato-common && make rules-tests

openapi:
	py $(CURDIR)/code/zato-openapi/src/zato/openapi/generator/cli.py $(filter-out $@,$(MAKECMDGOALS))

%:
	@:

rules-perf-tests:
	cd $(CURDIR)/code/zato-common && make rules-perf-tests

install-qa-reqs:
	$(CURDIR)/code/bin/pip install --upgrade -r $(CURDIR)/code/qa-requirements.txt
	npx playwright install
	mkdir -p $(CURDIR)/code/eggs/requests/ || true
	cp -v $(CURDIR)/code/patches/requests/* $(CURDIR)/code/eggs/requests/

functional-tests:
	$(MAKE) web-admin-tests
	$(MAKE) common-tests
	$(MAKE) server-tests
	$(MAKE) cli-tests
	$(MAKE) scheduler-tests
	$(MAKE) cy-tests

run-tests:
	$(MAKE) install-qa-reqs
	$(CURDIR)/code/bin/playwright install
	$(MAKE) static-check
	$(MAKE) functional-tests
