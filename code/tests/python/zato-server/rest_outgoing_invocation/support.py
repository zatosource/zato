# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the outgoing REST invocation tests build their connections with - the stubs of a server
# and of its connections, and the credentials the test endpoint is invoked with.

# stdlib
import os
from base64 import b64encode
from logging import Formatter, getLogger, INFO
from logging.handlers import RotatingFileHandler

# Zato
from zato.common.api import SEC_DEF_TYPE

# Test support
from rest_outgoing_stub.connection import Client_ID as Client_ID, Client_Secret as Client_Secret, new_connection, \
    ServerStub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

# The correlation ID most invocations are made with
Test_CID = 'zrest-test-cid-4f2a9c1e7b3d5a8f'

# The Basic Auth credentials, with a colon in the password
Basic_Username = 'john.smith'
Basic_Password = 'Test:Password.2026'

# The path the token endpoint is served under, relative to each test's own path
Token_Path_Suffix = '/oauth/token'

# The format of a server's log lines, without the context fields its filter adds
_log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'

# The size at which the test log file rotates, large enough for it not to rotate during a run
_log_max_bytes = 1_000_000_000

# ################################################################################################################################
# ################################################################################################################################

def get_basic_authorization(username:'str', password:'str') -> 'str':
    """ Returns the value of the Authorization header of the given Basic Auth credentials.
    """
    credentials = f'{username}:{password}'.encode('utf8')
    encoded = b64encode(credentials).decode('ascii')

    out = f'Basic {encoded}'
    return out

# ################################################################################################################################

def configure_rest_log(path:'str') -> 'None':
    """ Writes the lines of the zato_rest logger to the given file, the way a server writes them.
    """
    handler = RotatingFileHandler(path, mode='a', maxBytes=_log_max_bytes, backupCount=1, encoding='utf8')

    formatter = Formatter(_log_format)
    handler.setFormatter(formatter)

    logger = getLogger('zato_rest')
    logger.setLevel(INFO)
    logger.addHandler(handler)

# ################################################################################################################################

def read_log_lines(path:'str', text:'str') -> 'strlist':
    """ Returns the lines of a log file that contain the given text, oldest first.
    """
    out:'strlist' = []

    if not os.path.exists(path):
        return out

    with open(path, encoding='utf8') as file:
        for line in file:
            if text in line:
                line = line.rstrip('\n')
                out.append(line)

    return out

# ################################################################################################################################
# ################################################################################################################################

def new_basic_auth_connection(server:'ServerStub', address_host:'str', path:'str', **kwargs:'any_') -> 'HTTPSOAPWrapper':
    """ Builds one outgoing REST connection with the Basic Auth credentials of the suite.
    """
    out = new_connection(
        server,
        address_host,
        path,
        sec_type=SEC_DEF_TYPE.BASIC_AUTH,
        username=Basic_Username,
        password=Basic_Password,
        **kwargs,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################
