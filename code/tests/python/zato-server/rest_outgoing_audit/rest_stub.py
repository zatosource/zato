# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What an outgoing REST call reaches for when it is exercised offline - a wrapper whose
# invoke_http never touches the network, a response standing in for what requests returns
# and the environment that points the audit log at a throwaway database.

# stdlib
from contextlib import contextmanager
from http.client import BAD_REQUEST

# Zato
from zato.common.api import URL_TYPE
from zato.common.soap.common import SOAPVersion
from zato.common.test.zato_database import zato_database_engine
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
Server_Name = 'test-rest-audit-server'

# The name the connection under test goes by
Connection_Name = 'test.rest.audit'

# Where the connection points - never actually reached
Address_Host = 'https://example.invalid'
Address_Path = '/api'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def rest_audit_env() -> 'envgen':
    """ Points the audit log at a throwaway PostgreSQL database for the duration of a test.
    """
    with zato_database_engine():
        yield

# ################################################################################################################################
# ################################################################################################################################

class ResponseStub:
    """ Stands in for what requests returns - the status, its reason phrase and the body,
    with ok derived the way requests derives it.
    """

    def __init__(self, status_code:'int', reason:'str', text:'str') -> 'None':
        self.status_code = status_code
        self.reason = reason
        self.text = text
        self.ok = status_code < BAD_REQUEST
        self.headers = {}

# ################################################################################################################################
# ################################################################################################################################

class _ServerStub:
    """ Stands in for the server a wrapper writes its audit events under - the name
    is all the wrapper reads off it.
    """

    def __init__(self) -> 'None':
        self.name = Server_Name

# ################################################################################################################################
# ################################################################################################################################

def _new_wrapper(transport:'str', is_audit_log_active:'bool', url_path:'str'=Address_Path) -> 'HTTPSOAPWrapper':
    """ Builds one connection under test - real except for invoke_http, which the tests
    replace so that nothing ever goes on the wire.
    """
    config = {
        'id': 1,
        'name': Connection_Name,
        'is_internal': False,
        'use_queue': False,
        'is_active': True,
        'is_audit_log_active': is_audit_log_active,
        'timeout': 10,
        'pool_size': '',
        'sec_type': '',
        'transport': transport,
        'address_host': Address_Host,
        'address_url_path': url_path,
        'content_type': '',
        'data_format': '',
        'password': '',
        'ping_method': '',
        'soap_version': SOAPVersion.V11,
        'soap_action': '',
    }

    server = _ServerStub()

    out = HTTPSOAPWrapper(server, config)

    return out

# ################################################################################################################################

def new_rest_wrapper(*, is_audit_log_active:'bool'=True, url_path:'str'=Address_Path) -> 'HTTPSOAPWrapper':
    """ The REST connection under test, pointing at the given path.
    """
    out = _new_wrapper(URL_TYPE.PLAIN_HTTP, is_audit_log_active, url_path)
    return out

# ################################################################################################################################

def new_soap_wrapper(*, is_audit_log_active:'bool'=True) -> 'HTTPSOAPWrapper':
    """ The SOAP connection under test - the same wrapper, differing only in the transport
    its events are recorded under.
    """
    out = _new_wrapper(URL_TYPE.SOAP, is_audit_log_active)
    return out

# ################################################################################################################################
# ################################################################################################################################
