# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
from datetime import datetime, timezone
from logging import getLogger
from subprocess import CompletedProcess, PIPE, run, TimeoutExpired
from threading import Thread

# Zato
from zato.common.env_repo import Env_Repo, get_link_dir, write_json
from zato.common.github_app import get_git_auth_for_url, GitHubAppError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist, strnone, strstrdict

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

def _run_git(status:'Status', arguments:'strlist', cwd:'strnone'=None) -> 'CompletedProcess':
    """ Runs git with the App's token for an HTTPS address or the keys for an SSH one, and keeps what it printed.
    """
    try:
        auth = get_git_auth_for_url(get_link_dir(), status.url)
    except GitHubAppError as exception:
        raise RequestError(exception.message)

    command = ['git']
    command.extend(auth)
    command.extend(arguments)

    # The dashboard's own key is offered along with the user's, and neither git nor ssh may prompt for anything.
    env = dict(os.environ)
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GIT_SSH_COMMAND'] = f'ssh -o BatchMode=yes -i {_get_key_path()}'

    try:
        out = run(command, stdout=PIPE, stderr=PIPE, cwd=cwd, env=env, timeout=_Git_Timeout, text=True)
    except TimeoutExpired:
        raise RequestError(f'GitHub did not answer in {_Git_Timeout} seconds for {status.url}')
    except OSError as exception:
        raise RequestError(f'Git could not be run: {exception}')

    status.add_lines(out.stderr)

    return out

# ################################################################################################################################

def _list_branches(status:'Status') -> 'strstrdict':
    """ Runs git ls-remote and returns the branches with the commits they are at.
    """
    status.write(Env_Repo.State_Checking, f'Connecting to {status.url}')

    result = _run_git(status, ['ls-remote', '--heads', status.url])

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

def _get_checkout_dir() -> 'str':
    out = os.path.join(get_link_dir(), Env_Repo.Checkout)
    return out

# ################################################################################################################################

def _is_checkout_of(status:'Status', repo_dir:'str') -> 'bool':
    """ Returns whether the checkout is of the repository and branch the status is about.
    """
    if not os.path.isdir(os.path.join(repo_dir, '.git')):
        return False

    url = _run_git(status, ['remote', 'get-url', 'origin'], cwd=repo_dir)
    branch = _run_git(status, ['rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_dir)

    out = url.returncode == 0 and branch.returncode == 0 and url.stdout.strip() == status.url \
        and branch.stdout.strip() == status.branch

    return out

# ################################################################################################################################

def _clone(status:'Status') -> 'str':
    """ Clones the repository at its branch into the dashboard's own checkout, in place of whatever was there.
    """
    repo_dir = _get_checkout_dir()

    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir, ignore_errors=True)

    status.add_lines(f'Cloning {status.url} at {status.branch}')
    result = _run_git(status, ['clone', '--branch', status.branch, '--single-branch', status.url, repo_dir])

    if result.returncode != 0:
        shutil.rmtree(repo_dir, ignore_errors=True)
        raise RequestError(f'Clone of {status.url} at {status.branch} failed, exit code {result.returncode}')

    return repo_dir

# ################################################################################################################################

def _switch(status:'Status', branches:'strstrdict') -> 'None':
    """ Clones the repository at the branch and writes current.json with the repository, branch and commit.
    """
    commit = branches.get(status.branch)

    if not commit:
        raise RequestError(f'Branch {status.branch} not found in {status.url}')

    status.write(Env_Repo.State_Switching, f'Switching to {status.url} at {status.branch}')

    _ = _clone(status)

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

def _pull(status:'Status') -> 'None':
    """ Brings the dashboard's checkout up to date, or clones it if it is not there or is of something else.
    """
    repo_dir = _get_checkout_dir()

    status.write(Env_Repo.State_Pulling, f'Pulling {status.url} at {status.branch}')

    if _is_checkout_of(status, repo_dir):
        result = _run_git(status, ['pull', '--ff-only'], cwd=repo_dir)
        status.add_lines(result.stdout)

        if result.returncode != 0:
            raise RequestError(f'Pull of {status.url} failed, exit code {result.returncode}')
    else:
        _ = _clone(status)

    status.write(Env_Repo.State_Pulled, f'Pulled {status.url} at {status.branch}')

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
