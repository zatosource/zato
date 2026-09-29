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
    Static_Dir       = '/opt/zato-deploy/static'
    Data_Dir         = '/var/lib/zato-deploy'
    Lets_Encrypt_Dir = '/var/lib/zato-deploy/lets-encrypt'
    Lets_Encrypt_PEM = '/var/lib/zato-deploy/lets-encrypt/certificates/zato.pem'
    Lego             = '/var/lib/zato-deploy/lego'
    Self_Signed_Cert = '/var/lib/zato-deploy/self-signed.crt'
    Self_Signed_Key  = '/var/lib/zato-deploy/self-signed.key'
    Self_Signed_PEM  = '/var/lib/zato-deploy/self-signed.pem'
    Serial_Console   = '/dev/ttyS0'
    Docker_Socket    = '/var/run/docker.sock'
    NVMe_Device      = '/dev/disk/azure/local/by-index/1'
    NVMe_Mount       = '/mnt/nvme'

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
    Lets_Encrypt_Dir = '/opt/hot-deploy/ssl/lets-encrypt'
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
    fqdn:           str
    admin_username: str
    image:          str

# ################################################################################################################################
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

def load_config(path:'str') -> 'Config':
    """ Returns the configuration that cloud-init wrote.
    """
    values = read_env_file(path)

    out = Config()
    out.fqdn           = values['fqdn']
    out.admin_username = values['admin_username']
    out.image          = values['image']

    return out

# ################################################################################################################################
# ################################################################################################################################
