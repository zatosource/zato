
.PHONY: build
MAKEFLAGS += --silent

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-web-admin

run-tests:
	echo "Running access checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/admin/access/test_login_logout.py -s --nologcapture
	$(Zato_Python_Dir)/pytest $(CURDIR)/test/zato/admin/access/test_index.py -s --nologcapture
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/admin/playwright_/test_*.py -s --nologcapture

flake8:
	echo "Running flake8 checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/flake8 --config=$(CURDIR)/../tox.ini $(CURDIR)/

static-check:
	echo "Running static checks in $(Zato_Package_Name)"
	$(MAKE) flake8
