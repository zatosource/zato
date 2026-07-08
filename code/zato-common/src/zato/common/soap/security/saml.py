# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import NS, SOAPSecurityException
from zato.common.soap.envelope import get_security_header
from zato.common.util.xml_.constants import Algorithm, Transform
from zato.common.util.xml_.core import qname, to_timestamp, XMLSecurityException
from zato.common.util.xml_.token import parse_x509v3
from zato.common.util.xml_.wssec import compute_signature_value, validate_certificate_chain, verify_signature_value
from zato.common.util.xml_.xmlsec import decode_base64, digest_element, encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    Keystore = Keystore
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

_ds_nsmap = {
    'ds': NS.DS,
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

def _assertion_without_signature(assertion:'any_') -> 'any_':
    """ Returns a copy of an assertion with its ds:Signature child removed - the shape
    the enveloped-signature transform digests, both when signing and when verifying.
    """
    out = etree.fromstring(etree.tostring(assertion))

    signature = out.find(qname(NS.DS, 'Signature'))
    if signature is not None:
        out.remove(signature)

    return out

# ################################################################################################################################

def sign_assertion(
    assertion:'any_',
    keystore:'Keystore',
    signature_algorithm:'str'=Algorithm.RSA_SHA256,
    ) -> 'any_':
    """ Signs an assertion in place with an enveloped ds:Signature placed right after
    saml2:Issuer, as SAML Core requires - the profile health exchanges expect for XUA.
    Returns the ds:Signature element.
    """
    assertion_id = assertion.get('ID')

    signature = etree.Element(qname(NS.DS, 'Signature'), nsmap=_ds_nsmap)

    # The signed info lists what the signature covers ..
    signed_info = etree.SubElement(signature, qname(NS.DS, 'SignedInfo'))

    canonicalization_method = etree.SubElement(signed_info, qname(NS.DS, 'CanonicalizationMethod'))
    canonicalization_method.set('Algorithm', Algorithm.C14N_Exclusive)

    signature_method = etree.SubElement(signed_info, qname(NS.DS, 'SignatureMethod'))
    signature_method.set('Algorithm', signature_algorithm)

    # .. which is the assertion itself, referenced by its ID and digested with the signature removed.
    reference = etree.SubElement(signed_info, qname(NS.DS, 'Reference'))
    reference.set('URI', f'#{assertion_id}')

    transforms = etree.SubElement(reference, qname(NS.DS, 'Transforms'))

    enveloped_transform = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    enveloped_transform.set('Algorithm', Transform.Enveloped)

    canonical_transform = etree.SubElement(transforms, qname(NS.DS, 'Transform'))
    canonical_transform.set('Algorithm', Algorithm.C14N_Exclusive)

    digest_method = etree.SubElement(reference, qname(NS.DS, 'DigestMethod'))
    digest_method.set('Algorithm', Algorithm.SHA256)

    # The assertion carries no signature yet, so this is already the enveloped digest.
    digest_value = etree.SubElement(reference, qname(NS.DS, 'DigestValue'))
    digest_value.text = digest_element(assertion)

    # Now that the references are in place, the signed info itself can be signed.
    signature_bytes = compute_signature_value(signed_info, keystore, signature_algorithm)

    signature_value = etree.SubElement(signature, qname(NS.DS, 'SignatureValue'))
    signature_value.text = encode_base64(signature_bytes)

    # The signer's certificate travels inline so verifiers can pin it or chain it to an anchor.
    key_info = etree.SubElement(signature, qname(NS.DS, 'KeyInfo'))
    x509_data = etree.SubElement(key_info, qname(NS.DS, 'X509Data'))
    x509_certificate = etree.SubElement(x509_data, qname(NS.DS, 'X509Certificate'))
    x509_certificate.text = encode_base64(keystore.signing_certificate.public_bytes(Encoding.DER))

    # SAML Core mandates the signature immediately follows the Issuer element.
    issuer = assertion.find(qname(NS.SAML2, 'Issuer'))
    issuer_index = list(assertion).index(issuer)
    assertion.insert(issuer_index + 1, signature)

    return signature

# ################################################################################################################################

def _signer_chain(signature:'any_') -> 'any_':
    """ Returns the certificate chain carried in a signature's ds:KeyInfo, leaf first.
    """
    key_info = signature.find(qname(NS.DS, 'KeyInfo'))

    if key_info is None:
        raise XMLSecurityException('Assertion signature has no KeyInfo')

    x509_certificate = key_info.find(f'.//{qname(NS.DS, "X509Certificate")}')

    if x509_certificate is None:
        raise XMLSecurityException('Assertion signature has no X509Certificate')

    leaf = parse_x509v3(decode_base64(x509_certificate.text or ''))

    out = [leaf]
    return out

# ################################################################################################################################

def verify_assertion(assertion:'any_', keystore:'Keystore') -> 'any_':
    """ Verifies an assertion's enveloped signature - the reference digest, the signature
    value and the trust in the signer. Returns the signer's certificate.
    """
    signature = assertion.find(qname(NS.DS, 'Signature'))

    if signature is None:
        raise SOAPSecurityException('Assertion is not signed')

    try:
        chain = _signer_chain(signature)
        validate_certificate_chain(chain, keystore)

        # The declared digest must match the assertion digested with its signature removed.
        signed_info = signature.find(qname(NS.DS, 'SignedInfo'))
        reference = signed_info.find(qname(NS.DS, 'Reference'))
        digest_value_element = reference.find(qname(NS.DS, 'DigestValue'))
        expected_digest = ''.join((digest_value_element.text or '').split())

        actual_digest = digest_element(_assertion_without_signature(assertion))

        if actual_digest != expected_digest:
            raise XMLSecurityException('Assertion digest mismatch')

        # .. and the signature value itself must be genuine.
        verify_signature_value(signature, chain)

    except XMLSecurityException as e:
        raise SOAPSecurityException(e.args[0])

    out = chain[0]
    return out

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
