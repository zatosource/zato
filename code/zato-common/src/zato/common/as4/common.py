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

    # How many times one message is delivered in total before it is left alone, the first
    # attempt included, when the P-Mode does not say otherwise.
    Retry_Max_Attempts = 4

    # How long an attempt goes unanswered before it is repeated, in seconds.
    Retry_Interval_Seconds = 15 * 60

    # How long an exchange goes unanswered before its receipt counts as missing rather than late,
    # in seconds. This is what alerting reports on and what ends the retries whether the attempts
    # have run out or not.
    Missing_Receipt_Seconds = 24 * 3600

# ################################################################################################################################
# ################################################################################################################################

class Limits:
    """ What one incoming message is allowed to be and to cost. These are the ceilings that apply
    before a P-Mode has even been matched, so they are fixed rather than per exchange.
    """
    # How many MIME parts one message may carry. The AS4 profiles in use send one payload per
    # message, so this leaves room for the multi-payload case without leaving it open.
    Max_Part_Count = 16

    # How large one MIME part may be on the wire.
    Max_Part_Size_Bytes = 64 * 1024 * 1024

    # How large one part may be once decompressed. Decompression stops at this point rather than
    # running to completion and finding out afterwards.
    Max_Decompressed_Size_Bytes = 256 * 1024 * 1024

    # How far from the current time the eb:Timestamp of an incoming message may be, in either
    # direction. The allowance either way covers clock drift between the two parties.
    Timestamp_Window_Seconds = 300

# ################################################################################################################################
# ################################################################################################################################

# The separator between a message partition channel and a sub-channel of it, per ebMS 3.0 - a
# sub-channel is named by extending the name of the channel it belongs to.
Sub_Channel_Separator = '/'

# ################################################################################################################################

def serves_channel(served:'str', requested:'str') -> 'bool':
    """ Tells whether an endpoint serving one message partition channel serves the one a pull request
    asks about - the channel itself, or any sub-channel of it, which is named by extending its name.
    """
    if not served:
        out = False

    elif requested == served:
        out = True

    else:
        prefix = served + Sub_Channel_Separator
        out = requested.startswith(prefix)

    return out

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
