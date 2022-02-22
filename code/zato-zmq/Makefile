
.PHONY: static-check

PY_DIR=$(CURDIR)/../bin

pylint:
	echo Running pylint in zato-zmq
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-zmq/src/zato/zmq_

static-check:
	echo "Running static checks in zato-zmq"
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
