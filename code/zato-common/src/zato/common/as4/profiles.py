# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as4.common import CryptoSuite, Default, MEPBinding
from zato.common.as4.pmode import new_pmode, PMode
from zato.common.util.xml_.constants import Algorithm, TokenType

# ################################################################################################################################
# ################################################################################################################################

# Peppol identifier schemes and the transport-level agreement every Peppol exchange runs under.
Peppol_Party_ID_Type       = 'urn:fdc:peppol.eu:2017:identifiers:ap'
Peppol_Participant_ID_Type = 'iso6523-actorid-upis'
Peppol_Service_Type        = 'cenbii-procid-ubl'
Peppol_Agreement           = 'urn:fdc:peppol.eu:2017:agreements:tia:ap_provider'

# ################################################################################################################################
# ################################################################################################################################

def new_edelivery1_pmode() -> 'PMode':
    """ A P-Mode preset for the eDelivery AS4 1.x profile - the common usage profile
    that ICS2, EESSI and EUDAMED all build on: RSA-SHA256 signatures, AES-128-GCM
    encryption with RSA-OAEP key transport, GZIP compression, signed receipts.
    """

    # Our response to produce
    out = new_pmode()

    out.initiator.role = Default.Initiator_Role
    out.responder.role = Default.Responder_Role

    # These are already the defaults - restated here so that the preset
    # stays correct even if the defaults ever change.
    out.security.crypto_suite = CryptoSuite.RSA
    out.security.signature_algorithm = Algorithm.RSA_SHA256
    out.security.encryption_algorithm = Algorithm.AES128_GCM
    out.security.key_transport_algorithm = Algorithm.RSA_OAEP
    out.security.encrypt = True
    out.security.sign_receipts = True
    out.compress = True

    return out

# ################################################################################################################################

def new_edelivery2_pmode() -> 'PMode':
    """ A P-Mode preset for the eDelivery AS4 2.0 profile: Ed25519 signatures,
    AES-128-GCM encryption keyed through X25519 agreement with HKDF,
    and synchronous receipts only.
    """

    # Our response to produce
    out = new_edelivery1_pmode()

    out.security.crypto_suite = CryptoSuite.EdDSA
    out.security.signature_algorithm = Algorithm.Ed25519
    out.security.key_transport_algorithm = Algorithm.ECDH_ES

    return out

# ################################################################################################################################

def new_peppol_pmode() -> 'PMode':
    """ A P-Mode preset for the Peppol AS4 profile: push only, GZIP compression,
    signing without payload encryption (confidentiality comes from TLS),
    Peppol identifier schemes and the fixed transport infrastructure agreement.

    The caller still sets: the participant identifiers of both access points,
    the service (process identifier), the action (document type identifier)
    and the four-corner originalSender and finalRecipient properties.
    """

    # Our response to produce
    out = new_pmode()

    out.mep_binding = MEPBinding.Push

    out.agreement = Peppol_Agreement

    out.initiator.role = Default.Initiator_Role
    out.initiator.party_type = Peppol_Party_ID_Type

    out.responder.role = Default.Responder_Role
    out.responder.party_type = Peppol_Party_ID_Type

    out.service_type = Peppol_Service_Type

    out.original_sender_type = Peppol_Participant_ID_Type
    out.final_recipient_type = Peppol_Participant_ID_Type

    # Peppol signs everything but never encrypts on the message level.
    out.security.encrypt = False
    out.compress = True

    return out

# ################################################################################################################################

def new_ics2_pmode() -> 'PMode':
    """ A P-Mode preset for ICS2 - the eDelivery 1.x profile as narrowed by the ICS2
    interface control document annex II: the certificate chain travels as a PKIPath token
    and messages from customs are fetched with One-Way/Pull from an EORI-specific
    message partition channel.

    The caller still sets: the party identifiers, the service and action
    for the concrete message type, and the mpc to pull from.
    """

    # Our response to produce
    out = new_edelivery1_pmode()

    out.mep_binding = MEPBinding.Pull
    out.security.token_type = TokenType.PKIPath

    return out

# ################################################################################################################################
# ################################################################################################################################
