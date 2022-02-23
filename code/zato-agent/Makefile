
.PHONY: static-check

PY_DIR=$(CURDIR)/../bin

pylint:
	echo Running pylint in zato-agent
	$(PY_DIR)/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-agent/src/zato/agent

static-check:
	echo "Running static checks in zato-agent"
	$(PY_DIR)/flake8 --version 1>&2
	$(PY_DIR)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

type-check:
	echo "Running type checks in zato-agent"
	$(PY_DIR)/pyright -p $(CURDIR)/../pyproject.toml .
