# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import shutil
import subprocess
from typing import NamedTuple
from urllib.parse import urlparse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The resource group the test reads and the tags on it
    Resource_Group = 'zato-test-rg'
    Tag_Namespace  = 'zato_namespace'
    Tag_Hub        = 'zato_hub'
    Tag_App_ID     = 'zato_app_id'

    # The port the Kafka endpoint of a namespace listens on
    Kafka_Port = 9093

    # The authorization rule whose connection string is the PLAIN password
    Auth_Rule = 'RootManageSharedAccessKey'

    # The PLAIN username, with $$ standing for a literal $
    Plain_Username = '$$ConnectionString'

    # Where OAUTHBEARER tokens come from and what they are for
    Token_URL_Template = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    Scope_Template     = 'https://{namespace}.servicebus.windows.net/.default'

    # How long one az call may take
    Az_Timeout = 120

# ################################################################################################################################
# ################################################################################################################################

# What a resource group without tags reads as
_no_tags:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

class EventHubs(NamedTuple):
    """ Everything a test needs to reach one namespace under both SASL mechanisms.
    """
    bootstrap_address: str
    hub: str
    namespace: str
    connection_string: str
    app_id: str
    client_secret: str
    token_url: str
    scope: str

# ################################################################################################################################
# ################################################################################################################################

def _run_az(*command_parts:'str') -> 'anydict':
    """ Runs one az command and returns what it printed, parsed from JSON.
    """
    command = ['az', *command_parts, '--output', 'json']
    result = subprocess.run(command, capture_output=True, text=True, timeout=ModuleCtx.Az_Timeout)

    if result.returncode != 0:
        group = command_parts[0]
        command_name = command_parts[1]
        error = result.stderr.strip()
        msg = f'az {group} {command_name} failed: {error}'
        raise Exception(msg)

    out = json.loads(result.stdout)
    return out

# ################################################################################################################################

def _is_logged_in() -> 'bool':
    """ Whether az has an account to work with.
    """
    command = ['az', 'account', 'show']
    result = subprocess.run(command, capture_output=True, text=True, timeout=ModuleCtx.Az_Timeout)

    out = result.returncode == 0
    return out

# ################################################################################################################################

def _read_tags() -> 'anydict':
    """ The tags of the resource group.
    """
    command = ['az', 'group', 'show', '--name', ModuleCtx.Resource_Group, '--query', 'tags', '--output', 'json']
    result = subprocess.run(command, capture_output=True, text=True, timeout=ModuleCtx.Az_Timeout)

    # A group that does not exist has no tags ..
    if result.returncode != 0:
        out = _no_tags

    # .. a group that exists may have none either ..
    else:
        tags = json.loads(result.stdout)

        if tags is None:
            out = _no_tags

        # .. or it has some.
        else:
            out = tags

    return out

# ################################################################################################################################
# ################################################################################################################################

def missing_requirements() -> 'strlist':
    """ What this machine lacks for the live test to run.
    """
    out:'strlist' = []

    if not shutil.which('az'):
        out.append('az is not installed')
        return out

    if not _is_logged_in():
        out.append('az is not logged in')
        return out

    tags = _read_tags()

    if not tags:
        out.append(f'Resource group {ModuleCtx.Resource_Group} is missing')
        return out

    for tag in (ModuleCtx.Tag_Namespace, ModuleCtx.Tag_Hub, ModuleCtx.Tag_App_ID):
        if tag not in tags:
            out.append(f'Tag {tag} is missing from resource group {ModuleCtx.Resource_Group}')

    return out

# ################################################################################################################################

def describe() -> 'EventHubs':
    """ Reads everything the test needs through az.
    """
    # The tenant comes from the account ..
    account = _run_az('account', 'show')
    tenant_id = account['tenantId']

    # .. the names come from the tags ..
    tags = _read_tags()
    namespace = tags[ModuleCtx.Tag_Namespace]
    hub = tags[ModuleCtx.Tag_Hub]
    app_id = tags[ModuleCtx.Tag_App_ID]

    # .. the Kafka endpoint comes from the namespace ..
    namespace_info = _run_az(
        'eventhubs', 'namespace', 'show',
        '--resource-group', ModuleCtx.Resource_Group,
        '--name', namespace,
    )
    service_bus_endpoint = namespace_info['serviceBusEndpoint']
    endpoint = urlparse(service_bus_endpoint)
    bootstrap_address = f'{endpoint.hostname}:{ModuleCtx.Kafka_Port}'

    # .. the connection string comes from the authorization rule ..
    keys = _run_az(
        'eventhubs', 'namespace', 'authorization-rule', 'keys', 'list',
        '--resource-group', ModuleCtx.Resource_Group,
        '--namespace-name', namespace,
        '--name', ModuleCtx.Auth_Rule,
    )
    connection_string = keys['primaryConnectionString']

    # .. a fresh secret comes from the app registration ..
    credential = _run_az('ad', 'app', 'credential', 'reset', '--id', app_id)
    client_secret = credential['password']

    # .. and the token URL and scope come from the templates.
    token_url = ModuleCtx.Token_URL_Template.format(tenant_id=tenant_id)
    scope = ModuleCtx.Scope_Template.format(namespace=namespace)

    out = EventHubs(
        bootstrap_address=bootstrap_address,
        hub=hub,
        namespace=namespace,
        connection_string=connection_string,
        app_id=app_id,
        client_secret=client_secret,
        token_url=token_url,
        scope=scope,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
