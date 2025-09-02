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

perftest:
	cd $(CURDIR)/code/zato-common && $(MAKE) perftest USERS=$(word 2,$(MAKECMDGOALS)) TOPICS_MULTIPLIER=$(word 3,$(MAKECMDGOALS))

run-invokers:
	py code/zato-common/test/zato/common/pubsub/perftest/python_/__init__.py \
		--num-invokers $(if $(word 2,$(MAKECMDGOALS)),$(word 2,$(MAKECMDGOALS)),1) \
		--reqs-per-invoker $(if $(word 3,$(MAKECMDGOALS)),$(word 3,$(MAKECMDGOALS)),1) \
		--reqs-per-second $(if $(word 4,$(MAKECMDGOALS)),$(word 4,$(MAKECMDGOALS)),1.0)
