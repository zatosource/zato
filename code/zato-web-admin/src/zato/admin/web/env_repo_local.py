# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
from json import loads
from datetime import datetime, timezone
from logging import getLogger
from subprocess import CompletedProcess, PIPE, run, TimeoutExpired
from threading import Thread

# Zato
from zato.common.env_repo import Env_Repo, get_link_dir, parse_repo_name, read_status, write_json
from zato.common.github_app import get_git_auth_for_url, GitHubAppError, uninstall_app
from zato.common.repo_text import count_text, get_repo_label, summarize_changes

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, strlist, strnone, strstrdict

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

# Server functions the dashboard calls about checkouts, through zato.server.invoker
_Server_Invoker    = 'zato.server.invoker'
_Func_Get_Repo_Dir = 'get_env_repo_dir'
_Func_Deploy       = 'deploy_env_repo'

# The server tells where it keeps checkouts, once per dashboard process
_repo_dir = ''

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
    def __init__(self, action:'str', url:'str', branch:'str', client:'any_'=None) -> 'None':

        self.action = action
        self.url    = url
        self.branch = branch
        self.client = client
        self.label  = get_repo_label(url)
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

        self.lines.append(message)

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
    status.write(Env_Repo.State_Checking, f'Connecting to {status.label}')

    result = _run_git(status, ['ls-remote', '--heads', status.url])

    if result.returncode != 0:
        raise RequestError(f'GitHub refused access to {status.label}, exit code {result.returncode}')

    out:'strstrdict' = {}

    # Each line is a commit, a tab and refs/heads/<branch>.
    for line in result.stdout.splitlines():
        commit, _, ref = line.strip().partition('\t')
        if ref.startswith(_Heads_Prefix):
            out[ref[len(_Heads_Prefix):]] = commit

    status.branches = sorted(out)
    return out

# ################################################################################################################################

def _invoke(status:'Status', func_name:'str', request:'anydict') -> 'anydict':
    """ Calls a function of the server and returns what it returned, or raises RequestError.
    """
    if not status.client:
        raise RequestError('Server is not available')

    request = dict(request, func_name=func_name)

    try:
        response = status.client.invoke(_Server_Invoker, request)
    except Exception as exception:
        raise RequestError(f'Server could not be reached: {exception}')

    if not response.ok:
        raise RequestError(f'Server answered {func_name} with an error: {response.details}')

    data = response.data

    if isinstance(data, (str, bytes)):
        data = loads(data)

    out = dict(data)
    return out

# ################################################################################################################################

def _get_repo_dir(status:'Status') -> 'str':
    """ Returns the directory where the server keeps checkouts, which is <server dir>/repo.
    """
    global _repo_dir

    if not _repo_dir:
        response = _invoke(status, _Func_Get_Repo_Dir, {})
        _repo_dir = response['repo_dir']

    return _repo_dir

# ################################################################################################################################

def _get_checkout_dir(status:'Status') -> 'str':
    """ Returns where the repository is checked out, which is <server dir>/repo/<repository name>.
    """
    repo = parse_repo_name(status.url)

    if not repo:
        raise RequestError(f'Repository address is not valid: {status.url}')

    out = os.path.join(_get_repo_dir(status), repo.name)
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
    repo_dir = _get_checkout_dir(status)

    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir, ignore_errors=True)

    os.makedirs(os.path.dirname(repo_dir), exist_ok=True)

    status.add_lines(f'Cloning {status.label} at {status.branch} into {repo_dir}')
    result = _run_git(status, ['clone', '--branch', status.branch, '--single-branch', status.url, repo_dir])

    if result.returncode != 0:
        shutil.rmtree(repo_dir, ignore_errors=True)
        raise RequestError(f'Clone of {status.label} at {status.branch} failed, exit code {result.returncode}')

    return repo_dir

# ################################################################################################################################

def _write_current(status:'Status', commit:'str') -> 'None':
    """ Records in current.json what the dashboard's checkout is of.
    """
    data:'anydict' = {
        'url':      status.url,
        'branch':   status.branch,
        'commit':   commit,
        'env_name': '',
        'time':     datetime.now(timezone.utc).isoformat(),
    }

    write_json(Env_Repo.Current, data)

# ################################################################################################################################

def _get_head(status:'Status', repo_dir:'str') -> 'str':
    out = _run_git(status, ['rev-parse', 'HEAD'], cwd=repo_dir).stdout.strip()
    return out

# ################################################################################################################################

def _deploy(status:'Status', repo_dir:'str', files:'strlist', is_full:'bool') -> 'None':
    """ Has the server deploy the checkout - all of it after a clone or if the server does not know it yet, otherwise
    the files given - and tells how many services and enmasse objects that touched, if any.
    """
    response = _invoke(status, _Func_Deploy, {'path': repo_dir, 'files': files, 'is_full': is_full})

    services_new     = response.get('services_new') or 0
    services_updated = response.get('services_updated') or 0
    objects_created  = response.get('objects_created') or 0
    objects_updated  = response.get('objects_updated') or 0
    objects_deleted  = response.get('objects_deleted') or 0
    errors           = response.get('errors') or []

    parts:'strlist' = []

    if services_new:
        parts.append(count_text(services_new, 'new service'))

    if services_updated:
        parts.append(count_text(services_updated, 'updated service'))

    if objects_created:
        parts.append(count_text(objects_created, 'enmasse object created', 'enmasse objects created'))

    if objects_updated:
        parts.append(count_text(objects_updated, 'enmasse object updated', 'enmasse objects updated'))

    if objects_deleted:
        parts.append(count_text(objects_deleted, 'enmasse object deleted', 'enmasse objects deleted'))

    if parts:
        status.add_lines('Deployed ' + ', '.join(parts))

    for error in errors:
        status.add_lines(error)

    if errors:
        raise RequestError(f'Deployment of {status.label} failed, {count_text(len(errors), "file")} could not be deployed')

# ################################################################################################################################

def _pull(status:'Status') -> 'None':
    """ Brings the checkout up to date, or clones it if it is not there or is of something else, records it as what
    runs now and has the server deploy what changed. Nothing restarts.
    """
    repo_dir = _get_checkout_dir(status)

    status.write(Env_Repo.State_Pulling, f'Pulling {status.label} at {status.branch}')

    if not _is_checkout_of(status, repo_dir):
        _ = _clone(status)
        head = _get_head(status, repo_dir)
        _write_current(status, head)
        _deploy(status, repo_dir, [], True)
        status.write(Env_Repo.State_Pulled, f'Pulled {status.label} at {status.branch}, now at {head[:12]}')
        return

    before = _get_head(status, repo_dir)
    result = _run_git(status, ['pull', '--ff-only'], cwd=repo_dir)
    status.add_lines(result.stdout)

    if result.returncode != 0:
        raise RequestError(f'Pull of {status.label} failed, exit code {result.returncode}')

    after = _get_head(status, repo_dir)
    _write_current(status, after)

    if before == after:
        _deploy(status, repo_dir, [], False)
        status.write(Env_Repo.State_Pulled, f'{status.label} at {status.branch} is up to date')
        return

    changes = _run_git(status, ['diff', '--name-status', before, after], cwd=repo_dir)
    status.add_lines(summarize_changes(changes.stdout))

    files = _run_git(status, ['diff', '--name-only', before, after], cwd=repo_dir).stdout.split()
    _deploy(status, repo_dir, files, False)

    status.write(Env_Repo.State_Pulled, f'Pulled {status.label} at {status.branch}, now at {after[:12]}')

# ################################################################################################################################

def _disconnect(status:'Status') -> 'None':
    """ Takes the App's access away on GitHub, removes the checkout and current.json - nothing of the repository is left.
    """
    try:
        uninstall_app(get_link_dir())
    except GitHubAppError as exception:
        raise RequestError(exception.message)

    repo_dir = _get_checkout_dir(status)

    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir, ignore_errors=True)

    path = os.path.join(get_link_dir(), Env_Repo.Current)

    if os.path.exists(path):
        os.remove(path)

    status.write(Env_Repo.State_Disconnected, f'Disconnected from {status.label}')

# ################################################################################################################################

def _handle(action:'str', url:'str', branch:'str', client:'any_'=None) -> 'None':

    status = Status(action, url, branch, client)

    try:
        if action == Env_Repo.Action_Disconnect:
            _disconnect(status)
            return

        # Locally a switch is a pull, nothing runs from the checkout that would need a restart.
        if action in (Env_Repo.Action_Pull, Env_Repo.Action_Switch):
            _pull(status)
            return

        branches = _list_branches(status)

        if branches:
            status.write(Env_Repo.State_OK, f'Connected to {status.label}, {count_text(len(branches), "branch", "branches")}')
        else:
            status.write(Env_Repo.State_OK, f'Connected to {status.label}, the repository is empty')

    except RequestError as exception:
        status.write(Env_Repo.State_Error, exception.message)

    except Exception as exception:
        logger.warning('Request %s for %s at %s failed: %s', action, url, branch, exception)
        status.write(Env_Repo.State_Error, f'Request failed: {exception}')

# ################################################################################################################################

def handle_request(action:'str', url:'str', branch:'str', client:'any_'=None) -> 'None':
    """ Handles the request in a thread that ends once the status is written, the client is how the server is reached.
    """
    thread = Thread(target=_handle, args=(action, url, branch, client), name='env-repo-local', daemon=True)
    thread.start()

# ##############################################################################################################################

def handle_request_now(action:'str', url:'str', branch:'str') -> 'anydictnone':
    """ Handles the request here and now and returns the status it ended with.
    """
    _handle(action, url, branch)

    out = read_status()
    return out

# ################################################################################################################################
# ################################################################################################################################
