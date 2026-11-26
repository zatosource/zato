# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import sleep as gevent_sleep

# Zato
from zato.common.api import Groups, HTTP_SOAP, SEC_DEF_TYPE
from zato.common.dispatch import dispatcher
from zato.common.ext.bunch import Bunch
from zato.common.groups import Member
from zato.common.typing_ import cast_
from zato.common.util.url_dispatcher import build_methods_allowed_re, get_match_target
from zato.server.base.config_manager import ConfigManager
from zato.server.connection.http_soap.url_dispatcher import Matcher
from zato.server.groups.ctx import SecurityGroupsCtxBuilder

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.config import ConfigStore
    from zato.server.connection.http_soap.url_data import URLData

    ConfigStore = ConfigStore
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

member_list        = list[Member]
url_data_list      = list['URLData']
url_security_tuple = tuple['anydict', None]

# ################################################################################################################################
# ################################################################################################################################

Channel_ID   = 7001
Channel_Name = 'api.orders.reload'
URL_Path     = '/api/orders/reload'

Group_ID = 801

Security_ID     = 901
Security_Name   = 'api.orders.client'
Member_Group_ID = 802

Previous_Username = 'orders.client.previous'
Previous_Password = 'password.previous.0001'

New_Username = 'orders.client.new'
New_Password = 'password.new.0001'

# How many times the member list query gives up control before it returns
Member_List_Switch_Count = 3

_methods_allowed_re = build_methods_allowed_re(['GET', 'POST'])

# ################################################################################################################################
# ################################################################################################################################

class GroupsManagerStub:
    """ Returns a fixed member list and gives up control while it does, the way the SQL query behind it does.
    """
    def __init__(self, members:'member_list') -> 'None':
        self.members = members
        self.url_data_received:'url_data_list' = []

    def get_member_list(self, group_type:'str', url_data:'URLData', group_id:'intnone'=None) -> 'member_list':

        self.url_data_received.append(url_data)

        for _ in range(Member_List_Switch_Count):
            gevent_sleep(0)

        out = self.members
        return out

# ################################################################################################################################
# ################################################################################################################################

class ODBStub:
    """ The channel security the URLData of a configuration is built with.
    """
    def get_url_security(self, target:'str') -> 'url_security_tuple':
        out = ({}, None)
        return out

# ################################################################################################################################
# ################################################################################################################################

class ServerStub:
    """ The attributes of ParallelServer that the installation of a request dispatcher reads.
    """
    def __init__(self, groups_manager:'GroupsManagerStub') -> 'None':
        self.name = 'server1'
        self.odb = ODBStub()
        self.groups_manager = groups_manager
        self.return_tracebacks = False
        self.default_error_message = 'Internal server error'
        self.http_methods_allowed = ['GET', 'POST']

        self.security_groups_ctx_builder = SecurityGroupsCtxBuilder(cast_('ParallelServer', self))

# ################################################################################################################################
# ################################################################################################################################

def make_member() -> 'Member':
    """ The Basic Auth definition that belongs to the group protecting the channel.
    """
    out = Member()

    out.id = Security_ID
    out.name = f'{SEC_DEF_TYPE.BASIC_AUTH}-{Security_ID}-{Member_Group_ID}'
    out.type = Groups.Type.Group_Member
    out.group_id = Group_ID
    out.security_id = Security_ID
    out.sec_type = SEC_DEF_TYPE.BASIC_AUTH

    return out

# ################################################################################################################################

def make_channel_item() -> 'Bunch':
    """ A REST channel protected by one security group and nothing else.
    """
    config = {
        'url_path': URL_Path,
        'method': '',
        'http_accept': HTTP_SOAP.ACCEPT.ANY,
    }

    match_target = get_match_target(config, http_methods_allowed_re=_methods_allowed_re)

    out = Bunch()
    out.id = Channel_ID
    out.name = Channel_Name
    out.url_path = URL_Path
    out.method = ''
    out.http_accept = HTTP_SOAP.ACCEPT.ANY
    out.is_internal = False
    out.match_target = match_target
    out.match_target_compiled = Matcher(match_target)
    out.security_groups = [Group_ID]

    return out

# ################################################################################################################################

def make_basic_auth_config(username:'str', password:'str') -> 'anydict':
    """ The Basic Auth definitions of a configuration, keyed by name, each with its configuration under .config.
    """
    config = Bunch()
    config.id = Security_ID
    config.name = Security_Name
    config.username = username
    config.password = password
    config.is_active = True
    config.sec_type = SEC_DEF_TYPE.BASIC_AUTH

    item = Bunch()
    item.config = config

    out = {Security_Name: item}
    return out

# ################################################################################################################################

def make_config_store(username:'str', password:'str') -> 'ConfigStore':
    """ A configuration with one REST channel and the one Basic Auth definition its security group holds.
    """
    channel_item = make_channel_item()
    basic_auth = make_basic_auth_config(username, password)

    config_store = Bunch()
    config_store.http_soap = [channel_item]
    config_store.basic_auth = basic_auth
    config_store.mtls = {}
    config_store.ntlm = {}
    config_store.oauth = {}
    config_store.spnego = {}
    config_store.apikey = {}
    config_store.wss = {}

    out = cast_('ConfigStore', config_store)
    return out

# ################################################################################################################################

def make_config_manager(server:'ServerStub', config_store:'ConfigStore') -> 'ConfigManager':
    """ A ConfigManager with only the attributes that the installation of a request dispatcher reads.
    """
    out = object.__new__(ConfigManager)
    out.server = cast_('ParallelServer', server)
    out.config_store = config_store
    out.config_dispatcher = None

    return out

# ################################################################################################################################

def unlisten(config_manager:'ConfigManager') -> 'None':
    """ Unregisters the URLData of the installed dispatcher from the security events of the process.
    """
    url_data = config_manager.request_dispatcher.url_data
    dispatcher.unlisten(url_data.dispatcher_callback)

# ################################################################################################################################

def get_channel_items(config_manager:'ConfigManager') -> 'anylist':
    """ The channel items of the dispatcher that serves requests at the moment of the call.
    """
    request_dispatcher:'any_' = config_manager.request_dispatcher

    if request_dispatcher is None:
        out = []
    else:
        out = request_dispatcher.url_data.channel_data

    return out

# ################################################################################################################################
# ################################################################################################################################
