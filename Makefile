
.PHONY: build
MAKEFLAGS += --silent

cy-tests:
	cd $(CURDIR)/code/zato-cy && make run-tests

server-tests:
	cd $(CURDIR)/code/zato-server && make run-tests

run-tests:
	$(MAKE) cy-tests
	$(MAKE) server-tests
	$(MAKE) static-check

static-check:
	cd $(CURDIR)/code/zato-agent && $(MAKE) static-check
	cd $(CURDIR)/code/zato-broker && $(MAKE) static-check
	cd $(CURDIR)/code/zato-cli && $(MAKE) static-check
	cd $(CURDIR)/code/zato-client && $(MAKE) static-check
	cd $(CURDIR)/code/zato-common && $(MAKE) static-check
	cd $(CURDIR)/code/zato-cy && $(MAKE) static-check
	cd $(CURDIR)/code/zato-hl7 && $(MAKE) static-check
	cd $(CURDIR)/code/zato-lib && $(MAKE) static-check
	cd $(CURDIR)/code/zato-scheduler && $(MAKE) static-check
	cd $(CURDIR)/code/zato-server && $(MAKE) static-check
	cd $(CURDIR)/code/zato-sso && $(MAKE) static-check
	cd $(CURDIR)/code/zato-testing && $(MAKE) static-check
	cd $(CURDIR)/code/zato-web-admin && $(MAKE) static-check
	cd $(CURDIR)/code/zato-zmq && $(MAKE) static-check
	echo "Static checks OK"
