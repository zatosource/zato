# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# lxml
from lxml import etree

# Zato
from zato.common.as4.common import NS
from zato.common.as4.ebms import Body_Element_ID, Messaging_Element_ID
from zato.common.util.xml_.constants import Algorithm, TokenType
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.mime_ import part_list
from zato.common.util.xml_.wssec import add_attachment_reference, add_binary_security_token, add_element_reference, \
    add_key_info_saml_reference, add_key_info_token_reference, add_saml_token, compute_signature_value
from zato.common.util.xml_.xmlsec import encode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.pmode import SecurityConfig
    from zato.common.typing_ import any_
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_security_nsmap = {
    'wsse':   NS.WSSE,
    'wsse11': NS.WSSE11,
    'wsu':    NS.WSU,
}

_signature_nsmap = {
    'ds': NS.DS,
}

# ################################################################################################################################
# ################################################################################################################################

def get_security_header(envelope:'any_') -> 'any_':
    """ Returns the wsse:Security header of an envelope, creating it if needed.
    """
    header = envelope.find(qname(NS.SOAP, 'Header'))
    security = header.find(qname(NS.WSSE, 'Security'))

    if security is None:
        security = etree.SubElement(header, qname(NS.WSSE, 'Security'), nsmap=_security_nsmap)
        security.set(qname(NS.SOAP, 'mustUnderstand'), 'true')

    return security

# ################################################################################################################################

def sign_envelope(
    envelope:'any_',
    parts:'part_list',
    keystore:'Keystore',
    config:'SecurityConfig',
    ) -> 'any_':
    """ Signs an AS4 envelope in place: covers the eb:Messaging header, the SOAP body
    and every MIME attachment, and appends the resulting ds:Signature with its
    BinarySecurityToken to the wsse:Security header. Returns the ds:Signature element.

    This must run after compression and before encryption - the signature covers
    the compressed plaintext, which is also the order in which receivers reverse it.
    """
    security = get_security_header(envelope)

    # The signing certificate travels either as a binary token or, for exchanges keyed
    # by a security token service, as a SAML assertion confirming the key holder.
    if config.token_type == TokenType.SAML20:
        token_id = add_saml_token(security, keystore.saml_assertion)
    else:
        token_id = add_binary_security_token(security, keystore, config.token_type)

    signature = etree.SubElement(security, qname(NS.DS, 'Signature'), nsmap=_signature_nsmap)
    signature.set('Id', f'SIG-{uuid4().hex}')

    # The signed info lists everything the signature covers ..
    signed_info = etree.SubElement(signature, qname(NS.DS, 'SignedInfo'))

    canonicalization_method = etree.SubElement(signed_info, qname(NS.DS, 'CanonicalizationMethod'))
    canonicalization_method.set('Algorithm', Algorithm.C14N_Exclusive)

    signature_method = etree.SubElement(signed_info, qname(NS.DS, 'SignatureMethod'))
    signature_method.set('Algorithm', config.signature_algorithm)

    # .. the ebMS header and the (empty) SOAP body ..
    add_element_reference(signed_info, envelope, Messaging_Element_ID)
    add_element_reference(signed_info, envelope, Body_Element_ID)

    # .. and each attachment through the SwA content transform.
    for part in parts:
        add_attachment_reference(signed_info, part.content_id, part.data)

    # Now that all the references are in place, the signed info itself can be signed.
    signature_bytes = compute_signature_value(signed_info, keystore, config.signature_algorithm)

    signature_value = etree.SubElement(signature, qname(NS.DS, 'SignatureValue'))
    signature_value.text = encode_base64(signature_bytes)

    # The key info points back at the token so verifiers know which certificate signed this.
    if config.token_type == TokenType.SAML20:
        add_key_info_saml_reference(signature, token_id)
    else:
        add_key_info_token_reference(signature, token_id, config.token_type)

    return signature

# ################################################################################################################################
# ################################################################################################################################
