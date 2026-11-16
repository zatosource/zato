# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The control files through which the exactly-once tests steer the relay service of a test server. The relay runs
# in the server and the tests run in the test process, and both reach the same directory, which the
# Zato_Test_Exactly_Once_Dir variable names.

# stdlib
import glob
import os
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strintdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The environment variable with the path of the control directory
Env_Dir = 'Zato_Test_Exactly_Once_Dir'

# The topics of the relay
Input_Topic  = 'exactly-once.input'
Output_Topic = 'exactly-once.output'

# The subdirectories of the control directory
_hold_dir_name = 'hold'
_held_dir_name = 'held'
_fail_dir_name = 'fail'

# The file of the invocations of the relay
_invocations_file_name = 'invocations.txt'

# How often a held invocation and a waiting test look at the control files, in seconds
_poll_seconds = 0.1

# ################################################################################################################################
# ################################################################################################################################

def _get_control_dir() -> 'str':
    out = os.environ[Env_Dir]
    return out

# ################################################################################################################################

def _get_path(*parts:'str') -> 'str':
    control_dir = _get_control_dir()

    out = os.path.join(control_dir, *parts)
    return out

# ################################################################################################################################

def create_control_dir(control_dir:'str') -> 'None':
    """ Creates the control directory with its subdirectories.
    """
    for name in (_hold_dir_name, _held_dir_name, _fail_dir_name):
        path = os.path.join(control_dir, name)
        os.makedirs(path, exist_ok=True)

# ################################################################################################################################
# ################################################################################################################################

def record_invocation(key:'str') -> 'None':
    """ Appends the key of one invocation of the relay to the invocation file.
    """
    path = _get_path(_invocations_file_name)

    with open(path, 'a') as invocations_file:
        _ = invocations_file.write(key + '\n')

# ################################################################################################################################

def claim_hold(key:'str') -> 'str':
    """ Claims the hold of a key for the invocation that calls it, which is the only invocation that the hold applies to,
    and returns the path that the invocation waits on, or an empty string if no hold was requested.
    """
    process_id = os.getpid()
    held_name = f'{key}.{process_id}'

    hold_path = _get_path(_hold_dir_name, key)
    held_path = _get_path(_held_dir_name, held_name)

    try:
        os.rename(hold_path, held_path)
    except FileNotFoundError:
        out = ''
    else:
        out = held_path

    return out

# ################################################################################################################################

def wait_while_exists(path:'str') -> 'None':
    """ Waits for as long as the file exists.
    """
    while os.path.exists(path):
        time.sleep(_poll_seconds)

# ################################################################################################################################

def claim_failure(key:'str') -> 'bool':
    """ Claims the failure of a key, which only the first invocation that claims it receives.
    """
    path = _get_path(_fail_dir_name, key)

    try:
        os.remove(path)
    except FileNotFoundError:
        out = False
    else:
        out = True

    return out

# ################################################################################################################################
# ################################################################################################################################

def hold(key:'str') -> 'None':
    """ Makes the next invocation of the relay for the key wait until the key is released.
    """
    path = _get_path(_hold_dir_name, key)

    with open(path, 'w'):
        pass

# ################################################################################################################################

def wait_until_held(key:'str', timeout:'float') -> 'None':
    """ Waits until an invocation of the relay holds the key.
    """
    pattern = _get_path(_held_dir_name, f'{key}.*')
    deadline = time.monotonic() + timeout

    while not glob.glob(pattern):
        if time.monotonic() > deadline:
            raise Exception(f'Key `{key}` not held within {timeout}s')
        time.sleep(_poll_seconds)

# ################################################################################################################################

def release(key:'str') -> 'None':
    """ Releases the invocation that holds the key, and a hold not claimed yet.
    """
    hold_path = _get_path(_hold_dir_name, key)
    held_pattern = _get_path(_held_dir_name, f'{key}.*')

    paths = glob.glob(held_pattern)
    paths.append(hold_path)

    for path in paths:
        if os.path.exists(path):
            os.remove(path)

# ################################################################################################################################

def fail_once(key:'str') -> 'None':
    """ Makes the next invocation of the relay for the key publish and then raise an exception.
    """
    path = _get_path(_fail_dir_name, key)

    with open(path, 'w'):
        pass

# ################################################################################################################################
# ################################################################################################################################

def read_invocations() -> 'strlist':
    """ Returns the key of each invocation of the relay, in the order of the invocations.
    """
    path = _get_path(_invocations_file_name)
    out:'strlist' = []

    if not os.path.exists(path):
        return out

    with open(path) as invocations_file:
        for line in invocations_file:
            key = line.strip()
            if key:
                out.append(key)

    return out

# ################################################################################################################################

def count_invocations(key:'str') -> 'int':
    """ Returns how many times the relay was invoked for the key.
    """
    out = 0

    for item in read_invocations():
        if item == key:
            out += 1

    return out

# ################################################################################################################################

def wait_for_invocations(keys:'strlist', min_count:'int', timeout:'float') -> 'None':
    """ Waits until the relay was invoked at least the given number of times for each of the keys.
    """
    deadline = time.monotonic() + timeout

    while True:
        counts:'strintdict' = {}

        for item in read_invocations():
            if item in counts:
                counts[item] += 1
            else:
                counts[item] = 1

        missing:'strlist' = []

        for key in keys:
            if key not in counts:
                missing.append(key)
            elif counts[key] < min_count:
                missing.append(key)

        if not missing:
            return

        if time.monotonic() > deadline:
            raise Exception(f'Keys not invoked {min_count} times within {timeout}s: {missing}')

        time.sleep(_poll_seconds)

# ################################################################################################################################
# ################################################################################################################################
