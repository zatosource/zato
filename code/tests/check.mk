.PHONY: zato-check

Zato_Check_Script := $(dir $(lastword $(MAKEFILE_LIST)))python/tutorial_endpoints_check.py
Zato_Saved_Default_Goal := $(.DEFAULT_GOAL)

# The pytest plugin that appends each failure to /tmp/zato-test-failures.txt the moment it occurs.
# The root conftest loads it for the suites under code/tests/python, every other pytest run is prefixed
# with Zato_Test_Failure_Reports_Env and given Zato_Test_Failure_Reports.
Zato_Test_Lib_Dir := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))python/zato-common/lib)
Zato_Test_Failure_Reports_Env := PYTHONPATH=$(Zato_Test_Lib_Dir)
Zato_Test_Failure_Reports := -p failure_reports

# The pytest plugin that runs every test of a suite and starts the next run of the suite from the test that failed first,
# or from the test that was running when the run was interrupted, and from the first test under RESTART=1.
# The plugin is in the same directory as the plugin of the failure reports, so the run is prefixed
# with Zato_Test_Failure_Reports_Env, and it stores the test in the cache directory of the suite.
Zato_Test_Resume = -p resume_first_failure $(if $(RESTART),--resume-reset,)

zato-check:
	$(Zato_Test_Python) $(Zato_Check_Script)

.DEFAULT_GOAL := $(Zato_Saved_Default_Goal)

ifneq ($(filter test%,$(MAKECMDGOALS)),)
ifndef Zato_Check_Done
export Zato_Check_Done := 1
Zato_Check_Status := $(shell $(Zato_Test_Python) $(Zato_Check_Script) 1>&2 && echo ok)
ifneq ($(Zato_Check_Status),ok)
$(warning zato-check failed)
endif
endif
endif
