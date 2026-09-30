# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
from json import dumps, loads
from logging import getLogger

# Zato
from zato.common.typing_ import anydict, anydictnone, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Env_Repo:
    """ The directory that the host shares with the container, and the files in it.
    """
    Host_Link_Dir  = '/opt/zato/host-link'
    Local_Dir_Name = 'env-repo'
    Public_Key     = 'id_ed25519.pub'
    Request        = 'request.json'
    Status         = 'status.json'
    Current        = 'current.json'

    Action_Check  = 'check'
    Action_Switch = 'switch'

    State_Checking  = 'checking'
    State_OK        = 'ok'
    State_Switching = 'switching'
    State_Switched  = 'switched'
    State_Error     = 'error'

    Blueprint_Owner = 'zatosource'
    Blueprint_Name  = 'zato-project-blueprint'

    # The name of the repository created from the template
    New_Repo_Name = 'zato-environment'

    New_Repo_URL   = 'https://github.com/new?template_owner={owner}&template_name={name}&name={new_name}&visibility=private'
    Repo_SSH_URL   = 'git@github.com:{owner}/{name}.git'
    Repo_HTTPS_URL = 'https://github.com/{owner}/{name}'

# ################################################################################################################################
# ################################################################################################################################

# What a repository address may look like - a browser address, an SSH one or owner/name alone.
_Repo_Name = r'(?P<owner>[A-Za-z0-9_.-]+)/(?P<name>[A-Za-z0-9_.-]+?)'

_Repo_Patterns = [
    re.compile(r'^(?:https?://)?(?:www\.)?github\.com/' + _Repo_Name + r'(?:\.git)?(?:[/?#].*)?$'),
    re.compile(r'^(?:ssh://)?git@github\.com[:/]' + _Repo_Name + r'(?:\.git)?/?$'),
    re.compile(r'^' + _Repo_Name + r'(?:\.git)?$'),
]

# ################################################################################################################################
# ################################################################################################################################

class Repo_Name:
    """ The owner and name of a repository on GitHub, and the addresses built from them.
    """
    def __init__(self, owner:'str', name:'str') -> 'None':
        self.owner = owner
        self.name  = name

    @property
    def full_name(self) -> 'str':
        out = f'{self.owner}/{self.name}'
        return out

    @property
    def ssh_url(self) -> 'str':
        out = Env_Repo.Repo_SSH_URL.format(owner=self.owner, name=self.name)
        return out

    @property
    def https_url(self) -> 'str':
        out = Env_Repo.Repo_HTTPS_URL.format(owner=self.owner, name=self.name)
        return out

# ################################################################################################################################

def parse_repo_name(text:'str') -> 'Repo_Name | None':
    """ Returns the owner and name from any of the accepted address shapes, or None if the text is not one of them.
    """
    text = text.strip()

    for pattern in _Repo_Patterns:
        match = pattern.match(text)
        if match:
            out = Repo_Name(match.group('owner'), match.group('name'))
            return out

    return None

# ################################################################################################################################

def get_new_repo_url() -> 'str':

    out = Env_Repo.New_Repo_URL.format(
        owner=Env_Repo.Blueprint_Owner,
        name=Env_Repo.Blueprint_Name,
        new_name=Env_Repo.New_Repo_Name,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

# The link directory when there is no host, set by the dashboard
_local_dir = ''

# ################################################################################################################################

def set_local_dir(path:'str') -> 'None':
    global _local_dir
    _local_dir = path

# ################################################################################################################################

def is_host_mode() -> 'bool':
    """ Returns whether the host's link directory exists.
    """
    out = os.path.isdir(Env_Repo.Host_Link_Dir)
    return out

# ################################################################################################################################

def get_link_dir() -> 'str':

    if is_host_mode():
        out = Env_Repo.Host_Link_Dir
    else:
        out = _local_dir

    return out

# ################################################################################################################################

def _get_path(name:'str') -> 'str':
    out = os.path.join(get_link_dir(), name)
    return out

# ################################################################################################################################

def write_json(name:'str', data:'anydict') -> 'None':
    """ Writes a JSON file in the link directory through a temporary file and a rename.
    """
    link_dir = get_link_dir()
    os.makedirs(link_dir, exist_ok=True)

    path = os.path.join(link_dir, name)
    temp_path = path + '.tmp'

    with open(temp_path, 'w') as output_file:
        _ = output_file.write(dumps(data))

    os.replace(temp_path, path)

# ################################################################################################################################

def _read_text(name:'str') -> 'strnone':

    path = _get_path(name)

    if not os.path.exists(path):
        return None

    with open(path) as input_file:
        out = input_file.read()

    return out

# ################################################################################################################################

def _read_json(name:'str') -> 'anydictnone':

    text = _read_text(name)

    if text is None:
        return None

    try:
        out = loads(text)
    except ValueError:
        logger.warning('File %s in %s is not JSON', name, get_link_dir())
        out = None

    return out

# ################################################################################################################################

def read_public_key() -> 'str':

    out = _read_text(Env_Repo.Public_Key) or ''
    out = out.strip()

    return out

# ################################################################################################################################

def read_current() -> 'anydictnone':
    out = _read_json(Env_Repo.Current)
    return out

# ################################################################################################################################

def read_status() -> 'anydictnone':
    out = _read_json(Env_Repo.Status)
    return out

# ################################################################################################################################

def write_request(action:'str', url:'str', branch:'str') -> 'None':
    """ Writes request.json for the host.
    """
    data:'anydict' = {
        'action':          action,
        'env_repo_url':    url,
        'env_repo_branch': branch,
    }

    write_json(Env_Repo.Request, data)

    logger.info('Request written to %s: action=%s url=%s branch=%s', get_link_dir(), action, url, branch)

# ################################################################################################################################
# ################################################################################################################################
