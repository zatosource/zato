# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from hashlib import sha512
from http.client import CREATED, OK
from json import dumps
from secrets import token_hex
from urllib.parse import quote

# Live HL7
from live_hl7.credentials import PasswordRules
from live_hl7.http import Session, basic_auth, expect_status, is_http_ok, parse_json
from live_hl7.system import Handle, LiveSystem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# The service name in the compose file
Service = 'openhim'

# The root account the image creates - its password is replaced at first start
Root_Username = 'root@openhim.org'
Root_Initial_Password = 'openhim-password'

# Every tcp channel purpose, in the order of the compose file
Channel_Purposes = ('channel_1', 'channel_2', 'channel_3', 'channel_4')

# The ports the tcp channels bind inside the container, by purpose
Channel_Container_Ports = {
    'channel_1': 6001,
    'channel_2': 6002,
    'channel_3': 6003,
    'channel_4': 6004,
}

# Every tcp route waits this long for the far side to answer and close, in milliseconds
Route_Timeout_MS = 10000

# What a channel's containers reach this machine as
Host_Address = 'host.docker.internal'

# The statuses a transaction ends in, as the API spells them
Transaction_Successful = 'Successful'
Transaction_Completed_With_Errors = 'Completed with error(s)'
Transaction_Failed = 'Failed'

# What a channel's status field carries
Channel_Enabled = 'enabled'
Channel_Disabled = 'disabled'

# ################################################################################################################################
# ################################################################################################################################

class OpenHIM(LiveSystem):
    """ The interoperability layer - tcp channels in, tcp routes out, every transaction logged.
    """

    name = 'openhim'
    block_number = 4
    purposes = ('api', 'router_https', 'router_http') + Channel_Purposes
    password_rules = PasswordRules(8, False, False, False, False)
    images = {
        'mongo':   'mongo:4.4',
        'openhim': 'jembi/openhim-core@sha256:8d72295b598b7171bd95268f0421e2a4a198983be4f5e18c0cddeb12ca20ecce',
    }
    directory = os.path.dirname(__file__)
    summary = 'OpenHIM with tcp channels routing to mllp destinations, the interoperability layer of a health information exchange.'
    ui_purpose = 'api'
    ui_path = '/'
    ui_is_https = True
    ui_username = Root_Username

# ################################################################################################################################

    def is_ready(self, handle:'Handle') -> 'bool':
        url = handle.https_url('api') + '/heartbeat'

        out = is_http_ok(url, verify_tls=False)
        return out

# ################################################################################################################################

    def after_ready(self, handle:'Handle') -> 'None':
        """ Replaces the root password with ours - a restart already has it and skips the change.
        """
        session = _session(handle, Root_Initial_Password)
        result = session.get('/users/' + Root_Username)

        if result.status != OK:
            return

        result = session.request_json('PUT', '/users/' + Root_Username, {'password': handle.password})
        expect_status(result, OK, 'root password change')

# ################################################################################################################################
# ################################################################################################################################

def _session(handle:'Handle', password:'str') -> 'Session':
    out = Session(handle.https_url('api'), verify_tls=False)
    out.headers['Authorization'] = basic_auth(Root_Username, password)

    return out

# ################################################################################################################################

def login(handle:'Handle') -> 'Session':
    """ An API session as root with the password from the environment.
    """
    out = _session(handle, handle.password)

    result = out.get('/users/' + Root_Username)
    expect_status(result, OK, 'login')

    return out

# ################################################################################################################################

def add_client(session:'Session', client_id:'str', password:'str', roles:'anylist') -> 'None':
    """ A client the channels below allow - a facility on the exchange. The API stores what the console
    computes, a hash of the password followed by the salt, so that is computed here.
    """
    salt = token_hex(16)
    digest = sha512(password.encode('utf8') + salt.encode('utf8')).hexdigest()

    payload = {
        'clientID': client_id,
        'name':     client_id,
        'roles':    roles,
        'passwordAlgorithm': 'sha512',
        'passwordSalt': salt,
        'passwordHash': digest,
    }

    result = session.post_json('/clients', payload)
    expect_status(result, CREATED, f'client {client_id}')

# ################################################################################################################################

def add_tcp_channel(
    session:'Session',
    name:'str',
    purpose:'str',
    routes:'anylist',
    allow:'anylist',
    ) -> 'anydict':
    """ A tcp channel on one of the published ports, whose routes carry every message on as it arrived.
    Both bodies are kept, since reading a message back out of the transaction log is what an exchange is for.
    """
    payload = {
        'name':         name,
        'urlPattern':   '.*',
        'type':         'tcp',
        'tcpHost':      '0.0.0.0',
        'tcpPort':      Channel_Container_Ports[purpose],
        'allow':        allow,
        'authType':     'public',
        'routes':       routes,
        'status':       Channel_Enabled,
        'requestBody':  True,
        'responseBody': True,
    }

    result = session.post_json('/channels', payload)
    expect_status(result, CREATED, f'channel {name}')

    out = find_channel(session, name)
    return out

# ################################################################################################################################

def tcp_route(name:'str', host:'str', port:'int', *, is_primary:'bool'=True) -> 'anydict':
    """ One route writing the bytes a tcp channel received to the far side unchanged - the tcp type carries one
    MLLP frame where mllp would add a second, and the far side closing after its acknowledgment ends the read.
    """
    out:'anydict' = {
        'name':    name,
        'type':    'tcp',
        'host':    host,
        'port':    port,
        'primary': is_primary,
        'status':  'enabled',
        'timeout': Route_Timeout_MS,
    }

    return out

# ################################################################################################################################

def set_channel_status(session:'Session', channel_id:'str', status:'str') -> 'None':
    """ Enables or disables a channel - a disabled tcp channel has its port closed, so a facility
    connecting to it is turned away before a byte is read.
    """
    result = session.put_json(f'/channels/{channel_id}', {'status': status})
    expect_status(result, OK, f'status {status} of channel {channel_id}')

# ################################################################################################################################

def find_channel(session:'Session', name:'str') -> 'anydict':
    channels = session.get_json('/channels')

    for channel in channels:
        if channel['name'] == name:
            return channel

    raise Exception(f'No channel named {name}')

# ################################################################################################################################

def remove_channel(session:'Session', channel_id:'str') -> 'None':
    result = session.request('DELETE', f'/channels/{channel_id}')
    expect_status(result, OK, f'removal of channel {channel_id}')

# ################################################################################################################################

def transactions(session:'Session', channel_id:'str') -> 'any_':
    """ The transactions one channel handled, newest first, bodies included. The API reads its filters
    out of one JSON object in the query string.
    """
    filters = quote(dumps({'channelID': channel_id}))
    path = f'/transactions?filters={filters}&filterRepresentation=full'

    out = session.get_json(path)
    return out

# ################################################################################################################################

def transaction(session:'Session', transaction_id:'str') -> 'anydict':
    result = session.get(f'/transactions/{transaction_id}')
    expect_status(result, OK, f'transaction {transaction_id}')

    out = parse_json(result)
    return out

# ################################################################################################################################
# ################################################################################################################################
