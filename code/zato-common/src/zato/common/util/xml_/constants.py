# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class NS:
    """ XML namespaces shared by everything that builds or parses SOAP-family messages.
    """
    SOAP11 = 'http://schemas.xmlsoap.org/soap/envelope/'
    SOAP12 = 'http://www.w3.org/2003/05/soap-envelope'
    WSA    = 'http://www.w3.org/2005/08/addressing'
    WSSE   = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
    WSSE11 = 'http://docs.oasis-open.org/wss/oasis-wss-wssecurity-secext-1.1.xsd'
    WSU    = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'
    DS     = 'http://www.w3.org/2000/09/xmldsig#'
    XMLDSIG11 = 'http://www.w3.org/2009/xmldsig11#'
    XENC   = 'http://www.w3.org/2001/04/xmlenc#'
    XENC11 = 'http://www.w3.org/2009/xmlenc11#'
    XSI    = 'http://www.w3.org/2001/XMLSchema-instance'
    XOP    = 'http://www.w3.org/2004/08/xop/include'
    XMIME  = 'http://www.w3.org/2005/05/xmlmime'
    SAML2  = 'urn:oasis:names:tc:SAML:2.0:assertion'
    XLINK  = 'http://www.w3.org/1999/xlink'

# ################################################################################################################################
# ################################################################################################################################

class Algorithm:
    """ Algorithm identifiers from XML Signature, XML Encryption and their 1.1 revisions.
    """
    C14N_Exclusive  = 'http://www.w3.org/2001/10/xml-exc-c14n#'
    RSA_SHA256      = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
    Ed25519         = 'http://www.w3.org/2021/04/xmldsig-more#eddsa-ed25519'
    SHA256          = 'http://www.w3.org/2001/04/xmlenc#sha256'
    AES128_GCM      = 'http://www.w3.org/2009/xmlenc11#aes128-gcm'
    RSA_OAEP        = 'http://www.w3.org/2009/xmlenc11#rsa-oaep'
    MGF1_SHA256     = 'http://www.w3.org/2009/xmlenc11#mgf1sha256'
    ECDH_ES         = 'http://www.w3.org/2009/xmlenc11#ECDH-ES'
    HKDF            = 'http://www.w3.org/2021/04/xmldsig-more#hkdf'
    HMAC_SHA256     = 'http://www.w3.org/2001/04/xmldsig-more#hmac-sha256'
    AES128_KeyWrap  = 'http://www.w3.org/2001/04/xmlenc#kw-aes128'

# ################################################################################################################################
# ################################################################################################################################

class Transform:
    """ Transform identifiers from XML Signature and the WS-Security SOAP with Attachments profile 1.1.
    """
    Enveloped             = 'http://www.w3.org/2000/09/xmldsig#enveloped-signature'
    Attachment_Content    = 'http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Content-Signature-Transform'
    Attachment_Ciphertext = 'http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Ciphertext-Transform'

# ################################################################################################################################
# ################################################################################################################################

class TokenType:
    """ WS-Security token profile identifiers - the X.509 profile values go into
    the BinarySecurityToken ValueType attribute and the SAML Token Profile 1.1 values
    into the SecurityTokenReference of signatures keyed by a SAML assertion.
    """
    X509v3       = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3'
    PKIPath      = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509PKIPathv1'
    Base64Binary = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary'

    # SAML Token Profile 1.1 - SAML20 names the token type of a SAML 2.0 assertion
    # and SAML_ID says a KeyIdentifier carries the assertion's ID.
    SAML20  = 'http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.1#SAMLV2.0'
    SAML_ID = 'http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.1#SAMLID'

# ################################################################################################################################
# ################################################################################################################################
