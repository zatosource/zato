.PHONY: zato-check

# The directory of this file, which every Makefile that includes it runs its tests through
Zato_Tests_Dir := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

# Each recipe line runs under bash with pipefail through recipe_shell.sh, which records a line that fails
# in /tmp/zato-test-failures.txt with its target. Make expands .SHELLFLAGS for each line, with the target in $@.
SHELL := $(Zato_Tests_Dir)/recipe_shell.sh
.SHELLFLAGS = --target=$@ -o pipefail -c

# The test targets that make was asked for, which tells recipe_shell.sh that the lines it runs belong to a test run
export Zato_Test_Goal := $(strip $(filter test%,$(MAKECMDGOALS)) $(Zato_Test_Goal))

# The identifier of this run of make and the state file of its goals, one per directory of a Makefile, which nested
# makes inherit. With them, recipe_shell.sh and the resume_first_failure pytest plugin resume every goal after a run
# that failed or was interrupted, skipping the stages that completed and starting each pytest run from the test
# that failed first or was interrupted. RESTART=1 starts the goal from scratch.
ifndef Zato_Resume_Run_Id
export Zato_Resume_Run_Id := $(shell date +%s%N)
export Zato_Resume_State_Path := \
	$(Zato_Tests_Dir)/.resume-state/$(notdir $(CURDIR))/$(subst $() ,+,$(or $(MAKECMDGOALS),default))
endif
export RESTART

Zato_Check_Script := $(Zato_Tests_Dir)/python/tutorial_endpoints_check.py
Zato_Saved_Default_Goal := $(.DEFAULT_GOAL)

# The pytest plugin that appends each failure to /tmp/zato-test-failures.txt the moment it occurs.
# The root conftest loads it for the suites under code/tests/python, every other pytest run is prefixed
# with Zato_Test_Failure_Reports_Env and given Zato_Test_Failure_Reports.
Zato_Test_Lib_Dir := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))python/zato-common/lib)
Zato_Test_Failure_Reports_Env := PYTHONPATH=$(Zato_Test_Lib_Dir)
Zato_Test_Failure_Reports := -p failure_reports

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
