# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The control files through which the exactly-once tests steer the relay service of a test server, and the verification
# of what the relay committed. The relay runs in the server and the tests run in the test process, and both reach
# the same directory, which the Zato_Test_Exactly_Once_Dir variable names.

# stdlib
import glob
import os
import time
from dataclasses import dataclass

# gevent
from gevent.monkey import get_original

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.pubsub.sql.schema import delivery_table, message_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import strlist

    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# The variable that names the control directory
Env_Dir = 'Zato_Test_Exactly_Once_Dir'

# The topics of the relay
Input_Topic  = 'eo.input'
Output_Topic = 'eo.output'

# The subdirectories of the control directory
_hold_dir_name       = 'hold'
_held_dir_name       = 'held'
_fail_dir_name       = 'fail'
_write_hold_dir_name = 'write-hold'

# The file of the invocations of the relay
_invocations_file_name = 'invocations.txt'

# The files of the write lock that a relay invocation holds - the trigger names the key that takes the lock,
# the lock is held for as long as the active file exists, and the acquired file says that the lock is held.
_write_hold_trigger_suffix = '.trigger'
_write_hold_active_name    = 'active'
_write_hold_acquired_name  = 'acquired'

# How often a held invocation and a waiting test look at the control files, in seconds
_poll_seconds = 0.1

# How long the outputs remain unchanged before the delivery is considered settled, in seconds
_quiet_seconds = 2.0

# The sleep of the operating system, which a thread of the pool of the gevent hub blocks in
_native_sleep = get_original('time', 'sleep')

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
    for name in (_hold_dir_name, _held_dir_name, _fail_dir_name, _write_hold_dir_name):
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
    hold_path = _get_path(_hold_dir_name, key)
    held_path = _get_path(_held_dir_name, f'{key}.{os.getpid()}')

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

def claim_write_hold(key:'str') -> 'bool':
    """ Claims the write lock request of a key, which only the first invocation that claims it receives.
    """
    path = _get_path(_write_hold_dir_name, key + _write_hold_trigger_suffix)

    try:
        os.remove(path)
    except FileNotFoundError:
        out = False
    else:
        out = True

    return out

# ################################################################################################################################

def hold_write_lock() -> 'None':
    """ Runs in a thread of the pool under the write lock of the pub/sub database of the process
    and keeps the lock for as long as the active file exists.
    """
    active_path = _get_path(_write_hold_dir_name, _write_hold_active_name)
    acquired_path = _get_path(_write_hold_dir_name, _write_hold_acquired_name)

    with open(acquired_path, 'w'):
        pass

    while os.path.exists(active_path):
        _native_sleep(_poll_seconds)

    os.remove(acquired_path)

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

def arm_write_hold(key:'str') -> 'None':
    """ Makes the next invocation of the relay for the key take the write lock of the pub/sub database of its process,
    which every commit of that process waits for until the lock is released.
    """
    active_path = _get_path(_write_hold_dir_name, _write_hold_active_name)
    trigger_path = _get_path(_write_hold_dir_name, key + _write_hold_trigger_suffix)

    for path in (active_path, trigger_path):
        with open(path, 'w'):
            pass

# ################################################################################################################################

def wait_for_write_hold(timeout:'float') -> 'None':
    """ Waits until an invocation of the relay holds the write lock.
    """
    path = _get_path(_write_hold_dir_name, _write_hold_acquired_name)
    deadline = time.monotonic() + timeout

    while not os.path.exists(path):
        if time.monotonic() > deadline:
            raise Exception(f'Write lock not held within {timeout}s')
        time.sleep(_poll_seconds)

# ################################################################################################################################

def release_write_hold() -> 'None':
    """ Releases the write lock that an invocation of the relay holds.
    """
    path = _get_path(_write_hold_dir_name, _write_hold_active_name)

    if os.path.exists(path):
        os.remove(path)

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
        counts:'dict[str, int]' = {}

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

@dataclass(init=False)
class OutputCheck:
    """ What the relay committed for the keys of one test.
    """

    # The keys with no output row and the keys with more than one
    missing_keys: 'strlist'
    duplicated_keys: 'strlist'

    # The output rows of the test whose key was never published
    unexpected_keys: 'strlist'

    # The key of each output row of the test, in the order of the message IDs
    output_keys: 'strlist'

    # The delivery rows of the input topic that remain
    pending_count: 'int'

    @property
    def is_ok(self) -> 'bool':
        if self.missing_keys:
            return False

        if self.duplicated_keys:
            return False

        if self.unexpected_keys:
            return False

        if self.pending_count:
            return False

        out = True
        return out

    def __repr__(self) -> 'str':
        out = f'<OutputCheck missing:{self.missing_keys} duplicated:{self.duplicated_keys} ' \
            f'unexpected:{self.unexpected_keys} pending:{self.pending_count} outputs:{len(self.output_keys)}>'
        return out

# ################################################################################################################################

def check_outputs(engine:'Engine', keys:'strlist', prefix:'str') -> 'OutputCheck':
    """ Reads the output rows of the keys with the given prefix and the delivery rows of the input topic.
    """
    query = select(message_table.c.correl_id)
    query = query.where(message_table.c.topic_name == Output_Topic)
    query = query.where(message_table.c.correl_id.like(prefix + '%'))
    query = query.order_by(message_table.c.id)

    pending_query = select(func.count())
    pending_query = pending_query.select_from(delivery_table)
    pending_query = pending_query.where(delivery_table.c.topic_name == Input_Topic)

    with engine.connect() as connection:
        rows = connection.execute(query).fetchall()
        pending_count = connection.execute(pending_query).scalar_one()

    output_keys:'strlist' = []
    counts:'dict[str, int]' = {}

    for row in rows:
        output_keys.append(row.correl_id)

        if row.correl_id in counts:
            counts[row.correl_id] += 1
        else:
            counts[row.correl_id] = 1

    expected = set(keys)

    missing_keys:'strlist' = []
    duplicated_keys:'strlist' = []
    unexpected_keys:'strlist' = []

    for key in keys:
        if key not in counts:
            missing_keys.append(key)
        elif counts[key] > 1:
            duplicated_keys.append(key)

    for key in counts:
        if key not in expected:
            unexpected_keys.append(key)

    out = OutputCheck()
    out.missing_keys = missing_keys
    out.duplicated_keys = duplicated_keys
    out.unexpected_keys = unexpected_keys
    out.output_keys = output_keys
    out.pending_count = pending_count

    return out

# ################################################################################################################################

def wait_for_outputs(engine:'Engine', keys:'strlist', prefix:'str', timeout:'float') -> 'OutputCheck':
    """ Waits until no input delivery remains and every key has an output row, and then until the outputs
    remain unchanged for a while, which a commit still in flight would change, and returns the final check.
    """
    deadline = time.monotonic() + timeout

    while True:
        out = check_outputs(engine, keys, prefix)

        if not out.missing_keys:
            if not out.pending_count:
                break

        if time.monotonic() > deadline:
            return out

        time.sleep(_poll_seconds)

    while True:
        time.sleep(_quiet_seconds)

        latest = check_outputs(engine, keys, prefix)

        if latest.output_keys == out.output_keys:
            if latest.pending_count == out.pending_count:
                return latest

        if time.monotonic() > deadline:
            return latest

        out = latest

# ################################################################################################################################

def assert_exactly_once(check:'OutputCheck', keys:'strlist') -> 'None':
    """ Fails unless each key has exactly one output row, no other row exists, no input delivery remains
    and the output rows follow the order of publication.
    """
    assert check.is_ok, check
    assert check.output_keys == keys, check

# ################################################################################################################################
# ################################################################################################################################
