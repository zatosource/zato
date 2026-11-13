# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The state shared by the test modules and the assertions and readers they have in common.

# stdlib
import os
import sqlite3
import time

# lxml
import lxml.etree as etree

# Zato
from channel_client import ChannelClient
from channel_definitions import build_yaml

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import HTTPResponse
    from channel_environment import ChannelEnvironment
    from channel_tokens import IdentityProvider
    from zato.common.typing_ import any_, anydict, anylist, callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

_poll_interval = 0.2

# How long a configuration update or an audit log write may take to be visible, in seconds
Propagation_Timeout = 30

# The SOAP envelopes and the content types of SOAP 1.1 and 1.2
SOAP_11_Namespace = 'http://schemas.xmlsoap.org/soap/envelope/'
SOAP_12_Namespace = 'http://www.w3.org/2003/05/soap-envelope'

SOAP_11_Headers = {'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': '"urn:customers:GetCustomer"'}
SOAP_12_Headers = {'Content-Type': 'application/soap+xml; charset=utf-8; action="urn:customers:GetCustomer"'}

_soap_customer = '<customer_id>123</customer_id><name>John Smith</name>'
_soap_body = f'<soap:Body><GetCustomer xmlns="urn:customers">{_soap_customer}</GetCustomer></soap:Body>'

SOAP_11_Envelope = f'<soap:Envelope xmlns:soap="{SOAP_11_Namespace}"><soap:Header/>{_soap_body}</soap:Envelope>'
SOAP_12_Envelope = f'<soap:Envelope xmlns:soap="{SOAP_12_Namespace}"><soap:Header/>{_soap_body}</soap:Envelope>'

# The columns of the audit log events the tests read
_audit_columns = ('cid', 'source', 'event_type', 'object_name', 'ext_client_id', 'status', 'outcome', 'data')

# ################################################################################################################################
# ################################################################################################################################

class Suite:
    """ The server of the suite, the identity provider that signs its tokens and a client of the server.
    """

    def __init__(self, environment:'ChannelEnvironment', provider:'IdentityProvider') -> 'None':
        self.environment = environment
        self.provider = provider
        self.client = ChannelClient(environment.port)

    def import_yaml(self, **options:'any_') -> 'None':
        """ Imports the YAML of the suite with the given options in place of their defaults.
        """
        yaml_text = build_yaml(self.provider, **options)
        self.environment.import_yaml(yaml_text)

    def restore_yaml(self) -> 'None':
        """ Imports the YAML of the suite with every option at its default.
        """
        self.import_yaml()

    @property
    def audit_db_path(self) -> 'str':
        out = os.path.join(self.environment.temp_directory, 'audit.db')
        return out

# ################################################################################################################################
# ################################################################################################################################

def wait_until(condition:'callable_', timeout:'float' = Propagation_Timeout) -> 'any_':
    """ Calls the condition until it returns a true value and returns that value, or raises once the timeout expires.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if out := condition():
            return out
        time.sleep(_poll_interval)

    raise Exception(f'Condition {condition} not met within {timeout}s')

# ################################################################################################################################

def assert_json_error(response:'HTTPResponse', status:'int', details:'any_') -> 'anydict':
    """ Asserts that a response is a JSON error with the given status and details and returns its body.
    """
    assert response.status == status, response.body
    assert response.headers['content-type'] == 'application/json'

    out = response.json()

    assert out['result'] == 'Error'
    assert out['details'] == details
    assert out['cid']

    return out

# ################################################################################################################################

def assert_unauthorized(response:'HTTPResponse', challenge:'str' = '') -> 'None':
    """ Asserts that a request was rejected by the security definition of its channel.
    """
    assert response.status == 401, response.body
    assert response.json()['details'] == '401 Unauthorized'

    if challenge:
        assert response.get_header_values('WWW-Authenticate') == [challenge]
    else:
        assert response.get_header_values('WWW-Authenticate') == []

# ################################################################################################################################

def read_log_lines(path:'str', marker:'str') -> 'strlist':
    """ Returns the lines of a log file that contain the marker.
    """
    out:'strlist' = []

    if not os.path.exists(path):
        return out

    with open(path, encoding='utf-8', errors='replace') as log_file:
        for line in log_file:
            if marker in line:
                out.append(line.rstrip('\n'))

    return out

# ################################################################################################################################

def wait_for_log_lines(path:'str', marker:'str', count:'int' = 1) -> 'strlist':
    """ Waits until a log file holds at least the given number of lines with the marker and returns them.
    """

    def _condition() -> 'strlist':
        lines = read_log_lines(path, marker)
        if len(lines) >= count:
            return lines
        return []

    out = wait_until(_condition)
    return out

# ################################################################################################################################

def read_audit_events(db_path:'str', cid:'str') -> 'anylist':
    """ Returns the audit log events of a request, each as a dict of the columns the tests read.
    """
    out:'anylist' = []

    if not os.path.exists(db_path):
        return out

    column_list = ', '.join(_audit_columns)
    query = f'select {column_list} from event where cid = ? order by id'

    connection = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)

    try:
        rows = connection.execute(query, (cid,)).fetchall()
    finally:
        connection.close()

    for row in rows:
        event = dict(zip(_audit_columns, row))
        out.append(event)

    return out

# ################################################################################################################################

def parse_soap(body:'bytes') -> 'any_':
    """ Returns the root element of a SOAP response.
    """
    out = etree.fromstring(body)
    return out

# ################################################################################################################################

def find_text(root:'any_', path:'str') -> 'str':
    """ Returns the text of the first element under the root whose local name path matches.
    """
    parts = path.split('/')
    expression = ''

    for part in parts:
        expression += f"/*[local-name()='{part}']"

    elements = root.xpath('.' + expression)
    element = elements[0]

    out = element.text
    return out

# ################################################################################################################################
# ################################################################################################################################
