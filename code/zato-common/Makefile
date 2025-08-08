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
	$(Zato_Python_Dir)/pytest test/zato/common -v -W ignore::DeprecationWarning -W ignore::gevent.monkey.MonkeyPatchWarning

pubsub-tests:
	$(Zato_Python_Dir)/pytest test/zato/common/pubsub -v -W ignore::DeprecationWarning -W ignore::gevent.monkey.MonkeyPatchWarning
	$(Zato_Python_Dir)/pytest test/zato/common/matcher -v -W ignore::DeprecationWarning -W ignore::gevent.monkey.MonkeyPatchWarning
