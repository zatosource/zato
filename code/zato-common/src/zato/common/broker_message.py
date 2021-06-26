# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from inspect import isclass

# candv
from candv import Constants as _Constants, ValueConstant as _ValueConstant

# Python 2/3 compatibility
from future.utils import iteritems
from past.builtins import cmp

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

    TO_AMQP_PUBLISHING_CONNECTOR_ALL = '0003'
    TO_AMQP_CONSUMING_CONNECTOR_ALL = '0004'
    TO_AMQP_CONNECTOR_ALL = '0005'

    TO_JMS_WMQ_PUBLISHING_CONNECTOR_ALL = '0006'
    TO_JMS_WMQ_CONSUMING_CONNECTOR_ALL = '0007'
    TO_JMS_WMQ_CONNECTOR_ALL = '0008'

    USER_DEFINED_START = '5000'

TOPICS = {
    MESSAGE_TYPE.TO_SCHEDULER: '/zato/to-scheduler',

    MESSAGE_TYPE.TO_PARALLEL_ANY: '/zato/to-parallel/any',
    MESSAGE_TYPE.TO_PARALLEL_ALL: '/zato/to-parallel/all',

    MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_ALL: '/zato/connector/amqp/publishing/all',
    MESSAGE_TYPE.TO_AMQP_CONSUMING_CONNECTOR_ALL: '/zato/connector/amqp/consuming/all',
    MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL: '/zato/connector/amqp/all',

    MESSAGE_TYPE.TO_JMS_WMQ_PUBLISHING_CONNECTOR_ALL: '/zato/connector/jms-wmq/publishing/all',
    MESSAGE_TYPE.TO_JMS_WMQ_CONSUMING_CONNECTOR_ALL: '/zato/connector/jms-wmq/consuming/all',
    MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_ALL: '/zato/connector/jms-wmq/all',

}

KEYS = {k:v.replace('/zato','').replace('/',':') for k,v in TOPICS.items()}

class SCHEDULER(Constants):
    code_start = 100000

    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')
    EXECUTE = ValueConstant('')
    JOB_EXECUTED = ValueConstant('')
    SET_JOB_INACTIVE = ValueConstant('')

class ZMQ_SOCKET(Constants):
    code_start = 100200
    CLOSE = ValueConstant('')

class SECURITY(Constants):
    code_start = 100400

    BASIC_AUTH_CREATE = ValueConstant('')
    BASIC_AUTH_EDIT = ValueConstant('')
    BASIC_AUTH_DELETE = ValueConstant('')
    BASIC_AUTH_CHANGE_PASSWORD = ValueConstant('')

    JWT_CREATE = ValueConstant('')
    JWT_EDIT = ValueConstant('')
    JWT_DELETE = ValueConstant('')
    JWT_CHANGE_PASSWORD = ValueConstant('')

    WSS_CREATE = ValueConstant('')
    WSS_EDIT = ValueConstant('')
    WSS_DELETE = ValueConstant('')
    WSS_CHANGE_PASSWORD = ValueConstant('')

    OAUTH_CREATE = ValueConstant('')
    OAUTH_EDIT = ValueConstant('')
    OAUTH_DELETE = ValueConstant('')
    OAUTH_CHANGE_PASSWORD = ValueConstant('')

    NTLM_CREATE = ValueConstant('')
    NTLM_EDIT = ValueConstant('')
    NTLM_DELETE = ValueConstant('')
    NTLM_CHANGE_PASSWORD = ValueConstant('')

    AWS_CREATE = ValueConstant('')
    AWS_EDIT = ValueConstant('')
    AWS_DELETE = ValueConstant('')
    AWS_CHANGE_PASSWORD = ValueConstant('')

    APIKEY_CREATE = ValueConstant('')
    APIKEY_EDIT = ValueConstant('')
    APIKEY_DELETE = ValueConstant('')
    APIKEY_CHANGE_PASSWORD = ValueConstant('')

    XPATH_SEC_CREATE = ValueConstant('')
    XPATH_SEC_EDIT = ValueConstant('')
    XPATH_SEC_DELETE = ValueConstant('')
    XPATH_SEC_CHANGE_PASSWORD = ValueConstant('')

    TLS_CA_CERT_CREATE = ValueConstant('')
    TLS_CA_CERT_EDIT = ValueConstant('')
    TLS_CA_CERT_DELETE = ValueConstant('')

    TLS_CHANNEL_SEC_CREATE = ValueConstant('')
    TLS_CHANNEL_SEC_EDIT = ValueConstant('')
    TLS_CHANNEL_SEC_DELETE = ValueConstant('')

    TLS_KEY_CERT_CREATE = ValueConstant('')
    TLS_KEY_CERT_EDIT = ValueConstant('')
    TLS_KEY_CERT_DELETE = ValueConstant('')

class DEFINITION(Constants):
    code_start = 100600

    AMQP_CREATE = ValueConstant('')
    AMQP_EDIT = ValueConstant('')
    AMQP_DELETE = ValueConstant('')
    AMQP_CHANGE_PASSWORD = ValueConstant('')

    WMQ_CREATE = ValueConstant('')
    WMQ_EDIT = ValueConstant('')
    WMQ_DELETE = ValueConstant('')
    WMQ_CHANGE_PASSWORD = ValueConstant('')
    WMQ_PING = ValueConstant('')

    ZMQ_CREATE = ValueConstant('')
    ZMQ_EDIT = ValueConstant('')
    ZMQ_DELETE = ValueConstant('')

    CASSANDRA_CREATE = ValueConstant('')
    CASSANDRA_EDIT = ValueConstant('')
    CASSANDRA_DELETE = ValueConstant('')
    CASSANDRA_CHANGE_PASSWORD = ValueConstant('')

class OUTGOING(Constants):
    code_start = 100800

    AMQP_CREATE = ValueConstant('')
    AMQP_EDIT = ValueConstant('')
    AMQP_DELETE = ValueConstant('')
    AMQP_PUBLISH = ValueConstant('')

    WMQ_CREATE = ValueConstant('')
    WMQ_EDIT = ValueConstant('')
    WMQ_DELETE = ValueConstant('')
    WMQ_SEND = ValueConstant('')

    ZMQ_CREATE = ValueConstant('')
    ZMQ_EDIT = ValueConstant('')
    ZMQ_DELETE = ValueConstant('')
    ZMQ_SEND = ValueConstant('')

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

    SFTP_CREATE = ValueConstant('')
    SFTP_EDIT = ValueConstant('')
    SFTP_DELETE = ValueConstant('')
    SFTP_CHANGE_PASSWORD = ValueConstant('')
    SFTP_EXECUTE = ValueConstant('')
    SFTP_PING = ValueConstant('')

class CHANNEL(Constants):
    code_start = 101000

    AMQP_CREATE = ValueConstant('')
    AMQP_EDIT = ValueConstant('')
    AMQP_DELETE = ValueConstant('')
    AMQP_MESSAGE_RECEIVED = ValueConstant('')

    WMQ_CREATE = ValueConstant('')
    WMQ_EDIT = ValueConstant('')
    WMQ_DELETE = ValueConstant('')
    WMQ_MESSAGE_RECEIVED = ValueConstant('')

    ZMQ_CREATE = ValueConstant('')
    ZMQ_EDIT = ValueConstant('')
    ZMQ_DELETE = ValueConstant('')
    ZMQ_MESSAGE_RECEIVED = ValueConstant('')

    HTTP_SOAP_CREATE_EDIT = ValueConstant('') # Same for creating and updating
    HTTP_SOAP_DELETE = ValueConstant('')

    WEB_SOCKET_CREATE = ValueConstant('')
    WEB_SOCKET_EDIT = ValueConstant('')
    WEB_SOCKET_DELETE = ValueConstant('')
    WEB_SOCKET_BROADCAST = ValueConstant('')

    FTP_CREATE = ValueConstant('')
    FTP_EDIT = ValueConstant('')
    FTP_DELETE = ValueConstant('')
    FTP_PING = ValueConstant('')
    FTP_USER_CREATE = ValueConstant('')
    FTP_USER_EDIT = ValueConstant('')
    FTP_USER_DELETE = ValueConstant('')
    FTP_USER_CHANGE_PASSWORD = ValueConstant('')

class AMQP_CONNECTOR(Constants):
    """ Since 3.0, this is not used anymore.
    """
    code_start = 101200
    CLOSE = ValueConstant('')

class JMS_WMQ_CONNECTOR(Constants):
    """ Since 3.0, this is not used anymore.
    """
    code_start = 101400
    CLOSE = ValueConstant('')

class ZMQ_CONNECTOR(Constants):
    """ Since 3.0, this is not used anymore.
    """
    code_start = 101600
    CLOSE = ValueConstant('')

class SERVICE(Constants):
    code_start = 101800

    EDIT = ValueConstant('')
    DELETE = ValueConstant('')
    PUBLISH = ValueConstant('')

class STATS(Constants):
    code_start = 102000

    DELETE = ValueConstant('')
    DELETE_DAY = ValueConstant('')

class HOT_DEPLOY(Constants):
    code_start = 102200
    CREATE_SERVICE = ValueConstant('')
    CREATE_STATIC = ValueConstant('')
    CREATE_USER_CONF = ValueConstant('')
    AFTER_DEPLOY = ValueConstant('')

class SINGLETON(Constants):
    code_start = 102400
    CLOSE = ValueConstant('')

class MSG_NS(Constants):
    code_start = 102600

    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class MSG_XPATH(Constants):
    code_start = 102800

    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class MSG_JSON_POINTER(Constants):
    code_start = 103000

    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class PUB_SUB_TOPIC(Constants):
    code_start = 103200

    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')
    ADD_DEFAULT_PRODUCER = ValueConstant('')
    DELETE_DEFAULT_PRODUCER = ValueConstant('')

class PUB_SUB_PRODUCER(Constants):
    code_start = 103400

    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class PUB_SUB_CONSUMER(Constants):
    code_start = 103600

    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class CLOUD(Constants):
    code_start = 103800

    AWS_S3_CREATE_EDIT = ValueConstant('')
    AWS_S3_DELETE = ValueConstant('')

class NOTIF(Constants):
    code_start = 104000

    RUN_NOTIFIER = ValueConstant('')

    SQL_CREATE = ValueConstant('')
    SQL_EDIT = ValueConstant('')
    SQL_DELETE = ValueConstant('')

class SEARCH(Constants):
    code_start = 104200
    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

    ES_CREATE = ValueConstant('')
    ES_EDIT = ValueConstant('')
    ES_DELETE = ValueConstant('')
    ES_CHANGE_PASSWORD = ValueConstant('')

    SOLR_CREATE = ValueConstant('')
    SOLR_EDIT = ValueConstant('')
    SOLR_DELETE = ValueConstant('')
    SOLR_CHANGE_PASSWORD = ValueConstant('')

class QUERY(Constants):
    code_start = 104400

    CASSANDRA_CREATE = ValueConstant('')
    CASSANDRA_EDIT = ValueConstant('')
    CASSANDRA_DELETE = ValueConstant('')
    CASSANDRA_CHANGE_PASSWORD = ValueConstant('')

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

class RBAC(Constants):
    code_start = 105200

    ROLE_CREATE = ValueConstant('')
    ROLE_EDIT = ValueConstant('')
    ROLE_DELETE = ValueConstant('')

    CLIENT_ROLE_CREATE = ValueConstant('')
    CLIENT_ROLE_DELETE = ValueConstant('')

    PERMISSION_CREATE = ValueConstant('')
    PERMISSION_EDIT = ValueConstant('')
    PERMISSION_DELETE = ValueConstant('')

    ROLE_PERMISSION_CREATE = ValueConstant('')
    ROLE_PERMISSION_EDIT = ValueConstant('')
    ROLE_PERMISSION_DELETE = ValueConstant('')

class VAULT(Constants):
    code_start = 105400

    CONNECTION_CREATE = ValueConstant('')
    CONNECTION_EDIT = ValueConstant('')
    CONNECTION_DELETE = ValueConstant('')

    POLICY_CREATE = ValueConstant('')
    POLICY_EDIT = ValueConstant('')
    POLICY_DELETE = ValueConstant('')

class PUBSUB(Constants):
    code_start = 105600

    ENDPOINT_CREATE = ValueConstant('')
    ENDPOINT_EDIT = ValueConstant('')
    ENDPOINT_DELETE = ValueConstant('')

    SUBSCRIPTION_CREATE = ValueConstant('')
    SUBSCRIPTION_EDIT = ValueConstant('')
    SUBSCRIPTION_DELETE = ValueConstant('')

    TOPIC_CREATE = ValueConstant('')
    TOPIC_EDIT = ValueConstant('')
    TOPIC_DELETE = ValueConstant('')

    SUB_KEY_SERVER_SET = ValueConstant('') # This is shared by WSX and other endpoint types
    WSX_CLIENT_SUB_KEY_SERVER_REMOVE = ValueConstant('')

    DELIVERY_SERVER_CHANGE = ValueConstant('')

class SMS(Constants):
    code_start = 106000

    TWILIO_CREATE = ValueConstant('')
    TWILIO_EDIT = ValueConstant('')
    TWILIO_DELETE = ValueConstant('')

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

class SERVER_STATUS(Constants):
    code_start = 106800

    STATUS_CHANGED = ValueConstant('')

class GENERIC(Constants):
    code_start = 107000

    CONNECTION_CREATE = ValueConstant('')
    CONNECTION_EDIT = ValueConstant('')
    CONNECTION_DELETE = ValueConstant('')
    CONNECTION_CHANGE_PASSWORD = ValueConstant('')

class SSO(Constants):
    code_start = 107200

    USER_CREATE      = ValueConstant('')
    USER_EDIT        = ValueConstant('')

    LINK_AUTH_CREATE = ValueConstant('')
    LINK_AUTH_DELETE = ValueConstant('')

class EVENT(Constants):
    code_start = 107400

    PUSH = ValueConstant('')

code_to_name = {}

# To prevent 'RuntimeError: dictionary changed size during iteration'
item_name, item = None, None
_globals = list(iteritems(globals()))

for item_name, item in _globals:
    if isclass(item) and issubclass(item, Constants) and item is not Constants:
        for idx, (attr, const) in enumerate(item.items()):
            const.value = str(item.code_start + idx)
            code_to_name[const.value] = '{}_{}'.format(item_name, attr)
