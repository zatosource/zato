
.PHONY: build
MAKEFLAGS += --silent

cy-tests:
	cd $(CURDIR)/code/zato-cy && make run-tests

server-tests:
	cd $(CURDIR)/code/zato-server && make run-tests

run-tests:
	$(MAKE) cy-tests
	$(MAKE) server-tests
