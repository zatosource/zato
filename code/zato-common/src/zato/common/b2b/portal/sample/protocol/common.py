# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from hashlib import sha256
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

class Protocol:
    """ The messaging protocols a trading partner exchanges documents over.
    """
    ebXML = 'ebXML'
    AS2   = 'AS2'
    AS4   = 'AS4'

Protocols = [Protocol.ebXML, Protocol.AS2, Protocol.AS4]

# A messaging-layer message that names the business service it answers rather than a service of its own
Business_Service = ''

# ################################################################################################################################

class Vocabulary(NamedTuple):
    """ What the agreements and the messages of one protocol call the elements every protocol has.
    """
    agreement_label: str
    channel_path: str
    ack_action: str
    ack_noun: str
    receipt_noun: str
    error_action: str
    messaging_service: str
    has_business_signals: bool
    delivery_failure_code: str
    security_failure_code: str
    duplicate_code: str
    receipt_overdue_code: str

# ################################################################################################################################

Vocabularies = {
    Protocol.ebXML: Vocabulary(
        agreement_label='CPAId',
        channel_path='/exchange/{party_id}',
        ack_action='Acknowledgment',
        ack_noun='acknowledgment',
        receipt_noun='receipt acknowledgement',
        error_action='MessageError',
        messaging_service='urn:oasis:names:tc:ebxml-msg:service',
        has_business_signals=True,
        delivery_failure_code='DeliveryFailure',
        security_failure_code='SecurityFailure',
        duplicate_code='DuplicateElimination',
        receipt_overdue_code='TimeToAcknowledgeReceipt',
    ),
    Protocol.AS2: Vocabulary(
        agreement_label='Partnership',
        channel_path='/as2/receive',
        ack_action='MDN',
        ack_noun='MDN',
        receipt_noun='MDN',
        error_action='MDN',
        messaging_service=Business_Service,
        has_business_signals=False,
        delivery_failure_code='DeliveryFailure',
        security_failure_code='authentication-failed',
        duplicate_code='duplicate-document',
        receipt_overdue_code='MDNOverdue',
    ),
    Protocol.AS4: Vocabulary(
        agreement_label='AgreementRef',
        channel_path='/as4/msh',
        ack_action='Receipt',
        ack_noun='receipt',
        receipt_noun='receipt acknowledgement',
        error_action='Error',
        messaging_service=Business_Service,
        has_business_signals=True,
        delivery_failure_code='EBMS:0202',
        security_failure_code='EBMS:0101',
        duplicate_code='DuplicateDetection',
        receipt_overdue_code='TimeToAcknowledgeReceipt',
    ),
}

# ################################################################################################################################

class ProtocolViews(NamedTuple):
    """ The parts of the partner, agreement and message pages that differ from one protocol to another.
    """
    partner_identifiers: 'callable_'
    certificate_usages: 'strlist'
    agreement_parties: 'callable_'
    agreement_tabs: 'callable_'
    message_details: 'callable_'

# ################################################################################################################################
# ################################################################################################################################

# How many characters of base64 one line of a MIME part holds
_base64_line_length = 76

# ################################################################################################################################

def channel_path(protocol:'str', party_id:'str') -> 'str':
    """ The path of the HTTP endpoint a party receives the messages of the protocol on.
    """
    vocabulary = Vocabularies[protocol]

    out = vocabulary.channel_path.format(party_id=party_id)
    return out

# ################################################################################################################################

def is_signature_verified(message:'anydict') -> 'bool':
    vocabulary = Vocabularies[message['protocol']]

    out = message['error_code'] != vocabulary.security_failure_code
    return out

# ################################################################################################################################

def transport_label(message:'anydict') -> 'str':
    """ The label of the tab that says how a message went out or how it came in.
    """
    out = 'Transport' if message['direction'] == 'Outbound' else 'Reception'
    return out

# ################################################################################################################################

def opaque_bytes(seed:'str', size:'int') -> 'bytes':
    """ Bytes that stand in for the encrypted or signed content of a message, the same ones for the same seed.
    """
    out = b''
    counter = 0

    while len(out) < size:
        block = f'{seed}.{counter}'
        block = block.encode('utf8')
        out += sha256(block).digest()
        counter += 1

    out = out[:size]
    return out

# ################################################################################################################################

def opaque_text(seed:'str', size:'int') -> 'str':
    """ The base64 form of opaque bytes, on one line, as an XML element holds a key, a token or a signature value.
    """
    data = opaque_bytes(seed, size)

    out = b64encode(data).decode('ascii')
    return out

# ################################################################################################################################

def base64_lines(data:'bytes') -> 'strlist':
    """ The base64 form of the data, in the lines of the length MIME uses.
    """
    encoded = b64encode(data).decode('ascii')
    out:'strlist' = []

    for start in range(0, len(encoded), _base64_line_length):
        end = start + _base64_line_length
        out.append(encoded[start:end])

    return out

# ################################################################################################################################

def digest(text:'str') -> 'str':
    """ The base64 form of the SHA-256 digest of the text.
    """
    data = text.encode('utf8')
    value = sha256(data).digest()

    out = b64encode(value).decode('ascii')
    return out

# ################################################################################################################################
# ################################################################################################################################
