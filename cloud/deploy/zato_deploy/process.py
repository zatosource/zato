# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shlex
import subprocess
import time
from dataclasses import dataclass
from logging import getLogger

# Zato
from zato_deploy.common import clean_terminal_line, StageFailed, strlist, strnone, strstrdict
from zato_deploy.state import Progress

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CommandResult:
    exit_code: int
    stdout:    str
    stderr:    str

# ################################################################################################################################
# ################################################################################################################################

def _build_env(extra_env:'strstrdict | None') -> 'strstrdict':

    out = dict(os.environ)

    if extra_env:
        out.update(extra_env)

    return out

# ################################################################################################################################

def _log_output(label:'str', text:'str') -> 'None':

    text = text.rstrip()

    if text:
        logger.info('%s:\n%s', label, text)

# ################################################################################################################################

def run_command(
    command:'strlist',
    extra_env:'strstrdict | None'=None,
    cwd:'strnone'=None,
    timeout:'float | None'=None,
    ) -> 'CommandResult':
    """ Runs a command to completion and logs its command line, exit code, duration and all of its output.
    """
    env = _build_env(extra_env)
    command_line = shlex.join(command)

    logger.info('Running: %s', command_line)
    started = time.monotonic()

    try:
        completed = subprocess.run(command, capture_output=True, text=True, errors='replace', env=env, cwd=cwd, timeout=timeout)
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - started
        logger.error('Timed out after %.1fs: %s', elapsed, command_line)
        raise

    elapsed = time.monotonic() - started

    out = CommandResult()
    out.exit_code = completed.returncode
    out.stdout    = completed.stdout
    out.stderr    = completed.stderr

    logger.info('Exit code %d after %.1fs: %s', out.exit_code, elapsed, command_line)
    _log_output('stdout', out.stdout)
    _log_output('stderr', out.stderr)

    return out

# ################################################################################################################################

def run_logged(progress:'Progress', command:'strlist', extra_env:'strstrdict | None'=None, cwd:'strnone'=None) -> 'None':
    """ Runs a command with each line of its output going to the log, and raises StageFailed with its last line if it fails.
    """
    env = _build_env(extra_env)
    command_line = shlex.join(command)

    logger.info('Running: %s', command_line)
    started = time.monotonic()

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace', env=env, cwd=cwd)

    last_line = ''

    # Each line is logged the moment it appears ..
    if process.stdout:
        for line in process.stdout:
            line = clean_terminal_line(line)
            if line:
                progress.log(line)
                last_line = line

    exit_code = process.wait()
    elapsed = time.monotonic() - started

    logger.info('Exit code %d after %.1fs: %s', exit_code, elapsed, command_line)

    # .. and the last one usually says why the command failed, if it did.
    if exit_code != 0:
        if not last_line:
            last_line = f'{command[0]} exited with code {exit_code}'
        raise StageFailed(last_line)

# ################################################################################################################################
# ################################################################################################################################
