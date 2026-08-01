# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.as4.common import CryptoSuite, Default
from zato.common.util.xml_.constants import Algorithm, TokenType

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Party:
    """ One communicating party - its identifier, optional identifier type and the role it plays in the exchange.
    """
    party_id:   str = ''
    party_type: 'strnone' = None
    role:       str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SecurityConfig:
    """ The security-related subset of P-Mode parameters, following PMode[].Security.* from ebMS 3.0 appendix D.
    """
    # Which of the two crypto suites to use - this selects every algorithm below unless overridden.
    crypto_suite: str = CryptoSuite.RSA

    # PMode[].Security.X509.Signature.Algorithm - the digest that goes with it is SHA-256,
    # which is what both AS4 crypto suites prescribe.
    signature_algorithm: str = Algorithm.RSA_SHA256

    # PMode[].Security.X509.Encryption.Algorithm - AES-128-GCM under both suites, so only
    # the key transport differs between them and only it is configured here.
    key_transport_algorithm: str = Algorithm.RSA_OAEP

    # Whether outgoing payload parts are to be encrypted at all.
    encrypt: bool = True

    # How the signing certificate travels inside the message - a single leaf certificate
    # or the whole chain as a PKIPath (the latter is what ICS2 requires).
    token_type: str = TokenType.X509v3

    # Whether receipts must be signed and carry non-repudiation information.
    sign_receipts: bool = True

    # PMode[1].Security.UsernameToken.* - the credentials some networks require next to the
    # signature, e.g. to authorize a pull request. With no username configured no token is added
    # to what goes out and none is expected of what comes in. The password travels in the text form
    # of the UsernameToken profile, on a TLS connection.
    username_token_username: str = ''
    username_token_password: str = ''

    # Whether the eb:From PartyId of an incoming message is required to be the common name of the
    # certificate that signed it. Networks that issue one certificate per party identifier say yes.
    party_id_is_certificate_cn: bool = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ReceptionAwareness:
    """ PMode[1].ReceptionAwareness.* - the AS4 reliability feature. A sending access point that
    turns it on owes the message a receipt, repeats the delivery while none arrives and expects
    the receiving side to eliminate the duplicates that produces.
    """
    # PMode[1].ReceptionAwareness - whether the feature is used at all. With it off a message
    # is delivered once and whatever comes back is the end of it.
    is_enabled: bool = True

    # PMode[1].ReceptionAwareness.Retry - whether an unanswered message is delivered again.
    retry: bool = True

    # PMode[1].ReceptionAwareness.Retry.Parameters - how many deliveries one message gets in total,
    # the first attempt included, and how long an attempt goes unanswered before the next one.
    retry_max_attempts:     int = Default.Retry_Max_Attempts
    retry_interval_seconds: int = Default.Retry_Interval_Seconds

    # PMode[1].ReceptionAwareness.DuplicateDetection - whether the receiving side is expected to
    # recognize a repeated eb:MessageId. Retries are only safe to send because of it.
    duplicate_detection: bool = True

    # How long the exchange is given before its receipt counts as missing rather than late.
    # Past this point the retries stop and the exchange is what alerting reports.
    missing_receipt_seconds: int = Default.Missing_Receipt_Seconds

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PMode:
    """ An ebMS3 processing mode - the full configuration of one message exchange relationship.
    Parameter names follow appendix D of the ebMS 3.0 Core specification so that the tables
    in the eDelivery profile and the ICS2 interface control document map to fields one to one.
    """
    id: str = ''

    # PMode.Initiator.* and PMode.Responder.* - assigned by new_pmode.
    initiator: 'Party'
    responder: 'Party'

    # PMode.Agreement
    agreement:      'strnone' = None
    agreement_type: 'strnone' = None

    # PMode[1].Protocol.Address - where to send outgoing messages.
    endpoint_url: str = ''

    # PMode[1].BusinessInfo.*
    service:      str = Default.Service
    service_type: 'strnone' = None
    action:       str = Default.Action
    mpc:          str = Default.MPC

    # PMode[1].PayloadService.CompressionType - GZIP is the only type AS4 defines,
    # so this is a boolean switch rather than a value.
    compress: bool = True

    # PMode[1].Security.* - assigned by new_pmode.
    security: 'SecurityConfig'

    # PMode[1].ReceptionAwareness.* - assigned by new_pmode.
    reception_awareness: 'ReceptionAwareness'

    # Four-corner message properties - when set, they are added
    # as eb:MessageProperties (originalSender and finalRecipient).
    original_sender:      'strnone' = None
    original_sender_type: 'strnone' = None
    final_recipient:      'strnone' = None
    final_recipient_type: 'strnone' = None

    # HTTP behavior for outbound requests.
    http_timeout_seconds: int = Default.HTTP_Timeout_Seconds
    verify_tls: bool = True

# ################################################################################################################################
# ################################################################################################################################

def new_pmode() -> 'PMode':
    """ Returns a fresh P-Mode with its nested configuration objects in place.
    """

    # Our response to produce
    out = PMode()

    out.initiator = Party()
    out.responder = Party()
    out.security = SecurityConfig()
    out.reception_awareness = ReceptionAwareness()

    return out

# ################################################################################################################################
# ################################################################################################################################
