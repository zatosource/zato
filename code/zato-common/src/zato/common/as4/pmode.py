# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.as4.common import Algorithm, CryptoSuite, Default, MEP, MEPBinding, TokenType

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

    # PMode[].Security.X509.Signature.*
    signature_algorithm: str = Algorithm.RSA_SHA256
    digest_algorithm:    str = Algorithm.SHA256

    # PMode[].Security.X509.Encryption.*
    encryption_algorithm:    str = Algorithm.AES128_GCM
    key_transport_algorithm: str = Algorithm.RSA_OAEP
    key_transport_mgf:       str = Algorithm.MGF1_SHA256
    key_transport_digest:    str = Algorithm.SHA256

    # Whether outgoing payload parts are to be encrypted at all.
    encrypt: bool = True

    # How the signing certificate travels inside the message - a single leaf certificate
    # or the whole chain as a PKIPath (the latter is what ICS2 requires).
    token_type: str = TokenType.X509v3

    # Whether receipts must be signed and carry non-repudiation information.
    sign_receipts: bool = True

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PMode:
    """ An ebMS3 processing mode - the full configuration of one message exchange relationship.
    Parameter names follow appendix D of the ebMS 3.0 Core specification so that the tables
    in the eDelivery profile and the ICS2 interface control document map to fields one to one.
    """
    id: str = ''

    # PMode.MEP and PMode.MEPBinding
    mep:         str = MEP.One_Way
    mep_binding: str = MEPBinding.Push

    # PMode.Initiator.* and PMode.Responder.* - assigned by new_pmode.
    initiator: 'Party'
    responder: 'Party'

    # PMode.Agreement
    agreement:      'strnone' = None
    agreement_type: 'strnone' = None

    # PMode[1].Protocol.Address - where to send outgoing messages.
    endpoint_url: str = ''

    # PMode[1].BusinessInfo.*
    service:      str = Default.Test_Service
    service_type: 'strnone' = None
    action:       str = Default.Test_Action
    mpc:          str = Default.MPC

    # PMode[1].PayloadService.CompressionType - GZIP is the only type AS4 defines,
    # so this is a boolean switch rather than a value.
    compress: bool = True

    # PMode[1].Security.* - assigned by new_pmode.
    security: 'SecurityConfig'

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

    return out

# ################################################################################################################################
# ################################################################################################################################
