# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the SOAP client tests send and secure - a CDC IIS style message and the X.509 configs of both parties,
# shared by the envelope and security tests of test_client and the transport tests of test_client_transport.

# Zato
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.wss import Mode

# Test helpers
from certs import certificate_pem_path, private_key_pem_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_ns_cdc = 'urn:cdc:iisb:2011'

# ################################################################################################################################
# ################################################################################################################################

def sender_x509(parties:'any_', sign:'any_', encrypt:'any_') -> 'stranydict':
    """ The X.509 security config an outgoing connection presents - paths to our key material
    plus the receiver's certificate.
    """
    out = {
        'mode': Mode.X509,
        'sign': sign,
        'encrypt': encrypt,
        'signing_key': private_key_pem_path(parties.sender.signing_key),
        'signing_certificate_chain': certificate_pem_path(parties.sender.signing_certificate),
        'peer_certificate': certificate_pem_path(parties.receiver.signing_certificate),
    }
    return out

# ################################################################################################################################

def receiver_x509(parties:'any_', sign:'any_', encrypt:'any_') -> 'stranydict':
    """ The X.509 config the server enforces - paths to our decryption key plus the sender's pinned certificate.
    """
    out = {
        'mode': Mode.X509,
        'sign': sign,
        'encrypt': encrypt,
        'decryption_key': private_key_pem_path(parties.receiver.decryption_key),
        'peer_certificate': certificate_pem_path(parties.sender.signing_certificate),
    }
    return out

# ################################################################################################################################

def cdc_message() -> 'SOAPMessage':
    """ A CDC IIS style request carrying only business fields - never any credentials.
    """
    out = SOAPMessage()
    out.namespace = _ns_cdc
    out.facilityID = 'FL0001'
    out.hl7Message = 'MSH|^~\\&|MYEHR|FL0001|IIS|FLSHOTS|20260401||VXU^V04|12345|P|2.5.1'
    return out

# ################################################################################################################################
# ################################################################################################################################
