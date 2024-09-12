# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from collections import namedtuple
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import chain
from time import sleep
from uuid import uuid4

# Zato
from zato.cli import ManageCommand
from zato.common.api import All_Sec_Def_Types, Data_Format, GENERIC as COMMON_GENERIC, Groups as Common_Groups, \
    LDAP as COMMON_LDAP, NotGiven, PUBSUB as Common_PubSub, Sec_Def_Type, TLS as COMMON_TLS, Zato_No_Security, Zato_None
from zato.common.const import ServiceConst
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:

    from logging import Logger
    from zato.client import APIClient
    from zato.common.typing_ import any_, anydict, anylist, dictlist, list_, stranydict, strdict, strdictnone, strdictdict, \
        strstrdict, strlist, strlistdict, strnone

    APIClient = APIClient
    Logger = Logger
    strdictdict = strdictdict
    strlistdict = strlistdict

# ################################################################################################################################
# ################################################################################################################################

zato_enmasse_env1 = 'ZatoEnmasseEnv.'
zato_enmasse_env2 = 'Zato_Enmasse_Env.'
zato_enmasse_env_value_prefix = 'Zato_Enmasse_Env_'

DEFAULT_COLS_WIDTH = '15,100'

# ################################################################################################################################

class _NoValue:
    pass

_no_value1 = _NoValue()
_no_value2 = _NoValue()

# ################################################################################################################################

Code = namedtuple('Code', ('symbol', 'desc')) # type: ignore

WARNING_ALREADY_EXISTS_IN_ODB = Code('W01', 'already exists in ODB')
WARNING_MISSING_DEF = Code('W02', 'definition missing')
WARNING_MISSING_DEF_INCL_ODB = Code('W04', 'missing def incl. ODB')
ERROR_ITEM_INCLUDED_MULTIPLE_TIMES = Code('E01', 'item included multiple')
ERROR_INCLUDE_COULD_NOT_BE_PARSED = Code('E03', 'include parsing error')
ERROR_INVALID_INPUT = Code('E05', 'invalid input')
ERROR_UNKNOWN_ELEM = Code('E06', 'unrecognized import element')
ERROR_KEYS_MISSING = Code('E08', 'missing keys')
ERROR_INVALID_SEC_DEF_TYPE = Code('E09', 'invalid sec def type')
ERROR_INVALID_KEY = Code('E10', 'invalid key')
ERROR_SERVICE_NAME_MISSING = Code('E11', 'service name missing')
ERROR_SERVICE_MISSING = Code('E12', 'service missing')
ERROR_MISSING_DEP = Code('E13', 'dependency missing')
ERROR_COULD_NOT_IMPORT_OBJECT = Code('E13', 'could not import object')
ERROR_TYPE_MISSING = Code('E04', 'type missing')
Error_Include_Not_Found = Code('E14', 'include not found')

# ################################################################################################################################

outconn_wsx  = COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_WSX
outconn_ldap = COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_LDAP

_prefix_generic = 'zato_generic_connection'
_attr_outconn_wsx = f'{_prefix_generic}_{outconn_wsx}'
_attr_outconn_ldap = f'{_prefix_generic}_{outconn_ldap}'

# We need to have our own version because type "bearer_token" exists in enmasse only.
_All_Sec_Def_Types = All_Sec_Def_Types + ['bearer_token']

_pubsub_default = Common_PubSub.DEFAULT

zato_name_prefix = (
    'admin.',
    'admin.invoke',
    'ide_publisher',
    'pub.zato',
    'pubsub.demo',
    'pubsub.test',
    'zato.',
    '/zato',
    'zato.pubsub',
)


# ################################################################################################################################

def has_name_zato_prefix(name:'str') -> 'bool':
    name = name or ''
    for prefix in zato_name_prefix:
        if name.startswith(prefix):
            return True
    return False

# ################################################################################################################################

class ModuleCtx:

    class Include_Type:
        All  = 'all'
        LDAP = 'ldap'
        SQL  = 'sql'
        PubSub = 'pubsub'
        REST = 'rest'
        Scheduler = 'scheduler'
        Security = 'security'

    # An indicator that this is an include directive
    Item_Type_Include = 'include'

    # Maps enmasse definition types to include types
    Enmasse_Type = cast_('strdict', None)

    # Maps enmasse defintions types to their attributes that are to be included during an export
    Enmasse_Attr_List_Include = cast_('strlistdict', None)

    # Maps enmasse defintions types to their attributes that are to be excluded during an export
    Enmasse_Attr_List_Exclude = cast_('strlistdict', None)

    # Maps enmasse defintions types to their attributes that need to be renamed during an export
    Enmasse_Attr_List_Rename = cast_('strdictdict', None)

    # Maps enmasse values that need to be renamed during an export
    Enmasse_Attr_List_Value_Rename = cast_('strdictdict', None)

    # Maps enmasse values that need to be renamed during an import
    Enmasse_Attr_List_Value_Rename_Reverse = cast_('strdictdict', None)

    # Maps enmasse defintions types to their attributes that need to be converted to a list during an export
    Enmasse_Attr_List_As_List = cast_('strlistdict', None)

    # Maps enmasse defintions types to their attributes that will be always skipped during an export
    Enmasse_Attr_List_Skip_Always = cast_('strlistdict', None)

    # Maps enmasse defintions types to their attributes that will be skipped during an export if they are empty
    Enmasse_Attr_List_Skip_If_Empty = cast_('strlistdict', None)

    # Maps enmasse defintions types to their attributes that will be skipped during an export if they are True
    Enmasse_Attr_List_Skip_If_True = cast_('strlistdict', None)

    # Maps enmasse defintions types to their attributes that will be skipped during an export if they are False
    Enmasse_Attr_List_Skip_If_False = cast_('strlistdict', None)

    # Maps enmasse defintions types to their attributes that will be skipped during an export if their value matches configuration
    Enmasse_Attr_List_Skip_If_Value_Matches = cast_('strdictdict', None)

    # Maps enmasse defintions types to their attributes that will be skipped during an export if other values matche configuration
    Enmasse_Attr_List_Skip_If_Other_Value_Matches = cast_('strdict', None)

    # Maps enmasse defintions types to their attributes that will be turned into multiline strings
    Enmasse_Attr_List_As_Multiline = cast_('strlistdict', None)

    # Maps enmasse types to default values of their attributes
    Enmasse_Attr_List_Default_By_Type = cast_('strdictdict', None)

    # Maps pre-3.2 item types to the 3.2+ ones
    Enmasse_Item_Type_Name_Map = cast_('strdict', None)

    # As above, in the reverse direction
    Enmasse_Item_Type_Name_Map_Reverse = cast_('strdict', None)

    # As above, in the reverse direction, but only for specific types
    Enmasse_Item_Type_Name_Map_Reverse_By_Type = cast_('strdict', None)

    # How to sort attributes of a given object during an export
    Enmasse_Attr_List_Sort_Order = cast_('strlistdict', None)

    # How many seconds to wait for servers to start up
    Initial_Wait_Time = 60 * 60 * 12 # In seconds = 12 hours

    # How many seconds to wait for missing objects
    Missing_Wait_Time = 120

    # Extra security types that exist only in enmasse, such as bearer_token in lieu of oauth
    Extra_Security_Types = ['bearer_token']

# ################################################################################################################################

ModuleCtx.Enmasse_Type = {

    # REST connections
    'channel_plain_http': ModuleCtx.Include_Type.REST,
    'outconn_plain_http': ModuleCtx.Include_Type.REST,
    'zato_generic_rest_wrapper': ModuleCtx.Include_Type.REST,
    'zato_generic_connection': ModuleCtx.Include_Type.LDAP,

    # Security definitions
    'def_sec': ModuleCtx.Include_Type.Security,

    # Security definitions
    'security_groups': ModuleCtx.Include_Type.Security,

    # SQL Connections
    'outconn_sql':ModuleCtx.Include_Type.SQL,

    # Scheduler
    'scheduler':ModuleCtx.Include_Type.Scheduler,

    # Pub/sub
    'pubsub_topic':ModuleCtx.Include_Type.PubSub,
    'pubsub_endpoint':ModuleCtx.Include_Type.PubSub,
    'pubsub_sub':ModuleCtx.Include_Type.PubSub,
    'pubsub_subscription':ModuleCtx.Include_Type.PubSub,
}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Include = {

    # Security definitions
    'def_sec':  [
        'type',
        'name',
        'username',
        'realm',
        'auth_server_url',
        'client_id_field',
        'client_secret_field',
        'grant_type',
        'scopes',
        'extra_fields',
    ],

    # REST connections - Channels
    'channel_plain_http': [
        'name',
        'service',
        'url_path',
        'security_name',
        'security_groups',
        'is_active',
        'data_format',
        'connection',
        'transport',
    ],

    # REST connections - outgoing connections
    'outconn_plain_http': [
        'name',
        'host',
        'url_path',
        'security_name',
        'is_active',
        'data_format',
        'connection',
        'transport',
    ],

    # Scheduled tasks
    'scheduler':  [
        'name',
        'service',
        'job_type',
        'start_date',
        'weeks',
        'days',
        'hours',
        'minutes',
        'seconds',
        'cron_definition',
        'repeats',
        'extra',
    ],

    # LDAP outgoing connections
    _attr_outconn_ldap: [
        'type_',
        'name',
        'username',
        'auth_type',
        'server_list',
    ],

    # Outgoing WSX connections
    _attr_outconn_wsx: [
        'name',
        'address',
        'data_format',
        'has_auto_reconnect',
        'on_connect_service_name',
        'on_message_service_name',
        'on_close_service_name',
        'subscription_list',
    ],

    # Pub/sub - Endpoints
    'pubsub_endpoint':  [
        'name',
        'endpoint_type',
        'service_name',
        'topic_patterns',
        'sec_name',
    ],

    # Pub/sub - Topics
    'pubsub_topic':  [
        'name',
        'has_gd',
        'hook_service_name',
    ],

}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Exclude = {

    # REST connections - Channels
    'channel_plain_http': [
        'connection',
        'service_name',
        'transport',
    ],

    # REST connections - outgoing connections
    'outconn_plain_http': [
        'connection',
        'transport',
    ],

}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Rename = {

    # Security definitions
    'def_sec':  {
        'auth_server_url':'auth_endpoint'
    },

    # Pub/sub endpoints
    'pubsub_endpoint':  {
        'sec_name':'security_name'
    }

}

# ################################################################################################################################

#
# This is used during export
#
ModuleCtx.Enmasse_Attr_List_Value_Rename = {

    # Security definitions
    'def_sec':  {
        'type': [{'oauth':'bearer_token'}]
    },

    # Pub/sub endpoints
    'pubsub_endpoint':  {
        'endpoint_type': [{'srv':'service'}]
    },

    # Pub/sub subscriptions
    'pubsub_subscription':  {
        'endpoint_type': [{'srv':'service'}]
    },
}

# ################################################################################################################################

#
# This is used during import
#
ModuleCtx.Enmasse_Attr_List_Value_Rename_Reverse = {

    # Pub/sub endpoints
    'pubsub_endpoint':  {
        'endpoint_type': [{'service':'srv'}]
    },

    # Pub/sub subscriptions
    'pubsub_subscription':  {
        'endpoint_type': [{'service':'srv'}]
    },

    # Security - OAuth & Bearer Token
    'security':  {
        'type': [{'bearer_token':'oauth'}]
    },

}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_As_List = {

    # Security definitions
    'def_sec':  ['scopes', 'extra_fields'],
}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Skip_Always = {

    # Security groups
    'security_groups':  ['description', 'group_id', 'member_count', 'type'],
}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Skip_If_Empty = {

    # Security definitions
    'scheduler':  ['weeks', 'days', 'hours', 'minutes', 'seconds', 'cron_definition', 'repeats', 'extra'],

    # REST channels
    'channel_plain_http': ['data_format'],

    # Outgoing WSX connections
    _attr_outconn_wsx:  ['data_format', 'subscription_list'],

    # Pub/sub - Topics
    'pubsub_topic':  [
        'hook_service_name',
    ],

    # Pub/sub - Subscriptions
    'pubsub_subscription':  [
        'rest_connection',
        'service',
        'service_name',
    ],

}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Skip_If_True = {

    # Outgoing WSX connections
    _attr_outconn_wsx:  ['has_auto_reconnect'],
}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Skip_If_False = {

    # Pub/sub - Topics
    'pubsub_topic':  [
        'has_gd',
    ],
}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Skip_If_Value_Matches = {

    # E-Mail IMAP
    'email_imap':  {'get_criteria':'UNSEEN', 'timeout':10},

    # Pub/sub - Endpoints
    'pubsub_endpoint':  {'security_name':Zato_No_Security},

    # Pub/sub - Subscriptions
    'pubsub_subscription':  {'delivery_server':'server1'},
}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Skip_If_Other_Value_Matches = {

    # Security definitions
    'def_sec':  [
        {'criteria':[{'type':'apikey'}], 'attrs':['username']},
    ],

    # Pub/sub subscriptions
    'pubsub_subscription':  [
        {'criteria':[{'delivery_method':'pull'}], 'attrs':['rest_method', 'rest_connection']},
        {'criteria':[{'endpoint_type':'service'}], 'attrs':['rest_method', 'rest_connection']},
    ],
}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_As_Multiline = {

    # Security definitions
    'scheduler':  ['extra'],
    'pubsub_endpoint':  ['topic_patterns'],
}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Default_By_Type = {

    'pubsub_endpoint':  {
        'is_internal': False,
        'role': Common_PubSub.ROLE.PUBLISHER_SUBSCRIBER.id,

        # Note that it is not security_name because it has been already re-mapped to sec_name
        # by the time this check is taking place.
        'sec_name': Zato_No_Security,

    },

    'pubsub_topic':  {
        'has_gd': False,
        'is_api_sub_allowed': True,
        'max_depth_gd': _pubsub_default.TOPIC_MAX_DEPTH_GD,
        'max_depth_non_gd': _pubsub_default.TOPIC_MAX_DEPTH_NON_GD,
        'depth_check_freq': _pubsub_default.DEPTH_CHECK_FREQ,
        'pub_buffer_size_gd': _pubsub_default.PUB_BUFFER_SIZE_GD,
        'task_sync_interval': _pubsub_default.TASK_SYNC_INTERVAL,
        'task_delivery_interval': _pubsub_default.TASK_DELIVERY_INTERVAL,
    },

    'pubsub_subscription':  {
        'should_ignore_if_sub_exists': True,
        'should_delete_all': True,
    },

    'channel_rest': {
        'security_name': Zato_No_Security,
        'merge_url_params_req': True,
    },

    'outgoing_rest': {
        'security_name': Zato_No_Security,
        'merge_url_params_req': True,
    }
}

# ################################################################################################################################

ModuleCtx.Enmasse_Item_Type_Name_Map = {
    'def_sec': 'security',
    'channel_plain_http': 'channel_rest',
    'outconn_plain_http': 'outgoing_rest',
    'zato_generic_connection_outconn-ldap': 'outgoing_ldap',
    'zato_generic_connection_outconn-wsx': 'outgoing_wsx',
}

# ################################################################################################################################

ModuleCtx.Enmasse_Item_Type_Name_Map_Reverse = {}
for key, value in ModuleCtx.Enmasse_Item_Type_Name_Map.items():
    ModuleCtx.Enmasse_Item_Type_Name_Map_Reverse[value] = key

# ################################################################################################################################

ModuleCtx.Enmasse_Item_Type_Name_Map_Reverse_By_Type = {
    'pubsub_endpoint':  [{'security_name':'sec_name'}],
    'pubsub_subscription':  [{'topic_list':'topic_list_json'}],
}

# ################################################################################################################################

ModuleCtx.Enmasse_Attr_List_Sort_Order = {

    # REST connections - Channels
    'channel_plain_http': [
        'name',
        'service',
        'url_path',
        'security_name',
    ],

    # REST connections - outgoing connections
    'outconn_plain_http': [
        'name',
        'host',
        'url_path',
        'security_name',
        'is_active',
        'data_format',
    ],

    # Security definitions
    'def_sec':  [
        'name',
        'username',
        'password',
        'type',
        'realm',
        'auth_endpoint',
        'client_id_field',
        'client_secret_field',
        'grant_type',
        'scopes',
        'extra_fields',
    ],

    # Security groups
    'security_groups': [
        'name',
        'members',
    ],

    # Scheduled tasks
    'scheduler':  [
        'name',
        'service',
        'job_type',
        'start_date',
        'weeks',
        'days',
        'hours',
        'minutes',
        'seconds',
        'cron_definition',
        'repeats',
        'extra',
    ],

    # Outgoing WSX connections
    f'zato_generic_connection_{outconn_wsx}': [
        'name',
        'address',
        'data_format',
        'has_auto_reconnect',
        'on_connect_service_name',
        'on_message_service_name',
        'on_close_service_name',
        'subscription_list',
    ],

    # Pub/sub - Endpoints
    'pubsub_endpoint':  [
        'name',
        'endpoint_type',
        'security_name',
        'service_name',
        'topic_patterns',
    ],

    # Pub/sub - Topics
    'pubsub_topic':  [
        'name',
        'has_gd',
        'hook_service_name',
    ],

    # Pub/sub - Subscription
    'pubsub_subscription':  [
        'name',
        'endpoint_name',
        'endpoint_type',
        'delivery_method',
        'rest_connection',
        'rest_method',
        'delivery_server',
        'topic_list',
    ],

}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EnvKeyData:
    def_type:   'str'
    name:       'str'
    attr_name:  'str'
    attr_value: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _replace_item_type(is_import:'bool', item_type:'str') -> 'str':

    # Certain item types need to be replaced because they exist only in enmasse

    if is_import:
        if item_type == 'bearer_token':
            return 'oauth'
        else:
            return item_type

    else:
        if item_type == 'oauth':
            return 'bearer_token'
        else:
            return item_type

# ################################################################################################################################

def find_first(it, pred): # type: ignore
    """ Given any iterable, return the first element `elem` from it matching `pred(elem)`.
    """
    for obj in it: # type: ignore
        if pred(obj):
            return obj # type: ignore

# ################################################################################################################################

def dict_match(item_type, item, fields): # type: ignore
    """ Returns True if input item has all the fields matching.
    """

    for key, value in fields.items(): # type: ignore
        item_value = item.get(key)    # type: ignore
        if item_value != value:
            return False

    # If we are here, it means that we had a match
    return True

# ################################################################################################################################

#: List of zato services we explicitly don't support.
IGNORE_PREFIXES = {
    'zato.kvdb.data-dict.dictionary',
    'zato.kvdb.data-dict.translation',
}

# ################################################################################################################################

def try_keys(item:'strdict', keys:'strlist') -> 'any_':
    for key in keys:
        if value := item.get(key, NotGiven):
            if value is not NotGiven:
                return value
    else:
        raise Exception(f'Keys were not found -> {keys} -> {item}')

# ################################################################################################################################

def populate_services_from_apispec(client, logger): # type: ignore
    """ Request a list of services from the APISpec service, and merge the results into SERVICES_BY_PREFIX,
    creating new ServiceInfo instances to represent previously unknown services as appropriate.
    """

    # Python 2/3 compatibility
    from zato.common.ext.future.utils import iteritems

    response:'any_' = client.invoke('zato.apispec.get-api-spec', {
        'return_internal': True,
        'include': '*',
        'needs_sphinx': False
    })

    if not response.ok:
        logger.error('Could not fetch service list -> %s', response.inner.text)
        return

    by_prefix = {}  # { "zato.apispec": {"get-api-spec": { .. } } }

    for service in response.data: # type: ignore
        prefix, _, name = service['name'].rpartition('.') # type: ignore
        methods = by_prefix.setdefault(prefix, {}) # type: ignore
        methods[name] = service

    # Services belonging here may not have all the CRUD methods and it is expected that they do not
    allow_incomplete_methods = [
        'zato.outgoing.redis',
        'zato.pubsub.subscription',
        'zato.security',
        'zato.security.rbac.client-role'
    ]

    for prefix, methods in iteritems(by_prefix): # type: ignore

        # Ignore prefixes lacking 'get-list', 'create' and 'edit' methods.
        if not all(n in methods for n in ('get-list', 'create', 'edit')):

            # RBAC client roles cannot be edited so it is fine that they lack the 'edit' method.
            if prefix not in allow_incomplete_methods:
                continue

        if prefix in IGNORE_PREFIXES:
            continue

        service_info = SERVICE_BY_PREFIX.get(prefix)
        if service_info is None:
            service_info = ServiceInfo(prefix=prefix, name=make_service_name(prefix))
            SERVICE_BY_PREFIX[prefix] = service_info
            SERVICE_BY_NAME[service_info.name] = service_info
            SERVICES.append(service_info)

        service_info.methods = methods

# The common prefix for a set of services is tested against the first element in this list using startswith().
# If it matches, that prefix is replaced by the second element. The prefixes must match exactly if the first element
# does not end in a period.
SHORTNAME_BY_PREFIX:'anylist' = [
    ('zato.pubsub.', 'pubsub'),
    ('zato.definition.', 'def'),
    ('zato.email.', 'email'),
    ('zato.message.namespace', 'def_namespace'),
    ('zato.cloud.aws.s3', 'cloud_aws_s3'),
    ('zato.message.json-pointer', 'json_pointer'),
    ('zato.notif.', 'notif'),
    ('zato.outgoing.', 'outconn'),
    ('zato.scheduler.job', 'scheduler'),
    ('zato.search.', 'search'),
    ('zato.security.tls.channel', 'tls_channel_sec'),
    ('zato.security.', ''),
    ('zato.channel.', ''),
]

# ################################################################################################################################

def make_service_name(prefix): # type: ignore

    # This can be done quickly
    if 'groups' in prefix:
        return 'security_groups'

    # stdlib
    import re

    escaped = re.sub('[.-]', '_', prefix)
    for module_prefix, name_prefix in SHORTNAME_BY_PREFIX:
        if prefix.startswith(module_prefix) and module_prefix.endswith('.'):
            name = escaped[len(module_prefix):]
            if name_prefix:
                name = '{}_{}'.format(name_prefix, name)
            return name
        elif prefix == module_prefix:
            return name_prefix

    return escaped

# ################################################################################################################################

def normalize_service_name(item): # type: ignore
    """ Given an item originating from the API or from an import file, if the item contains either the 'service'
    or 'service_name' keys, ensure the other key is set. Either the dict contains neither key, or both keys set
    to the same value."""
    if 'service' in item or 'service_name' in item:
        item.setdefault('service', item.get('service_name'))
        item.setdefault('service_name', item.get('service'))

# ################################################################################################################################

def test_item(item, condition): # type: ignore
    """ Given a dictionary `cond` containing some conditions to test an item for, return True if those conditions match.
    Currently only supports testing whether a field has a particular value. Returns ``True`` if `cond` is ``None``."""

    if condition is not None:

        condition = condition if isinstance(condition, list) else [condition] # type: ignore

        for condition_config in condition: # type: ignore

            only_if_field:'any_' = condition_config.get('only_if_field')
            only_if_value:'any_' = condition_config.get('only_if_value')

            if not isinstance(only_if_value, (list, tuple)):
                only_if_value = [only_if_value]

            if only_if_field and item.get(only_if_field) not in only_if_value:
                return False

    return True

# ################################################################################################################################

# Note that the order of items in this list matters
_security_fields = ['security', 'sec_def', 'security_name']

# All keys under which a security name can be found
_security_keys = ['security_name', 'sec_name', 'sec_def']

# ################################################################################################################################

def resolve_security_field_name(item:'strdict') -> 'str':

    default = 'security'

    for name in _security_fields:
        if name in item:
            return name
    else:
        return default

# ################################################################################################################################
# ################################################################################################################################

class ServiceInfo:
    def __init__(self, prefix=None, name=None, object_dependencies=None, service_dependencies=None, export_filter=None): # type: ignore
        assert name or prefix

        # Short service name as appears in export data.
        self.name = cast_('str', name or prefix)

        # Optional name of the object enumeration/retrieval service.
        self.prefix = prefix

        # Overwritten by populate_services_from_apispec().
        self.methods = {}

        # Specifies a list of object dependencies:
        # field_name: {"dependent_type": "shortname", "dependent_field":
        # "fieldname", "empty_value": None, or e.g. Zato_No_Security}
        self.object_dependencies = object_dependencies or {}

        # Specifies a list of service dependencies. The field's value contains
        # the name of a service that must exist.
        # field_name: {"only_if_field": "field_name" or None, "only_if_value": "value" or None}
        self.service_dependencies = service_dependencies or {}

        # List of field/value specifications that should be ignored during export:
        # field_name: value
        self.export_filter = export_filter or {}

# ################################################################################################################################

    @property
    def is_security(self): # type: ignore
        """ If True, indicates the service is source of authentication credentials for use in another service.
        """
        return self.prefix and self.prefix.startswith('zato.security.') # type: ignore

# ################################################################################################################################

    def get_service_name(self, method): # type: ignore
        return self.methods.get(method, {}).get('name') # type: ignore

# ################################################################################################################################

    def get_required_keys(self): # type: ignore
        """ Return the set of keys required to create a new instance.
        """
        method_sig:'any_' = self.methods.get('create')
        if method_sig is None:
            return set() # type: ignore

        input_required:'any_' = method_sig.get('input_required', [])
        required = {elem['name'] for elem in input_required}
        required.discard('cluster_id')
        return required

# ################################################################################################################################

    def __repr__(self):
        return '<ServiceInfo for {}>'.format(self.prefix)

# ServiceInfo templates for services that have additional semantics not yet described by apispec.
# To be replaced by introspection later.
SERVICES = [
    ServiceInfo(
        name='channel_amqp',
        prefix='zato.channel.amqp',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_amqp',
                'dependent_field': 'name',
            },
        },
        service_dependencies={
            'service_name': {}
        },
    ),
    ServiceInfo(
        name='web_socket',
        prefix='zato.channel.web-socket',
        object_dependencies={
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': Zato_No_Security,
                'id_field': 'security_id',
            },
        },
        service_dependencies={
            'service': {}
        },
    ),

    ServiceInfo(
        name='pubsub_endpoint',
        prefix='zato.pubsub.endpoint',
        object_dependencies={
            'ws_channel_name': {
                'dependent_type': 'web_socket',
                'dependent_field': 'name',
                'condition': {
                    'only_if_field': 'endpoint_type',
                    'only_if_value': 'wsx',
                },
                'id_field': 'ws_channel_id',
            },
            'sec_name': {
                'dependent_type': 'basic_auth',
                'dependent_field': 'name',
                'empty_value': Zato_No_Security,
                'condition': {
                    'only_if_field': 'endpoint_type',
                    'only_if_value': ['soap', 'rest'],
                },
                'id_field': 'security_id',
            }
        },
    ),

    ServiceInfo(
        name='pubsub_subscription',
        prefix='zato.pubsub.subscription',
        object_dependencies={
            'endpoint_name': {
                'dependent_type': 'pubsub_endpoint',
                'dependent_field': 'name',
            },
            'rest_connection': {
                'dependent_type': 'http_soap',
                'dependent_field': 'name',
                'condition': [
                {
                    'only_if_field': 'endpoint_type',
                    'only_if_value': ['soap', 'rest'],
                },
                {
                    'only_if_field': 'delivery_method',
                    'only_if_value': ['push'],
                }
                ],
            },
        },
    ),

    ServiceInfo(
        name='channel_jms_wmq',
        prefix='zato.channel.jms-wmq',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_jms_wmq',
                'dependent_field': 'name',
            },
        },
        service_dependencies={
            'service_name': {}
        },
    ),
    ServiceInfo(
        name='channel_zmq',
        prefix='zato.channel.zmq',
        service_dependencies={
            'service_name': {}
        },
    ),
    ServiceInfo(
        name='def_sec',
        prefix='zato.security',
    ),
    ServiceInfo(
        name='http_soap',
        prefix='zato.http-soap',
        # Covers outconn_plain_http, outconn_soap, channel_plain_http, channel_soap
        object_dependencies={
            'security': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': Zato_No_Security,
                'id_field': 'security_id',
            },
            'sec_def': {
                'dependent_type': 'def_sec',
                'dependent_field': 'name',
                'empty_value': Zato_No_Security,
                'id_field': 'security_id',
            },
        },
        service_dependencies={
            'service_name': {
                'id_field': 'service_id',
                'condition': {
                    'only_if_field': 'connection',
                    'only_if_value': 'channel',
                },
            }
        },
        export_filter={
            'is_internal': True,
        }
    ),
    ServiceInfo(
        name='scheduler',
        service_dependencies={
            'service_name': {
                'id_field': 'service_id',
            }
        },
    ),
    ServiceInfo(
        name='notif_sql',
        prefix='zato.notif.sql',
        object_dependencies={
            'def_name': {
                'dependent_type': 'outconn_sql',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='outconn_amqp',
        prefix='zato.outgoing.amqp',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_amqp',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='outconn_jms_wmq',
        prefix='zato.outgoing.jms-wmq',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_jms_wmq',
                'dependent_field': 'name',
            },
        },
    ),
    ServiceInfo(
        name='outconn_redis',
        prefix='zato.outgoing.redis',
    ),
    ServiceInfo(
        name='query_cassandra',
        prefix='zato.query.cassandra',
        object_dependencies={
            'def_name': {
                'dependent_type': 'def_cassandra',
                'dependent_field': 'name',
                'empty_value': Zato_No_Security,
            },
        },
    ),
]

SERVICE_BY_NAME = {info.name: info for info in SERVICES}
SERVICE_BY_PREFIX = {info.prefix: info for info in SERVICES}

HTTP_SOAP_KINDS = (
    # item_type             connection      transport
    ('channel_soap',        'channel',      'soap'),
    ('channel_plain_http',  'channel',      'plain_http'),
    ('outconn_soap',        'outgoing',     'soap'),
    ('outconn_plain_http',  'outgoing',     'plain_http')
)

HTTP_SOAP_ITEM_TYPES = {elem[0] for elem in HTTP_SOAP_KINDS}

# ################################################################################################################################
# ################################################################################################################################

class _DummyLink: # type: ignore
    """ Pip requires URLs to have a .url attribute.
    """
    def __init__(self, url): # type: ignore
        self.url = url

# ################################################################################################################################
# ################################################################################################################################

class Notice:

    def __init__(self, value_raw, value, code): # type: ignore
        self.value_raw = value_raw
        self.value = value
        self.code = code

    def __repr__(self):
        return "<{} at {} value_raw:'{}' value:'{}' code:'{}'>".format(
            self.__class__.__name__, hex(id(self)), self.value_raw,
            self.value, self.code)

# ################################################################################################################################
# ################################################################################################################################


class Results:
    def __init__(self, warnings=None, errors=None, service=None): # type: ignore

        # List of Warning instances
        self.warnings = warnings or []

        # List of Error instances
        self.errors = errors or []

        self.service_name = service.get_name() if service else None

    def add_error(self, raw, code, msg, *args): # type: ignore
        if args:
            msg:'any_' = msg.format(*args)
        _:'any_' = self.errors.append(Notice(raw, msg, code))

# ################################################################################################################################

    def add_warning(self, raw, code, msg, *args): # type: ignore
        if args:
            msg:'any_' = msg.format(*args)
        _:'any_'= self.warnings.append(Notice(raw, msg, code))

# ################################################################################################################################

    @property
    def ok(self):
        return not (self.warnings or self.errors)

# ################################################################################################################################
# ################################################################################################################################

class InputValidator:
    def __init__(self, json): # type: ignore
        #: Validation result.
        self.results = Results()
        #: Input JSON to validate.
        self.json = json

# ################################################################################################################################

    def validate(self):
        # type: () -> Results

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        for item_type, items in iteritems(self.json): # type: ignore
            for item in items: # type: ignore
                self.validate_one(item_type, item)

        return self.results

# ################################################################################################################################

    def validate_one(self, item_type:'str', item:'strdict') -> 'None':
        if item_type not in SERVICE_BY_NAME:
            raw = (item_type, sorted(SERVICE_BY_NAME))
            self.results.add_error(raw, ERROR_INVALID_KEY, "Invalid key '{}', must be one of '{}'", item_type, sorted(SERVICE_BY_NAME))
            return

        item_dict = dict(item)
        service_info = SERVICE_BY_NAME[item_type]
        required_keys:'any_' = service_info.get_required_keys()

        # OK, the keys are there, but do they all have non-None values?
        for req_key in required_keys:
            if item.get(req_key) is None: # 0 or '' can be correct values
                raw = (req_key, required_keys, item_dict, item_type)
                self.results.add_error(raw, ERROR_KEYS_MISSING, "Key '{}' must exist in {}: {}", req_key, item_type, item_dict)

# ################################################################################################################################
# ################################################################################################################################

class DependencyScanner:

    def __init__(self, json:'strdict', is_import:'bool', is_export:'bool', ignore_missing:'bool'=False) -> 'None':
        self.json = json
        self.is_import = is_import
        self.is_export = is_export
        self.ignore_missing = ignore_missing
        self.missing = {}

# ################################################################################################################################

    def find_sec(self, fields:'strdict') -> 'strdictnone':

        for service in SERVICES:
            if service.is_security:
                service_name = service.name # _replace_item_type(False, service.name)
                item = self.find(service_name, fields)
                if item is not None:
                    return item

# ################################################################################################################################

    def find(self, item_type:'str', fields:'strdict') -> 'strdictnone':

        if item_type in ['def_sec']:
            return self.find_sec(fields)

        items = self.json.get(item_type, ())

        for item in items:
            if dict_match(item_type, item, fields):
                return item

# ################################################################################################################################

    def scan_item(self, item_type:'str', item:'Bunch', results:'Results') -> 'None':
        """ Scan the data of a single item for required dependencies, recording any that are missing in self.missing.
        """

        missing_item:'any_'

        #
        # Preprocess item type
        #
        if item_type == 'bearer_token':
            item_type = 'oauth'

        service_info = SERVICE_BY_NAME[item_type] # type: ServiceInfo

        for dep_key, dep_info in service_info.object_dependencies.items(): # type: ignore

            if not test_item(item, dep_info.get('condition')):
                continue

            if item.get('security_id') == 'ZATO_SEC_USE_RBAC':
                continue

            # Special-case HTTP connections
            if item_type == 'http_soap': # type: ignore
                dep_key = resolve_security_field_name(item)

            if dep_key not in item:
                results.add_error(
                    (dep_key, dep_info), ERROR_MISSING_DEP, '{} lacks required `{}` field: {}', item_type, dep_key, item)

            value:'any_' = item.get(dep_key)

            if value != dep_info.get('empty_value'):

                dep_type:'any_' = dep_info['dependent_type']
                dep_field:'any_' = dep_info['dependent_field']

                dep = self.find(dep_type, {dep_field: value})

                if dep is None:

                    key = (dep_type, value)
                    name:'str' = item.get('name') or ''

                    # Do not report internal objects that have not been exported
                    if has_name_zato_prefix(name):
                        continue

                    # Same here
                    if has_name_zato_prefix(value):
                        continue

                    if name:
                        missing_item = name
                    else:
                        missing_item = [item_type, key]

                    missing_items:'any_' = self.missing.setdefault(key, [])
                    missing_items.append(missing_item)

# ################################################################################################################################

    def scan(self) -> 'Results':

        results = Results()
        for item_type, items in self.json.items():

            #
            # Preprocess item type
            #
            item_type = _replace_item_type(True, item_type)

            for item in items:
                self.scan_item(item_type, item, results)

        if not self.ignore_missing:
            for (missing_type, missing_name), dep_names in sorted(self.missing.items()): # type: ignore
                existing = sorted(item.name for item in self.json.get(missing_type, []))
                raw:'any_' = (missing_type, missing_name, dep_names, existing)

                results.add_warning(
                    raw, WARNING_MISSING_DEF, "'{}' is needed by '{}' but was not among '{}'",
                        missing_name, sorted(dep_names), existing)

        return results

# ################################################################################################################################
# ################################################################################################################################

class ObjectImporter:
    def __init__(
        self,
        client,     # type: APIClient
        logger,     # type: Logger
        object_mgr, # type: ObjectManager
        json,       # type: strdict
        is_import,  # type: bool
        is_export,  # type: bool
        ignore_missing, # type: bool
        args            # type: any_
    ) -> 'None':

        # Bunch
        from bunch import bunchify

        # Zato client.
        self.client:'any_' = client

        self.logger = logger

        # Validation result.
        self.results = Results()

        # ObjectManager instance.
        self.object_mgr = object_mgr

        # JSON to import.
        self.json = bunchify(json)

        # Command-line arguments
        self.args = args

        self.is_import = is_import
        self.is_export = is_export

        self.ignore_missing = ignore_missing

# ################################################################################################################################

    def validate_service_required(self, item_type, item): # type: ignore

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        service_info = SERVICE_BY_NAME[item_type]
        item_dict:'any_' = dict(item)

        for dep_field, dep_info in iteritems(service_info.service_dependencies): # type: ignore
            if not test_item(item, dep_info.get('condition')):
                continue

            service_name:'any_' = item.get(dep_field)
            raw:'any_' = (service_name, item_dict, item_type)
            if not service_name:
                self.results.add_error(raw, ERROR_SERVICE_NAME_MISSING,
                    'No {} service key defined type {}: {}', dep_field, item_type, item_dict)
            elif service_name not in self.object_mgr.services:
                self.results.add_error(raw, ERROR_SERVICE_MISSING,
                    'Service `{}` from `{}` missing in ODB ({})', service_name, item_dict, item_type)

# ################################################################################################################################

    def validate_import_data(self):

        results = Results()
        dep_scanner = DependencyScanner(
            self.json,
            self.is_import,
            self.is_export,
            ignore_missing=self.ignore_missing
        )
        scan_results = dep_scanner.scan()

        if not scan_results.ok:
            return scan_results

        for warning in scan_results.warnings: # type: ignore
            missing_type, missing_name, dep_names, existing = warning.value_raw # type: ignore
            if not self.object_mgr.find(missing_type, {'name': missing_name}):
                raw:'any_' = (missing_type, missing_name)
                results.add_warning(raw, WARNING_MISSING_DEF_INCL_ODB, "Definition '{}' not found in JSON/ODB ({}), needed by '{}'",
                                    missing_name, missing_type, dep_names)

        for item_type, items in self.json.items(): # type: ignore

            #
            # Preprocess item type
            #
            item_type = _replace_item_type(True, item_type)

            for item in items: # type: ignore
                self.validate_service_required(item_type, item)

        return results

# ################################################################################################################################

    def remove_from_import_list(self, item_type, name): # type: ignore

        #
        # Preprocess item type
        #

        list_:'any_' = self.json.get(item_type, [])
        item = find_first(list_, lambda item: item.name == name) # type: ignore
        if item:
            _:'any_' = list_.remove(item)
        else:
            raise KeyError('Tried to remove missing %r named %r' % (item_type, name))

# ################################################################################################################################

    def should_skip_item(self, item_type, attrs, is_edit): # type: ignore

        # Plain HTTP channels cannot create JSON-RPC ones
        if item_type == 'http_soap' and attrs.name.startswith('json.rpc.channel'):
            return True

        # Root RBAC role cannot be edited
        elif item_type == 'rbac_role' and attrs.name == 'Root':
            return True

        # RBAC client roles cannot be edited
        elif item_type == 'rbac_client_role' and is_edit:
            return True

# ################################################################################################################################

    def _set_generic_connection_secret(self, name, type_, secret): # type: ignore

        response:'any_' = self.client.invoke('zato.generic.connection.change-password', {
            'name': name,
            'type_': type_,
            'password1': secret,
            'password2': secret
        })

        if not response.ok:
            raise Exception('Unexpected response; e:{}'.format(response))
        else:
            self.logger.info('Set password for generic connection `%s` (%s)', name, type_)

# ################################################################################################################################

    def _needs_change_password(self, item_type, attrs, is_edit): # type: ignore

        # By default, assume that we do need to change a given password.
        out = True

        if is_edit and item_type == 'rbac_role_permission':
            out = False

        if item_type == 'zato_generic_connection' and attrs.get('type_') == COMMON_GENERIC.CONNECTION.TYPE.OUTCONN_WSX:
            out = False

        if item_type == 'pubsub_subscription':
            out = False

        return out

# ################################################################################################################################

    def _resolve_attrs(self, item_type:'str', attrs:'any_') -> 'any_':

        for key, orig_value in attrs.items():

            # .. preprocess values only if they are strings ..
            if isinstance(orig_value, str):

                if orig_value.startswith(zato_enmasse_env1):
                    _prefix = zato_enmasse_env1
                elif orig_value.startswith(zato_enmasse_env2):
                    _prefix = zato_enmasse_env2
                else:
                    _prefix = None

                if _prefix:

                    value = orig_value.split(_prefix)
                    value = value[1]

                    if not value:
                        raise Exception('Could not build a value from `{}` in `{}`'.format(orig_value, item_type))
                    else:
                        value = os.environ.get(value, NotGiven)
                        if value is NotGiven:
                            if key.startswith(('is_', 'should_', 'needs_')):
                                value = None
                            else:
                                value = 'Env-Value-Not-Found-' + orig_value + '.' + uuid4().hex

                    attrs[key] = value

        return attrs

# ################################################################################################################################

    def _import(self, item_type:'str', attrs:'any_', is_edit:'bool') -> 'None':

        # First, resolve values pointing to parameter placeholders and environment variables ..
        attrs = self._resolve_attrs(item_type, attrs)

        #
        # Preprocess the data to be imported
        #

        attrs_dict = dict(attrs)

        # Generic connections cannot import their IDs during edits
        if item_type == 'zato_generic_connection' and is_edit:
            _= attrs_dict.pop('id', None)

        # We handle security groups only
        elif item_type == 'security_groups':
            attrs['group_type'] = Common_Groups.Type.API_Clients

        # RBAC objects cannot refer to other objects by their IDs
        elif item_type == 'rbac_role_permission':
            _= attrs_dict.pop('id', None)
            _= attrs_dict.pop('perm_id', None)
            _= attrs_dict.pop('role_id', None)
            _= attrs_dict.pop('service_id', None)

        elif item_type == 'rbac_client_role':
            _= attrs_dict.pop('id', None)
            _= attrs_dict.pop('role_id', None)

        elif item_type == 'rbac_role':
            _= attrs_dict.pop('id', None)
            _= attrs_dict.pop('parent_id', None)

        elif item_type == 'oauth':

            if not 'data_format' in attrs:
                attrs['data_format'] = Data_Format.JSON

            if not 'client_id_field' in attrs:
                attrs['client_id_field'] = 'client_id'

            if not 'client_secret_field' in attrs:
                attrs['client_secret_field'] = 'client_secret'

            if not 'grant_type' in attrs:
                attrs['grant_type'] = 'client_credentials'

            if auth_endpoint := attrs.pop('auth_endpoint', None):
                attrs['auth_server_url'] = auth_endpoint

            if scopes := attrs.get('scopes'):
                if isinstance(scopes, list):
                    scopes = '\n'.join(scopes)
                    attrs['scopes'] = scopes

            if extra_fields := attrs.get('extra_fields'):
                if isinstance(extra_fields, list):
                    extra_fields = '\n'.join(extra_fields)
                    attrs['extra_fields'] = extra_fields

        attrs.cluster_id = self.client.cluster_id
        attrs.is_source_external = True

        response = self._import_object(item_type, attrs, is_edit)

        if response and response.ok:
            if self._needs_change_password(item_type, attrs, is_edit):
                object_id = response.data['id']
                response = self._maybe_change_password(object_id, item_type, attrs)

        # We quit on first error encountered
        if response and not response.ok:
            raw = (item_type, attrs_dict, response.details)
            self.results.add_error(raw, ERROR_COULD_NOT_IMPORT_OBJECT,
                "Could not import (is_edit {}) '{}' with '{}', response from '{}' was '{}'",
                    is_edit, attrs.name, attrs_dict, item_type, response.details)
            return self.results # type: ignore

        # It's been just imported so we don't want to create it in next steps
        # (this in fact would result in an error as the object already exists).
        if is_edit:
            self.remove_from_import_list(item_type, attrs.name)

        # If this is a generic connection and it has a secret set (e.g. MongoDB password),
        # we need to explicitly set it for the connection we are editing.
        if item_type == 'zato_generic_connection' and attrs_dict.get('secret'):
            if self._needs_change_password(item_type, attrs, is_edit):
                self._set_generic_connection_secret(attrs_dict['name'], attrs_dict['type_'], attrs_dict['secret'])

        # We'll see how expensive this call is. Seems to be but let's see in practice if it's a burden.
        self.object_mgr.populate_objects_by_type(item_type)

# ################################################################################################################################

    def add_warning(self, results, item_type, value_dict, item): # type: ignore
        raw:'any_' = (item_type, value_dict)
        results.add_warning(
            raw, WARNING_ALREADY_EXISTS_IN_ODB, '{} already exists in ODB {} ({})', dict(value_dict), dict(item), item_type)

# ################################################################################################################################

    def find_already_existing_odb_objects(self):

        results = Results()
        for item_type, items in self.json.items(): # type: ignore

            #
            # Preprocess item type
            #
            item_type = _replace_item_type(True, item_type)

            for item in items: # type: ignore
                name:'any_' = item.get('name')
                if not name:
                    raw:'any_' = (item_type, item)
                    results.add_error(raw, ERROR_KEYS_MISSING, '{} has no `name` key ({})', dict(item), item_type)

                if item_type == 'http_soap':
                    connection:'any_' = item.get('connection')
                    transport:'any_' = item.get('transport')

                    existing:'any_' = find_first(self.object_mgr.objects.http_soap,
                        lambda item: connection == item.connection and transport == item.transport and name == item.name) # type: ignore

                    if existing is not None:
                        self.add_warning(results, item_type, item, existing)

                else:
                    existing = self.object_mgr.find(item_type, {'name': name})

                    if existing is not None:
                        self.add_warning(results, item_type, item, existing)

        return results

# ################################################################################################################################

    def may_be_dependency(self, item_type): # type: ignore
        """ Returns True if input item_type may be possibly a dependency, for instance,
        a security definition may be potentially a dependency of channels or a web socket
        object may be a dependency of pub/sub endpoints.
        """
        service_by_name = SERVICE_BY_NAME[item_type]

        if service_by_name.is_security:
            return True

        elif 'def' in item_type:
            return True

        elif item_type in {'web_socket', 'pubsub_endpoint', 'http_soap'}:
            return True

        else:
            return False

# ################################################################################################################################

    def _import_basic_auth(self, data:'dictlist', *, is_edit:'bool') -> 'None':

        # Local variables
        service_name = 'zato.common.import-objects'
        import_type = 'edit' if is_edit else 'create'

        # Build a request for the service
        imports = {
            'basic_auth': data
        }

        # .. details of how many objects we are importing ..
        len_imports = {
            'basic_auth': len(imports['basic_auth']),
        }

        # .. log what we are about to do ..
        self.logger.info(f'Invoking -> import security ({import_type}) -> {service_name} -> {len_imports}')

        _ = self.client.invoke(service_name, imports)

# ################################################################################################################################

    def _import_pubsub_objects(self, data:'strlistdict') -> 'None':

        # Local variables
        service_name = 'zato.common.import-objects'

        # Resolve all values first ..
        for item_type, values in data.items():
            for idx, value in enumerate(values):
                value = dict(value)
                value = self._resolve_attrs(item_type, value)
                values[idx] = value

        # .. details of how many objects we are importing ..
        len_imports = {
            'topics': len(data['pubsub_topic']),
            'endpoints': len(data['pubsub_endpoint']),
            'subs': len(data['pubsub_subscription']),
        }

        # .. log what we are about to do ..
        self.logger.info(f'Invoking -> import pub/sub -> {service_name} -> {len_imports}')
        _ = self.client.invoke(service_name, data)

# ################################################################################################################################

    def _trigger_sync_server_objects(self, *, sync_security:'bool'=True, sync_pubsub:'bool'=True):

        # Local variables
        service_name = 'pub.zato.common.sync-objects'

        # Request to send to the server
        request = {
            'security': sync_security,
            'pubsub': sync_pubsub,
        }

        self.logger.info(f'Invoking -> trigger sync -> {service_name}')
        _ = self.client.invoke(service_name, request)

# ################################################################################################################################

    def _build_existing_objects_to_edit_during_import(self, already_existing:'any_') -> 'any_':

        existing_defs = []
        existing_rbac_role = []
        existing_rbac_role_permission = []
        existing_rbac_client_role = []
        existing_other = []

        for w in already_existing.warnings: # type: ignore
            item_type, value = w.value_raw # type: ignore
            value = value

            if 'def' in item_type:
                existing = existing_defs
            elif item_type == 'rbac_role':
                existing = existing_rbac_role
            elif item_type == 'rbac_role_permission':
                existing = existing_rbac_role_permission
            elif item_type == 'rbac_client_role':
                existing = existing_rbac_client_role
            else:
                existing = existing_other
            existing.append(w)

        existing_combined:'any_' = existing_defs + existing_rbac_role + existing_rbac_role_permission + \
            existing_rbac_client_role + existing_other

        return existing_combined

# ################################################################################################################################

    def _build_new_objects_to_create_during_import(self, existing_combined:'any_') -> 'any_':

        # stdlib
        from collections import OrderedDict

        new_defs = []
        new_rbac_role = []
        new_rbac_role_permission = []
        new_rbac_client_role = []
        new_other = []

        # Use an ordered dict to iterate over the data with dependencies first
        self_json = deepcopy(self.json)
        self_json_ordered:'any_' = OrderedDict()

        # All the potential dependencies will be handled in this specific order
        dep_order = [
            'def_sec',
            'basic_auth',
            'apikey',
            'ntlm',
            'oauth',
            'jwt',
            'aws',
            'tls_key_cert',
            'tls_channel_sec',
            'security_groups',
            # 'wss',
            # 'openstack',
            # 'xpath_sec',
            # 'vault_conn_sec',
            'http_soap',
            'web_socket',
            'pubsub_topic',
            'pubsub_endpoint',
        ]

        # Do populate the dependencies first ..
        for dep_name in dep_order:
            self_json_ordered[dep_name] = self_json.get(dep_name, [])

        # .. now, populate everything that is not a dependency.
        for key, value in self_json.items(): # type: ignore
            if key not in dep_order:
                self_json_ordered[key] = value

        for item_type, items in self_json_ordered.items(): # type: ignore

            #
            # Preprocess item type
            #
            item_type = _replace_item_type(True, item_type)

            if self.may_be_dependency(item_type):

                if item_type == 'rbac_role':
                    append_to = new_rbac_role
                elif item_type == 'rbac_role_permission':
                    append_to = new_rbac_role_permission
                elif item_type == 'rbac_client_role':
                    append_to = new_rbac_client_role
                else:
                    append_to = new_defs
            else:
                append_to = new_other

            append_to.append({item_type: items})

        # This is everything new that we know about ..
        new_combined:'any_' = new_defs + new_rbac_role + new_rbac_role_permission + new_rbac_client_role + new_other

        # .. now, go through it once more and filter out elements that we know should be actually edited, not created ..
        to_remove = []

        for new_elem in new_combined:
            for item_type, value_list in new_elem.items():
                for value_dict in value_list:
                    value_dict = value_dict.toDict()

                    for existing_elem in existing_combined:
                        existing_item_type, existing_item = existing_elem.value_raw
                        if item_type == existing_item_type:
                            if value_dict.get('name', _no_value1) == existing_item.get('name', _no_value2):
                                to_remove.append({
                                    'item_type': item_type,
                                    'item': value_dict,
                                })
                                break

        for elem in to_remove: # type: ignore
            item_type = elem['item_type'] # type: ignore
            item = elem['item'] # type: ignore

            for new_elem in new_combined:
                for new_item_type, value_list in new_elem.items():
                    for idx, value_dict in enumerate(value_list):
                        value_dict = value_dict.toDict()

                        if new_item_type == item_type:
                            if value_dict['name'] == item['name']:
                                value_list.pop(idx)

        return new_combined

# ################################################################################################################################

    def import_objects(self, already_existing) -> 'Results': # type: ignore

        # stdlib
        from time import sleep

        rbac_sleep = getattr(self.args, 'rbac_sleep', 1)
        rbac_sleep = float(rbac_sleep)

        existing_combined = self._build_existing_objects_to_edit_during_import(already_existing)
        new_combined = self._build_new_objects_to_create_during_import(existing_combined)

        # Extract and load Basic Auth definitions as a whole, before any other updates (edit)
        basic_auth_edit = self._extract_basic_auth(existing_combined, is_edit=True)
        self._import_basic_auth(basic_auth_edit, is_edit=True)

        # Extract and load Basic Auth definitions as a whole, before any other updates (create)
        basic_auth_create = self._extract_basic_auth(new_combined, is_edit=False)
        self._import_basic_auth(basic_auth_create, is_edit=False)

        self._trigger_sync_server_objects(sync_pubsub=False)
        self.object_mgr.refresh_objects()

        for w in existing_combined:

            item_type, attrs = w.value_raw

            if self.should_skip_item(item_type, attrs, True):
                continue

            # Basic Auth definitions have been already handled above (edit)
            if item_type == Sec_Def_Type.BASIC_AUTH:
                continue

            # Skip pub/sub objects because they are handled separately (edit)
            if item_type.startswith('pubsub'):
                continue

            results = self._import(item_type, attrs, True)

            if 'rbac' in item_type:
                sleep(rbac_sleep)

            if results:
                return results

        #
        # Create new objects, again, definitions come first ..
        #

        # A container for pub/sub objects to be handled separately
        pubsub_objects:'strlistdict' = {
            'pubsub_endpoint': [],
            'pubsub_topic': [],
            'pubsub_subscription': [],
        }

        # Extract and load Basic Auth definitions as a whole, before any other updates (create)
        self._trigger_sync_server_objects(sync_pubsub=False)
        self.object_mgr.refresh_objects()

        for elem in new_combined:
            for item_type, attr_list in elem.items():
                for attrs in attr_list:

                    if self.should_skip_item(item_type, attrs, False):
                        continue

                    # Basic Auth definitions have been already handled above (create)
                    if item_type == Sec_Def_Type.BASIC_AUTH:
                        continue

                    # Pub/sub objects are handled separately at the end of this function (create)
                    if item_type.startswith('pubsub'):
                        container = pubsub_objects[item_type]
                        container.append(attrs)
                        continue

                    results = self._import(item_type, attrs, False)

                    if 'rbac' in item_type:
                        sleep(rbac_sleep)

                    if results:
                        return results

        # Handle pub/sub objeccts as a whole here
        self._import_pubsub_objects(pubsub_objects)

        # Now, having imported all the objects, we can trigger their synchronization among the members of the cluster
        self._trigger_sync_server_objects(sync_security=False)

        return self.results

# ################################################################################################################################

    def _extract_basic_auth(self, data:'any_', *, is_edit:'bool') -> 'dictlist':

        out:'dictlist' = []

        if is_edit:
            for item in data:
                value_raw = item.value_raw
                item_type, attrs = value_raw
                if item_type == Sec_Def_Type.BASIC_AUTH:
                    attrs = dict(attrs)
                    attrs = self._resolve_attrs('basic_auth', attrs)
                    out.append(attrs)
        else:
            for item in data:
                if basic_auth := item.get(Sec_Def_Type.BASIC_AUTH):
                    for elem in basic_auth:
                        attrs = dict(elem)
                        attrs = self._resolve_attrs('basic_auth', attrs)
                        out.append(attrs)

        return out

# ################################################################################################################################

    def _swap_service_name(self, required, attrs, first, second): # type: ignore
        if first in required and second in attrs:
            attrs[first] = attrs[second]

# ################################################################################################################################

    def _import_object(self, def_type, item, is_edit): # type: ignore

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        service_info = SERVICE_BY_NAME[def_type]

        if is_edit:
            service_name:'any_' = service_info.get_service_name('edit')
        else:
            service_name:'any_' = service_info.get_service_name('create')

        # service and service_name are interchangeable
        required:'any_' = service_info.get_required_keys()
        self._swap_service_name(required, item, 'service', 'service_name')
        self._swap_service_name(required, item, 'service_name', 'service')

        # Fetch an item from a cache of ODB objects and assign its ID to item so that the Edit service knows what to update.
        if is_edit:
            lookup_config:'any_' = {'name': item.name}
            if def_type == 'http_soap':
                lookup_config['connection'] = item.connection
                lookup_config['transport'] = item.transport
            odb_item:'any_' = self.object_mgr.find(def_type, lookup_config)
            item.id = odb_item.id

        for field_name, info in iteritems(service_info.object_dependencies): # type: ignore

            if item.get('security_id') == 'ZATO_SEC_USE_RBAC':
                continue

            if field_name in _security_fields:
                field_name = resolve_security_field_name(item)

            item_type:'any_' = info['dependent_type']
            dependent_field:'any_' = info['dependent_field']

            if item.get(field_name) != info.get('empty_value') and 'id_field' in info:

                id_field:'any_' = info['id_field']

                if field_name in _security_keys:
                    field_value = try_keys(item, _security_keys)
                else:
                    field_value:'any_' = item[field_name]

                # Ignore explicit indicators of the absence of a security definition
                if field_value != Zato_No_Security:
                    criteria:'any_' = {dependent_field: field_value}
                    dep_obj:'any_' = self.object_mgr.find(item_type, criteria)
                    item[id_field] = dep_obj.id

        if service_name and service_info.name != 'def_sec':

            self.logger.info(f'Invoking -> import -> {service_name} for {service_info.name} ({def_type})')
            response = self.client.invoke(service_name, item)

            if response.ok:
                verb = 'Updated' if is_edit else 'Created'
                self.logger.info('%s object `%s` with %s', verb, item.name, service_name)

            return response

# ################################################################################################################################

    def _maybe_change_password(self, object_id, item_type, attrs): # type: ignore

        # stdlib
        from time import sleep

        service_info = SERVICE_BY_NAME[item_type]
        service_name:'any_' = service_info.get_service_name('change-password')
        if service_name is None or 'password' not in attrs:
            return None

        response = self.client.invoke(service_name, {
            'id': object_id,
            'password1': attrs.password,
            'password2': attrs.password,
        })

        if response.ok:
            self.logger.info("Updated password for '{}' ({})".format(attrs.name, service_name))

            # Wait for a moment before continuing to let AMQP connectors change their passwords.
            # This is needed because we may want to create channels right after the password
            # has been changed and this requires valid credentials, including the very
            # which is being changed here.
            if item_type == 'def_amqp':
                sleep(5)

        return response

class ObjectManager:
    def __init__(self, client, logger): # type: ignore
        self.client = client # type: any_
        self.logger = logger # type: Logger

# ################################################################################################################################

    def find(self, item_type, fields, *, check_sec=True): # type: ignore

        if check_sec:
            if item_type == 'def_sec' or item_type in _All_Sec_Def_Types:
                return self.find_sec(fields)

        # This probably isn't necessary any more:
        item_type:'any_' = item_type.replace('-', '_')
        objects_by_type:'any_' = self.objects.get(item_type, ())

        return find_first(objects_by_type, lambda item: dict_match(item_type, item, fields)) # type: ignore

# ################################################################################################################################

    def find_sec(self, fields): # type: ignore
        """ Find any security definition with the given name.
        """
        for service in SERVICES:

            if service.is_security:
                item:'any_' = self.find(service.name, fields, check_sec=False)
                if item is not None:
                    return item

# ################################################################################################################################

    def refresh(self):
        self.refresh_services()
        self.refresh_objects()

# ################################################################################################################################

    def refresh_services(self):

        # Bunch
        from bunch import Bunch

        response:'any_' = self.client.invoke('zato.service.get-list', {
            'cluster_id': self.client.cluster_id, # type: ignore
            'name_filter': '*'
        })

        if not response.ok:
            raise Exception('Unexpected response; e:{}'.format(response))

        if response.has_data:

            # Make sure we access the correct part of the response,
            # because it may be wrapped in a pagination structure.
            data = self.get_data_from_response_data(response.data)
            self.services = {service['name']: Bunch(service) for service in data}

# ################################################################################################################################

    def fix_up_odb_object(self, item_type, item): # type: ignore
        """ For each ODB object, ensure fields that specify a dependency have their associated name field updated
        to match the dependent object. Otherwise, ensure the field is set to the corresponding empty value
        (either None or Zato_No_Security).
        """

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        normalize_service_name(item)
        service_info = SERVICE_BY_NAME[item_type]

        if item_type in ('json_rpc', 'http_soap'):

            if item['sec_use_rbac'] is True:
                item['security_id'] = 'ZATO_SEC_USE_RBAC'

            elif item_type == 'json_rpc' and item['security_id'] is None:
                item['security_id'] = 'ZATO_NONE'

        for field_name, info in iteritems(service_info.object_dependencies): # type: ignore

            if 'id_field' not in info:
                continue

            if not test_item(item, info.get('condition')):
                # If the field's condition is false, then just set empty values and stop.
                item[field_name] = info.get('empty_value')
                item[info['id_field']] = None
                continue

            dep_id:'any_' = item.get(info['id_field'])

            if dep_id is None:
                item[field_name] = info.get('empty_value')
                continue

            dep = self.find(info['dependent_type'], {'id': dep_id})

            if (dep_id != 'ZATO_SEC_USE_RBAC') and (field_name != 'sec_name' and dep is None):
                if not dep:
                    msg = 'Dependency not found, name:`{}`, field_name:`{}`, type:`{}`, dep_id:`{}`, dep:`{}`, item:`{}`'
                    raise Exception(msg.format(service_info.name, field_name, info['dependent_type'], dep_id, dep,
                        item.toDict()))
                else:
                    item[field_name] = dep[info['dependent_field']]

            # JSON-RPC channels cannot have empty security definitions on exports
            if item_type == 'http_soap' and item['name'].startswith('json.rpc.channel'):
                if not item['security_id']:
                    item['security_id'] = 'ZATO_NONE'

        return item # type: ignore

# ################################################################################################################################

    ignored_names = (
        ServiceConst.API_Admin_Invoke_Username,
        'pubapi',
    )

    def is_ignored_name(self, item_type, item, is_sec_def): # type: ignore

        if 'name' not in item:
            return False

        name:'any_' = item.name.lower()

        # Special-case scheduler jobs that can be overridden by users
        if name.startswith('zato.wsx.cleanup'):
            return False

        if item_type not in {'pubsub_subscription', 'rbac_role_permission'}:

            if name in self.ignored_names:
                return True

            elif 'zato' in name and (not 'unittest' in name):
                if is_sec_def:
                    return False
                else:
                    return True

# ################################################################################################################################

    def delete(self, item_type, item): # type: ignore
        service_info = SERVICE_BY_NAME[item_type]

        service_name:'any_' = service_info.get_service_name('delete')
        if service_name is None:
            self.logger.error('Prefix {} has no delete service'.format(item_type))
            return

        response = self.client.invoke(service_name, {
            'cluster_id': self.client.cluster_id,
            'id': item.id,
        })
        if response.ok:
            self.logger.info('Deleted {} ID {}'.format(item_type, item.id))
        else:
            self.logger.error('Could not delete {} ID {}: {}'.format(item_type, item.id, response))

# ################################################################################################################################

    def delete_all(self):

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        count = 0
        for item_type, items in iteritems(self.objects): # type: ignore
            for item in items: # type: ignore
                self.delete(item_type, item)
                count += 1
        return count

# ################################################################################################################################

    def get_data_from_response_data(self, response_data): # type: ignore

        # Generic connections' GetList includes metadata in responses so we need to dig into actual data
        if '_meta' in response_data:
            keys:'any_' = list(response_data)
            keys.remove('_meta')
            response_key:'any_' = keys[0]
            data:'any_' = response_data[response_key]
        else:
            data:'any_' = response_data

        return data

# ################################################################################################################################

    def populate_objects_by_type(self, item_type:'str') -> 'None':

        # Ignore artificial objects
        if item_type in {'def_sec'}:
            return

        # Bunch
        from bunch import Bunch

        # Zato
        from zato.common.const import SECRETS

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems
        from zato.common.py23_.past.builtins import basestring # type: ignore

        service_info = SERVICE_BY_NAME[item_type]

        # Temporarily preserve function of the old enmasse.
        service_name:'any_' = service_info.get_service_name('get-list')

        if service_name is None:
            self.logger.info('Type `%s` has no `get-list` service (%s)', service_info, item_type)
            return

        self.logger.debug('Invoking -> getter -> %s for %s (%s)', service_name, service_info.name, item_type)

        request = {
            'cluster_id': self.client.cluster_id,
        }

        if service_name == 'zato.http-soap.get-list':
            request['needs_security_group_names'] = True

        elif service_name == 'zato.groups.get-list':
            request['group_type'] = Common_Groups.Type.API_Clients
            request['needs_members'] = True
            request['needs_short_members'] = True

        response = self.client.invoke(service_name, request)

        if not response.ok:
            self.logger.warning('Could not fetch objects of type {}: {}'.format(service_info.name, response.details))
            return

        self.objects[service_info.name] = []

        if response.has_data:
            data = self.get_data_from_response_data(response.data)

            # A flag indicating if this service is related to security definitions
            is_sec_def = 'zato.security' in service_name

            for item in map(Bunch, data):

                if self.is_ignored_name(item_type, item, is_sec_def):
                    continue

                # Passwords are always exported in an encrypted form so we need to decrypt them ourselves
                for key, value in iteritems(item): # type: ignore
                    if isinstance(value, basestring):
                        if value.startswith(SECRETS.PREFIX):
                            item[key] = None # Enmasse does not export secrets such as passwords or other auth information

                self.objects[service_info.name].append(item)

# ################################################################################################################################

    def refresh_security_objects(self):
        self.refresh_objects(sec_only=True)

# ################################################################################################################################

    def refresh_objects(self, *, sec_only:'bool'=False):

        # stdlib
        from operator import attrgetter

        # Bunch
        from bunch import Bunch

        self.objects = Bunch()
        for service_info in sorted(SERVICES, key=attrgetter('name')):

            if sec_only:
                if not service_info.is_security:
                    continue

            self.populate_objects_by_type(service_info.name)

        for item_type, items in self.objects.items(): # type: ignore
            for item in items: # type: ignore
                self.fix_up_odb_object(item_type, item)

# ################################################################################################################################
# ################################################################################################################################

class JsonCodec:
    extension = '.json'

    def load(self, file_, results): # type: ignore

        # Zato
        from zato.common.json_internal import loads

        return loads(file_.read())

    def dump(self, file_, object_): # type: ignore

        # Zato
        from zato.common.json_internal import dumps

        file_.write(dumps(object_, indent=1, sort_keys=True))

# ################################################################################################################################
# ################################################################################################################################

class YamlCodec:
    extension = '.yaml'

    def load(self, file_:'any_', results:'any_') -> 'strdict':

        # Local imports
        import yaml
        from zato.common.util.config import extract_param_placeholders

        # Read the data as string ..
        data = file_.read()

        # .. replace named placeholders ..
        params = extract_param_placeholders(data)

        # .. go through each placeholder ..
        for param in params:

            # .. check if it points to an environment variable ..
            if zato_enmasse_env2 in param:

                # .. we are here if we can find an environment variable ..
                # .. based on a placeholder parameter, so we now need ..
                # .. to extract the value of this variable or use a default one ..
                env_variable_name = param.replace(zato_enmasse_env2, '')
                env_variable_name = env_variable_name[1:-1]

                # .. let's find this variable or use the default one ..
                env_value = os.environ.get(env_variable_name, 'Missing_Value_' + env_variable_name)

                # .. now, we can insert this variable in the original value ..
                data = data.replace(param, env_value)

        # .. and return a dict object representing the file.
        out = yaml.load(data, yaml.FullLoader)
        return out

    def dump(self, file_, object_): # type: ignore

        # pyaml
        import pyaml

        file_.write(pyaml.dump(object_, vspacing=True))

# ################################################################################################################################
# ################################################################################################################################

class InputParser:
    def __init__(
        self,
        path:'str',
        logger:'Logger',
        codec:'YamlCodec | JsonCodec',
        ignore_missing_includes:'bool',
    ) -> 'None':

        # stdlib
        import os

        self.path = os.path.abspath(path)
        self.logger = logger
        self.codec = codec
        self.ignore_missing_includes = ignore_missing_includes

# ################################################################################################################################

    def _load_file(self, path:'str') -> 'strdict':

        try:
            with open(path) as f:
                data:'strdict' = self.codec.load(f, None) # type: ignore
        except Exception as e:
            from yaml.error import YAMLError
            if isinstance(e, YAMLError):
                raise
            else:
                self.logger.info('Caught an exception -> %s', e)
                data = {}

        return data

# ################################################################################################################################

    def _parse_file(self, path:'str', results:'Results') -> 'strdict':

        # First, open the main file ..
        data:'strdict' = self._load_file(path) or {}

        # .. go through all the files that we potentially need to include ..
        for item_type, values in deepcopy(data).items():

            for item in values:

                # .. only include files will be taken into account ..
                if self.is_include(item_type, item):

                    # .. build a full path to the file to be included ..
                    include_path = self._get_full_path(item)

                    if path == include_path:
                        raw = (include_path,)
                        results.add_error(raw, ERROR_INVALID_INPUT, f'Include cannot include itself `{include_path}`', item)
                        continue

                    if not os.path.exists(include_path):
                        if not self.ignore_missing_includes:
                            raw = (include_path,)
                            results.add_error(raw, Error_Include_Not_Found, f'Include not found `{include_path}`', item)
                            continue

                    # .. load the actual contents to be included ..
                    data_to_include = self._parse_file(include_path, results)

                    # .. go through each of the items that the file to be included defines ..
                    for item_type_to_include, values_to_include in data_to_include.items():

                        # .. make sure we append the new data to what we potentially already have ..
                        if item_type_to_include in data:
                            data[item_type_to_include].extend(values_to_include)

                        # .. otherwise, we create a new key for it ..
                        else:
                            data[item_type_to_include] = values_to_include

        # .. remove any potential include section from further processing ..
        _ = data.pop(ModuleCtx.Item_Type_Include, None)

        # .. now, we are ready to return the whole data set to our caller.
        return data

# ################################################################################################################################

    def _get_full_path(self, include_path:'str') -> 'str':

        # stdlib
        import os

        curdir = os.path.dirname(self.path)
        joined = os.path.join(curdir, include_path.replace('file://', '')) # type: ignore

        return os.path.abspath(joined)

# ################################################################################################################################

    def is_include(self, item_type:'str', item:'str | strdict') -> 'bool':
        return item_type == ModuleCtx.Item_Type_Include and isinstance(item, str)

# ################################################################################################################################

    def parse_def_sec(self, item:'strdict', results:'Results') -> 'None':

        # Bunch
        from bunch import Bunch

        # While reading old enmasse files, expand def_sec entries out to their original service type.
        sec_type = item.pop('type', None)
        if sec_type is None:
            raw = ('def_sec', item)
            results.add_error(
                raw, ERROR_TYPE_MISSING, "security definition '{}' has no required 'type' key (def_sec)", item)
            return

        service_names = [elem.name for elem in SERVICES if elem.is_security]
        service_names.extend(ModuleCtx.Extra_Security_Types)

        if sec_type not in service_names:
            raw = (sec_type, service_names, item)
            results.add_error(raw, ERROR_INVALID_SEC_DEF_TYPE,
                "Invalid type '{}', must be one of '{}' (def_sec)", sec_type, service_names)
            return

        self.json.setdefault(sec_type, []).append(Bunch(item))
        self.json.setdefault('def_sec', []).append(Bunch(item))

# ################################################################################################################################

    def parse_item(self, item_type:'str', item:'str | strdict', results:'Results') -> 'None':

        # Bunch
        from bunch import Bunch

        if item_type == 'def_sec':
            self.parse_def_sec(cast_('strdict', item), results)

        else:
            items:'any_' = self.json.get(item_type) or []
            _:'any_' = items.append(Bunch(cast_('strdict', item)))
            self.json[item_type] = items

# ################################################################################################################################

    def _maybe_fixup_http_soap(self, original_item_type:'str', item:'strdict') -> 'str':
        # Preserve old format by merging http-soap subtypes into one.
        for item_type, connection, transport in HTTP_SOAP_KINDS:
            if item_type == original_item_type:
                item['connection'] = connection
                item['transport'] = transport
                return 'http_soap'
        return original_item_type

# ################################################################################################################################

    def _is_item_type_recognized(self, item_type:'str') -> 'bool':

        if item_type == ModuleCtx.Item_Type_Include:
            return True

        elif item_type in ModuleCtx.Enmasse_Type:
            return True

        elif item_type in ModuleCtx.Enmasse_Item_Type_Name_Map_Reverse:
            return True

        elif item_type in SERVICE_BY_NAME:
            return True

        elif item_type in HTTP_SOAP_ITEM_TYPES:
            return True

        else:
            return False

# ################################################################################################################################

    def parse_items(self, data:'strdict', results:'Results') -> 'None':

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        for item_type, items in iteritems(data):

            if not self._is_item_type_recognized(item_type):
                raw = (item_type,)
                results.add_error(raw, ERROR_UNKNOWN_ELEM, 'Ignoring unknown element type {} in the input.', item_type)
                continue

            for item in items:
                current_item_type = item_type
                if isinstance(item, dict):
                    current_item_type = self._maybe_fixup_http_soap(item_type, item)
                    normalize_service_name(item)
                self.parse_item(current_item_type, item, results)

# ################################################################################################################################

    def _parse_env_key(self, key:'str') -> 'EnvKeyData':

        # Our response to produce
        out = EnvKeyData()

        # .. remove non-business information first ..
        key = key.replace(zato_enmasse_env_value_prefix, '')

        # .. turn double underscores into dots that shells do not allow ..
        key = key.replace('__', '.')

        # .. now, we know that we have components separated by underscores ..
        key_split = key.split('_')

        # .. we expect for these three components to exist in this order ..
        def_type  = key_split[0]
        name      = key_split[1]
        attr_name = key_split[2]

        # .. populate the response ..
        out.def_type  = def_type
        out.name      = name
        out.attr_name = attr_name

        # .. now, we can return the result.
        return out

# ################################################################################################################################

    def _extract_config_from_env(self, env:'strstrdict') -> 'list_[EnvKeyData]':

        # Our response to produce
        out:'list_[EnvKeyData]' = []

        # First pass, through environemnt variables as they were defined ..
        for key in env.keys():

            # . this is the value, to be used as it is ..
            value = env.pop(key)

            # .. the key needs to be transformed into a business object ..
            env_key_data = self._parse_env_key(key)

            # .. enrich the business object with the actual value ..
            env_key_data.attr_value = value

            # .. make use of it ..
            out.append(env_key_data)

        # .. now, we can return the result to our caller.
        return out

# ################################################################################################################################

    def _pre_process_input_before_import(self, data:'strdict') -> 'strdict':

        # Get all environment variables that we may potentially use ..
        env = deepcopy(os.environ)

        # .. remove any variables that are not ours ..
        for key in list(env):
            if not key.startswith(zato_enmasse_env_value_prefix):
                _ = env.pop(key)

        # .. turn it into a config dict ..
        env_config = self._extract_config_from_env(cast_('strdict', env))

        # .. this can be built upfront in case it is needed ..
        if not 'zato_generic_connection' in data:
            data['zato_generic_connection'] = []

        # .. turn out simple definitions into generic ones if this is applicable ..
        for new_name, old_name in ModuleCtx.Enmasse_Item_Type_Name_Map_Reverse.items():

            # .. this should be a generic connection ..
            if old_name.startswith('zato_generic_connection'):

                # .. extract its type ..
                wrapper_type = old_name.replace('zato_generic_connection_', '')

                # .. pop a list of such connections to process ..
                value_list = data.pop(new_name, [])

                # .. go through each of them ..
                for value in value_list:

                    # .. populate the type ..
                    value['type_'] = wrapper_type

                    # .. populate wrapper type-specific attributes ..
                    if wrapper_type == outconn_wsx:

                        if not 'is_outconn' in value:
                            value['is_outconn'] = True

                        if not 'is_channel' in value:
                            value['is_channel'] = False

                        if not 'is_internal' in value:
                            value['is_internal'] = False

                        if not 'pool_size' in value:
                            value['pool_size'] = 1

                        if not 'sec_use_rbac' in value:
                            value['sec_use_rbac'] = False

                        if not 'is_zato' in value:
                            value['is_zato'] = False

                        if not 'data_format' in value:
                            value['data_format'] = Data_Format.JSON

                        if not 'has_auto_reconnect' in value:
                            value['has_auto_reconnect'] = True

                        if not 'security_def' in value:
                            value['security_def'] = Zato_None

                    elif wrapper_type == outconn_ldap:

                        # .. passwords are to be turned into secrets ..
                        if password := value.pop('password', None):
                            value['secret'] = password

                        value['is_outconn'] = True
                        value['is_channel'] = False

                        if not 'auto_bind' in value:
                            value['auto_bind'] = COMMON_LDAP.AUTO_BIND.DEFAULT.id

                        if not 'connect_timeout' in value:
                            value['connect_timeout'] = COMMON_LDAP.DEFAULT.CONNECT_TIMEOUT

                        if not 'get_info' in value:
                            value['get_info'] = COMMON_LDAP.GET_INFO.SCHEMA.id

                        if not 'ip_mode' in value:
                            value['ip_mode'] = COMMON_LDAP.IP_MODE.IP_SYSTEM_DEFAULT.id

                        if not 'is_internal' in value:
                            value['is_internal'] = False

                        if not 'is_read_only' in value:
                            value['is_read_only'] = False

                        if not 'is_stats_enabled' in value:
                            value['is_stats_enabled'] = False

                        if not 'is_tls_enabled' in value:
                            value['is_tls_enabled'] = False

                        if not 'pool_exhaust_timeout' in value:
                            value['pool_exhaust_timeout'] = COMMON_LDAP.DEFAULT.POOL_EXHAUST_TIMEOUT

                        if not 'pool_ha_strategy' in value:
                            value['pool_ha_strategy'] = COMMON_LDAP.POOL_HA_STRATEGY.ROUND_ROBIN.id

                        if not 'pool_keep_alive' in value:
                            value['pool_keep_alive'] = COMMON_LDAP.DEFAULT.POOL_KEEP_ALIVE

                        if not 'pool_lifetime' in value:
                            value['pool_lifetime'] = COMMON_LDAP.DEFAULT.POOL_LIFETIME

                        if not 'pool_max_cycles' in value:
                            value['pool_max_cycles'] = COMMON_LDAP.DEFAULT.POOL_MAX_CYCLES

                        if not 'pool_name' in value:
                            value['pool_name'] = ''

                        if not 'pool_size' in value:
                            value['pool_size'] = COMMON_LDAP.DEFAULT.POOL_SIZE

                        if not 'sasl_mechanism' in value:
                            value['sasl_mechanism'] = ''

                        if not 'sec_use_rbac' in value:
                            value['sec_use_rbac'] = False

                        if not 'should_check_names' in value:
                            value['should_check_names'] = False

                        if not 'should_log_messages' in value:
                            value['should_log_messages'] = False

                        if not 'should_return_empty_attrs' in value:
                            value['should_return_empty_attrs'] = True

                        if not 'tls_ciphers' in value:
                            value['tls_ciphers'] = COMMON_TLS.DEFAULT.CIPHERS

                        if not 'tls_private_key_file' in value:
                            value['tls_private_key_file'] = ''

                        if not 'tls_validate' in value:
                            value['tls_validate'] = COMMON_TLS.CERT_VALIDATE.CERT_REQUIRED.id

                        if not 'tls_version' in value:
                            value['tls_version'] = COMMON_TLS.DEFAULT.VERSION

                        if not 'use_auto_range' in value:
                            value['use_auto_range'] = True

                        if not 'use_tls' in value:
                            value['use_tls'] = False

                    # .. finally, we can append it for later use ..
                    _ = data['zato_generic_connection'].append(value)

        # Preprocess all items ..
        for item_type, items in data.items():

            # Remove IDs from all the generic connections ..
            if item_type == 'zato_generic_connection':
                for item in items:
                    _ = item.pop('id', None)

            # For values that need to be renamed ..
            attr_list_value_rename_reverse  = ModuleCtx.Enmasse_Attr_List_Value_Rename_Reverse.get(item_type) or {}

            # .. optionally, rename selected values ..
            for attr_name, value_map_list in attr_list_value_rename_reverse.items():
                for value_map in value_map_list:
                    for item in items:
                        if value := item.get(attr_name, NotGiven):
                            if value is not NotGiven:
                                if value in value_map:
                                    new_value = value_map[value]
                                    item[attr_name] = new_value

        # .. add values for attributes that are optional ..
        for def_type, items in data.items():

            # .. replace new names with old ones but only for specific types ..
            if item_type_name_map_reverse_by_type := ModuleCtx.Enmasse_Item_Type_Name_Map_Reverse_By_Type.get(def_type):

                # .. go through each time that will potentially have the old name ..
                for item in items:

                    # .. go through each of the names to be replaced ..
                    for name_dict in item_type_name_map_reverse_by_type:

                        for new_name, old_name  in name_dict.items():

                            # .. check if the old name is given on input ..
                            if new_name_value := item.get(new_name, NotGiven):

                                # .. we enter here if the old name exists ..
                                if new_name_value is not NotGiven:

                                    # .. if we are here, we know we can swap the names ..
                                    item[old_name] = item.pop(new_name)

            # .. for attributes that should be populated if they do not exist ..
            attr_list_default_by_type = ModuleCtx.Enmasse_Attr_List_Default_By_Type.get(def_type) or {}

            # .. go through each definition ..
            for item in items:

                # .. this could be an include directive which we can skip here ..
                if not isinstance(item, dict):
                    continue

                # .. add type hints ..
                item = cast_('strdict', item)

                # .. everything is active unless it is configured not to be ..
                if not 'is_active' in item:
                    item['is_active'] = True

                # .. add default attributes if they do not exist ..
                for default_key, default_value in attr_list_default_by_type.items():
                    if default_key not in item:
                        item[default_key] = default_value

                # .. populate attributes based on environment variables ..
                for env_key_data in env_config:

                    # .. we need to match the type of the object ..
                    if def_type == env_key_data.def_type:

                        # .. as well as its name ..
                        if item.get('name') == env_key_data.name:

                            # .. if we do have a match, we can populate the value of an attribute ..
                            item[env_key_data.attr_name] = env_key_data.attr_value

        # .. potentially replace new names that are on input with what the server expects (old names) ..
        for new_name, old_name in ModuleCtx.Enmasse_Item_Type_Name_Map_Reverse.items():
            value = data.pop(new_name, None) or None
            if value is not None:
                data[old_name] = value

        return data

# ################################################################################################################################

    def parse(self):

        # A business object reprenting the results of an import .
        results = Results()

        # .. this is where the actual data is kept ..
        self.json = {}

        # .. extract a basic dict ..
        data = self._parse_file(cast_('str', self.path), results) # type: ignore

        # .. pre-process its contents ..
        data = self._pre_process_input_before_import(data)

        if not results.ok:
            return results

        self.parse_items(data, results)
        return results

# ################################################################################################################################
# ################################################################################################################################

class Enmasse(ManageCommand):
    """ Manages server objects en masse.
    """
    opts:'dictlist' = [
        {'name':'--server-url', 'help':'URL of the server that enmasse should talk to, provided in host[:port] format. Defaults to server.conf\'s \'gunicorn_bind\''},  # noqa: E501
        {'name':'--export-local', 'help':'Export local file definitions into one file (can be used with --export)', 'action':'store_true'},
        {'name':'--export', 'help':'Export server objects to a file (can be used with --export-local)', 'action':'store_true'},
        {'name':'--export-odb', 'help':'Same as --export', 'action':'store_true'},
        {'name':'--output', 'help':'Path to a file to export data to', 'action':'store'},
        {'name':'--include-type', 'help':'A list of definition types to include in an export', 'action':'store', 'default':'all'},
        {'name':'--include-name', 'help':'Only objects containing any of the names provided will be exported', 'action':'store', 'default':'all'},
        {'name':'--import', 'help':'Import definitions from a local file (excludes --export-*)', 'action':'store_true'},
        {'name':'--clean-odb', 'help':'Delete all ODB definitions before proceeding', 'action':'store_true'},
        {'name':'--format', 'help':'Select output format ("json" or "yaml")', 'choices':('json', 'yaml'), 'default':'yaml'},
        {'name':'--dump-format', 'help':'Same as --format', 'choices':('json', 'yaml'), 'default':'yaml'},
        {'name':'--ignore-missing-defs', 'help':'Ignore missing definitions when exporting to file', 'action':'store_true'},
        {'name':'--ignore-missing-includes', 'help':'Ignore include files that do not exist', 'action':'store_true'},
        {'name':'--exit-on-missing-file', 'help':'If input file does not exist, exit with status code 0', 'action':'store_true'},
        {'name':'--replace', 'help':'Force replacing already server objects during import', 'action':'store_true'},
        {'name':'--replace-odb-objects', 'help':'Same as --replace', 'action':'store_true'},
        {'name':'--input', 'help':'Path to input file with objects to import'},
        {'name':'--initial-wait-time', 'help':'How many seconds to initially wait for a server', 'default':ModuleCtx.Initial_Wait_Time},
        {'name':'--missing-wait-time', 'help':'How many seconds to wait for missing objects', 'default':ModuleCtx.Missing_Wait_Time},
        {'name':'--env-file', 'help':'Path to an .ini file with environment variables'},
        {'name':'--rbac-sleep', 'help':'How many seconds to sleep for after creating an RBAC object', 'default':'1'},
        {'name':'--cols-width', 'help':'A list of columns width to use for the table output, default: {}'.format(DEFAULT_COLS_WIDTH), 'action':'store_true'},
    ]

    CODEC_BY_EXTENSION:'strdict' = {
        'json': JsonCodec,
        'yaml': YamlCodec,
        'yml': YamlCodec,
    }

# ################################################################################################################################

    def _on_server(self, args:'any_') -> 'None':

        # stdlib
        import os
        import sys
        from time import sleep

        # Bunch
        from bunch import Bunch

        # Zato
        from zato.cli.check_config import CheckConfig
        from zato.common.util.api import get_client_from_server_conf
        from zato.common.util.env import populate_environment_from_file

        # Local aliases
        input_path:'strnone'  = None
        output_path:'strnone' = None
        exit_on_missing_file = getattr(self.args, 'exit_on_missing_file', True)

        self.args = args
        self.curdir = os.path.abspath(self.original_dir)
        self.json = {}
        has_import = getattr(args, 'import', False)

        # For type hints
        self.missing_wait_time:'int' = getattr(self.args, 'missing_wait_time', None) or ModuleCtx.Missing_Wait_Time
        self.missing_wait_time = int(self.missing_wait_time)

        # Assume False unless it is overridden later on
        self.is_import = False
        self.is_export = False

        # Whether we should include files that do not exist
        self.ignore_missing_includes = getattr(self.args, 'ignore_missing_includes', False)

        # Initialize environment variables ..
        env_path = self.normalize_path('env_file', exit_if_missing=False)
        _ = populate_environment_from_file(env_path)

        self.replace_objects:'bool' = True
        self.export_odb:'bool' = getattr(args, 'export', False) or getattr(args, 'export_odb', False)

        # .. make sure the input file path is correct ..
        if args.export_local or has_import:
            input_path = self.normalize_path('input', exit_if_missing=exit_on_missing_file, log_if_missing=True)

        # .. make sure the output file path is correct ..
        if args.output:
            output_path = self.normalize_path(
                'output',
                exit_if_missing=True,
                needs_parent_dir=True,
                log_if_missing=True,
            )

        # .. the output serialization format. Not used for input ..
        format:'str' = args.format or args.dump_format
        self.codec = self.CODEC_BY_EXTENSION[format]()

        #
        # Tasks and scenarios
        #
        # 1) Export all local JSON files into one (--export-local)
        # 2) Export all definitions from ODB (--export-odb)
        # 3) Export all local JSON files with ODB definitions merged into one (--export-local --export-odb):
        # -> 4) Import definitions from a local JSON file (--import)
        #    4a) bail out if local JSON overrides any from ODB (no --replace-odb-objects)
        #    4b) override whatever is found in ODB with values from JSON (--replace-odb-objects)
        #

        try:
            initial_wait_time = float(args.initial_wait_time)
        except Exception:
            initial_wait_time = ModuleCtx.Initial_Wait_Time

        # Get the client object, waiting until the server is started ..
        self.client = get_client_from_server_conf(self.component_dir, initial_wait_time=initial_wait_time) # type: ignore

        # .. just to be on the safe side, optionally wait a bit more
        initial_wait_time = os.environ.get('ZATO_ENMASSE_INITIAL_WAIT_TIME')
        if initial_wait_time:
            initial_wait_time = int(initial_wait_time)
            self.logger.warning('Sleeping for %s s', initial_wait_time)
            sleep(initial_wait_time)

        self.object_mgr = ObjectManager(self.client, self.logger)
        self.client.invoke('zato.ping')
        populate_services_from_apispec(self.client, self.logger)

        if True not in (args.export_local, self.export_odb, args.clean_odb, has_import):
            self.logger.error('At least one of --clean, --export-local, --export-odb or --import is required, stopping now')
            sys.exit(self.SYS_ERROR.NO_OPTIONS)

        # Populate the flags for our users
        if has_import:
            self.is_import = True

        if args.export_local or self.export_odb:
            self.is_export = True

        if args.clean_odb:
            self.object_mgr.refresh()
            count = self.object_mgr.delete_all()
            self.logger.info('Deleted {} items'.format(count))

        if self.export_odb or has_import:
            # Checks if connections to ODB/Redis are configured properly
            cc = CheckConfig(self.args)
            cc.show_output = False
            cc.execute(Bunch(path='.'))

            # Get back to the directory we started in so following commands start afresh as well
            os.chdir(self.curdir)

        # Imports and export are mutually excluding
        if has_import and (args.export_local or self.export_odb):
            self.logger.error('Cannot specify import and export options at the same time, stopping now')
            sys.exit(self.SYS_ERROR.CONFLICTING_OPTIONS)

        if args.export_local or has_import:
            self.load_input(input_path)

        # .. extract the include lists used to export objects ..
        include_type = getattr(args, 'include_type', '')
        include_name = getattr(args, 'include_name', '')

        include_type = self._extract_include(include_type)
        include_name = self._extract_include(include_name)

        # 3)
        if args.export_local and self.export_odb:
            _ = self.report_warnings_errors(self.export_local_odb())
            self.write_output(output_path, include_type, include_name)

        # 1)
        elif args.export_local:
            _ = self.report_warnings_errors(self.export())
            self.write_output(output_path, include_type, include_name)

        # 2)
        elif self.export_odb:
            if self.report_warnings_errors(self.run_odb_export()):
                self.write_output(output_path, include_type, include_name)

        # 4) a/b
        elif has_import:
            warnings_errors_list = self.run_import()
            _ = self.report_warnings_errors(warnings_errors_list)

# ################################################################################################################################

    def load_input(self, input_path): # type: ignore

        # stdlib
        import sys

        _, _, ext = self.args.input.rpartition('.')
        codec_class = self.CODEC_BY_EXTENSION.get(ext.lower())
        if codec_class is None:
            exts = ', '.join(sorted(self.CODEC_BY_EXTENSION))
            self.logger.error('Unrecognized file extension "{}": must be one of {}'.format(ext.lower(), exts))
            sys.exit(self.SYS_ERROR.INVALID_INPUT)

        parser = InputParser(input_path, self.logger, codec_class(), self.ignore_missing_includes)
        results = parser.parse()

        if not results.ok:
            self.logger.error('Input parsing failed')
            _ = self.report_warnings_errors([results])
            sys.exit(self.SYS_ERROR.INVALID_INPUT)

        self.json = parser.json

# ################################################################################################################################

    def normalize_path(
        self,
        arg_name,         # type: str
        *,
        exit_if_missing,  # type: bool
        needs_parent_dir=False, # type: bool
        log_if_missing=False,   # type: bool
    ) -> 'str':

        # Local aliases
        path_to_check:'str' = ''
        arg_param = getattr(self.args, arg_name, None) or ''

        # Potentially, expand the path to our home directory ..
        arg_name = os.path.expanduser(arg_param)

        # Turn the name into a full path unless it already is one ..
        if os.path.isabs(arg_name):
            arg_path = arg_name
        else:
            arg_path = os.path.join(self.curdir, arg_param)
            arg_path = os.path.abspath(arg_path)

        # .. we need for a directory to exist ..
        if needs_parent_dir:
            path_to_check = os.path.join(arg_path, '..')
            path_to_check = os.path.abspath(path_to_check)

        # .. or for the actual file to exist ..
        else:
            path_to_check = arg_path

        # .. make sure that it does exist ..
        if not os.path.exists(path_to_check):

            # .. optionally, exit the process if it does not ..
            if exit_if_missing:

                if log_if_missing:
                    self.logger.info(f'Path not found: `{path_to_check}`')

                # Zato
                import sys
                sys.exit()

        # .. if we are here, it means that we have a valid, absolute path to return ..
        return arg_path

# ################################################################################################################################

    def _extract_include(self, include_type:'str') -> 'strlist': # type: ignore

        # Local aliases
        out:'strlist' = []

        # Turn the string into a list of items that we will process ..
        include_type:'strlist' = include_type.split(',') # type: ignore
        include_type = [item.strip().lower() for item in include_type]

        # .. ignore explicit types if all types are to be returned ..
        if ModuleCtx.Include_Type.All in include_type:
            include_type = [ModuleCtx.Include_Type.All]
        else:
            out[:] = include_type

        # .. if we do not have anything, it means that we are including all types ..
        if not out:
            out = [ModuleCtx.Include_Type.All]

        # .. now, we are ready to return our response.
        return out

# ################################################################################################################################

    def _should_write_type_to_output(
        self,
        item_type,    # type: str
        item,         # type: strdict
        include_type, # type: strlist
    ) -> 'bool':

        # Get an include type that matches are item type ..
        enmasse_include_type = ModuleCtx.Enmasse_Type.get(item_type)

        # .. if there is no match, it means that we do not write it on output ..
        if not enmasse_include_type:
            return False

        # .. check further if this type is what we had on input ..
        if not enmasse_include_type in include_type:
            return False

        # .. if we are here, we know we should write this type to output.
        return True

# ################################################################################################################################

    def _should_write_name_to_output(
        self,
        item_type,    # type: str
        item_name,    # type: str
        include_name, # type: strlist
    ) -> 'bool':

        # Try every name pattern that we have ..
        for name in include_name:

            # .. indicate that this item should be written if there is a match
            if name in item_name:
                return True

        # .. if we are here, it means that we have not matched any name earlier, ..
        # .. in which case, this item should not be included in the output.
        return False

# ################################################################################################################################

    def _preprocess_item_attrs_during_export(
        self,
        attr_key,  # type: str
        item_type, # type: str
        item,      # type: strdict
    ) -> 'strdict':

        # Check if there is an explicit list of include attributes to return for the type ..
        attr_list_include = ModuleCtx.Enmasse_Attr_List_Include.get(attr_key) or []

        # .. as above, for attributes that are explicitly configured to be excluded ..
        attr_list_exclude = ModuleCtx.Enmasse_Attr_List_Exclude.get(attr_key) or []

        # .. as above, for attributes that need to be renamed ..
        attr_list_rename  = ModuleCtx.Enmasse_Attr_List_Rename.get(attr_key) or {}

        # .. as above, for values that need to be renamed ..
        attr_list_value_rename  = ModuleCtx.Enmasse_Attr_List_Value_Rename.get(attr_key) or {}

        # .. as above, for attributes that need to be turned into a list ..
        attr_list_as_list = ModuleCtx.Enmasse_Attr_List_As_List.get(attr_key) or []

        # .. as above, for attributes that should be skipped if they are empty ..
        attr_list_as_multiline = ModuleCtx.Enmasse_Attr_List_As_Multiline.get(attr_key) or []

        # .. as above, for attributes that should be always skipped ..
        attr_list_skip_always = ModuleCtx.Enmasse_Attr_List_Skip_Always.get(attr_key) or []

        # .. as above, for attributes that should be skipped if they are empty ..
        attr_list_skip_if_empty = ModuleCtx.Enmasse_Attr_List_Skip_If_Empty.get(attr_key) or []

        # .. as above, for attributes that should be skipped if their value is True ..
        attr_list_skip_if_true = ModuleCtx.Enmasse_Attr_List_Skip_If_True.get(attr_key) or []

        # .. as above, for attributes that should be skipped if their value is False ..
        attr_list_skip_if_false = ModuleCtx.Enmasse_Attr_List_Skip_If_False.get(attr_key) or []

        # .. as above, for attributes that should be skipped if they have a specific value ..
        attr_list_skip_if_value_matches = ModuleCtx.Enmasse_Attr_List_Skip_If_Value_Matches.get(attr_key) or {}

        # .. as above, for attributes that should be skipped if other values match ..
        attr_list_skip_if_other_value_matches = ModuleCtx.Enmasse_Attr_List_Skip_If_Other_Value_Matches.get(attr_key) or {}

        # .. to make sure the dictionary does not change during iteration ..
        item_copy = deepcopy(item)

        # .. we enter here if there is anything to be explicitly process ..
        if attr_list_include or attr_list_exclude:

            # .. go through everything that we have ..
            for attr in item_copy:

                # .. remove from the item that we are returning any attr that is not to be included
                if attr not in attr_list_include:
                    _ = item.pop(attr, None)

                # .. remove any attribute that is explictly configured to be excluded ..
                if attr in attr_list_exclude:
                    _ = item.pop(attr, None)

        # .. optionally, rename selected attributes ..
        for old_name, new_name in attr_list_rename.items():
            if value := item.pop(old_name, NotGiven):
                if value is not NotGiven:
                    item[new_name] = value

        # .. optionally, rename selected values ..
        for attr_name, value_map_list in attr_list_value_rename.items():
            for value_map in value_map_list:
                if value := item.get(attr_name, NotGiven):
                    if value is not NotGiven:
                        if value in value_map:
                            new_value = value_map[value]
                            item[attr_name] = new_value

        # .. optionally, turn selected attributes into lists ..
        for attr in attr_list_as_list:
            if value := item.pop(attr, NotGiven):
                if value is not NotGiven:
                    if isinstance(value, str):
                        value = value.splitlines()
                        value.sort()
                    item[attr] = value

        # .. optionally, turn selected attributes into multi-line string objects ..
        for attr in attr_list_as_multiline:
            if value := item.pop(attr, NotGiven):
                if value is not NotGiven:
                    if isinstance(value, str):
                        value = value.splitlines()
                        value = '\n'.join(value)
                        item[attr] = value

        # .. optionally, certain attributes will be always skipped ..
        for attr in attr_list_skip_always:
            _ = item.pop(attr, NotGiven)

        # .. optionally, skip empty attributes ..
        for attr in attr_list_skip_if_empty:
            if value := item.pop(attr, NotGiven):
                if value is not NotGiven:
                    if value:
                        item[attr] = value

        # .. optionally, skip True attributes ..
        for attr in attr_list_skip_if_true:
            if value := item.pop(attr, NotGiven):
                if value is not True:
                    if value:
                        item[attr] = value

        # .. optionally, skip False attributes ..
        for attr in attr_list_skip_if_false:
            if value := item.pop(attr, NotGiven):
                if value is not False:
                    if value:
                        item[attr] = value

        # .. optionally, skip attributes that match configuration ..
        for pattern_key, pattern_value in attr_list_skip_if_value_matches.items():
            if value := item.pop(pattern_key, NotGiven): # type: ignore
                if value != pattern_value:
                    item[pattern_key] = value

        # .. optionally, skip attributes if other attributes have a specific value ..
        if attr_list_skip_if_other_value_matches:

            for config_dict in attr_list_skip_if_other_value_matches:

                criteria = config_dict['criteria']
                attrs_to_skip = config_dict['attrs']

                for criterion in criteria:
                    for criterion_key, criterion_value in criterion.items():
                        item_value = item.get(criterion_key, NotGiven)
                        if item_value is not NotGiven:
                            if item_value == criterion_value:
                                for attr in attrs_to_skip:
                                    _ = item.pop(attr, None)

        # .. ID's are never returned ..
        _ = item.pop('id', None)

        # .. service ID's are never returned ..
        _ = item.pop('service_id', None)

        # .. the is_active flag is never returned if it is of it default value, which is True ..
        if item.get('is_active') is True:
            _ = item.pop('is_active', None)

        # .. names of security definitions attached to an object are also skipped if they are the default ones ..
        if item.get('security_name') in ('', None):
            _ = item.pop('security_name', None)

        # .. the data format of REST objects defaults to JSON which is why we do not return it, unless it is different ..
        if item_type in {'channel_plain_http', 'outconn_plain_http', 'zato_generic_rest_wrapper'}:
            if item.get('data_format') == Data_Format.JSON:
                _ = item.pop('data_format', None)

        return item

# ################################################################################################################################

    def _sort_item_attrs(
        self,
        attr_key, # type: str
        item,     # type: strdict
    ) -> 'strdict':

        # stdlib
        from collections import OrderedDict

        # Turn the item into an object whose attributes can be sorted ..
        item = OrderedDict(item)

        # .. go through each of the attribute in the order of preference, assuming that we have any matching one ..
        # .. it needs to be reversed because we are pushing each such attribute to the front, as in a stack ..
        for attr in reversed(ModuleCtx.Enmasse_Attr_List_Sort_Order.get(attr_key) or []):

            if attr in item:
                item.move_to_end(attr, last=False)

        return item

# ################################################################################################################################

    def _should_write_to_output(
        self,
        item_type, # type: str
        item,      # type: strdict
        include_type, # type: strlist
        include_name, # type: strlist
    ) -> 'bool':

        # Type hints
        name:'str'

        # Local aliases
        if item_type == 'pubsub_subscription':
            name = item['endpoint_name']
        else:
            name = item['name']

        # By default, assume this item should be written to ouput unless we contradict it below ..
        out:'bool' = True

        # We will make use of input includes only if we are not to export all of them
        has_all_types = ModuleCtx.Include_Type.All in include_type
        has_all_names = ModuleCtx.Include_Type.All in include_name

        has_type = not has_all_types
        has_name = not has_all_names

        # Certain internal objects should never be exported ..
        if item_type == 'def_sec':

            # .. do not write RBAC definitions ..
            if 'rbac' in item['type']:
                return False

        # .. do not write internal definitions ..
        if has_name_zato_prefix(name):
            return False

        # We enter this branch if we are to export specific types ..
        if not has_all_types:
            out_by_type = self._should_write_type_to_output(item_type, item, include_type)
        else:
            out_by_type = False

        # We enter this branch if we are to export objects of specific names ..
        if not has_all_names:
            item_name = item.get('name') or ''
            item_name = item_name.lower()
            out_by_name = self._should_write_name_to_output(item_type, item_name, include_name)
        else:
            out_by_name = False

        # We enter here if we have both type and name on input, which means that we need to and-join them ..
        if has_type and has_name:
            out = out_by_type and out_by_name
        else:
            if has_type:
                out = out_by_type
            elif has_name:
                out = out_by_name

        # .. we are ready to return our output
        return out

# ################################################################################################################################

    def _rewrite_pubsub_subscriptions_during_export(self, subs:'dictlist') -> 'dictlist':

        # Bunch
        from bunch import Bunch, bunchify

        # Our response to produce
        out:'dictlist' = []

        # Local variables
        subs_by_key:'anydict' = {}

        #
        # We are going to group subscriptions by these keys
        #
        # - Endpoint name
        # - Delivery method
        # - REST method
        # - REST connection
        # - Delivery server
        #

        for sub in subs:

            # .. for dot attribute access ..
            sub = Bunch(sub)

            # .. build a composite key to later add topics to it ..
            key:'any_' = (sub.endpoint_name, sub.delivery_method, sub.rest_method, sub.rest_connection, sub.delivery_server)

            # .. add the key if it does not already exist ..
            if key not in subs_by_key:
                subs_by_key[key] = bunchify({
                    'endpoint_name': sub.get('endpoint_name'),
                    'endpoint_type': sub.get('endpoint_type'),
                    'delivery_method': sub.get('delivery_method'),
                    'rest_method': sub.get('rest_method'),
                    'rest_connection': sub.get('rest_connection'),
                    'service_name': sub.get('service_name'),
                    'delivery_server': sub.get('delivery_server'),
                    'topic_list': []
                })

            # .. at this point, we know we have a list for this key so we can access it ..
            subs_by_key_dict = subs_by_key[key]

            # .. and append the current topic to what we are building for the caller ..
            subs_by_key_dict.topic_list.append(sub.topic_name)

        # .. now, we can discard the keys and we will be left with subscriptions alone ..
        for idx, sub_info in enumerate(subs_by_key.values(), 1):

            # .. return topics sorted alphabetically ..
            sub_info.topic_list.sort()

            # .. make sure we are returning a dict ..
            sub_info = sub_info.toDict()

            # .. each subscription needs a name ..
            sub_info['name'] = 'Subscription.' + str(idx).zfill(9)

            # .. append it for our caller ..
            out.append(sub_info)

        # .. now, we can return the result
        return out

# ################################################################################################################################

    def write_output(
        self,
        output_path,  # type: strnone
        include_type, # type: strlist
        include_name, # type: strlist
    ) -> 'None':

        # stdlib
        import os
        import re
        from datetime import datetime
        from collections import OrderedDict

        # Bunch
        from zato.bunch import debunchify

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        # Local aliases
        to_write:'strdict' = {}

        # Make a copy and remove Bunch; pyaml does not like Bunch instances.
        output:'strdict' = debunchify(self.json)
        output = deepcopy(output)

        # Preserve old format by splitting out particular types of http-soap.
        for item in output.pop('http_soap', []):
            for item_type, connection, transport in HTTP_SOAP_KINDS:
                if item['connection'] == connection and item['transport'] == transport:
                    output.setdefault(item_type, []).append(item)

        # Preserve old format by wrapping security services into one key.
        output['def_sec'] = []
        for service_info in SERVICES:
            if service_info.is_security:
                output['def_sec'].extend(
                    dict(item, type=service_info.name)
                    for item in output.pop(service_info.name, [])
                )

        # .. rewrite pub/sub subscriptions in a way that is easier to handle ..
        if subs := output.get('pubsub_subscription'):
            output['pubsub_subscription'] = self._rewrite_pubsub_subscriptions_during_export(subs)

        # .. go through everything that we collected in earlier steps in the process ..
        for item_type, items in iteritems(output): # type: ignore

            # .. add type hints ..
            items = cast_('dictlist', items)

            # .. this is a new list of items to write ..
            # .. based on the list from output ..
            to_write_items:'dictlist' = []

            # .. now, go through each item in the original output ..
            for item in items:

                # .. add type hints ..
                item = cast_('strdict', item)
                item = deepcopy(item)

                # .. normalize attributes ..
                normalize_service_name(item)

                # .. make sure we want to write this item on output ..
                if not self._should_write_to_output(item_type, item, include_type, include_name):
                    continue

                # .. this is required because generic connections are differentiated ..
                # .. by their embedded 'type_' attribute, rather but item_type itself ..
                if item_type == 'zato_generic_connection':
                    wrapper_type = item['type_']
                    attr_key = f'{item_type}_{wrapper_type}'
                else:
                    attr_key = item_type

                # .. this will rename or remove any attributes from this item that we do not need ..
                item = self._preprocess_item_attrs_during_export(attr_key, item_type, item)

                # .. sort the attributes in the order we want them to appear in the outpur file ..
                item = self._sort_item_attrs(attr_key, item)

                # .. if we are here, it means that we want to include this item on output ..
                to_write_items.append(item)

            # .. sort item lists to be written ..
            to_write_items.sort(key=lambda item: item.get('name', '').lower())

            # .. now, append this new list to what is to be written ..
            # .. but only if there is anything to be written for that type ..
            if to_write_items:
                to_write[item_type] = to_write_items

        # .. replace non-generic connection item type names ..
        for old_name, new_name in ModuleCtx.Enmasse_Item_Type_Name_Map.items():
            value = to_write.pop(old_name, None)
            if value:
                to_write[new_name] = value

        # .. now, replace generic connection types which are more involved ..
        new_names:'any_' = {
            'outgoing_ldap': [],
            'outgoing_wsx': [],
        }

        for old_name, value_list in to_write.items():
            value_list = cast_('anylist', value_list)
            if old_name == 'zato_generic_connection':
                for idx, value in enumerate(value_list):
                    if wrapper_type := value.get('type_'):
                        attr_key = f'{old_name}_{wrapper_type}'
                        if new_name := ModuleCtx.Enmasse_Item_Type_Name_Map.get(attr_key):
                            _ = value.pop('type_')
                            new_names[new_name].append(value)
                            value_list.pop(idx)

        # .. append the new names extracted from generic connections to what we need to write ..
        for new_name, value_list in new_names.items():
            if value_list:
                to_write[new_name] = value_list

        # .. if there are no generic connections left at this point, this key can be deleted ..
        if not to_write.get('zato_generic_connection'):
            _ = to_write.pop('zato_generic_connection', None)

        # .. this lets us move individual keys around ..
        to_write = OrderedDict(to_write)

        # .. certain keys should be stored in a specific order at the head of the output ..
        key_order = reversed([
            'security_groups',
            'security',
            'channel_rest',
            'outgoing_rest',
        ])

        # .. do move the keys now, in the order specified above ..
        for key in key_order:
            if key in to_write:
                to_write.move_to_end(key, last=False)

        # .. if we have the name of a file to use, do use it ..
        if output_path:
            name = output_path

        # .. otherwise, use a new file ..
        else:
            now = datetime.now().isoformat() # Not in UTC, we want to use user's TZ
            name = 'zato-export-{}{}'.format(re.sub('[.:]', '_', now), self.codec.extension)

        with open(os.path.join(self.curdir, name), 'w') as f:
            self.codec.dump(f, to_write)

        self.logger.info('Data exported to {}'.format(f.name))

# ################################################################################################################################

    def get_warnings_errors(self, items): # type: ignore
        warn_idx = 1
        error_idx = 1
        warn_err = {}

        for item in items: # type: ignore

            for warning in item.warnings: # type: ignore
                warn_err['warn{:04}/{} {}'.format(warn_idx, warning.code.symbol, warning.code.desc)] = warning.value
                warn_idx += 1

            for error in item.errors: # type: ignore
                warn_err['err{:04}/{} {}'.format(error_idx, error.code.symbol, error.code.desc)] = error.value
                error_idx += 1

        warn_no = warn_idx-1
        error_no = error_idx-1

        return warn_err, warn_no, error_no # type: ignore

# ################################################################################################################################

    def report_warnings_errors(self, items): # type: ignore

        # stdlib
        import logging

        warn_err, warn_no, error_no = self.get_warnings_errors(items)
        table = self.get_table(warn_err)

        warn_plural = '' if warn_no == 1 else 's'
        error_plural = '' if error_no == 1 else 's'

        if warn_no or error_no:
            if error_no:
                level = logging.ERROR
            else:
                level = logging.WARN

            prefix = '{} warning{} and {} error{} found:\n'.format(warn_no, warn_plural, error_no, error_plural)
            self.logger.log(level, prefix + table.draw()) # type: ignore

        else:
            # A signal that we found no warnings nor errors
            return True

# ################################################################################################################################

    def get_table(self, out): # type: ignore

        # texttable
        import texttable

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        cols_width = self.args.cols_width if getattr(self.args, 'cols_width', None) else DEFAULT_COLS_WIDTH
        cols_width = (elem.strip() for elem in cols_width.split(','))
        cols_width = [int(elem) for elem in cols_width]

        table = texttable.Texttable()
        _ = table.set_cols_width(cols_width)

        # Use text ('t') instead of auto so that boolean values don't get converted into ints
        _ = table.set_cols_dtype(['t', 't'])

        rows = [['Key', 'Value']]
        rows.extend(sorted(iteritems(out)))

        _ = table.add_rows(rows)

        return table

# ################################################################################################################################

    def merge_odb_json(self):

        # stdlib
        import copy

        # Python 2/3 compatibility
        from zato.common.ext.future.utils import iteritems

        results = Results()
        merged = copy.deepcopy(self.object_mgr.objects)

        for json_key, json_elems in iteritems(self.json): # type: ignore
            if 'http' in json_key or 'soap' in json_key:
                odb_key = 'http_soap'
            else:
                odb_key:'any_' = json_key

            if odb_key not in merged:
                sorted_merged:'any_' = sorted(merged)
                raw:'any_' = (json_key, odb_key, sorted_merged)
                results.add_error(raw, ERROR_INVALID_KEY, "JSON key '{}' not one of '{}'", odb_key, sorted_merged)
            else:
                for json_elem in json_elems: # type: ignore
                    if 'http' in json_key or 'soap' in json_key:
                        connection, transport = json_key.split('_', 1)
                        connection = 'outgoing' if connection == 'outconn' else connection

                        for odb_elem in merged.http_soap: # type: ignore
                            if odb_elem.get('transport') == transport and odb_elem.get('connection') == connection:
                                if odb_elem.name == json_elem.name:
                                    merged.http_soap.remove(odb_elem)
                    else:
                        for odb_elem in merged[odb_key]: # type: ignore
                            if odb_elem.name == json_elem.name:
                                merged[odb_key].remove(odb_elem)
                    merged[odb_key].append(json_elem)

        if results.ok:
            self.json = merged
        return results

# ################################################################################################################################

    def export(self):
        # Find any definitions that are missing
        dep_scanner = DependencyScanner(self.json, self.is_import, self.is_export, ignore_missing=self.args.ignore_missing_defs)
        missing_defs = dep_scanner.scan()
        if not missing_defs.ok:
            self.logger.error('Failed to find all definitions needed')
            return [missing_defs]

        # Validate if every required input element has been specified.
        results = InputValidator(self.json).validate()
        if not results.ok:
            self.logger.error('Required elements missing')
            return [results]

        return [] # type: ignore

# ################################################################################################################################

    def export_local_odb(self, needs_local=True): # type: ignore
        self.object_mgr.refresh()
        self.logger.info('ODB objects read')

        results = self.merge_odb_json()
        if not results.ok:
            return [results]
        self.logger.info('ODB objects merged in')

        return self.export()

# ################################################################################################################################

    def run_odb_export(self):
        return self.export_local_odb(False)

# ################################################################################################################################

    def _get_missing_objects(self, warnings_errors:'list_[Results]') -> 'strlist':

        # Our response to produce
        out:'strlist' = []

        for item in warnings_errors:

            for elem in chain(item.warnings, item.errors): # type: ignore
                elem = cast_('Notice', elem)
                if elem.code == ERROR_SERVICE_MISSING:
                    enmasse_elem:'stranydict' = elem.value_raw[1]
                    service_name = enmasse_elem['service']
                    out.append(service_name)

        # Return everything we have found to our caller, sorted alphabetically
        return sorted(out)

# ################################################################################################################################

    def run_import(self) -> 'anylist':

        # Local variables
        start_time = datetime.utcnow()
        wait_until = start_time + timedelta(seconds=self.missing_wait_time)

        # Run the initial import ..
        warnings_errors = self._run_import()

        while warnings_errors:

            # Loop variables
            now = datetime.utcnow()

            # .. if we have already waited enough, we can already return ..
            if now > wait_until:
                return warnings_errors

            # .. if there is anything that we need to wait for, ..
            # .. such as missing services, we will keep running ..
            missing = self._get_missing_objects(warnings_errors)

            # .. if nothing is missing, we can return as well ..
            if not missing:
                return warnings_errors

            # .. for reporting purposes, get information on how much longer are to wait ..
            wait_delta = wait_until - now

            # .. report what we are waiting for ..
            msg = f'Enmasse waiting; timeout -> {wait_delta}; missing -> {missing}'
            self.logger.info(msg)

            # .. do wait now ..
            sleep(2)

            # .. re-run the import ..
            warnings_errors = self._run_import()

        # .. either we run out of time or we have succeed, in either case, we can return.
        return warnings_errors

# ################################################################################################################################

    def _run_import(self) -> 'anylist':

        # Make sure we have the latest state of information ..
        self.object_mgr.refresh()

        # .. build an object that will import the definitions ..
        importer = ObjectImporter(self.client, self.logger, self.object_mgr, self.json,  # type: ignore
            self.is_import, self.is_export, ignore_missing=self.args.ignore_missing_defs, args=self.args)

        # .. find channels and jobs that require services that do not exist ..
        results = importer.validate_import_data()
        if not results.ok:
            return [results]

        already_existing = importer.find_already_existing_odb_objects()
        if not already_existing.ok and not self.replace_objects:
            return [already_existing]

        results = importer.import_objects(already_existing)
        if not results.ok:
            return [results]

        return []

# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import sys

    # Bunch
    from bunch import Bunch

    args = Bunch()
    args.verbose = True
    args.store_log = False
    args.store_config = False
    args.format = 'yaml'
    args.export_local = False
    args.export_odb = False
    args.clean_odb = False
    args.ignore_missing_defs = False
    args.output = None
    args.rbac_sleep = 1

    # args['replace'] = True
    # args['import'] = True
    args['export'] = True

    args.path  = sys.argv[1]
    args.input = sys.argv[2] if 'import' in args else ''

    enmasse = Enmasse(args)
    enmasse.run(args)
