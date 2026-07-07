# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import NS, SOAPSecurityException
from zato.common.soap.envelope import get_security_header
from zato.common.util.xml_.core import qname, to_timestamp

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone
    any_ = any_
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# How long an assertion stays valid.
Assertion_TTL_Seconds = 300

# The subject confirmation method of assertions vouched for by the sender.
Confirmation_Sender_Vouches = 'urn:oasis:names:tc:SAML:2.0:cm:sender-vouches'

# The format of NameID values that are plain strings.
NameID_Unspecified = 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified'

_saml_nsmap = {
    'saml2': NS.SAML2,
}

# ################################################################################################################################
# ################################################################################################################################

def new_assertion(
    issuer:'str',
    subject:'str',
    audience:'strnone'=None,
    ttl_seconds:'int'=Assertion_TTL_Seconds,
    ) -> 'any_':
    """ Returns a new unsigned saml2:Assertion with a sender-vouches subject confirmation -
    the shape health exchanges and government gateways expect from a service provider.
    """
    now = datetime.now(timezone.utc)
    not_on_or_after = now + timedelta(seconds=ttl_seconds)

    assertion = etree.Element(qname(NS.SAML2, 'Assertion'), nsmap=_saml_nsmap)
    assertion.set('ID', f'_{uuid4().hex}')
    assertion.set('Version', '2.0')
    assertion.set('IssueInstant', to_timestamp(now))

    issuer_element = etree.SubElement(assertion, qname(NS.SAML2, 'Issuer'))
    issuer_element.text = issuer

    subject_element = etree.SubElement(assertion, qname(NS.SAML2, 'Subject'))

    name_id = etree.SubElement(subject_element, qname(NS.SAML2, 'NameID'))
    name_id.set('Format', NameID_Unspecified)
    name_id.text = subject

    confirmation = etree.SubElement(subject_element, qname(NS.SAML2, 'SubjectConfirmation'))
    confirmation.set('Method', Confirmation_Sender_Vouches)

    conditions = etree.SubElement(assertion, qname(NS.SAML2, 'Conditions'))
    conditions.set('NotBefore', to_timestamp(now))
    conditions.set('NotOnOrAfter', to_timestamp(not_on_or_after))

    if audience:
        audience_restriction = etree.SubElement(conditions, qname(NS.SAML2, 'AudienceRestriction'))
        audience_element = etree.SubElement(audience_restriction, qname(NS.SAML2, 'Audience'))
        audience_element.text = audience

    return assertion

# ################################################################################################################################

def add_attribute(assertion:'any_', name:'str', value:'str') -> 'None':
    """ Adds one attribute to an assertion's AttributeStatement, creating the statement
    on first use - this is how role and organization details travel with the assertion.
    """
    statement = assertion.find(qname(NS.SAML2, 'AttributeStatement'))

    if statement is None:
        statement = etree.SubElement(assertion, qname(NS.SAML2, 'AttributeStatement'))

    attribute = etree.SubElement(statement, qname(NS.SAML2, 'Attribute'))
    attribute.set('Name', name)

    attribute_value = etree.SubElement(attribute, qname(NS.SAML2, 'AttributeValue'))
    attribute_value.text = value

# ################################################################################################################################

def add_assertion(envelope:'any_', assertion:'any_') -> 'None':
    """ Places a saml2:Assertion in the security header of an envelope. The assertion
    may also be raw bytes, e.g. one issued and signed by an external identity provider.
    """
    if isinstance(assertion, bytes):
        assertion = etree.fromstring(assertion)

    security = get_security_header(envelope)
    security.append(assertion)

# ################################################################################################################################

def get_assertion(envelope:'any_') -> 'any_':
    """ Returns the saml2:Assertion of an incoming message.
    """
    security = get_security_header(envelope)
    assertion = security.find(qname(NS.SAML2, 'Assertion'))

    if assertion is None:
        raise SOAPSecurityException('Message has no SAML assertion')

    return assertion

# ################################################################################################################################
# ################################################################################################################################
