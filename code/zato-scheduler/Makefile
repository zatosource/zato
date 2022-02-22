
.PHONY: build
MAKEFLAGS += --silent

PY_DIR=$(CURDIR)/../bin

run-tests:
	echo "Running unit-tests in zato-scheduler"
	$(PY_DIR)/nosetests $(CURDIR)/test/zato/test_*.py -s

pylint:
	echo Running pylint in zato-scheduler
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-scheduler/src/zato/scheduler

static-check:
	echo "Running static checks in zato-scheduler"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
