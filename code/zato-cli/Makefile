
.PHONY: ruff test test-mcp

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-cli

Zato_Test_Python := $(Zato_Python_Dir)/py
include $(CURDIR)/../tests/check.mk

# The directory of the suites, which their modules import env_helper from
Zato_Enmasse_Test_Dir := $(CURDIR)/test/zato/enmasse_

test:
	$(Zato_Test_Failure_Reports_Env) $(Zato_Python_Dir)/py -m pytest $(Zato_Enmasse_Test_Dir) \
		-v -s -o pythonpath=$(Zato_Enmasse_Test_Dir) -o cache_dir=$(CURDIR)/../tests/.pytest_cache_cli \
		-W ignore::DeprecationWarning $(Zato_Test_Failure_Reports) $(Zato_Test_Resume) $(PYTEST_ARGS)

test-mcp:
	$(Zato_Test_Failure_Reports_Env) $(Zato_Python_Dir)/py -m pytest $(Zato_Enmasse_Test_Dir)/test_mcp_auth.py \
		-v -o pythonpath=$(Zato_Enmasse_Test_Dir) $(Zato_Test_Failure_Reports)

ruff:
	echo "Running ruff in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/ruff check $(CURDIR)/
