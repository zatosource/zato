# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from string import Template
from traceback import format_exc

# lxml
from lxml import etree
from lxml.objectify import ObjectPath as _ObjectPath

# Zato
from zato.common.exception import ParsingException

# ################################################################################################################################
# ################################################################################################################################

# XML namespace for use in all Zato's own services.
zato_namespace = 'https://zato.io/ns/v1'
zato_ns_map = {None: zato_namespace}

soapenv11_namespace = 'http://schemas.xmlsoap.org/soap/envelope/'
soapenv12_namespace = 'http://www.w3.org/2003/05/soap-envelope'

wsse_namespace = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
wsu_namespace = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'

common_namespaces = {
    'soapenv':soapenv11_namespace,
    'wsse':wsse_namespace,
    'wsu':wsu_namespace,
    'zato':zato_namespace
}

soap_doc = Template("""<soap:Envelope xmlns:soap='%s'><soap:Body>$body</soap:Body></soap:Envelope>""" % soapenv11_namespace)

soap_body_path = '/soapenv:Envelope/soapenv:Body'
soap_body_xpath = etree.XPath(soap_body_path, namespaces=common_namespaces)

soap_fault_path = '/soapenv:Envelope/soapenv:Body/soapenv:Fault'
soap_fault_xpath = etree.XPath(soap_fault_path, namespaces=common_namespaces)

wsse_password_type_text = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'
supported_wsse_password_types = (wsse_password_type_text,)

wsse_username_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Username'
wsse_username_xpath = etree.XPath(wsse_username_path, namespaces=common_namespaces)

wsse_password_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password'
wsse_password_xpath = etree.XPath(wsse_password_path, namespaces=common_namespaces)

wsse_password_type_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Password/@Type'
wsse_password_type_xpath = etree.XPath(wsse_password_type_path, namespaces=common_namespaces)

wsse_nonce_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsse:Nonce'
wsse_nonce_xpath = etree.XPath(wsse_nonce_path, namespaces=common_namespaces)

wsu_username_created_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsse:UsernameToken/wsu:Created'
wsu_username_created_xpath = etree.XPath(wsu_username_created_path, namespaces=common_namespaces)

wsu_expires_path = '/soapenv:Envelope/soapenv:Header/wsse:Security/wsu:Timestamp/wsu:Expires'
wsu_expires_xpath = etree.XPath(wsu_expires_path, namespaces=common_namespaces)

wsse_username_objectify = '{}Security'.format(wsse_namespace)
wsse_username_token_objectify = '{}UsernameToken'.format(wsse_namespace)

zato_data_path = soap_data_path = '/soapenv:Envelope/soapenv:Body/*[1]'
zato_data_xpath = soap_data_xpath = etree.XPath(zato_data_path, namespaces=common_namespaces)

zato_result_path = '//zato:zato_env/zato:result'
zato_result_xpath = etree.XPath(zato_result_path, namespaces=common_namespaces)

zato_cid_path = '//zato:zato_env/zato:cid'
zato_cid_xpath = etree.XPath(zato_result_path, namespaces=common_namespaces)

zato_details_path = '//zato:zato_env/zato:details'
zato_details_xpath = etree.XPath(zato_details_path, namespaces=common_namespaces)

# ################################################################################################################################
# ################################################################################################################################

class path(object):
    def __init__(self, path, raise_on_not_found=False, ns='', text_only=False):
        self.path = path
        self.ns = ns
        self.raise_on_not_found = raise_on_not_found
        self.text_only = text_only
        self.children_only = False
        self.children_only_idx = None

    def get_from(self, elem):
        if self.ns:
            _path = '{{{}}}{}'.format(self.ns, self.path)
        else:
            _path = self.path
        try:
            if self.children_only:
                elem = elem.getchildren()[self.children_only_idx]
            value = _ObjectPath(_path)(elem)
            if self.text_only:
                return value.text
            return value
        except(ValueError, AttributeError):
            if self.raise_on_not_found:
                raise ParsingException(None, format_exc())
            else:
                return None

# ################################################################################################################################
# ################################################################################################################################

class zato_path(path):
    def __init__(self, path, raise_on_not_found=False, text_only=False):
        super(zato_path, self).__init__(path, raise_on_not_found, zato_namespace, text_only)
        self.children_only = True
        self.children_only_idx = 1 # 0 is zato_env

# ################################################################################################################################
# ################################################################################################################################
