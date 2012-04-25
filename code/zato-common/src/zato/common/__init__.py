# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from httplib import responses
from string import Template
from traceback import format_exc

# lxml
from lxml import etree
from lxml import objectify
from lxml.objectify import ObjectPath as _ObjectPath

# Bunch
from bunch import Bunch

# The namespace for use in all Zato's own services.
zato_namespace = "http://gefira.pl/zato" # TODO: Change it to a target URL when we finally have it
zato_ns_map = {None: zato_namespace}

# Convenience access functions and constants.

lxml_py_namespace = "http://codespeak.net/lxml/objectify/pytype"

soapenv_namespace = "http://schemas.xmlsoap.org/soap/envelope/"
soap_doc = Template("""<soap:Envelope xmlns:soap="%s"><soap:Body>$body</soap:Body></soap:Envelope>""" % soapenv_namespace)

soap_body_path = "/soapenv:Envelope/soapenv:Body"
soap_body_xpath = etree.XPath(soap_body_path, namespaces={"soapenv":soapenv_namespace})

soap_fault_path = "/soapenv:Envelope/soapenv:Body/soapenv:Fault"
soap_fault_xpath = etree.XPath(soap_fault_path, namespaces={"soapenv":soapenv_namespace})

wsse_namespace = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
wsu_namespace = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd"

wss_namespaces = {"soapenv":soapenv_namespace, "wsse":wsse_namespace, "wsu":wsu_namespace}

wsse_password_type_text = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText"

supported_wsse_password_types = (wsse_password_type_text, )

wsse_username_path = "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Username"
wsse_username_xpath = etree.XPath(wsse_username_path, namespaces=wss_namespaces)

wsse_password_path = "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password"
wsse_password_xpath = etree.XPath(wsse_password_path, namespaces=wss_namespaces)

wsse_password_type_path = "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password/@Type"
wsse_password_type_xpath = etree.XPath(wsse_password_type_path, namespaces=wss_namespaces)

wsse_nonce_path = "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Nonce"
wsse_nonce_xpath = etree.XPath(wsse_nonce_path, namespaces=wss_namespaces)

wsu_username_created_path = "/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsu:Created"
wsu_username_created_xpath = etree.XPath(wsu_username_created_path, namespaces=wss_namespaces)

wsu_expires_path = "/soapenv:Envelope/soapenv:Header/wsse:Security/wsu:Timestamp/wsu:Expires"
wsu_expires_xpath = etree.XPath(wsu_expires_path, namespaces=wss_namespaces)

wsse_username_objectify = "{%s}Security" % wsse_namespace
wsse_username_token_objectify = "{%s}UsernameToken" % wsse_namespace

zato_data_path = "/soapenv:Envelope/soapenv:Body/zato:zato_message/zato:response"
zato_data_xpath = etree.XPath(zato_data_path, namespaces={"soapenv":soapenv_namespace, "zato":zato_namespace})

zato_result_path = "/soapenv:Envelope/soapenv:Body/zato:zato_message/zato:zato_env/zato:result"
zato_result_path_xpath = etree.XPath(zato_result_path, namespaces={"soapenv":soapenv_namespace, "zato":zato_namespace})

scheduler_date_time_format = "%Y-%m-%d %H:%M:%S"

soap_date_time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

# Classes that have this attribute defined (no matter the value) will not be deployed
# onto servers.
DONT_DEPLOY_ATTR_NAME = 'zato_dont_import'

# A convenient constant used in several places, simplifies passing around
# arguments which are, well, not given (as opposed to being None, an empty string etc.)
ZATO_NOT_GIVEN = b"ZATO_NOT_GIVEN"

# Also used in a couple of places.
ZATO_OK = "ZATO_OK"
ZATO_ERROR = "ZATO_ERROR"
ZATO_WARNING = "ZATO_WARNING"
ZATO_NONE = b"ZATO_NONE"

# Used when there's a need for encrypting/decrypting a well-known data.
ZATO_CRYPTO_WELL_KNOWN_DATA = 'ZATO'

# Status of a server's join request
ZATO_JOIN_REQUEST_ACCEPTED = 'ACCEPTED'

# All URL types Zato understands.
url_type = Bunch()
url_type.soap = 'soap'
url_type.plain_http = 'plain_http'

# Whether WS-Security passwords are transmitted in clear-text or not.
ZATO_WSS_PASSWORD_CLEAR_TEXT = Bunch(name='clear_text', label='Clear text')
ZATO_WSS_PASSWORD_TYPES = {
    ZATO_WSS_PASSWORD_CLEAR_TEXT.name:ZATO_WSS_PASSWORD_CLEAR_TEXT.label,
}

ZATO_FIELD_OPERATORS = {
    'is-equal-to': '==',
    'is-not-equal-to': '!=',
    }

ZMQ_OUTGOING_TYPES = ('PUSH',)
ZMQ_CHANNEL_TYPES = ('PULL', 'SUB')

ZATO_ODB_POOL_NAME = 'ZATO_ODB'

SOAP_VERSIONS = ('1.1', '1.2')

SECURITY_TYPES = {'basic_auth':'HTTP Basic Auth', 'tech_acc':'Tech account', 'wss':'WS-Security'}

class SIMPLE_IO:
    class FORMAT:
        XML = 'xml'
        JSON = 'json'
        
class DEPLOYMENT_STATUS:
    DEPLOYED = 'deployed'

# How much various ZeroMQ ports are shifted with regards to the base port
# configured for the cluster. The name of a port contains information who talks
# with whom and over what ports.
PORTS = Bunch()
PORTS.BROKER_PUSH_WORKER_THREAD_PULL = 0
PORTS.WORKER_THREAD_PUSH_BROKER_PULL = 1
PORTS.BROKER_PUB_WORKER_THREAD_SUB = 2

PORTS.BROKER_PUSH_SINGLETON_PULL = 10
PORTS.SINGLETON_PUSH_BROKER_PULL = 11

PORTS.BROKER_PUSH_PUBLISHING_CONNECTOR_AMQP_PULL = 20
PORTS.PUBLISHING_CONNECTOR_AMQP_PUSH_BROKER_PULL = 21
PORTS.BROKER_PUB_PUBLISHING_CONNECTOR_AMQP_SUB = 22

PORTS.BROKER_PUSH_CONSUMING_CONNECTOR_AMQP_PULL = 30
PORTS.CONSUMING_CONNECTOR_AMQP_PUSH_BROKER_PULL = 31
PORTS.BROKER_PUB_CONSUMING_CONNECTOR_AMQP_SUB = 32

PORTS.BROKER_PUSH_PUBLISHING_CONNECTOR_JMS_WMQ_PULL = 40
PORTS.PUBLISHING_CONNECTOR_JMS_WMQ_PUSH_BROKER_PULL = 41
PORTS.BROKER_PUB_PUBLISHING_CONNECTOR_JMS_WMQ_SUB = 42

PORTS.BROKER_PUSH_CONSUMING_CONNECTOR_JMS_WMQ_PULL = 50
PORTS.CONSUMING_CONNECTOR_JMS_WMQ_PUSH_BROKER_PULL = 51
PORTS.BROKER_PUB_CONSUMING_CONNECTOR_JMS_WMQ_SUB = 52

PORTS.BROKER_PUSH_PUBLISHING_CONNECTOR_ZMQ_PULL = 60
PORTS.PUBLISHING_CONNECTOR_ZMQ_PUSH_BROKER_PULL = 61
PORTS.BROKER_PUB_PUBLISHING_CONNECTOR_ZMQ_SUB = 62

PORTS.BROKER_PUSH_CONSUMING_CONNECTOR_ZMQ_PULL = 70
PORTS.CONSUMING_CONNECTOR_ZMQ_PUSH_BROKER_PULL = 71
PORTS.BROKER_PUB_CONSUMING_CONNECTOR_ZMQ_SUB = 72


class path(object):
    def __init__(self, path, raise_on_not_found=False, ns="", text_only=False):
        self.path = path
        self.ns = ns
        self.raise_on_not_found = raise_on_not_found
        self.text_only = text_only

    def get_from(self, elem):
        _path = "{%s}%s" % (self.ns, self.path)
        try:
            value = _ObjectPath(_path)(elem)
            if self.text_only:
                return value.text
            return value
        except(ValueError, AttributeError), e:
            if self.raise_on_not_found:
                raise ParsingException(None, format_exc(e))
            else:
                return None

class zato_path(path):
    def __init__(self, path, raise_on_not_found=False, text_only=False):
        super(zato_path, self).__init__("zato_message." + path, raise_on_not_found,
                                        zato_namespace, text_only)

class ZatoException(Exception):
    """ Base class for all Zato custom exceptions.
    """
    def __init__(self, cid=None, msg=None):
        super(ZatoException, self).__init__(msg)
        self.cid = cid
        self.msg = msg

class ClientSecurityException(ZatoException):
    """ An exception for signalling errors stemming from security problems
    on the client side, such as invalid username or password.
    """

class ConnectionException(ZatoException):
    """ Encountered a problem with an external connections, such as to AMQP brokers.
    """
    
class HTTPException(ZatoException):
    """ Raised when the underlying error condition can be easily expressed
    as one of the HTTP status codes.
    """
    def __init__(self, cid, msg, status):
        super(HTTPException, self).__init__(cid, msg)
        self.status = status
        self.reason = responses[status]
        
class ParsingException(ZatoException):
    """ Raised when the error is to do with parsing of documents, such as an input
    XML document.
    """
    
class SourceInfo(object):
    """ A bunch of attributes dealing the service's source code.
    """
    def __init__(self):
        self.source = None
        self.source_html = None
        self.path = None
        self.hash = None
        self.hash_method = None
        self.server_name = None
