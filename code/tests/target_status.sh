#!/bin/bash

# The last recipe line of a target of the Zato Makefile whose test lines each run even after an earlier one failed.
# recipe_shell.sh records each failed line of a test run in the state file of the goal as an entry
# "failed <run id> <target>", and this script exits with an error when the current run of make has such an entry
# for the target, so that the target fails once all of its test lines have run.
#
# Invoked as: target_status.sh <target>

target="$1"

if grep -qx "failed $Zato_Resume_Run_Id $target" "$Zato_Resume_State_Path"; then
    echo ">>> One or more test lines of $target failed, each failure is recorded in /tmp/zato-test-failures.txt"
    exit 1
fi
