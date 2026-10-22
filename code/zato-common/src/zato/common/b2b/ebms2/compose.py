# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.b2b.ebms2.common import Default, MSHService
from zato.common.b2b.ebms2.header import add_ack_requested, add_manifest, add_message_header, add_message_order, \
    add_sync_reply, HeaderParty, Manifest, ManifestReference, MessageData, MessageHeader
from zato.common.b2b.ebms2.message import new_envelope, serialize
from zato.common.b2b.ebms2.packaging import package
from zato.common.b2b.ebms2.signals import add_acknowledgment, add_error_list, add_status_request, add_status_response
from zato.common.b2b.ebms2.signature import resolve_digest_algorithm, resolve_signature_algorithm, sign_envelope
from zato.common.crypto.api import CryptoManager
from zato.common.util.xml_.core import Id_Size_Bits

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.b2b.common.keys import LocalKeys
    from zato.common.b2b.ebms2.agreement import Binding, NonRepudiation
    from zato.common.b2b.ebms2.header import AckRequested, MessageOrder
    from zato.common.b2b.ebms2.packaging import Package, payload_list
    from zato.common.b2b.ebms2.signals import Acknowledgment, ErrorList, StatusRequest, StatusResponse
    from zato.common.typing_ import any_
    AckRequested = AckRequested
    Acknowledgment = Acknowledgment
    any_ = any_
    Binding = Binding
    datetime = datetime
    ErrorList = ErrorList
    LocalKeys = LocalKeys
    MessageOrder = MessageOrder
    NonRepudiation = NonRepudiation
    Package = Package
    payload_list = payload_list
    StatusRequest = StatusRequest
    StatusResponse = StatusResponse

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Signing:
    """ The key and the algorithms a message is signed with.
    """
    local_keys:          'LocalKeys'
    signature_algorithm: str
    digest_algorithm:    str

# ################################################################################################################################

@dataclass(init=False)
class Composition:
    """ Everything one outgoing ebMS 2.0 message consists of.
    """
    header: 'MessageHeader'

    ack_requested:   'AckRequested | None' = None
    sync_reply:      bool = False
    message_order:   'MessageOrder | None' = None
    acknowledgment:  'Acknowledgment | None' = None
    error_list:      'ErrorList | None' = None
    status_request:  'StatusRequest | None' = None
    status_response: 'StatusResponse | None' = None

    payloads: 'payload_list'
    signing:  'Signing | None' = None

    def __init__(self) -> 'None':
        self.payloads = []

# ################################################################################################################################

@dataclass(init=False)
class Composed:
    """ A composed message - its envelope, the signature in it, if it is signed, and the bytes and headers to send.
    """
    envelope:  'any_'
    signature: 'any_'
    package:   'Package'

# ################################################################################################################################
# ################################################################################################################################

def new_message_id() -> 'str':
    """ Returns a fresh MessageId in the form of an RFC 2822 msg-id without its angle brackets.
    """
    random_part = CryptoManager.generate_hex_string(Id_Size_Bits)

    out = f'{random_part}@{Default.Message_Id_Domain}'
    return out

# ################################################################################################################################

def new_message_header(
    binding:'Binding',
    now:'datetime',
    conversation_id:'str',
    message_id:'str',
    ref_to_message_id:'str'='',
    ) -> 'MessageHeader':
    """ Returns the header of a message that is exchanged the way a binding says.
    """
    from_party = HeaderParty()
    from_party.party_ids = binding.from_party.party_ids

    to_party = HeaderParty()
    to_party.party_ids = binding.to_party.party_ids

    if send_binding := binding.send_binding:
        from_party.role = send_binding.role_name

    if receive_binding := binding.receive_binding:
        to_party.role = receive_binding.role_name

    message_data = MessageData()
    message_data.message_id = message_id
    message_data.timestamp = now
    message_data.ref_to_message_id = ref_to_message_id

    out = MessageHeader()
    out.from_party = from_party
    out.to_party = to_party
    out.cpa_id = binding.agreement.cpa_id
    out.conversation_id = conversation_id
    out.service = binding.service
    out.service_type = binding.service_type
    out.action = binding.action
    out.message_data = message_data

    return out

# ################################################################################################################################

def new_reply_header(original:'MessageHeader', action:'str', now:'datetime') -> 'MessageHeader':
    """ Returns the header of a message service handler message that answers another message.
    """
    from_party = HeaderParty()
    from_party.party_ids = original.to_party.party_ids

    to_party = HeaderParty()
    to_party.party_ids = original.from_party.party_ids

    message_data = MessageData()
    message_data.message_id = new_message_id()
    message_data.timestamp = now
    message_data.ref_to_message_id = original.message_data.message_id

    out = MessageHeader()
    out.from_party = from_party
    out.to_party = to_party
    out.cpa_id = original.cpa_id
    out.conversation_id = original.conversation_id
    out.service = MSHService.Service
    out.action = action
    out.message_data = message_data

    return out

# ################################################################################################################################

def signing_for(non_repudiation:'NonRepudiation | None', local_keys:'LocalKeys') -> 'Signing':
    """ Returns how a message is signed - with the algorithms that the non-repudiation requirements name,
    or with the default ones when there are no such requirements.
    """
    out = Signing()
    out.local_keys = local_keys

    if non_repudiation:
        signature_algorithm = non_repudiation.signature_algorithms[0]
        out.signature_algorithm = resolve_signature_algorithm(signature_algorithm)
        out.digest_algorithm = resolve_digest_algorithm(non_repudiation.hash_function)
    else:
        out.signature_algorithm = Default.Signature_Algorithm
        out.digest_algorithm = Default.Digest_Algorithm

    return out

# ################################################################################################################################
# ################################################################################################################################

def compose(composition:'Composition') -> 'Composed':
    """ Builds the envelope of a message, signs it if it is to be signed, and packages it with its payloads.
    """
    envelope, soap_header, soap_body = new_envelope()

    _ = add_message_header(soap_header, composition.header)

    if composition.sync_reply:
        add_sync_reply(soap_header)

    if composition.ack_requested:
        add_ack_requested(soap_header, composition.ack_requested)

    if composition.message_order:
        add_message_order(soap_header, composition.message_order)

    if composition.acknowledgment:
        add_acknowledgment(soap_header, composition.acknowledgment)

    if composition.error_list:
        add_error_list(soap_header, composition.error_list)

    # Every payload is listed in the manifest ..
    if composition.payloads:

        manifest = Manifest()

        for payload in composition.payloads:
            reference = ManifestReference()
            reference.href = f'cid:{payload.content_id}'
            manifest.references.append(reference)

        add_manifest(soap_body, manifest)

    if composition.status_request:
        add_status_request(soap_body, composition.status_request)

    if composition.status_response:
        add_status_response(soap_body, composition.status_response)

    # .. the signature covers the envelope and the payloads ..
    if signing := composition.signing:
        signature = sign_envelope(
            envelope, composition.payloads, signing.local_keys, signing.signature_algorithm, signing.digest_algorithm)
    else:
        signature = None

    # .. and the envelope travels in the first MIME part.
    envelope_bytes = serialize(envelope)

    out = Composed()
    out.envelope = envelope
    out.signature = signature
    out.package = package(envelope_bytes, composition.payloads)

    return out

# ################################################################################################################################
# ################################################################################################################################
