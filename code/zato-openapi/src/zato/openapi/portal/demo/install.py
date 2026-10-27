# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import os
import subprocess
import sys
from argparse import ArgumentParser
from shutil import copyfile
from typing import NamedTuple

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.ext.configobj_ import ConfigObj

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_File_Name       = 'api-portal-demo.ini'
    Env_Section         = 'env'
    Enmasse_File_Name   = 'enmasse.yaml'
    Services_Dir_Name   = 'services'
    Service_File_Prefix = 'api_portal_demo_'
    Missing_Wait_Time   = '120'
    Service_Modules     = ('patients.py', 'scheduling.py', 'clinical.py', 'exchange.py', 'analytics.py')

# ################################################################################################################################
# ################################################################################################################################

class Credential(NamedTuple):
    name:    str
    kind:    str
    env_key: str

# ################################################################################################################################
# ################################################################################################################################

# The security definitions of the demo and the environment variables their secrets are read from
_credentials = [
    Credential('healthcare.clinician',        'Basic Auth',   'Healthcare_Demo_Clinician_Password'),
    Credential('healthcare.scheduler',        'Basic Auth',   'Healthcare_Demo_Scheduler_Password'),
    Credential('healthcare.analyst',          'Basic Auth',   'Healthcare_Demo_Analyst_Password'),
    Credential('healthcare.referral-partner', 'Basic Auth',   'Healthcare_Demo_Referral_Partner_Password'),
    Credential('healthcare.lab-system',       'API Key',      'Healthcare_Demo_Lab_System_Key'),
    Credential('healthcare.ward-board',       'API Key',      'Healthcare_Demo_Ward_Board_Key'),
    Credential('healthcare.admission-feed',   'API Key',      'Healthcare_Demo_Admission_Feed_Key'),
    Credential('healthcare.patient-portal',   'Bearer token', 'Healthcare_Demo_Patient_Portal_Token'),
]

_demo_dir = os.path.dirname(os.path.abspath(__file__))

# ################################################################################################################################
# ################################################################################################################################

def _load_secrets(env_path:'str') -> 'stranydict':
    """ Returns the secrets of the demo, reusing the ones an earlier run stored and generating the others.
    """
    # The file is read if it exists and created otherwise ..
    config:'any_' = ConfigObj(env_path)

    if ModuleCtx.Env_Section not in config:
        config[ModuleCtx.Env_Section] = {}

    section = config[ModuleCtx.Env_Section]

    # .. every secret not stored yet is generated ..
    for credential in _credentials:
        if credential.env_key not in section:
            section[credential.env_key] = CryptoManager.generate_password(to_str=True)

    # .. and the file is written back so that the next run signs in with the same credentials.
    config.write()

    out = dict(section)
    return out

# ################################################################################################################################

def _deploy_services(server_dir:'str') -> 'None':
    """ Copies the demo service modules to the hot-deploy directory of the server.
    """
    source_dir = os.path.join(_demo_dir, ModuleCtx.Services_Dir_Name)
    pickup_dir = os.path.join(server_dir, 'pickup', 'incoming', 'services')

    for module_name in ModuleCtx.Service_Modules:
        source_path = os.path.join(source_dir, module_name)
        target_path = os.path.join(pickup_dir, ModuleCtx.Service_File_Prefix + module_name)
        _ = copyfile(source_path, target_path)

# ################################################################################################################################

def _import_definitions(zato_path:'str', server_dir:'str', env_path:'str') -> 'None':
    """ Imports the security definitions, the groups and the REST channels of the demo,
    waiting for the services to be hot-deployed first.
    """
    enmasse_path = os.path.join(_demo_dir, ModuleCtx.Enmasse_File_Name)

    command = [
        zato_path, 'enmasse', server_dir,
        '--import',
        '--input', enmasse_path,
        '--env-file', env_path,
        '--missing-wait-time', ModuleCtx.Missing_Wait_Time,
    ]

    # The import logs every definition it compares, so its output is shown only if it fails.
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        sys.exit(result.returncode)

# ################################################################################################################################

def _print_credentials(secrets:'stranydict', env_path:'str') -> 'None':
    """ Prints the credentials the demo's callers sign in to the API portal with.
    """
    name_width = 0
    kind_width = 0

    for credential in _credentials:
        name_width = max(name_width, len(credential.name))
        kind_width = max(kind_width, len(credential.kind))

    print()

    for credential in _credentials:
        name = credential.name.ljust(name_width)
        kind = credential.kind.ljust(kind_width)
        secret = secrets[credential.env_key]
        print(f'{name}  {kind}  {secret}')

    print()
    print(f'Credentials stored in {env_path}')

# ################################################################################################################################

def main() -> 'None':
    """ Sets up the healthcare demo of the API portal on a server.
    """
    parser = ArgumentParser()
    _ = parser.add_argument('--server-dir', required=True)
    _ = parser.add_argument('--zato', required=True)
    args = parser.parse_args()

    server_dir = os.path.abspath(os.path.expanduser(args.server_dir))

    # The secrets are kept in the environment directory, next to the server ..
    env_dir = os.path.dirname(server_dir)
    env_path = os.path.join(env_dir, ModuleCtx.Env_File_Name)
    secrets = _load_secrets(env_path)

    # .. the services go to hot deployment ..
    _deploy_services(server_dir)

    # .. enmasse waits for them before it creates the channels ..
    _import_definitions(args.zato, server_dir, env_path)

    # .. and the credentials are printed for signing in to the portal.
    _print_credentials(secrets, env_path)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
