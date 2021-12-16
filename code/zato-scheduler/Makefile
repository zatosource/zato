
.PHONY: static-check

pylint:
	echo Running pylint in zato-scheduler
	$(CURDIR)/../bin/pylint --verbose \
		--rcfile $(CURDIR)/../pylint.ini \
				 $(CURDIR)/../zato-scheduler/src/zato/scheduler

static-check:
	echo "Running static checks in zato-scheduler"
	$(CURDIR)/../bin/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/
