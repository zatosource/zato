# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import shlex

# Zato
from zato_deploy.common import Path, strlist, strstrdict
from zato_deploy.process import CommandResult, run_command

# ################################################################################################################################
# ################################################################################################################################

# The only shape of a private repository address that is accepted, an SSH one on GitHub.
_SSH_URL_Pattern = re.compile(r'^git@github\.com:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git$')

_Remote_Timeout = 120

# ################################################################################################################################
# ################################################################################################################################

def is_ssh_url(url:'str') -> 'bool':

    out = bool(_SSH_URL_Pattern.match(url))
    return out

# ################################################################################################################################

def get_ssh_command(is_verbose:'bool'=False) -> 'str':
    """ Returns the ssh command that git uses, with the deploy key and GitHub's own host keys and nothing else.
    """
    command = [
        'ssh',
        '-i', Path.Env_Repo_Key,
        '-o', f'UserKnownHostsFile={Path.Known_Hosts}',
        '-o', 'StrictHostKeyChecking=yes',
        '-o', 'IdentitiesOnly=yes',
        '-o', 'BatchMode=yes',
    ]

    if is_verbose:
        command.extend(['-o', 'LogLevel=VERBOSE'])

    out = shlex.join(command)
    return out

# ################################################################################################################################

def get_git_env(is_verbose:'bool'=False) -> 'strstrdict':

    out = {
        'GIT_SSH_COMMAND': get_ssh_command(is_verbose),
        'GIT_TERMINAL_PROMPT': '0',
    }

    return out

# ################################################################################################################################

def run_git(arguments:'strlist', cwd:'str | None'=None, is_verbose:'bool'=False) -> 'CommandResult':

    command = ['git']
    command.extend(arguments)

    out = run_command(command, get_git_env(is_verbose), cwd=cwd, timeout=_Remote_Timeout)
    return out

# ################################################################################################################################

def ensure_key(key_path:'str') -> 'None':
    """ Generates the deploy key if there is none yet, without a passphrase because nothing is there to type it.
    """
    if os.path.exists(key_path):
        return

    _ = run_command(['ssh-keygen', '-t', 'ed25519', '-N', '', '-C', 'zato-deploy', '-f', key_path])
    os.chmod(key_path, 0o600)

# ################################################################################################################################

def read_public_key(key_path:'str') -> 'str':

    result = run_command(['ssh-keygen', '-y', '-f', key_path])

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def get_head_commit(repo_dir:'str') -> 'str':

    result = run_git(['rev-parse', 'HEAD'], cwd=repo_dir)

    out = result.stdout.strip()
    return out

# ################################################################################################################################
# ################################################################################################################################
