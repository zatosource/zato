# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re

# pytest
import pytest

# Zato
from zato.common.test.b2b_interoperability import FixtureDirectory

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The directory of the fixtures, which the parametrized tests list when they are collected.
_tests_dir = os.path.dirname(__file__)
_messages_dir = os.path.join(_tests_dir, '..', 'fixtures', 'messages')
_fixture_directory = FixtureDirectory(_messages_dir)
_fixture_name_list = _fixture_directory.names()

# The namespaces a fixture may declare - the ones of the specifications, including the misspelled and the slashless forms
# that senders use, and the ones of the tests.
_allowed_namespaces = {
    'http://schemas.xmlsoap.org/soap/envelope/',
    'http://schemas.xmlsoap.org/soap/envelope',
    'http://schemas.xmlsoap.org/soap/encoding/',
    'http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd',
    'http://www.w3.org/1999/xlink',
    'http://www.w3.org/2001/XMLSchema-instance',
    'http://www.w3c.org/2001/XML-Schema-Instance',
    'http://www.w3.org/2001/XMLSchema',
    'http://www.w3.org/2000/09/xmldsig#',
    'http://www.w3.org/XML/1998/namespace',
}

# The prefix of every namespace and URN that the tests define.
_test_urn_prefix = 'urn:zato:b2b:test'

# The prefix of the URNs of ebMS 2.0.
_ebms_urn_prefix = 'urn:oasis:names:tc:ebxml-msg:'

# The hosts of the specifications that URLs may name.
_specification_hosts = {
    'schemas.xmlsoap.org',
    'www.oasis-open.org',
    'www.w3.org',
    'www.w3c.org',
}

# The domains reserved for documentation and tests.
_reserved_domain_suffixes = ('.test', '.example.com')
_reserved_domains = {'example.com', '127.0.0.1'}
_documentation_network_prefix = '192.0.2.'

# The length from which a run of base64 characters is taken to be a key, a certificate or a signature value.
_max_base64_run = 64

_namespace_pattern = re.compile(r'xmlns(?::[\w.-]+)?="([^"]*)"')
_url_pattern = re.compile(r'https?://([^/"\s<>#]+)')
_urn_pattern = re.compile(r'urn:[^"\s<>]+')
_ipv4_pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
_domain_pattern = re.compile(r'@([\w.-]+)')
_signature_pattern = re.compile(r'<(?:[\w-]+:)?Signature[\s>]')
_base64_expression = rf'[A-Za-z0-9+/]{{{_max_base64_run},}}'
_base64_pattern = re.compile(_base64_expression)

# ################################################################################################################################
# ################################################################################################################################

def _fixture_text(name:'str') -> 'str':
    data = _fixture_directory.load(name)

    out = data.decode('utf-8')
    return out

# ################################################################################################################################

def _is_reserved_host(host:'str') -> 'bool':
    """ Says whether a host is one that is reserved for documentation and tests, or one without a domain at all.
    """
    host = host.lower()

    if host in _reserved_domains:
        out = True
    elif host.endswith(_reserved_domain_suffixes):
        out = True
    elif host.startswith(_documentation_network_prefix):
        out = True
    else:
        out = '.' not in host

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('name', _fixture_name_list)
class TestFixtureContent:
    """ Every fixture names only the specifications and the parties, hosts and identifiers of the tests.
    """

    def test_namespaces(self, name:'str') -> 'None':
        text = _fixture_text(name)

        for namespace in _namespace_pattern.findall(text):
            if namespace not in _allowed_namespaces:
                assert namespace.startswith(_test_urn_prefix), namespace

    def test_url_hosts(self, name:'str') -> 'None':
        text = _fixture_text(name)

        for host in _url_pattern.findall(text):
            if host not in _specification_hosts:
                assert _is_reserved_host(host), host

    def test_urns(self, name:'str') -> 'None':
        text = _fixture_text(name)

        for urn in _urn_pattern.findall(text):
            if not urn.startswith(_ebms_urn_prefix):
                assert urn.startswith(_test_urn_prefix), urn

    def test_addresses(self, name:'str') -> 'None':
        text = _fixture_text(name)

        for address in _ipv4_pattern.findall(text):
            assert _is_reserved_host(address), address

    def test_identifier_domains(self, name:'str') -> 'None':
        text = _fixture_text(name)

        for domain in _domain_pattern.findall(text):
            assert _is_reserved_host(domain), domain

    def test_no_stored_signature(self, name:'str') -> 'None':
        text = _fixture_text(name)

        # Signatures are created at test time with the keys of the tests, so no fixture has one of its own.
        assert _signature_pattern.search(text) is None

    def test_no_key_material(self, name:'str') -> 'None':
        text = _fixture_text(name)

        assert _base64_pattern.search(text) is None

# ################################################################################################################################
# ################################################################################################################################
