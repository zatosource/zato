Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-common

rules-perf-tests:
	cd $(CURDIR) && PYTHONPATH=$(CURDIR)/.. python test/zato/common/rules/test_perf.py

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8

run-tests:
	$(MAKE) pubsub-tests
	$(Zato_Python_Dir)/pytest test/zato/common \
		-v \
		-W ignore::DeprecationWarning \
		-W ignore::gevent.monkey.MonkeyPatchWarning \
		--ignore=test/zato/common/matcher \
		--ignore=test/zato/common/pubsub

pubsub-tests:
	zato enmasse ~/env/qs-1/server1 --import --input $(CURDIR)/src/zato/common/pubsub/server/config.yaml --verbose
	$(Zato_Python_Dir)/pytest test/zato/common/pubsub/live \
		-v -s \
		--log-cli-level=INFO \
		--log-cli-format='%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s' \
		--log-cli-date-format='%Y-%m-%d %H:%M:%S,%f' \
		--log-disable=faker \
		-W ignore::DeprecationWarning \
		-W ignore::gevent.monkey.MonkeyPatchWarning
	$(Zato_Python_Dir)/pytest test/zato/common/pubsub/backend -v -W ignore::DeprecationWarning -W ignore::gevent.monkey.MonkeyPatchWarning
	$(Zato_Python_Dir)/pytest test/zato/common/pubsub/rest_server -v -W ignore::DeprecationWarning -W ignore::gevent.monkey.MonkeyPatchWarning
	$(Zato_Python_Dir)/pytest test/zato/common/matcher -v -W ignore::DeprecationWarning -W ignore::gevent.monkey.MonkeyPatchWarning
