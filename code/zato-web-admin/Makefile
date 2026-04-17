
.PHONY: build
MAKEFLAGS += --silent

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-web-admin

test:
	echo "Running access checks in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/admin/access/test_login_logout.py
	$(Zato_Python_Dir)/py $(CURDIR)/test/zato/admin/access/test_index.py

ruff:
	echo "Running ruff in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/ruff check $(CURDIR)/
