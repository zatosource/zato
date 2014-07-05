# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from inspect import isclass

# Bunch
from bunch import Bunch

# candv
from candv import Constants, ValueConstant

class Constants(_Constants):
    values = _Constants.constants

class MESSAGE:
    MESSAGE_TYPE_LENGTH = 4
    TOKEN_LENGTH = 32
    TOKEN_START = MESSAGE_TYPE_LENGTH
    TOKEN_END = MESSAGE_TYPE_LENGTH + TOKEN_LENGTH
    PAYLOAD_START = MESSAGE_TYPE_LENGTH + TOKEN_LENGTH
    NULL_TOKEN = '0' * TOKEN_LENGTH

class MESSAGE_TYPE:
    TO_SINGLETON = b'0000'
    TO_PARALLEL_ANY = b'0001'
    TO_PARALLEL_ALL = b'0002'

    TO_AMQP_PUBLISHING_CONNECTOR_ALL = b'0003'
    TO_AMQP_CONSUMING_CONNECTOR_ALL = b'0004'
    TO_AMQP_CONNECTOR_ALL = b'0005'
    
    TO_JMS_WMQ_PUBLISHING_CONNECTOR_ALL = b'0006'
    TO_JMS_WMQ_CONSUMING_CONNECTOR_ALL = b'0007'
    TO_JMS_WMQ_CONNECTOR_ALL = b'0008'
    
    TO_ZMQ_PUBLISHING_CONNECTOR_ALL = b'0009'
    TO_ZMQ_CONSUMING_CONNECTOR_ALL = b'0010'
    TO_ZMQ_CONNECTOR_ALL = b'0011'

    USER_DEFINED_START = b'5000'

TOPICS = {
    MESSAGE_TYPE.TO_SINGLETON: b'/zato/to-singleton',

    MESSAGE_TYPE.TO_PARALLEL_ANY: b'/zato/to-parallel/any',
    MESSAGE_TYPE.TO_PARALLEL_ALL: b'/zato/to-parallel/all',

    MESSAGE_TYPE.TO_AMQP_PUBLISHING_CONNECTOR_ALL: b'/zato/connector/amqp/publishing/all',
    MESSAGE_TYPE.TO_AMQP_CONSUMING_CONNECTOR_ALL: b'/zato/connector/amqp/consuming/all',
    MESSAGE_TYPE.TO_AMQP_CONNECTOR_ALL: b'/zato/connector/amqp/all',

    MESSAGE_TYPE.TO_JMS_WMQ_PUBLISHING_CONNECTOR_ALL: b'/zato/connector/jms-wmq/publishing/all',
    MESSAGE_TYPE.TO_JMS_WMQ_CONSUMING_CONNECTOR_ALL: b'/zato/connector/jms-wmq/consuming/all',
    MESSAGE_TYPE.TO_JMS_WMQ_CONNECTOR_ALL: b'/zato/connector/jms-wmq/all',

    MESSAGE_TYPE.TO_ZMQ_PUBLISHING_CONNECTOR_ALL: b'/zato/connector/zmq/publishing/all',
    MESSAGE_TYPE.TO_ZMQ_CONSUMING_CONNECTOR_ALL: b'/zato/connector/zmq/consuming/all',
    MESSAGE_TYPE.TO_ZMQ_CONNECTOR_ALL: b'/zato/connector/zmq/all',
}

KEYS = {k:v.replace('/zato','').replace('/',':') for k,v in TOPICS.items()}

class SCHEDULER(Constants):
    code_start = 100000

    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')
    EXECUTE = ValueConstant('')
    JOB_EXECUTED = ValueConstant('')

class ZMQ_SOCKET(Constants):
    code_start = 100200
    CLOSE = ValueConstant('')

class SECURITY(Constants):
    code_start = 100400

    BASIC_AUTH_CREATE = ValueConstant('')
    BASIC_AUTH_EDIT = ValueConstant('')
    BASIC_AUTH_DELETE = ValueConstant('')
    BASIC_AUTH_CHANGE_PASSWORD = ValueConstant('')

    TECH_ACC_CREATE = ValueConstant('')
    TECH_ACC_EDIT = ValueConstant('')
    TECH_ACC_DELETE = ValueConstant('')
    TECH_ACC_CHANGE_PASSWORD = ValueConstant('')

    WSS_CREATE = ValueConstant('')
    WSS_EDIT = ValueConstant('')
    WSS_DELETE = ValueConstant('')
    WSS_CHANGE_PASSWORD = ValueConstant('')

    # New in 2.0
    OAUTH_CREATE = ValueConstant('')
    OAUTH_EDIT = ValueConstant('')
    OAUTH_DELETE = ValueConstant('')
    OAUTH_CHANGE_PASSWORD = ValueConstant('')

    # New in 2.0
    NTLM_CREATE = ValueConstant('')
    NTLM_EDIT = ValueConstant('')
    NTLM_DELETE = ValueConstant('')
    NTLM_CHANGE_PASSWORD = ValueConstant('')

    # New in 2.0
    AWS_CREATE = ValueConstant('')
    AWS_EDIT = ValueConstant('')
    AWS_DELETE = ValueConstant('')
    AWS_CHANGE_PASSWORD = ValueConstant('')

    # New in 2.0
    OPENSTACK_CREATE = ValueConstant('')
    OPENSTACK_EDIT = ValueConstant('')
    OPENSTACK_DELETE = ValueConstant('')
    OPENSTACK_CHANGE_PASSWORD = ValueConstant('')

    # New in 2.0
    APIKEY_CREATE = ValueConstant('')
    APIKEY_EDIT = ValueConstant('')
    APIKEY_DELETE = ValueConstant('')
    APIKEY_CHANGE_PASSWORD = ValueConstant('')

    # New in 2.0
    XPATH_SEC_CREATE = ValueConstant('')
    XPATH_SEC_EDIT = ValueConstant('')
    XPATH_SEC_DELETE = ValueConstant('')
    XPATH_SEC_CHANGE_PASSWORD = ValueConstant('')

class DEFINITION(Constants):
    code_start = 100600

    AMQP_CREATE = ValueConstant('')
    AMQP_EDIT = ValueConstant('')
    AMQP_DELETE = ValueConstant('')
    AMQP_CHANGE_PASSWORD = ValueConstant('')

    JMS_WMQ_CREATE = ValueConstant('')
    JMS_WMQ_EDIT = ValueConstant('')
    JMS_WMQ_DELETE = ValueConstant('')

    ZMQ_CREATE = ValueConstant('')
    ZMQ_EDIT = ValueConstant('')
    ZMQ_DELETE = ValueConstant('')

    # New in 2.0
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

    JMS_WMQ_CREATE = ValueConstant('')
    JMS_WMQ_EDIT = ValueConstant('')
    JMS_WMQ_DELETE = ValueConstant('')
    JMS_WMQ_SEND = ValueConstant('')

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

class CHANNEL(Constants):
    code_start = 101000

    AMQP_CREATE = ValueConstant('')
    AMQP_EDIT = ValueConstant('')
    AMQP_DELETE = ValueConstant('')
    AMQP_MESSAGE_RECEIVED = ValueConstant('')

    JMS_WMQ_CREATE = ValueConstant('')
    JMS_WMQ_EDIT = ValueConstant('')
    JMS_WMQ_DELETE = ValueConstant('')
    JMS_WMQ_MESSAGE_RECEIVED = ValueConstant('')

    ZMQ_CREATE = ValueConstant('')
    ZMQ_EDIT = ValueConstant('')
    ZMQ_DELETE = ValueConstant('')
    ZMQ_MESSAGE_RECEIVED = ValueConstant('')

    HTTP_SOAP_CREATE_EDIT = ValueConstant('') # Same for creating and updating
    HTTP_SOAP_DELETE = ValueConstant('')
    HTTP_SOAP_AUDIT_RESPONSE = ValueConstant('') # New in 2.0
    HTTP_SOAP_AUDIT_PATTERNS = ValueConstant('') # New in 2.0
    HTTP_SOAP_AUDIT_STATE = ValueConstant('') # New in 2.0
    HTTP_SOAP_AUDIT_CONFIG = ValueConstant('') # New in 2.0

class AMQP_CONNECTOR(Constants):
    code_start = 101200
    CLOSE = ValueConstant('')

class JMS_WMQ_CONNECTOR(Constants):
    code_start = 101400
    CLOSE = ValueConstant('')

class ZMQ_CONNECTOR(Constants):
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
    CREATE = ValueConstant('')

class SINGLETON(Constants):
    code_start = 102400
    CLOSE = ValueConstant('')


class MSG_NS(Constants):
    code_start = 102600

    # New in 2.0
    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class MSG_XPATH(Constants):
    code_start = 102800

    # New in 2.0
    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class MSG_JSON_POINTER(Constants):
    code_start = 103000

    # New in 2.0
    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class PUB_SUB_TOPIC(Constants):
    code_start = 103200

    # New in 2.0
    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')
    ADD_DEFAULT_PRODUCER = ValueConstant('')
    DELETE_DEFAULT_PRODUCER = ValueConstant('')

class PUB_SUB_PRODUCER(Constants):
    code_start = 103400

    # New in 2.0
    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class PUB_SUB_CONSUMER(Constants):
    code_start = 103600

    # New in 2.0
    CREATE = ValueConstant('')
    EDIT = ValueConstant('')
    DELETE = ValueConstant('')

class CLOUD(Constants):
    code_start = 103800

    # New in 2.0
    OPENSTACK_SWIFT_CREATE_EDIT = ValueConstant('')
    OPENSTACK_SWIFT_DELETE = ValueConstant('')

    # New in 2.0
    AWS_S3_CREATE_EDIT = ValueConstant('')
    AWS_S3_DELETE = ValueConstant('')

class NOTIF(Constants):
    code_start = 104000

    # New in 2.0
    RUN_NOTIFIER = b'11900'
    CLOUD_OPENSTACK_SWIFT_CREATE_EDIT = b'11901'
    CLOUD_OPENSTACK_SWIFT_DELETE = b'11902'

class SEARCH(Constants):
    code_start = 104200

    ES_CREATE = b'13001'
    ES_EDIT = b'13002'
    ES_DELETE = b'13003'
    ES_CHANGE_PASSWORD = b'13004'

class QUERY(Constants):
    code_start = 104400

    CASSANDRA_CREATE = b'13150'
    CASSANDRA_EDIT = b'13151'
    CASSANDRA_DELETE = b'13152'
    CASSANDRA_CHANGE_PASSWORD = b'13153'

code_to_name = {}

# To prevent 'RuntimeError: dictionary changed size during iteration'
item_name, item = None, None

for item_name, item in globals().items():
    if isclass(item) and issubclass(item, Constants) and item is not Constants:
        for idx, (attr, const) in enumerate(item.items()):
            const.value = str(item.code_start + idx)
            code_to_name[const.value.encode('utf-8')] = '{}_{}'.format(item_name, attr)
