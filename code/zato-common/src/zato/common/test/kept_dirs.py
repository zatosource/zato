# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from shutil import rmtree

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strintdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variables in which the failure_reports pytest plugin keeps the number of failures of the session
    # and the path of the file that it appends each failure to
    Env_Failure_Count = 'Zato_Test_Failure_Count'
    Env_Failures_Path = 'Zato_Test_Failures_Path'

    # The number of failures when the plugin is not loaded or no test has failed yet
    No_Failures = 0

    # The line that names each directory kept for inspection, in the output of the session
    Kept_Marker = '>>> ZATO TEST DIRECTORY KEPT'

# ################################################################################################################################
# ################################################################################################################################

# The number of failures of the session at the time each test directory was created
_failure_count_at_creation:'strintdict' = {}

# ################################################################################################################################
# ################################################################################################################################

def get_failure_count() -> 'int':
    """ Returns the number of tests that have failed in the session so far.
    """
    value = os.environ.get(ModuleCtx.Env_Failure_Count)

    if value is None:
        out = ModuleCtx.No_Failures
    else:
        out = int(value)

    return out

# ################################################################################################################################

def make_test_dir(prefix:'str') -> 'str':
    """ Creates a temporary directory for the environment of a test and records the number of failures at that time.
    """
    out = tempfile.mkdtemp(prefix=prefix)
    _failure_count_at_creation[out] = get_failure_count()

    return out

# ################################################################################################################################

def keep_test_dir(path:'str', reason:'str') -> 'None':
    """ Leaves a test directory in place for inspection and names it in the output of the session
    and, when the failure_reports plugin is loaded, in its failures file.
    """
    _ = _failure_count_at_creation.pop(path, None)

    text = f'\n{ModuleCtx.Kept_Marker} {path} - {reason}\n'
    print(text, file=sys.stderr, flush=True)

    failures_path = os.environ.get(ModuleCtx.Env_Failures_Path)

    if failures_path is not None:
        with open(failures_path, 'a') as failures_file:
            _ = failures_file.write(text)

# ################################################################################################################################

def remove_test_dir(path:'str') -> 'None':
    """ Removes a test directory, unless a test failed after it was created, in which case the directory,
    with the logs and the configuration of the environment, is kept for inspection.
    """
    failure_count = get_failure_count()

    if failure_count > _failure_count_at_creation.pop(path):
        keep_test_dir(path, 'a test failed while the directory was in use')
    else:
        rmtree(path, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
