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
from string import Template

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
wsse_password_type_digest = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest"

supported_wsse_password_types = (wsse_password_type_text, wsse_password_type_digest)

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

zato_data_path = "/soapenv:Envelope/soapenv:Body/zato:zato_message/zato:data"
zato_data_xpath = etree.XPath(zato_data_path, namespaces={"soapenv":soapenv_namespace, "zato":zato_namespace})

zato_result_path = "/soapenv:Envelope/soapenv:Body/zato:zato_message/zato:zato_env/zato:result"
zato_result_path_xpath = etree.XPath(zato_result_path, namespaces={"soapenv":soapenv_namespace, "zato":zato_namespace})

scheduler_date_time_format = "%Y-%m-%d %H:%M:%S"

soap_date_time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

# All IPC & AMQP config messages must start with this prefixes.
ZATO_CONFIG_REQUEST = "ZATO_CONFIG_REQUEST\n"
ZATO_CONFIG_RESPONSE = "ZATO_CONFIG_RESPONSE\n"

# A convenient constant used in several places, simplifies passing around
# arguments which are, well, not given (as opposed to being None, an empty string etc.)
ZATO_NOT_GIVEN = b"ZATO_NOT_GIVEN"

# Also used in a couple of places.
ZATO_OK = "ZATO_OK"
ZATO_ERROR = "ZATO_ERROR"
ZATO_WARNING = "ZATO_WARNING"

# Used when there's a need for encrypting/decrypting a well-known data.
ZATO_CRYPTO_WELL_KNOWN_DATA = 'ZATO'

# Status of a server's join request
ZATO_JOIN_REQUEST_ACCEPTED = 'ACCEPTED'

# All URL types Zato understands.
ZATO_URL_TYPE_SOAP = 'soap'
ZATO_URL_TYPE_PLAIN_HTTP = 'plain_http'

# Whether WS-Security passwords are transmitted in clear-text or not.
ZATO_WSS_PASSWORD_CLEAR_TEXT = Bunch(name='clear-text', label='Clear text')
ZATO_WSS_PASSWORD_DIGEST = Bunch(name='digest', label='Digest')
ZATO_WSS_PASSWORD_TYPES = {
    ZATO_WSS_PASSWORD_CLEAR_TEXT.name:ZATO_WSS_PASSWORD_CLEAR_TEXT.label,
    ZATO_WSS_PASSWORD_DIGEST.name:ZATO_WSS_PASSWORD_DIGEST.label
}

ZATO_FIELD_OPERATORS = {
    'is-equal-to': '==',
    'is-not-equal-to': '!=',
    }

# How much various ZeroMQ ports are shifted with regards to the base port
# configured for the cluster. The name of a port contains information who talks
# with whom and over what ports.
PORTS = Bunch()
PORTS.BROKER_PUSH_WORKER_THREAD_PULL = 0
PORTS.BROKER_WORKER_THREAD_PUSH_BROKER_PULL = 1
PORTS.BROKER_PUB_WORKER_THREAD_SUB = 2
PORTS.BROKER_SINGLETON_PUSH = 10
PORTS.BROKER_SINGLETON_PULL = 11

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
                raise
            else:
                return None
        else:
            return value

class zato_path(path):
    def __init__(self, path, raise_on_not_found=False, text_only=False):
        super(zato_path, self).__init__("zato_message." + path, raise_on_not_found,
                                        zato_namespace, text_only)

class ZatoException(Exception):
    """ Base class for all Zato custom exceptions.
    """
    
class ClientSecurityException(ZatoException):
    """ An exception for signalling errors stemming from security problems
    on the client side, such as invalid username or password.
    """
    
class ConnectionException(ZatoException):
    """ Encountered a problem with an external connections, such as to AMQP brokers.
    """