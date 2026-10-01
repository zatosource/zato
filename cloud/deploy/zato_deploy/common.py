# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from typing import Any

# ################################################################################################################################
# ################################################################################################################################

any_       = Any
anydict    = dict[str, Any]
anylist    = list[Any]
floatnone  = float | None
strlist    = list[str]
strnone    = str | None
strstrdict = dict[str, str]

# ################################################################################################################################
# ################################################################################################################################

class Stage_ID:
    Certificate  = 'certificate'
    Docker       = 'docker'
    Storage      = 'storage'
    Download     = 'download'
    Env_Repo     = 'env-repo'
    Requirements = 'requirements'
    Environment  = 'environment'
    Components   = 'components'
    Checking     = 'checking'

# ################################################################################################################################

class Status:
    Pending = 'pending'
    Active  = 'active'
    Done    = 'done'
    Failed  = 'failed'

# ################################################################################################################################

class Line_Kind:
    OK    = 'ok'
    Error = 'error'

# ################################################################################################################################

class Path:
    Config           = '/etc/zato-deploy/deploy.env'
    Container_Env    = '/etc/zato-deploy/container.env'
    Env_Repo_Config  = '/etc/zato-deploy/env-repo.env'
    Env_Repo_Key     = '/etc/zato-deploy/env-repo-key'
    Env_Secrets      = '/etc/zato-deploy/env-secrets.env'
    Program_Dir      = '/opt/zato-deploy'
    Files_List       = '/opt/zato-deploy/files.txt'
    Static_Dir       = '/opt/zato-deploy/static'
    Known_Hosts      = '/opt/zato-deploy/github_known_hosts'
    Env_Repos_Dir    = '/opt/zato/env-repos'
    Env_Repo_Link    = '/opt/zato/env-repo'
    Data_Dir         = '/var/lib/zato-deploy'
    Link_Dir         = '/var/lib/zato-deploy/link'
    Lets_Encrypt_Dir = '/var/lib/zato-deploy/lets-encrypt'
    Lets_Encrypt_PEM = '/var/lib/zato-deploy/lets-encrypt/certificates/zato.pem'
    Lego             = '/var/lib/zato-deploy/lego'
    Self_Signed_Cert = '/var/lib/zato-deploy/self-signed.crt'
    Self_Signed_Key  = '/var/lib/zato-deploy/self-signed.key'
    Self_Signed_PEM  = '/var/lib/zato-deploy/self-signed.pem'
    Log_Dir          = '/var/log/zato-deploy'
    Deploy_Log       = '/var/log/zato-deploy/deploy.log'
    Env_Repo_Log     = '/var/log/zato-deploy/env-repo.log'
    Run_Dir          = '/run/zato-deploy'
    Serving_Marker   = '/run/zato-deploy/serving'
    Ready_Marker     = '/run/zato-deploy/ready'
    Restart_Reason   = '/run/zato-deploy/restart-reason'
    Serial_Console   = '/dev/ttyS0'
    Docker_Socket    = '/var/run/docker.sock'
    Boot_ID          = '/proc/sys/kernel/random/boot_id'
    Uptime           = '/proc/uptime'
    Local_Disk_Mount = '/mnt/nvme'

# ################################################################################################################################

class Port:
    Dashboard          = 8184
    Deploy             = 18184
    ACME               = 443
    Load_Balancer      = 11223
    Server             = 17010
    Dashboard_Internal = 8182
    OpenAPI_Console    = 8088

# ################################################################################################################################

class Container:
    Name             = 'zato'
    User             = 'zato'
    Log_Tag          = 'zato'
    Lets_Encrypt_Dir = '/opt/hot-deploy/ssl/lets-encrypt'
    Hot_Deploy_Dir   = '/opt/hot-deploy'
    Enmasse_File     = '/opt/hot-deploy/enmasse/enmasse.yaml'
    Env_INI_File     = '/opt/hot-deploy/enmasse/env.ini'
    Requirements     = '/opt/hot-deploy/python-reqs/requirements.txt'
    Host_Link_Dir    = '/opt/zato/host-link'
    Published_Ports  = ['22022:22', '443:11228', '8184:8184', '11224:11224', '11553:11553']

# ################################################################################################################################

class Lego:
    Version      = 'v5.5.1'
    URL_Template = 'https://github.com/go-acme/lego/releases/download/{version}/lego_{version}_linux_{architecture}.tar.gz'
    Server       = 'https://acme-v02.api.letsencrypt.org/directory'
    Cert_Name    = 'zato'
    Profile      = 'classic'

    # The names that the release archives use for each machine type.
    Architectures = {
        'x86_64':  'amd64',
        'aarch64': 'arm64',
    }

# ################################################################################################################################

class Local_Disk:
    """ The lsblk model names of the local NVMe disks that VM sizes with such a disk come with.
    """
    Models = [
        'Microsoft NVMe Direct Disk',
        'Amazon EC2 NVMe Instance Storage',
    ]

# ################################################################################################################################

class Blueprint:
    URL    = 'https://github.com/zatosource/zato-project-blueprint.git'
    Branch = 'main'

# ################################################################################################################################

class Env_Repo_Layout:
    """ The paths inside an environment directory of the repository.
    """
    Enmasse        = 'config/enmasse/enmasse.yaml'
    Requirements   = 'config/python-reqs/requirements.txt'
    Auto_Generated = 'config/auto-generated'
    Env_INI        = 'config/auto-generated/env.ini'

# ################################################################################################################################

class Link_File:
    """ The files in the directory shared with the container.
    """
    Public_Key = 'id_ed25519.pub'
    Request    = 'request.json'
    Status     = 'status.json'
    Current    = 'current.json'

# ################################################################################################################################

class Env_Repo_Action:
    Check      = 'check'
    Switch     = 'switch'
    Disconnect = 'disconnect'
    Pull       = 'pull'

# ################################################################################################################################

class Env_Repo_State:
    Checking  = 'checking'
    OK        = 'ok'
    Error     = 'error'
    Switching    = 'switching'
    Disconnected = 'disconnected'
    Pulling      = 'pulling'
    Pulled       = 'pulled'

# ################################################################################################################################

class Restart_Reason:
    Boot   = 'boot'
    Switch = 'switch'
    Sync   = 'sync'

# ################################################################################################################################

class Systemd_Unit:
    Deploy        = 'zato-deploy.service'
    Env_Repo_Path = 'zato-env-repo.path'
    Env_Repo      = 'zato-env-repo.service'
    Env_Repo_Time = 'zato-env-repo.timer'
    Docker        = ['docker.service', 'docker.socket', 'containerd.service']

# ################################################################################################################################

# The values of Zato_Install_Updates that turn the updates off, as the container's entrypoint reads them.
_Updates_Off = ('False', 'false')

# ################################################################################################################################
# ################################################################################################################################

class StageFailed(Exception):
    """ Raised when a stage cannot continue, with the message the page shows.
    """
    def __init__(self, message:'str') -> 'None':
        super().__init__(message)
        self.message = message

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Config:
    fqdn:               str
    admin_username:     str
    image:              str
    is_install_updates: bool

# ################################################################################################################################

@dataclass(init=False)
class EnvRepoConfig:
    url:    str
    branch: str

# ################################################################################################################################
# ################################################################################################################################

def clean_terminal_line(line:'str') -> 'str':
    """ Returns a line as a terminal would end up showing it, since progress counters redraw themselves
    in place with carriage returns and backspaces.
    """
    # Only what comes after the last carriage return stays on screen ..
    _, _, line = line.rpartition('\r')

    characters:'strlist' = []

    for character in line:

        # .. each backspace takes back the character before it ..
        if character == '\b':
            if characters:
                _ = characters.pop()
            continue

        # .. and of the other control characters, only tabs are kept.
        if character == '\t':
            characters.append(character)
            continue

        if character.isprintable():
            characters.append(character)

    out = ''.join(characters)
    out = out.rstrip()

    return out

# ################################################################################################################################

def read_env_file(path:'str') -> 'strstrdict':
    """ Returns the key=value lines of a file, each value taken literally up to the end of its line.
    """
    out:'strstrdict' = {}

    with open(path) as input_file:
        lines = input_file.read().splitlines()

    for line in lines:
        if not line:
            continue
        key, _, value = line.partition('=')
        out[key] = value

    return out

# ################################################################################################################################

def write_env_file(path:'str', values:'strstrdict') -> 'None':

    lines:'strlist' = []

    for key, value in values.items():
        lines.append(f'{key}={value}')

    text = '\n'.join(lines) + '\n'

    with open(path, 'w') as output_file:
        _ = output_file.write(text)

# ################################################################################################################################

def load_config(path:'str') -> 'Config':
    """ Returns the configuration that cloud-init wrote, with the updates setting read from the container's environment.
    """
    values = read_env_file(path)
    container_values = read_env_file(Path.Container_Env)

    out = Config()
    out.fqdn               = values['fqdn']
    out.admin_username     = values['admin_username']
    out.image              = values['image']
    out.is_install_updates = container_values['Zato_Install_Updates'] not in _Updates_Off

    return out

# ################################################################################################################################

def load_env_repo_config(path:'str') -> 'EnvRepoConfig':
    """ Returns the repository to run, which is the public blueprint unless one was configured.
    """
    values = read_env_file(path)

    out = EnvRepoConfig()
    out.url    = values['env_repo_url']
    out.branch = values['env_repo_branch']

    if not out.url:
        out.url    = Blueprint.URL
        out.branch = Blueprint.Branch

    return out

# ################################################################################################################################
# ################################################################################################################################
