# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import sys
from datetime import datetime, timezone
from logging import getLogger

# Zato
from zato_deploy.common import anydict, Blueprint, Env_Repo_Action, Env_Repo_State, Link_File, load_env_repo_config, Path, \
    read_env_file, Restart_Reason, strlist, Systemd_Unit, write_env_file
from zato_deploy.git import is_repo_url, run_git
from zato_deploy.github_app import GitHubAppError, uninstall_app
from zato_deploy.repo_text import count_text, get_repo_label, summarize_changes
from zato_deploy.process import run_command
from zato_deploy.run_log import setup_logging

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Sync_Flag = '--sync'

_Request_Keys = {'action', 'env_repo_url', 'env_repo_branch'}
_Actions      = {Env_Repo_Action.Check, Env_Repo_Action.Switch, Env_Repo_Action.Disconnect, Env_Repo_Action.Pull}

# How many lines of git's output the status keeps for the dashboard.
_Max_Status_Lines = 40

_Heads_Prefix = 'refs/heads/'

# ################################################################################################################################
# ################################################################################################################################

class RequestError(Exception):
    def __init__(self, message:'str') -> 'None':
        super().__init__(message)
        self.message = message

# ################################################################################################################################
# ################################################################################################################################

class Status:
    """ What the dashboard reads about the request that is being handled.
    """
    def __init__(self, action:'str', url:'str', branch:'str') -> 'None':

        self.action = action
        self.url    = url
        self.branch = branch
        self.label  = get_repo_label(url)
        self.message = ''
        self.lines:'strlist' = []
        self.branches:'strlist' = []

# ################################################################################################################################

    def add_line(self, text:'str') -> 'None':

        logger.info('%s', text)
        self.lines.append(text)

        del self.lines[:-_Max_Status_Lines]

# ################################################################################################################################

    def write(self, state:'str', message:'str') -> 'None':

        logger.info('Status %s - %s', state, message)

        if self.message:
            self.lines.append(self.message)

        self.message = message

        data = {
            'action':   self.action,
            'url':      self.url,
            'branch':   self.branch,
            'state':    state,
            'message':  message,
            'lines':    self.lines,
            'branches': self.branches,
            'time':     datetime.now(timezone.utc).isoformat(),
        }

        path = os.path.join(Path.Link_Dir, Link_File.Status)
        temp_path = path + '.tmp'

        with open(temp_path, 'w') as output_file:
            json.dump(data, output_file, indent=2)

        os.replace(temp_path, path)

# ################################################################################################################################
# ################################################################################################################################

def _read_request(path:'str') -> 'anydict':

    with open(path) as input_file:
        text = input_file.read()

    logger.info('Request read from %s: %s', path, text.strip())

    try:
        out = json.loads(text)
    except ValueError as exception:
        raise RequestError(f'Request is not JSON: {exception}')

    if not isinstance(out, dict):
        raise RequestError('Request is not an object')

    keys = set(out)

    if keys != _Request_Keys:
        raise RequestError(f'Request has keys {sorted(keys)}, expected {sorted(_Request_Keys)}')

    for key in _Request_Keys:
        if not isinstance(out[key], str):
            raise RequestError(f'{key} is not a string')

    if out['action'] not in _Actions:
        raise RequestError(f'Unknown action: {out["action"]}')

    if not is_repo_url(out['env_repo_url']):
        raise RequestError('Repository address must look like https://github.com/owner/name.git')

    return out

# ################################################################################################################################

def _check_branch_name(branch:'str') -> 'None':

    if not branch:
        raise RequestError('Branch name is empty')

    result = run_command(['git', 'check-ref-format', '--branch', branch])

    if result.exit_code != 0:
        raise RequestError(f'Branch name is not valid: {branch}')

# ################################################################################################################################

def _add_output_lines(status:'Status', text:'str') -> 'None':

    for line in text.strip().splitlines():
        line = line.strip()
        if line:
            status.add_line(line)

# ################################################################################################################################

def _list_branches(status:'Status') -> 'None':
    """ Runs git ls-remote with the App's token or the deploy key and keeps the branches it lists.
    """
    status.write(Env_Repo_State.Checking, f'Connecting to {status.label}')

    result = run_git(['ls-remote', '--heads', status.url], is_verbose=True, url=status.url)

    _add_output_lines(status, result.stderr)

    if result.exit_code != 0:
        raise RequestError(f'GitHub refused access to {status.label}, exit code {result.exit_code}')

    # Each line is a commit, a tab and refs/heads/<branch>.
    for line in result.stdout.splitlines():
        _, _, ref = line.strip().partition('\t')
        if ref.startswith(_Heads_Prefix):
            status.branches.append(ref[len(_Heads_Prefix):])

    status.branches.sort()

# ################################################################################################################################

def _restart_deploy(reason:'str') -> 'None':

    os.makedirs(Path.Run_Dir, exist_ok=True)

    with open(Path.Restart_Reason, 'w') as output_file:
        _ = output_file.write(reason + '\n')

    _ = run_command(['systemctl', 'restart', '--no-block', Systemd_Unit.Deploy])

# ################################################################################################################################

def _switch(status:'Status') -> 'None':
    """ Points the configuration at the repository and restarts the deployment, which clones it and brings the page back.
    """
    values = {
        'env_repo_url':    status.url,
        'env_repo_branch': status.branch,
    }

    write_env_file(Path.Env_Repo_Config, values)
    status.add_line(f'Configuration written to {Path.Env_Repo_Config}')

    status.write(Env_Repo_State.Switching, f'Switching to {status.label} at {status.branch}, the environment restarts with it')

# ################################################################################################################################

def _disconnect(status:'Status') -> 'bool':
    """ Takes the App's access away on GitHub and clears the configured repository, so the deployment restarts
    with the public blueprint. Returns whether a restart is due, which it is not if the blueprint ran already.
    """
    try:
        uninstall_app(Path.Link_Dir)
    except GitHubAppError as exception:
        raise RequestError(exception.message)

    configured = read_env_file(Path.Env_Repo_Config)

    if not configured['env_repo_url']:
        status.write(Env_Repo_State.Disconnected, f'Disconnected from {status.label}')
        return False

    values = {
        'env_repo_url':    '',
        'env_repo_branch': '',
    }

    write_env_file(Path.Env_Repo_Config, values)
    status.add_line(f'Configuration cleared in {Path.Env_Repo_Config}')

    status.write(Env_Repo_State.Switching, f'Disconnected from {status.label}, the environment restarts with {get_repo_label(Blueprint.URL)}')
    return True

# ################################################################################################################################

def _pull(status:'Status') -> 'None':
    """ Brings the checkout up to date with GitHub, and nothing restarts - the running environment picks the files up
    the way it picks up any other change to them.
    """
    if not os.path.isdir(Path.Env_Repo_Link):
        raise RequestError(f'No checkout at {Path.Env_Repo_Link}')

    repo_dir = os.path.realpath(Path.Env_Repo_Link)

    status.write(Env_Repo_State.Pulling, f'Pulling {status.label} at {status.branch}')

    before = run_git(['rev-parse', 'HEAD'], cwd=repo_dir).stdout.strip()
    result = run_git(['pull', '--ff-only'], cwd=repo_dir, is_verbose=True, url=status.url)

    _add_output_lines(status, result.stderr)
    _add_output_lines(status, result.stdout)

    if result.exit_code != 0:
        raise RequestError(f'Pull of {status.label} failed, exit code {result.exit_code}')

    after = run_git(['rev-parse', 'HEAD'], cwd=repo_dir).stdout.strip()

    if before == after:
        status.write(Env_Repo_State.Pulled, f'{status.label} at {status.branch} is up to date')
        return

    changes = run_git(['diff', '--name-status', before, after], cwd=repo_dir)
    status.add_line(summarize_changes(changes.stdout))

    status.write(Env_Repo_State.Pulled, f'Pulled {status.label} at {status.branch}, now at {after[:12]}')

# ################################################################################################################################

def handle_request() -> 'None':
    """ Handles the request that the dashboard left in the shared directory, if there is one.
    """
    request_path = os.path.join(Path.Link_Dir, Link_File.Request)

    if not os.path.exists(request_path):
        logger.info('No request at %s', request_path)
        return

    status = Status('', '', '')
    is_switched = False

    try:
        request = _read_request(request_path)

        status = Status(request['action'], request['env_repo_url'], request['env_repo_branch'])

        if status.action == Env_Repo_Action.Disconnect:
            is_switched = _disconnect(status)

        elif status.action == Env_Repo_Action.Pull:
            _pull(status)

        elif status.action == Env_Repo_Action.Switch:
            _list_branches(status)
            _check_branch_name(status.branch)

            if status.branch not in status.branches:
                raise RequestError(f'Branch {status.branch} not found in {status.label}')

            _switch(status)
            is_switched = True

        else:
            _list_branches(status)
            if status.branches:
                status.write(Env_Repo_State.OK, f'Connected to {status.label}, {count_text(len(status.branches), "branch", "branches")}')
            else:
                status.write(Env_Repo_State.OK, f'Connected to {status.label}, the repository is empty')

    except RequestError as exception:
        status.write(Env_Repo_State.Error, exception.message)

    finally:
        if os.path.exists(request_path):
            os.remove(request_path)
            logger.info('Request removed from %s', request_path)

    # The deployment restarts only once the request is gone, so the path unit does not start this again with a stale one.
    if is_switched:
        _restart_deploy(Restart_Reason.Switch)

# ################################################################################################################################

def sync() -> 'None':
    """ Restarts the deployment if the configured branch has commits that the checkout does not.
    """
    if not os.path.exists(Path.Ready_Marker):
        logger.info('Sync skipped, %s does not exist', Path.Ready_Marker)
        return

    if not os.path.isdir(Path.Env_Repo_Link):
        logger.info('Sync skipped, %s is not a directory', Path.Env_Repo_Link)
        return

    config = load_env_repo_config(Path.Env_Repo_Config)
    repo_dir = os.path.realpath(Path.Env_Repo_Link)

    fetch = run_git(['fetch', 'origin', config.branch], cwd=repo_dir, url=config.url)

    if fetch.exit_code != 0:
        logger.info('Sync skipped, fetch of %s failed with exit code %d', config.branch, fetch.exit_code)
        return

    head       = run_git(['rev-parse', 'HEAD'], cwd=repo_dir).stdout.strip()
    fetch_head = run_git(['rev-parse', 'FETCH_HEAD'], cwd=repo_dir).stdout.strip()

    if head == fetch_head:
        logger.info('Sync found no new commits, HEAD is %s', head)
        return

    logger.info('Sync found new commits, HEAD is %s and FETCH_HEAD is %s, restarting the deployment', head, fetch_head)
    _restart_deploy(Restart_Reason.Sync)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':

    setup_logging(Path.Env_Repo_Log)

    if _Sync_Flag in sys.argv:
        sync()
    else:
        handle_request()

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
