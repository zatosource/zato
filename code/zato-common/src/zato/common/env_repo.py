# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
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
    Link_Dir   = '/opt/zato/host-link'
    Public_Key = 'id_ed25519.pub'
    Request    = 'request.json'
    Status     = 'status.json'
    Current    = 'current.json'

    Action_Check  = 'check'
    Action_Switch = 'switch'

    Blueprint_Owner = 'zatosource'
    Blueprint_Name  = 'zato-project-blueprint'

    # The name of the repository that GitHub creates from the template for the user.
    New_Repo_Name = 'zato-environment'

    New_Repo_URL = 'https://github.com/new?template_owner={owner}&template_name={name}&owner={login}&name={new_name}&visibility=private'
    Deploy_Key_URL = 'https://github.com/{login}/{new_name}/settings/keys/new'
    Repo_SSH_URL = 'git@github.com:{login}/{new_name}.git'

# ################################################################################################################################
# ################################################################################################################################

def _get_path(name:'str') -> 'str':
    out = os.path.join(Env_Repo.Link_Dir, name)
    return out

# ################################################################################################################################

def is_available() -> 'bool':
    """ Returns whether this container runs on a host with the deployment program, which is what makes the screen useful.
    """
    out = os.path.isdir(Env_Repo.Link_Dir)
    return out

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
        logger.warning('File %s in %s is not JSON', name, Env_Repo.Link_Dir)
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
    """ Leaves a request for the host, which acts on it the moment the file appears.
    """
    data:'anydict' = {
        'action':          action,
        'env_repo_url':    url,
        'env_repo_branch': branch,
    }

    path = _get_path(Env_Repo.Request)
    temp_path = path + '.tmp'

    with open(temp_path, 'w') as output_file:
        _ = output_file.write(dumps(data))

    os.replace(temp_path, path)

    logger.info('Request written to %s: action=%s url=%s branch=%s', path, action, url, branch)

# ################################################################################################################################

def get_new_repo_url(login:'str') -> 'str':

    out = Env_Repo.New_Repo_URL.format(
        owner=Env_Repo.Blueprint_Owner,
        name=Env_Repo.Blueprint_Name,
        login=login,
        new_name=Env_Repo.New_Repo_Name,
    )

    return out

# ################################################################################################################################

def get_deploy_key_url(login:'str') -> 'str':

    out = Env_Repo.Deploy_Key_URL.format(login=login, new_name=Env_Repo.New_Repo_Name)
    return out

# ################################################################################################################################

def get_repo_ssh_url(login:'str') -> 'str':

    out = Env_Repo.Repo_SSH_URL.format(login=login, new_name=Env_Repo.New_Repo_Name)
    return out

# ################################################################################################################################
# ################################################################################################################################
