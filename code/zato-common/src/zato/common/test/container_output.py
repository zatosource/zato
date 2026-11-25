# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re
import subprocess
import time
from threading import Thread, Timer

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from logging import Logger
    from zato.common.typing_ import any_, strlist, strstrdict

    # Dummy assignments to satisfy type checkers
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often a stopped container is checked for having been started again, in seconds
    Poll_Interval_Seconds = 1.0

    # The timestamp that docker logs --timestamps writes in front of each line of a container
    Timestamp_Pattern = re.compile(r'^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d+))?Z$')

    # The number of digits that the fraction of a second of a timestamp is padded to, for comparisons
    Fraction_Digits = 9

    # The state of a container that stopped
    Exited_Status = 'exited'

    # The format of a time that is compared with the timestamps of docker
    Since_Format = '%Y-%m-%dT%H:%M:%S.%fZ'

# ################################################################################################################################
# ################################################################################################################################

def _get_sort_key(timestamp:'str') -> 'str':
    """ Returns a key that orders the timestamps of docker logs, whose fractions of a second have no trailing zeros,
    or an empty string if the text is not a timestamp.
    """
    match = ModuleCtx.Timestamp_Pattern.match(timestamp)

    if not match:
        return ''

    seconds, fraction = match.groups()

    if fraction is None:
        fraction = ''

    fraction = fraction.ljust(ModuleCtx.Fraction_Digits, '0')

    out = f'{seconds}.{fraction}'
    return out

# ################################################################################################################################

def _get_container_id(name:'str') -> 'str':
    result = subprocess.run(['docker', 'inspect', '--format', '{{.Id}}', name], capture_output=True, text=True, check=True)
    out = result.stdout.strip()
    return out

# ################################################################################################################################

def _container_exists(container_id:'str') -> 'bool':
    result = subprocess.run(['docker', 'inspect', '--format', '{{.Id}}', container_id], capture_output=True, check=False)
    out = result.returncode == 0
    return out

# ################################################################################################################################

def has_exited_since(name:'str', since:'datetime') -> 'bool':
    """ Returns True if a container is stopped and it stopped at or after the given time, which is in UTC.
    """
    result = subprocess.run(
        ['docker', 'inspect', '--format', '{{.State.Status}} {{.State.FinishedAt}}', name],
        capture_output=True, text=True, check=True)

    status, finished_at = result.stdout.split()

    if status != ModuleCtx.Exited_Status:
        return False

    since_timestamp = since.strftime(ModuleCtx.Since_Format)

    out = _get_sort_key(finished_at) >= _get_sort_key(since_timestamp)
    return out

# ################################################################################################################################

def _follow_container(container_id:'str', label:'str', logger:'Logger') -> 'None':
    """ Writes the output of a container to the logger, across its stops and starts, until the container is removed.
    """
    since = ''
    last_key = ''

    while True:

        # Each pass starts where the previous one ended ..
        command:'strlist' = ['docker', 'logs', '--follow', '--timestamps']

        if since:
            command.extend(['--since', since])

        command.append(container_id)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
        stdout = cast_('any_', process.stdout)

        # .. writes each line that is newer than the last one written ..
        for line in stdout:
            timestamp, _, text = line.partition(' ')
            key = _get_sort_key(timestamp)

            # A line without a timestamp comes from the docker command, not from the container
            if not key:
                continue

            if key <= last_key:
                continue

            since = timestamp
            last_key = key

            text = text.rstrip()

            if text:
                logger.info('[%s] %s', label, text)

        _ = process.wait()

        # .. the output ends when the container stops, and the thread ends when the container is removed ..
        if not _container_exists(container_id):
            return

        # .. otherwise, the container may be started again.
        time.sleep(ModuleCtx.Poll_Interval_Seconds)

# ################################################################################################################################

def follow_container_output(name:'str', label:'str', logger:'Logger') -> 'None':
    """ Writes each line of the stdout and stderr of a container to the logger, with the label in front, in a background
    thread that follows the container across its stops and starts until the container is removed.
    """
    container_id = _get_container_id(name)

    thread = Thread(target=_follow_container, args=(container_id, label, logger), name=f'output-{name}', daemon=True)
    thread.start()

# ################################################################################################################################

def run_command_with_output(
    command:'strlist',
    label:'str',
    logger:'Logger',
    env:'strstrdict',
    timeout_seconds:'float',
    ) -> 'int':
    """ Runs a command, writes each line of its stdout and stderr to the logger as the command writes it,
    with the label in front, and returns the exit code. The command is killed once the timeout elapses.
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace', env=env)
    stdout = cast_('any_', process.stdout)

    timer = Timer(timeout_seconds, process.kill)
    timer.start()

    try:
        for line in stdout:
            line = line.rstrip()

            if line:
                logger.info('[%s] %s', label, line)

        out = process.wait()

    finally:
        timer.cancel()

    return out

# ################################################################################################################################
# ################################################################################################################################
