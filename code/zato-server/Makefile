
.PHONY: build
MAKEFLAGS += --silent

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-server

pubsub-tests:
	echo "Running pub/sub tests in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/pubsub/test_pubapi_rest.py -s
	$(Zato_Python_Dir)/py        $(CURDIR)/test/zato/pubsub/test_pubapi_services.py
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/pubsub/test_publish.py -s

wsx-tests:
	echo "Running WSX tests in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/wsx/test_*.py -s

kvdb-tests:
	echo "Running KVDB tests in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/kvdb/test_*.py -s

run-tests:
	echo "Running tests in $(Zato_Package_Name)"
	$(MAKE) pubsub-tests
	$(MAKE) wsx-tests
	$(MAKE) kvdb-tests
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/test_sio_*.py -s
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/file_transfer/test_*.py -s
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/apispec/test_*.py -s
	$(Zato_Python_Dir)/py        $(CURDIR)/test/zato/commands_/test_*.py
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/pattern/test_*.py -s
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/rest/test_*.py -s
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/server_rpc/test_*.py -s
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/stats/test_*.py -s

pylint:
	echo Running pylint in $(Zato_Package_Name)
	$(Zato_Python_Dir)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-server/src/zato/server

mypy-apispec:
	echo "Running mypy in $(Zato_Package_Name) / apispec"
	$(Zato_Python_Dir)/mypy --config-file=$(CURDIR)/../mypy.ini \
		$(CURDIR)/src/zato/server/apispec/

mypy-pubsub:
	echo "Running mypy in $(Zato_Package_Name) / pubsub"
	$(Zato_Python_Dir)/mypy --config-file=$(CURDIR)/../mypy.ini \
		$(CURDIR)/src/zato/server/pubsub/

pyright-apispec:
	$(Zato_Python_Dir)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/apispec/

pyright-pubsub:
	$(Zato_Python_Dir)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/*.py
	$(Zato_Python_Dir)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/core/*.py
	$(Zato_Python_Dir)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/pubsub/delivery/*.py
	$(Zato_Python_Dir)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/service/internal/pubsub/*.py
	$(Zato_Python_Dir)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/service/internal/pubsub/task/*.py
	$(Zato_Python_Dir)/pyright -p $(CURDIR)/../pyproject.toml $(CURDIR)/src/zato/server/service/internal/pubsub/task/delivery/*.py

mypy:
	$(MAKE) mypy-apispec
	$(MAKE) mypy-pubsub

pyright:
	$(MAKE) pyright-apispec
	$(MAKE) pyright-pubsub

type-check:
	echo "Running type checks ($(Zato_Package_Name))"
	$(MAKE) mypy
	$(MAKE) pyright

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	$(MAKE) flake8
	$(MAKE) type-check
