
.PHONY: build
MAKEFLAGS += --silent

default: run-tests
PY_DIR=$(CURDIR)/../bin

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

flake8:
	cd $(CURDIR)/code/zato-agent     && $(MAKE) flake8
	cd $(CURDIR)/code/zato-broker    && $(MAKE) flake8
	cd $(CURDIR)/code/zato-cli       && $(MAKE) flake8
	cd $(CURDIR)/code/zato-client    && $(MAKE) flake8
	cd $(CURDIR)/code/zato-common    && $(MAKE) flake8
	cd $(CURDIR)/code/zato-distlock  && $(MAKE) flake8
	cd $(CURDIR)/code/zato-cy        && $(MAKE) flake8
	cd $(CURDIR)/code/zato-hl7       && $(MAKE) flake8
	cd $(CURDIR)/code/zato-lib       && $(MAKE) flake8
	cd $(CURDIR)/code/zato-scheduler && $(MAKE) flake8
	cd $(CURDIR)/code/zato-server    && $(MAKE) flake8
	cd $(CURDIR)/code/zato-sso       && $(MAKE) flake8
	cd $(CURDIR)/code/zato-testing   && $(MAKE) flake8
	cd $(CURDIR)/code/zato-web-admin && $(MAKE) flake8
	cd $(CURDIR)/code/zato-zmq       && $(MAKE) flake8
	$(CURDIR)/code/bin/flake8 --config=$(CURDIR)/code/tox.ini $(CURDIR)/code/util
	echo "Flake8 checks OK"

static-check:
	$(CURDIR)/code/bin/flake8 --config=$(CURDIR)/code/tox.ini $(CURDIR)/code/util
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
	echo "Static checks OK"

	$(MAKE) type-check

type-check:
	cd $(CURDIR)/code/zato-common && $(MAKE) type-check
	cd $(CURDIR)/code/zato-server && $(MAKE) type-check
	echo "Type checks OK"

type-check-pubsub:
	cd $(CURDIR)/code/zato-server && $(MAKE) pyright-pubsub
	echo "Type checks OK"

mypy:
	cd $(CURDIR)/code/zato-common && $(MAKE) mypy
	cd $(CURDIR)/code/zato-server && $(MAKE) mypy
	echo "Mypy checks OK"

web-admin-tests:
	cd $(CURDIR)/code/zato-web-admin && make run-tests

scheduler-tests:
	cd $(CURDIR)/code/zato-scheduler && make run-tests

install-qa-reqs:
	$(CURDIR)/code/bin/pip install --upgrade -r $(CURDIR)/code/qa-requirements.txt
	$(CURDIR)/code/bin/pip install -U nose --use-feature=no-binary-enable-wheel-cache --no-binary :all:
	npx -y playwright install
	mkdir -p $(CURDIR)/code/eggs/requests/ || true
	cp -v $(CURDIR)/code/patches/requests/* $(CURDIR)/code/eggs/requests/

functional-tests:
	$(MAKE) web-admin-tests
	$(MAKE) common-tests
	$(MAKE) server-tests
	$(MAKE) cli-tests
	$(MAKE) scheduler-tests
	$(MAKE) cy-tests
	@if [ "$(ZATO_TEST_SSO)" = "true" ]; then $(MAKE) sso-tests; fi

run-tests:
	$(MAKE) install-qa-reqs
	$(CURDIR)/code/bin/playwright install
	$(MAKE) static-check
	$(MAKE) functional-tests
