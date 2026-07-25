# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding

# lxml
from lxml import etree

# Zato
from zato.common.util.xml_.constants import NS, TokenType, WSU_ID
from zato.common.util.xml_.core import new_id, parse_xml, qname, XMLSecurityException
from zato.common.util.xml_.keystore import certificate_list
from zato.common.util.xml_.token import build_pkipath, parse_pkipath, parse_x509v3
from zato.common.util.xml_.xmlsec import decode_base64, encode_base64, find_by_wsu_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    Keystore = Keystore

# ################################################################################################################################
# ################################################################################################################################

def add_binary_security_token(security:'any_', keystore:'Keystore', token_type:'str') -> 'str':
    """ Adds the BinarySecurityToken carrying our signing certificate (or the whole chain
    for PKIPath) and returns its wsu:Id for the signature to reference.
    """
    token_id = new_id('X509-')

    # A PKIPath token carries the entire chain, the X509v3 one just the leaf certificate.
    if token_type == TokenType.PKIPath:
        token_bytes = build_pkipath(keystore.signing_certificate_chain)
    else:
        token_bytes = keystore.signing_certificate.public_bytes(Encoding.DER)

    token = etree.SubElement(security, qname(NS.WSSE, 'BinarySecurityToken'))
    token.set('EncodingType', TokenType.Base64Binary)
    token.set('ValueType', token_type)
    token.set(WSU_ID, token_id)
    token.text = encode_base64(token_bytes)

    out = token_id
    return out

# ################################################################################################################################

# ################################################################################################################################

def add_key_info_token_reference(signature:'any_', token_id:'str', token_type:'str') -> 'None':
    """ Appends the ds:KeyInfo that points a signature back at its BinarySecurityToken,
    so verifiers know which certificate signed the message.
    """
    key_info = etree.SubElement(signature, qname(NS.DS, 'KeyInfo'))
    token_reference = etree.SubElement(key_info, qname(NS.WSSE, 'SecurityTokenReference'))
    reference = etree.SubElement(token_reference, qname(NS.WSSE, 'Reference'))
    reference.set('URI', f'#{token_id}')
    reference.set('ValueType', token_type)

# ################################################################################################################################

def add_saml_token(security:'any_', assertion:'any_') -> 'str':
    """ Places a SAML 2.0 assertion in the security header as the message's token,
    per the SAML Token Profile 1.1 - security token services such as the Australian
    SBR's VANguard issue these instead of certificates travelling as binary tokens.
    Accepts the assertion as bytes or as an element and returns its ID for the
    signature's key identifier to point at.
    """
    if assertion is None:
        raise XMLSecurityException('No SAML assertion to add as a token')

    if isinstance(assertion, bytes):
        assertion = parse_xml(assertion)

    assertion_id = assertion.get('ID')

    if not assertion_id:
        raise XMLSecurityException('SAML assertion has no ID')

    security.append(assertion)

    out = assertion_id
    return out

# ################################################################################################################################

def add_key_info_saml_reference(signature:'any_', assertion_id:'str') -> 'None':
    """ Appends the ds:KeyInfo that points a signature at a SAML assertion -
    a SecurityTokenReference whose KeyIdentifier carries the assertion's ID,
    per the SAML Token Profile 1.1.
    """
    key_info = etree.SubElement(signature, qname(NS.DS, 'KeyInfo'))

    token_reference = etree.SubElement(key_info, qname(NS.WSSE, 'SecurityTokenReference'))
    token_reference.set(qname(NS.WSSE11, 'TokenType'), TokenType.SAML20)

    key_identifier = etree.SubElement(token_reference, qname(NS.WSSE, 'KeyIdentifier'))
    key_identifier.set('ValueType', TokenType.SAML_ID)
    key_identifier.text = assertion_id

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################

def extract_signer_chain(signature:'any_', security:'any_') -> 'certificate_list':
    """ Resolves the signature's key info to the signer's certificate chain, leaf first -
    either out of the referenced BinarySecurityToken or, for signatures keyed by
    a SAML assertion, out of the assertion's holder-of-key confirmation.
    """
    key_info = signature.find(qname(NS.DS, 'KeyInfo'))
    token_reference = key_info.find(qname(NS.WSSE, 'SecurityTokenReference'))

    if token_reference is None:
        raise XMLSecurityException('Signature has no SecurityTokenReference')

    reference = token_reference.find(qname(NS.WSSE, 'Reference'))

    if reference is None:

        # With no direct reference, the token may be a SAML assertion named by its ID.
        key_identifier = token_reference.find(qname(NS.WSSE, 'KeyIdentifier'))

        if key_identifier is not None and key_identifier.get('ValueType') == TokenType.SAML_ID:
            out = _extract_saml_signer_chain(security, key_identifier.text or '')
            return out

        raise XMLSecurityException('SecurityTokenReference has no Reference')

    token_id = (reference.get('URI') or '')[1:]
    token = find_by_wsu_id(security, token_id)

    if token is None:
        raise XMLSecurityException(f'BinarySecurityToken `{token_id}` is missing')

    token_bytes = decode_base64(token.text or '')
    value_type = token.get('ValueType')

    # A PKIPath token carries the whole chain, an X509v3 one just the leaf.
    if value_type == TokenType.PKIPath:
        out = parse_pkipath(token_bytes)
    else:
        leaf = parse_x509v3(token_bytes)
        out = [leaf]

    return out

# ################################################################################################################################

def _extract_saml_signer_chain(security:'any_', assertion_id:'str') -> 'certificate_list':
    """ Returns the signer's certificate out of a SAML assertion's holder-of-key
    subject confirmation - the assertion vouches that whoever holds the matching
    private key is the subject, so that certificate is what verifies the signature.
    """
    assertion = None

    for candidate in security.findall(qname(NS.SAML2, 'Assertion')):
        if candidate.get('ID') == assertion_id:
            assertion = candidate
            break

    if assertion is None:
        raise XMLSecurityException(f'SAML assertion `{assertion_id}` is missing')

    confirmation = assertion.find(f'.//{qname(NS.SAML2, "SubjectConfirmation")}')

    certificate_element = None
    if confirmation is not None:
        certificate_element = confirmation.find(f'.//{qname(NS.DS, "X509Certificate")}')

    if certificate_element is None:
        raise XMLSecurityException(f'SAML assertion `{assertion_id}` carries no signer certificate')

    leaf = parse_x509v3(decode_base64(certificate_element.text or ''))

    out = [leaf]
    return out

# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
