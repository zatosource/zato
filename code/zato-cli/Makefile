
.PHONY: ruff test test-mcp

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-cli

Zato_Test_Python := $(Zato_Python_Dir)/py
include $(CURDIR)/../tests/check.mk

test:
	$(Zato_Python_Dir)/py -m unittest discover -s $(CURDIR)/test/zato/enmasse_ -p 'test_*.py' -v

test-mcp:
	$(Zato_Python_Dir)/py -m pytest $(CURDIR)/test/zato/enmasse_/test_mcp_auth.py -v

ruff:
	echo "Running ruff in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/ruff check $(CURDIR)/
