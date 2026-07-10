.PHONY: zato-check

Zato_Check_Script := $(dir $(lastword $(MAKEFILE_LIST)))python/tutorial_endpoints_check.py
Zato_Saved_Default_Goal := $(.DEFAULT_GOAL)

zato-check:
	$(Zato_Test_Python) $(Zato_Check_Script)

.DEFAULT_GOAL := $(Zato_Saved_Default_Goal)

ifneq ($(filter test%,$(MAKECMDGOALS)),)
ifndef Zato_Check_Done
export Zato_Check_Done := 1
Zato_Check_Status := $(shell $(Zato_Test_Python) $(Zato_Check_Script) 1>&2 && echo ok)
ifneq ($(Zato_Check_Status),ok)
$(error zato-check failed)
endif
endif
endif
