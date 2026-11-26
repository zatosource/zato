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
#
# Each run of make resumes its goal after the previous run of the same goal failed or was interrupted. The Makefile
# exports the identifier of the run, Zato_Resume_Run_Id, and the state file of the goal, Zato_Resume_State_Path,
# which holds these entries:
#
#   run <run id>                      - the run of make that the entries below were last carried into
#   pending <pid>                     - a line that started and has not completed, so the run failed or was interrupted
#   done <run id> <stage id>          - a stage that completed
#   first <run id> <stage id> <test>  - the test that a pytest run failed first in or was interrupted in
#   failed <run id> <target>          - a target with a line that failed, which target_status.sh reports at its end
#
# The first line of a run of make keeps the done and first entries if the previous run left a pending line behind,
# unless RESTART is set, and drops them otherwise. A stage is either one pytest run, which the resume_first_failure
# plugin skips or resumes, or one line that runs cargo test or pyright, which this script skips.

Failures_Path=/tmp/zato-test-failures.txt
Failure_Marker='>>> ZATO TEST FAILURE'
Tail_Lines=80
Line_Max_Bytes=4000
Test_Lib_Dir="${0%/*}/python/zato-common/lib"

target="${1#--target=}"
shift

if [ -z "$target" ]; then
    exec /bin/bash "$@"
fi

line="${*: -1}"
log_path="/tmp/logs-$target.txt"
capture_path=''

# The state file of the goal is rewritten under a lock that the pytest plugin appends its entries under too
state_path="$Zato_Resume_State_Path"
lock_path="$state_path.lock"
mkdir -p "${state_path%/*}"

line_stage_id="line-$(printf '%s\n%s' "$target" "$line" | sha1sum | cut -d' ' -f1)"

if [[ "$line" =~ cargo\ (test|nextest)|pyright ]] && [[ "$line" != *pytest* ]]; then
    is_line_stage=1
else
    is_line_stage=''
fi

is_skipped=''

{
    flock 9

    state_run_id=''
    if [ -f "$state_path" ]; then
        read -r _ state_run_id < "$state_path"
    fi

    # The first line of this run of make decides whether the run resumes the previous one ..
    if [ "$state_run_id" != "$Zato_Resume_Run_Id" ]; then
        if [ -z "$RESTART" ] && [ -f "$state_path" ] && grep -q '^pending ' "$state_path"; then
            { echo "run $Zato_Resume_Run_Id"; grep -v -e '^run ' -e '^pending ' -e '^failed ' "$state_path"; } > "$state_path.tmp"
            echo ">>> Resuming from where the previous run of this goal stopped, RESTART=1 starts it from scratch"
        else
            echo "run $Zato_Resume_Run_Id" > "$state_path.tmp"
        fi
        mv "$state_path.tmp" "$state_path"
    fi

    # .. a line stage that completed in an earlier run is skipped ..
    if [ -n "$is_line_stage" ]; then
        done_run_id=$(awk -v id="$line_stage_id" '$1 == "done" && $3 == id { out = $2 } END { print out }' "$state_path")
        if [ -n "$done_run_id" ] && [ "$done_run_id" != "$Zato_Resume_Run_Id" ]; then
            is_skipped=1
        fi
    fi

    # .. and any other line is pending until it completes.
    if [ -z "$is_skipped" ]; then
        echo "pending $$" >> "$state_path"
    fi

} 9>"$lock_path"

if [ -n "$is_skipped" ]; then
    echo ">>> Skipping a stage of $target, which completed in the previous run"
    exit 0
fi

# The plugin tells the passes of a loop of this line apart by the Zato_Test_* variables that the line names
export Zato_Resume_Line="$line"

# Every pytest run of a test goal, or of a line that names pytest, loads the plugin that resumes it,
# which a line of a nested make inherits from the line of the make that started it.
if [ -z "${Zato_Resume_Pytest_Addopts+set}" ] && { [ -n "$Zato_Test_Goal" ] || [[ "$line" == *pytest* ]]; }; then
    export Zato_Resume_Pytest_Addopts="$PYTEST_ADDOPTS"
    export PYTEST_ADDOPTS="${PYTEST_ADDOPTS:+$PYTEST_ADDOPTS }-p resume_first_failure"
    export PYTHONPATH="$Test_Lib_Dir${PYTHONPATH:+:$PYTHONPATH}"
fi

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

    # A line that completed is no longer pending, and a line stage is recorded as done, while a line that failed
    # stays pending, as does one whose shell was interrupted, so that the next run resumes the goal.
    {
        flock 9
        grep -vx "pending $$" "$state_path" > "$state_path.tmp"
        if [ -n "$is_line_stage" ]; then
            echo "done $Zato_Resume_Run_Id $line_stage_id" >> "$state_path.tmp"
        fi
        mv "$state_path.tmp" "$state_path"
    } 9>"$lock_path"

    exit 0
fi

# The status line of a target reports the failures of its other lines, which are already recorded
if [[ "$line" == *target_status.sh* ]]; then
    exit "$status"
fi

# A failed line marks its target as failed, so that the status line of the target fails once its other lines ran
{
    flock 9
    echo "failed $Zato_Resume_Run_Id $target" >> "$state_path"
} 9>"$lock_path"

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
