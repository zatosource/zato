
.PHONY: build ruff
MAKEFLAGS += --silent

Zato_Python_Dir=$(CURDIR)/../bin
Zato_Package_Name=zato-web-admin

Zato_Test_Python := $(Zato_Python_Dir)/py
include $(CURDIR)/../tests/check.mk

ruff:
	echo "Running ruff in $(Zato_Package_Name)"
	$(Zato_Python_Dir)/ruff check $(CURDIR)/
