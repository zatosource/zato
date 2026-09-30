# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, timezone
from logging import getLogger
from subprocess import PIPE, run, TimeoutExpired
from threading import Thread

# Zato
from zato.common.env_repo import Env_Repo, write_json

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# In seconds
_Git_Timeout = 60

# How many lines of git's output the status keeps
_Max_Status_Lines = 40

# ################################################################################################################################
# ################################################################################################################################

class RequestError(Exception):
    def __init__(self, message:'str') -> 'None':
        super().__init__(message)
        self.message = message

# ################################################################################################################################
# ################################################################################################################################

class Status:
    """ Writes status.json in the link directory.
    """
    def __init__(self, action:'str', url:'str', branch:'str') -> 'None':

        self.action = action
        self.url    = url
        self.branch = branch
        self.lines:'strlist' = []

# ################################################################################################################################

    def add_lines(self, text:'str') -> 'None':

        for line in text.strip().splitlines():
            line = line.strip()
            if line:
                self.lines.append(line)

        del self.lines[:-_Max_Status_Lines]

# ################################################################################################################################

    def write(self, state:'str', message:'str') -> 'None':

        logger.info('Status %s - %s', state, message)

        data:'anydict' = {
            'action':  self.action,
            'url':     self.url,
            'branch':  self.branch,
            'state':   state,
            'message': message,
            'lines':   self.lines,
            'time':    datetime.now(timezone.utc).isoformat(),
        }

        write_json(Env_Repo.Status, data)

# ################################################################################################################################
# ################################################################################################################################

def _check_access(status:'Status') -> 'str':
    """ Runs git ls-remote for the branch and returns the commit it is at.
    """
    status.write(Env_Repo.State_Checking, f'Checking access to {status.url}')

    command = ['git', 'ls-remote', '--heads', status.url, status.branch]

    # Neither git nor ssh may prompt for anything.
    env = dict(os.environ)
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GIT_SSH_COMMAND'] = 'ssh -o BatchMode=yes'

    try:
        result = run(command, stdout=PIPE, stderr=PIPE, env=env, timeout=_Git_Timeout, text=True)
    except TimeoutExpired:
        raise RequestError(f'GitHub did not answer in {_Git_Timeout} seconds for {status.url}')
    except OSError as exception:
        raise RequestError(f'Git could not be run: {exception}')

    status.add_lines(result.stderr)

    if result.returncode != 0:
        raise RequestError(f'GitHub refused access to {status.url}, exit code {result.returncode}')

    stdout = result.stdout.strip()

    if not stdout:
        raise RequestError(f'Branch {status.branch} not found in {status.url}')

    status.add_lines(stdout)

    out = stdout.split()[0]
    return out

# ################################################################################################################################

def _switch(status:'Status', commit:'str') -> 'None':
    """ Writes current.json with the repository, branch and commit.
    """
    status.write(Env_Repo.State_Switching, f'Switching to {status.url} at {status.branch}')

    data:'anydict' = {
        'url':      status.url,
        'branch':   status.branch,
        'commit':   commit,
        'env_name': '',
        'time':     datetime.now(timezone.utc).isoformat(),
    }

    write_json(Env_Repo.Current, data)

    status.write(Env_Repo.State_Switched, f'Switched to {status.url} at {status.branch}')

# ################################################################################################################################

def _handle(action:'str', url:'str', branch:'str') -> 'None':

    status = Status(action, url, branch)

    try:
        commit = _check_access(status)

        if action == Env_Repo.Action_Switch:
            _switch(status, commit)
        else:
            status.write(Env_Repo.State_OK, f'Access to {url} at {branch} works')

    except RequestError as exception:
        status.write(Env_Repo.State_Error, exception.message)

    except Exception as exception:
        logger.warning('Request %s for %s at %s failed: %s', action, url, branch, exception)
        status.write(Env_Repo.State_Error, f'Request failed: {exception}')

# ################################################################################################################################

def handle_request(action:'str', url:'str', branch:'str') -> 'None':
    """ Handles the request in a thread that ends once the status is written.
    """
    thread = Thread(target=_handle, args=(action, url, branch), name='env-repo-local', daemon=True)
    thread.start()

# ################################################################################################################################
# ################################################################################################################################
