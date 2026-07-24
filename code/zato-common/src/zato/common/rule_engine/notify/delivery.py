# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.notify.credentials import load_credentials, NotifyConfigError
from zato.common.rule_engine.sql.constants import Chat_Kind_Slack, Chat_Kind_Teams, Chat_Kinds
from zato.server.connection.chat.slack import SlackClient
from zato.server.connection.cloud.microsoft_teams import MicrosoftTeamsClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import anydict, dictlist

# ################################################################################################################################
# ################################################################################################################################

# The connection name the chat clients report themselves under in logs.
Client_Name = 'rule-engine-notify'

# What the settings screen's test button sends.
Test_Message = 'Test message from the Zato rule engine.'

# ################################################################################################################################
# ################################################################################################################################

def _build_slack_client(values:'anydict') -> 'SlackClient':
    """ Builds a Slack client from decrypted credentials.
    """
    # The required token plus the optional address override used against local test servers.
    config = dict(values)
    config['name'] = Client_Name

    out = SlackClient(config)
    return out

# ################################################################################################################################

def _build_teams_client(values:'anydict') -> 'MicrosoftTeamsClient':
    """ Builds a Microsoft Teams client from decrypted credentials.
    """
    # The Graph client expects the secret under its own key ..
    config = dict(values)
    config['name'] = Client_Name
    config['secret'] = config.pop('client_secret')

    # .. everything else - tenant_id, client_id and the optional address,
    # .. auth_server_url and verify_tls overrides - passes through unchanged.
    out = MicrosoftTeamsClient(config)
    return out

# ################################################################################################################################

_client_builders = {
    Chat_Kind_Slack: _build_slack_client,
    Chat_Kind_Teams: _build_teams_client,
}

# ################################################################################################################################
# ################################################################################################################################

def build_clients(backend:'RuleSQLBackend') -> 'anydict':
    """ Builds one client per configured chat platform, keyed by kind.
    """
    out = {}

    for kind in Chat_Kinds:
        values = load_credentials(backend, kind)

        # An unconfigured platform simply has no client.
        if values is None:
            continue

        builder = _client_builders[kind]
        out[kind] = builder(values)

    return out

# ################################################################################################################################

def send_message(clients:'anydict', kind:'str', target:'str', text:'str') -> 'None':
    """ Delivers one message to one destination through an already built client.
    """
    # A destination without matching credentials cannot be delivered to ..
    if kind not in clients:
        message = f'No {kind} credentials are configured'
        raise NotifyConfigError(message)

    client = clients[kind]

    # .. each platform's client has its own send signature.
    if kind == Chat_Kind_Slack:
        _ = client.send(channel=target, text=text)
    else:
        _ = client.send(to=target, text=text)

# ################################################################################################################################

def send_test_message(backend:'RuleSQLBackend', kind:'str', target:'str') -> 'None':
    """ Sends the settings screen's test message to one target.
    """
    clients = build_clients(backend)
    send_message(clients, kind, target, Test_Message)

# ################################################################################################################################
# ################################################################################################################################

def _list_slack_targets(client:'SlackClient') -> 'dictlist':
    """ Returns the channels a Slack workspace offers as delivery targets.
    """
    out = []

    # Channels come from the conversations API ..
    response = client.invoke('conversations.list')

    # .. and each one is addressed simply by its name.
    for channel in response['channels']:
        name = channel['name']
        row = {'target': name, 'name': f'#{name}'}
        out.append(row)

    return out

# ################################################################################################################################

def _list_teams_targets(client:'MicrosoftTeamsClient') -> 'dictlist':
    """ Returns the team channels a Microsoft 365 tenant offers as delivery targets.
    """
    out = []
    service_url = client.impl.protocol.service_url

    # Every team the tenant has ..
    response = client.impl.con.get(f'{service_url}teams')
    teams = response.json()

    for team in teams['value']:
        team_name = team['displayName']
        team_id = team['id']

        # .. and every channel within it, addressed as 'Team name/Channel name'.
        response = client.impl.con.get(f'{service_url}teams/{team_id}/channels')
        channels = response.json()

        for channel in channels['value']:
            channel_name = channel['displayName']
            target = f'{team_name}/{channel_name}'
            row = {'target': target, 'name': target}
            out.append(row)

    return out

# ################################################################################################################################

def list_targets(backend:'RuleSQLBackend', kind:'str') -> 'dictlist':
    """ Returns the live targets one platform offers, for the destination picker.
    """
    clients = build_clients(backend)

    # Without credentials there is nothing to list ..
    if kind not in clients:
        message = f'No {kind} credentials are configured'
        raise NotifyConfigError(message)

    client = clients[kind]

    # .. each platform enumerates its targets its own way.
    if kind == Chat_Kind_Slack:
        out = _list_slack_targets(client)
    else:
        out = _list_teams_targets(client)

    return out

# ################################################################################################################################
# ################################################################################################################################
