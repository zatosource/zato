
.PHONY: build
MAKEFLAGS += --silent

default: run-tests

common-tests:
	cd $(CURDIR)/code/zato-common && make run-tests

cy-tests:
	cd $(CURDIR)/code/zato-cy && make run-tests

pylint:
	cd $(CURDIR)/code/zato-agent     && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-broker    && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-cli       && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-client    && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-common    && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-distlock  && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-cy        && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-hl7       && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-lib       && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-scheduler && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-server    && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-sso       && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-testing   && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-web-admin && $(MAKE) pylint || true
	cd $(CURDIR)/code/zato-zmq       && $(MAKE) pylint || true

server-tests:
	cd $(CURDIR)/code/zato-server && make run-tests

cli-tests:
	cd $(CURDIR)/code/zato-cli && make run-tests

sso-tests:
	cd $(CURDIR)/code/zato-sso && make run-tests

static-check:
	cd $(CURDIR)/code/zato-agent     && $(MAKE) static-check
	cd $(CURDIR)/code/zato-broker    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-cli       && $(MAKE) static-check
	cd $(CURDIR)/code/zato-client    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-common    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-distlock  && $(MAKE) static-check
	cd $(CURDIR)/code/zato-cy        && $(MAKE) static-check
	cd $(CURDIR)/code/zato-hl7       && $(MAKE) static-check
	cd $(CURDIR)/code/zato-lib       && $(MAKE) static-check
	cd $(CURDIR)/code/zato-scheduler && $(MAKE) static-check
	cd $(CURDIR)/code/zato-server    && $(MAKE) static-check
	cd $(CURDIR)/code/zato-sso       && $(MAKE) static-check
	cd $(CURDIR)/code/zato-testing   && $(MAKE) static-check
	cd $(CURDIR)/code/zato-web-admin && $(MAKE) static-check
	cd $(CURDIR)/code/zato-zmq       && $(MAKE) static-check
	$(CURDIR)/code/bin/flake8 --config=$(CURDIR)/code/tox.ini $(CURDIR)/code/util
	echo "Static checks OK"

type-check:
	cd $(CURDIR)/code/zato-common && $(MAKE) type-check
	cd $(CURDIR)/code/zato-server && $(MAKE) type-check
	echo "Type checks OK"

web-admin-tests:
	cd $(CURDIR)/code/zato-web-admin && make run-tests

scheduler-tests:
	cd $(CURDIR)/code/zato-scheduler && make run-tests

install-qa-reqs:
	$(CURDIR)/code/bin/pip install --upgrade -r $(CURDIR)/code/qa-requirements.txt
	npx --yes playwright install
	cp -v $(CURDIR)/code/patches/requests/* $(CURDIR)/code/eggs/requests/

run-tests:
	$(MAKE) install-qa-reqs
	$(MAKE) static-check
	$(MAKE) type-check
	$(MAKE) common-tests
	$(MAKE) server-tests
	$(MAKE) cli-tests
	$(MAKE) scheduler-tests
	$(MAKE) sso-tests
	$(MAKE) web-admin-tests
	$(MAKE) cy-tests
