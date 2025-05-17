# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from inspect import isclass

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems
from zato.common.py23_.past.builtins import cmp

from zato.common.ext.candv import Constants as _Constants, ValueConstant as _ValueConstant

class Constants(_Constants):
    values = _Constants.constants

class ValueConstant(_ValueConstant):

    def __cmp__(self, other):
        return cmp(self.value, (other.value if isinstance(other, ValueConstant) else other))

class MESSAGE:
    MESSAGE_TYPE_LENGTH = 4
    TOKEN_LENGTH = 32
    TOKEN_START = MESSAGE_TYPE_LENGTH
    TOKEN_END = MESSAGE_TYPE_LENGTH + TOKEN_LENGTH
    PAYLOAD_START = MESSAGE_TYPE_LENGTH + TOKEN_LENGTH
    NULL_TOKEN = '0' * TOKEN_LENGTH

class MESSAGE_TYPE:
    TO_SCHEDULER = '0000'
    TO_PARALLEL_ANY = '0001'
    TO_PARALLEL_ALL = '0002'

    USER_DEFINED_START = '5000'

TOPICS = {
    MESSAGE_TYPE.TO_SCHEDULER: '/zato/to-scheduler',

    MESSAGE_TYPE.TO_PARALLEL_ANY: '/zato/to-parallel/any',
    MESSAGE_TYPE.TO_PARALLEL_ALL: '/zato/to-parallel/all',

}

KEYS = {k:v.replace('/zato','').replace('/',':') for k,v in TOPICS.items()}

class SCHEDULER(Constants):
    code_start = 100000

    PAUSE = ValueConstant('')
    RESUME = ValueConstant('')
    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')
    EXECUTE = ValueConstant('')
    JOB_EXECUTED = ValueConstant('')
    SET_JOB_INACTIVE = ValueConstant('')
    SET_SERVER_ADDRESS = ValueConstant('')
    SET_SCHEDULER_ADDRESS = ValueConstant('')

class SECURITY(Constants):
    code_start = 100400

    BASIC_AUTH_CREATE = ValueConstant('')
    BASIC_AUTH_EDIT = ValueConstant('')
    BASIC_AUTH_DELETE = ValueConstant('')
    BASIC_AUTH_CHANGE_PASSWORD = ValueConstant('')

    OAUTH_CREATE = ValueConstant('')
    OAUTH_EDIT = ValueConstant('')
    OAUTH_DELETE = ValueConstant('')
    OAUTH_CHANGE_PASSWORD = ValueConstant('')

    NTLM_CREATE = ValueConstant('')
    NTLM_EDIT = ValueConstant('')
    NTLM_DELETE = ValueConstant('')
    NTLM_CHANGE_PASSWORD = ValueConstant('')

    APIKEY_CREATE = ValueConstant('')
    APIKEY_EDIT = ValueConstant('')
    APIKEY_DELETE = ValueConstant('')
    APIKEY_CHANGE_PASSWORD = ValueConstant('')

class OUTGOING(Constants):
    code_start = 100800

    AMQP_CREATE = ValueConstant('')
    AMQP_EDIT = ValueConstant('')
    AMQP_DELETE = ValueConstant('')
    AMQP_PUBLISH = ValueConstant('')

    SQL_CREATE_EDIT = ValueConstant('') # Same for creating and updating the pools
    SQL_CHANGE_PASSWORD = ValueConstant('')
    SQL_DELETE = ValueConstant('')

    HTTP_SOAP_CREATE_EDIT = ValueConstant('') # Same for creating and updating
    HTTP_SOAP_DELETE = ValueConstant('')

    FTP_CREATE_EDIT = ValueConstant('') # Same for creating and updating
    FTP_DELETE = ValueConstant('')
    FTP_CHANGE_PASSWORD = ValueConstant('')

    ODOO_CREATE = ValueConstant('')
    ODOO_EDIT = ValueConstant('')
    ODOO_DELETE = ValueConstant('')
    ODOO_CHANGE_PASSWORD = ValueConstant('')

    SAP_CREATE = ValueConstant('')
    SAP_EDIT = ValueConstant('')
    SAP_DELETE = ValueConstant('')
    SAP_CHANGE_PASSWORD = ValueConstant('')

    REST_WRAPPER_CHANGE_PASSWORD = ValueConstant('')

class CHANNEL(Constants):
    code_start = 101000

    AMQP_CREATE = ValueConstant('')
    AMQP_EDIT = ValueConstant('')
    AMQP_DELETE = ValueConstant('')
    AMQP_MESSAGE_RECEIVED = ValueConstant('')

    HTTP_SOAP_CREATE_EDIT = ValueConstant('') # Same for creating and updating
    HTTP_SOAP_DELETE = ValueConstant('')

    FTP_CREATE = ValueConstant('')
    FTP_EDIT = ValueConstant('')
    FTP_DELETE = ValueConstant('')
    FTP_PING = ValueConstant('')
    FTP_USER_CREATE = ValueConstant('')
    FTP_USER_EDIT = ValueConstant('')
    FTP_USER_DELETE = ValueConstant('')
    FTP_USER_CHANGE_PASSWORD = ValueConstant('')

class SERVICE(Constants):
    code_start = 101800

    EDIT = ValueConstant('')
    DELETE = ValueConstant('')
    PUBLISH = ValueConstant('')

class HOT_DEPLOY(Constants):
    code_start = 102200
    CREATE_SERVICE = ValueConstant('')
    CREATE_STATIC = ValueConstant('')
    CREATE_USER_CONF = ValueConstant('')
    AFTER_DEPLOY = ValueConstant('')

class SEARCH(Constants):
    code_start = 104200
    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

    ES_CREATE = ValueConstant('')
    ES_EDIT = ValueConstant('')
    ES_DELETE = ValueConstant('')
    ES_CHANGE_PASSWORD = ValueConstant('')

class EMAIL(Constants):
    code_start = 104800

    SMTP_CREATE = ValueConstant('')
    SMTP_EDIT = ValueConstant('')
    SMTP_DELETE = ValueConstant('')
    SMTP_CHANGE_PASSWORD = ValueConstant('')

    IMAP_CREATE = ValueConstant('')
    IMAP_EDIT = ValueConstant('')
    IMAP_DELETE = ValueConstant('')
    IMAP_CHANGE_PASSWORD = ValueConstant('')

class CACHE(Constants):
    code_start = 106400

    BUILTIN_CREATE = ValueConstant('')
    BUILTIN_EDIT = ValueConstant('')
    BUILTIN_DELETE = ValueConstant('')

    BUILTIN_STATE_CHANGED_CLEAR = ValueConstant('')

    BUILTIN_STATE_CHANGED_DELETE = ValueConstant('')
    BUILTIN_STATE_CHANGED_DELETE_BY_PREFIX = ValueConstant('')
    BUILTIN_STATE_CHANGED_DELETE_BY_SUFFIX = ValueConstant('')
    BUILTIN_STATE_CHANGED_DELETE_BY_REGEX = ValueConstant('')
    BUILTIN_STATE_CHANGED_DELETE_CONTAINS = ValueConstant('')
    BUILTIN_STATE_CHANGED_DELETE_NOT_CONTAINS = ValueConstant('')
    BUILTIN_STATE_CHANGED_DELETE_CONTAINS_ALL = ValueConstant('')
    BUILTIN_STATE_CHANGED_DELETE_CONTAINS_ANY = ValueConstant('')

    BUILTIN_STATE_CHANGED_EXPIRE = ValueConstant('')
    BUILTIN_STATE_CHANGED_EXPIRE_BY_PREFIX = ValueConstant('')
    BUILTIN_STATE_CHANGED_EXPIRE_BY_SUFFIX = ValueConstant('')
    BUILTIN_STATE_CHANGED_EXPIRE_BY_REGEX = ValueConstant('')
    BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS = ValueConstant('')
    BUILTIN_STATE_CHANGED_EXPIRE_NOT_CONTAINS = ValueConstant('')
    BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS_ALL = ValueConstant('')
    BUILTIN_STATE_CHANGED_EXPIRE_CONTAINS_ANY = ValueConstant('')

    BUILTIN_STATE_CHANGED_SET = ValueConstant('')
    BUILTIN_STATE_CHANGED_SET_BY_PREFIX = ValueConstant('')
    BUILTIN_STATE_CHANGED_SET_BY_SUFFIX = ValueConstant('')
    BUILTIN_STATE_CHANGED_SET_BY_REGEX = ValueConstant('')
    BUILTIN_STATE_CHANGED_SET_CONTAINS = ValueConstant('')
    BUILTIN_STATE_CHANGED_SET_NOT_CONTAINS = ValueConstant('')
    BUILTIN_STATE_CHANGED_SET_CONTAINS_ALL = ValueConstant('')
    BUILTIN_STATE_CHANGED_SET_CONTAINS_ANY = ValueConstant('')

    MEMCACHED_CREATE = ValueConstant('')
    MEMCACHED_EDIT = ValueConstant('')
    MEMCACHED_DELETE = ValueConstant('')

class GENERIC(Constants):
    code_start = 107000

    CONNECTION_CREATE = ValueConstant('')
    CONNECTION_EDIT = ValueConstant('')
    CONNECTION_DELETE = ValueConstant('')
    CONNECTION_CHANGE_PASSWORD = ValueConstant('')

class SSO(Constants):
    code_start = 107200

    USER_CREATE = ValueConstant('')
    USER_EDIT   = ValueConstant('')

class Common(Constants):
    code_start = 107800
    Sync_Objects = ValueConstant('')

class Groups(Constants):
    code_start = 108000
    Edit = ValueConstant('')
    Edit_Member_List = ValueConstant('')
    Delete = ValueConstant('')

code_to_name = {}

# To prevent 'RuntimeError: dictionary changed size during iteration'
item_name, item = None, None
_globals = list(iteritems(globals()))

for item_name, item in _globals:
    if isclass(item) and issubclass(item, Constants) and item is not Constants:
        for idx, (attr, const) in enumerate(item.items()):
            const.value = str(item.code_start + idx)
            code_to_name[const.value] = '{}_{}'.format(item_name, attr)
