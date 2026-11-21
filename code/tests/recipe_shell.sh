#!/bin/bash

# The shell of each recipe line of the Zato Makefile. It runs the line under bash with pipefail and, when the line
# exits with a non-zero code, appends a failure record to the failures file that the failure_reports pytest plugin
# appends each failed test to, so that every failure of every target is recorded in one file, whether it comes from
# pytest, cargo, unittest, a compiler or any other command.
#
# Invoked as: recipe_shell.sh --target=<target> -o pipefail -c '<recipe line>'
# The target is empty for the $(shell ...) function of make, in which case the line runs with no record.
#
# A line that writes no log of its own, during a run of a test target named in Zato_Test_Goal, has its output
# captured as well, so that its record holds the end of that output.

Failures_Path=/tmp/zato-test-failures.txt
Failure_Marker='>>> ZATO TEST FAILURE'
Tail_Lines=80
Line_Max_Bytes=4000

target="${1#--target=}"
shift

if [ -z "$target" ]; then
    exec /bin/bash "$@"
fi

line="${*: -1}"
log_path="/tmp/logs-$target.txt"
capture_path=''

# The size of the failures file before the line runs tells whether anything the line ran has already recorded its failure
if [ -f "$Failures_Path" ]; then
    size_before=$(stat -c %s "$Failures_Path")
else
    size_before=0
fi

# A line that appends to the log of its target is recorded with the end of that log ..
if [[ "$line" == *"$log_path"* ]] || [ -z "$Zato_Test_Goal" ]; then
    /bin/bash "$@"
    status=$?

# .. while the output of any other line of a test run is captured for its record.
else
    capture_path=$(mktemp /tmp/zato-recipe-line.XXXXXX)
    /bin/bash "$@" 2>&1 | tee "$capture_path"
    status=${PIPESTATUS[0]}
fi

if [ "$status" -eq 0 ]; then
    if [ -n "$capture_path" ]; then
        rm -f "$capture_path"
    fi
    exit 0
fi

if [ -f "$Failures_Path" ]; then
    size_after=$(stat -c %s "$Failures_Path")
else
    size_after=0
fi

timestamp=$(date '+%Y-%m-%d %H:%M:%S')

{
    echo
    echo "$Failure_Marker $timestamp target $target exited with code $status"

    # A failure that a test, or a nested make, recorded during this line is already in the file with its details ..
    if [ "$size_after" -gt "$size_before" ]; then
        echo "The failure recorded above is the cause."

    # .. while any other failure is recorded with the line that failed and the end of its output.
    else
        echo "Recipe line:"
        echo "$line" | head -c "$Line_Max_Bytes"
        echo

        if [ -n "$capture_path" ]; then
            echo "Last $Tail_Lines lines of the output of the line:"
            tail -n "$Tail_Lines" "$capture_path"

        elif [ -f "$log_path" ]; then
            echo "Last $Tail_Lines lines of $log_path:"
            tail -n "$Tail_Lines" "$log_path"

        else
            echo "The output of the line is on the console only."
        fi
    fi

    echo
} >> "$Failures_Path"

if [ -n "$capture_path" ]; then
    rm -f "$capture_path"
fi

exit "$status"
