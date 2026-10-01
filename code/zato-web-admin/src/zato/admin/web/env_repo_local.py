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
from zato.common.env_repo import Env_Repo, get_link_dir, write_json
from zato.common.github_app import get_git_auth_for_url, GitHubAppError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# In seconds
_Git_Timeout = 60

# How many lines of git's output the status keeps
_Max_Status_Lines = 40

_Heads_Prefix = 'refs/heads/'

# The environment variables that name the project directory, the first one found is the one used.
_Project_Root_Keys = ('Zato_Project_Root', 'Zato_Hot_Deploy_Dir', 'ZATO_HOT_DEPLOY_DIR')

# ################################################################################################################################
# ################################################################################################################################

def _get_key_path() -> 'str':
    out = os.path.join(get_link_dir(), Env_Repo.Private_Key)
    return out

# ################################################################################################################################

def ensure_key() -> 'None':
    """ Creates the dashboard's own deploy key pair in the link directory unless it is there already.
    """
    path = _get_key_path()

    if os.path.exists(path):
        return

    os.makedirs(os.path.dirname(path), exist_ok=True)

    command = ['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-C', Env_Repo.Key_Comment, '-f', path]

    try:
        result = run(command, stdout=PIPE, stderr=PIPE, timeout=_Git_Timeout, text=True)
    except (OSError, TimeoutExpired) as exception:
        logger.warning('Deploy key not created at %s: %s', path, exception)
        return

    if result.returncode != 0:
        logger.warning('Deploy key not created at %s, exit code %d: %s', path, result.returncode, result.stderr.strip())
        return

    logger.info('Deploy key created at %s', path)

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
        self.branches:'strlist' = []

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
            'state':    state,
            'message':  message,
            'lines':    self.lines,
            'branches': self.branches,
            'time':     datetime.now(timezone.utc).isoformat(),
        }

        write_json(Env_Repo.Status, data)

# ################################################################################################################################
# ################################################################################################################################

def _list_branches(status:'Status') -> 'strstrdict':
    """ Runs git ls-remote and returns the branches with the commits they are at.
    """
    status.write(Env_Repo.State_Checking, f'Connecting to {status.url}')

    # An HTTPS address is read with the App's token, an SSH one with the deploy key.
    try:
        auth = get_git_auth_for_url(get_link_dir(), status.url)
    except GitHubAppError as exception:
        raise RequestError(exception.message)

    command = ['git']
    command.extend(auth)
    command.extend(['ls-remote', '--heads', status.url])

    # The dashboard's own key is offered along with the user's, and neither git nor ssh may prompt for anything.
    env = dict(os.environ)
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GIT_SSH_COMMAND'] = f'ssh -o BatchMode=yes -i {_get_key_path()}'

    try:
        result = run(command, stdout=PIPE, stderr=PIPE, env=env, timeout=_Git_Timeout, text=True)
    except TimeoutExpired:
        raise RequestError(f'GitHub did not answer in {_Git_Timeout} seconds for {status.url}')
    except OSError as exception:
        raise RequestError(f'Git could not be run: {exception}')

    status.add_lines(result.stderr)

    if result.returncode != 0:
        raise RequestError(f'GitHub refused access to {status.url}, exit code {result.returncode}')

    out:'strstrdict' = {}

    # Each line is a commit, a tab and refs/heads/<branch>.
    for line in result.stdout.splitlines():
        commit, _, ref = line.strip().partition('\t')
        if ref.startswith(_Heads_Prefix):
            out[ref[len(_Heads_Prefix):]] = commit

    status.branches = sorted(out)
    return out

# ################################################################################################################################

def _switch(status:'Status', branches:'strstrdict') -> 'None':
    """ Writes current.json with the repository, branch and commit.
    """
    commit = branches.get(status.branch)

    if not commit:
        raise RequestError(f'Branch {status.branch} not found in {status.url}')

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

def _get_checkout_dir() -> 'str':
    """ Returns the git checkout that the project directory this dashboard was started with is in.
    """
    project_root = ''

    for key in _Project_Root_Keys:
        value = os.environ.get(key, '')
        if value:
            project_root = value.split(':')[0].strip()
            break

    if not project_root:
        raise RequestError(f'No project directory is configured, set {_Project_Root_Keys[0]}')

    if not os.path.isdir(project_root):
        raise RequestError(f'Project directory {project_root} does not exist')

    command = ['git', 'rev-parse', '--show-toplevel']

    try:
        result = run(command, stdout=PIPE, stderr=PIPE, cwd=project_root, timeout=_Git_Timeout, text=True)
    except (OSError, TimeoutExpired) as exception:
        raise RequestError(f'Git could not be run in {project_root}: {exception}')

    if result.returncode != 0:
        raise RequestError(f'Project directory {project_root} is not in a git checkout')

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def _pull(status:'Status') -> 'None':
    """ Runs git pull in the checkout the project is in, with the user's own keys or the App's token.
    """
    repo_dir = _get_checkout_dir()

    status.write(Env_Repo.State_Pulling, f'Pulling {status.url} in {repo_dir}')

    try:
        auth = get_git_auth_for_url(get_link_dir(), status.url)
    except GitHubAppError as exception:
        raise RequestError(exception.message)

    command = ['git']
    command.extend(auth)
    command.extend(['pull', '--ff-only'])

    env = dict(os.environ)
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GIT_SSH_COMMAND'] = f'ssh -o BatchMode=yes -i {_get_key_path()}'

    try:
        result = run(command, stdout=PIPE, stderr=PIPE, cwd=repo_dir, env=env, timeout=_Git_Timeout, text=True)
    except TimeoutExpired:
        raise RequestError(f'GitHub did not answer in {_Git_Timeout} seconds for {status.url}')
    except OSError as exception:
        raise RequestError(f'Git could not be run: {exception}')

    status.add_lines(result.stderr)
    status.add_lines(result.stdout)

    if result.returncode != 0:
        raise RequestError(f'Pull of {status.url} failed, exit code {result.returncode}')

    status.write(Env_Repo.State_Pulled, f'Pulled {status.url} in {repo_dir}')

# ################################################################################################################################

def _disconnect(status:'Status') -> 'None':
    """ Removes current.json, which is all that ties this dashboard to the repository.
    """
    path = os.path.join(get_link_dir(), Env_Repo.Current)

    if os.path.exists(path):
        os.remove(path)

    status.write(Env_Repo.State_Disconnected, f'Disconnected from {status.url}')

# ################################################################################################################################

def _handle(action:'str', url:'str', branch:'str') -> 'None':

    status = Status(action, url, branch)

    try:
        if action == Env_Repo.Action_Disconnect:
            _disconnect(status)
            return

        if action == Env_Repo.Action_Pull:
            _pull(status)
            return

        branches = _list_branches(status)

        if action == Env_Repo.Action_Switch:
            _switch(status, branches)
        elif branches:
            status.write(Env_Repo.State_OK, f'Connected to {url}')
        else:
            status.write(Env_Repo.State_OK, f'Connected to {url}, the repository is empty')

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
