# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.xml_.constants import NS as CommonNS

# ################################################################################################################################
# ################################################################################################################################

class NS(CommonNS):
    """ XML namespaces used across AS4 messages - the shared ones plus the ebXML family.
    """
    SOAP    = CommonNS.SOAP12
    EBMS    = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/'
    EBBP    = 'http://docs.oasis-open.org/ebxml-bp/ebbp-signals-2.0'
    SBDH    = 'http://www.unece.org/cefact/namespaces/StandardBusinessDocumentHeader'

# ################################################################################################################################
# ################################################################################################################################

class MEP:
    """ Message exchange pattern identifiers from ebMS 3.0.
    """
    One_Way = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/oneWay'
    Two_Way = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/twoWay'

# ################################################################################################################################
# ################################################################################################################################

class MEPBinding:
    """ Message exchange pattern binding identifiers from ebMS 3.0.
    """
    Push = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/push'
    Pull = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/pull'

# ################################################################################################################################
# ################################################################################################################################

class Default:
    """ Values that ebMS 3.0 and the eDelivery profile define as defaults.
    """
    MPC             = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/defaultMPC'
    Initiator_Role  = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator'
    Responder_Role  = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder'
    Test_Service    = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/service'
    Test_Action     = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/test'
    Party_ID_Type_Unregistered = 'urn:oasis:names:tc:ebcore:partyid-type:unregistered'

    # HTTP timeout for outbound AS4 requests.
    HTTP_Timeout_Seconds = 120

# ################################################################################################################################
# ################################################################################################################################

class CompressionType:
    """ Payload part property values for the AS4 compression feature.
    """
    GZIP = 'application/gzip'

# ################################################################################################################################
# ################################################################################################################################

class EbMSError:
    """ Error codes from ebMS 3.0 Core section 6.7 that this implementation raises or recognizes.
    """
    Value_Not_Recognized      = 'EBMS:0001'
    Feature_Not_Supported     = 'EBMS:0002'
    Value_Inconsistent        = 'EBMS:0003'
    Other                     = 'EBMS:0004'
    Connection_Failure        = 'EBMS:0005'
    Empty_Message_Partition   = 'EBMS:0006'
    Mime_Inconsistency        = 'EBMS:0007'
    Invalid_Header            = 'EBMS:0009'
    Processing_Mode_Mismatch  = 'EBMS:0010'
    Failed_Authentication     = 'EBMS:0101'
    Failed_Decryption         = 'EBMS:0102'
    Policy_Noncompliance      = 'EBMS:0103'
    Dysfunctional_Reliability = 'EBMS:0201'
    Delivery_Failure          = 'EBMS:0202'
    Missing_Receipt           = 'EBMS:0301'
    Invalid_Receipt           = 'EBMS:0302'
    Decompression_Failure     = 'EBMS:0303'

# ################################################################################################################################
# ################################################################################################################################

# The error detail the Peppol AS4 profile mandates when the receiving access point
# does not serve the participant a document is addressed to.
Peppol_Not_Serviced = 'PEPPOL:NOT_SERVICED'

# ################################################################################################################################
# ################################################################################################################################

class Severity:
    """ Severity values for eb:Error elements.
    """
    Failure = 'failure'
    Warning = 'warning'

# ################################################################################################################################
# ################################################################################################################################

class CryptoSuite:
    """ Names of the two crypto suites, one per eDelivery AS4 profile generation.
    """
    RSA   = 'rsa'    # eDelivery AS4 1.x - RSA-SHA256 + AES-128-GCM with RSA-OAEP key transport
    EdDSA = 'eddsa'  # eDelivery AS4 2.0 - Ed25519 + AES-128-GCM with X25519 key agreement

# ################################################################################################################################
# ################################################################################################################################

class AS4Exception(Exception):
    """ Base class for all AS4-related exceptions.
    """

# ################################################################################################################################
# ################################################################################################################################

class AS4ProtocolException(AS4Exception):
    """ Raised when an incoming message violates the AS4 or ebMS3 rules. Carries the ebMS error code
    so that the inbound pipeline can produce the matching eb:Error signal.
    """
    def __init__(self, error_code:'str', detail:'str') -> 'None':
        super().__init__(f'{error_code} {detail}')
        self.error_code = error_code
        self.detail = detail

# ################################################################################################################################
# ################################################################################################################################

class AS4SecurityException(AS4ProtocolException):
    """ Raised when signature verification, decryption or certificate validation fails.
    """

# ################################################################################################################################
# ################################################################################################################################
