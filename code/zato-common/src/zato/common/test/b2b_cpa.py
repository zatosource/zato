# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from dataclasses import dataclass
from datetime import timedelta

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding

# lxml
from lxml.etree import Element, SubElement, tostring

# Zato
from zato.common.b2b.ebms2.common import Actor, Default, MessageOrderSemantics, NS, PerMessage, SyncReplyMode
from zato.common.util.xml_.core import qname, to_timestamp

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from cryptography.x509 import Certificate
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import any_
    any_ = any_
    Certificate = Certificate
    datetime = datetime
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

Party_Id_Type = 'urn:zato:b2b:party-id'

Default_CPA_Id = 'b2b-test-agreement'
Default_Service = 'urn:zato:b2b:test:orders'
Default_Action = 'Submit'

Sender_Name = 'b2b-sender'
Receiver_Name = 'b2b-receiver'

Sender_Endpoint = 'http://127.0.0.1:17010/ebms2/sender'
Receiver_Endpoint = 'http://127.0.0.1:17010/ebms2/receiver'

Sender_Role = 'Buyer'
Receiver_Role = 'Seller'

# How long a generated agreement is in effect on either side of the moment it is generated.
Validity_Days = 365

# The values of the elements an agreement always carries the same way.
_cpa_version = '2_0b'
_ebms_version = '2.0'
_status_agreed = 'agreed'
_xlink_type_simple = 'simple'
_transport_protocol = 'HTTP'
_transport_protocol_version = '1.1'
_non_repudiation_protocol = 'http://www.w3.org/2000/09/xmldsig#'
_process_name = 'b2b-test-process'
_process_version = '1.0'
_process_href = 'urn:zato:b2b:test:process'
_role_href_prefix = 'urn:zato:b2b:test:role:'
_party_ref_prefix = 'urn:zato:b2b:test:party:'
_package_id = 'b2b-package'
_simple_part_header = 'b2b-part-header'
_simple_part_payload = 'b2b-part-payload'
_header_media_type = 'text/xml'
_payload_media_type = 'application/xml'
_multipart_media_type = 'multipart/related'
_composite_id = 'b2b-composite'
_boolean_true = 'true'
_boolean_false = 'false'

# The two sides of a document exchange and the non-repudiation element of each.
_exchange_bindings = (
    ('ebXMLSenderBinding', 'SenderNonRepudiation'),
    ('ebXMLReceiverBinding', 'ReceiverNonRepudiation'),
)

_parts = (
    (_simple_part_header, _header_media_type),
    (_simple_part_payload, _payload_media_type),
)

_nsmap = {
    'tns':   NS.CPA,
    'xlink': NS.XLINK,
    'ds':    NS.DS,
}

_xlink_href = qname(NS.XLINK, 'href')
_xlink_type = qname(NS.XLINK, 'type')

_ds_key_info = qname(NS.DS, 'KeyInfo')
_ds_x509_data = qname(NS.DS, 'X509Data')
_ds_x509_certificate = qname(NS.DS, 'X509Certificate')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ChannelSettings:
    """ The MessagingCharacteristics of one delivery channel.
    """
    sync_reply_mode:         str = SyncReplyMode.No_Reply
    ack_requested:           str = PerMessage.Always
    ack_signature_requested: str = PerMessage.Never
    duplicate_elimination:   str = PerMessage.Always
    actor:                   str = Actor.To_Party_MSH

# ################################################################################################################################

@dataclass(init=False)
class ServiceSettings:
    """ One service of an agreement with the action the sender sends under it.
    """
    service:      str
    service_type: str = ''
    action:       str

service_settings_list = list[ServiceSettings]

# ################################################################################################################################

@dataclass(init=False)
class PartySettings:
    """ One party of a generated agreement.
    """
    name:          str
    party_id:      str
    party_id_type: str = Party_Id_Type
    role:          str
    endpoint:    str
    certificate: 'Certificate'

    # The business action bindings of the party, by direction.
    can_send:    bool = False
    can_receive: bool = False

# ################################################################################################################################

@dataclass(init=False)
class AgreementSettings:
    """ Everything a generated agreement varies by.
    """
    cpa_id: str = Default_CPA_Id
    start:  'datetime'
    end:    'datetime'

    service:      str = Default_Service
    service_type: str = ''
    action:       str = Default_Action

    # Further services, each with one action, that the sender sends to the receiver as well.
    extra_services: 'service_settings_list'

    sender:         'PartySettings'
    receiver:       'PartySettings'
    ca_certificate: 'Certificate'

    business_channel: 'ChannelSettings'
    msh_channel:      'ChannelSettings'

    # Whether business messages and message service handler messages are signed.
    is_signed:     bool = True
    is_msh_signed: bool = False

    hash_function:       str = Default.Digest_Algorithm
    signature_algorithm: str = Default.Signature_Algorithm

    retries:          int = 3
    retry_interval:   str = 'PT30S'
    persist_duration: str = 'P1D'
    message_order:    str = MessageOrderSemantics.Not_Guaranteed

# ################################################################################################################################
# ################################################################################################################################

def new_settings(parties:'TestParties', now:'datetime') -> 'AgreementSettings':
    """ Returns the settings of an agreement in effect around the given moment, under which the sender sends
    the default action to the receiver.
    """
    validity = timedelta(days=Validity_Days)

    sender = PartySettings()
    sender.name = Sender_Name
    sender.party_id = Sender_Name
    sender.role = Sender_Role
    sender.endpoint = Sender_Endpoint
    sender.certificate = parties.sender.certificate
    sender.can_send = True

    receiver = PartySettings()
    receiver.name = Receiver_Name
    receiver.party_id = Receiver_Name
    receiver.role = Receiver_Role
    receiver.endpoint = Receiver_Endpoint
    receiver.certificate = parties.receiver.certificate
    receiver.can_receive = True

    msh_channel = ChannelSettings()
    msh_channel.ack_requested = PerMessage.Never
    msh_channel.duplicate_elimination = PerMessage.Never

    out = AgreementSettings()
    out.extra_services = []
    out.start = now - validity
    out.end = now + validity
    out.sender = sender
    out.receiver = receiver
    out.ca_certificate = parties.ca_certificate
    out.business_channel = ChannelSettings()
    out.msh_channel = msh_channel

    return out

# ################################################################################################################################
# ################################################################################################################################

def _add(parent:'any_', name:'str', text:'str'='') -> 'any_':
    child_tag = qname(NS.CPA, name)

    out = SubElement(parent, child_tag)

    if text:
        out.text = text

    return out

# ################################################################################################################################

def _set(element:'any_', name:'str', value:'str') -> 'None':
    attribute_name = qname(NS.CPA, name)
    element.set(attribute_name, value)

# ################################################################################################################################

def _add_xlink(element:'any_', href:'str') -> 'None':
    element.set(_xlink_type, _xlink_type_simple)
    element.set(_xlink_href, href)

# ################################################################################################################################

def _add_protocol(parent:'any_', name:'str', text:'str', version:'str'='') -> 'None':
    element = _add(parent, name, text)

    if version:
        _set(element, 'version', version)

# ################################################################################################################################

def _add_reference(parent:'any_', name:'str', attribute:'str', value:'str') -> 'None':
    element = _add(parent, name)
    _set(element, attribute, value)

# ################################################################################################################################

def _add_certificate(parent:'any_', cert_id:'str', certificate:'Certificate') -> 'None':

    element = _add(parent, 'Certificate')
    _set(element, 'certId', cert_id)

    der = certificate.public_bytes(Encoding.DER)
    encoded = b64encode(der)

    key_info = SubElement(element, _ds_key_info)
    x509_data = SubElement(key_info, _ds_x509_data)
    certificate_element = SubElement(x509_data, _ds_x509_certificate)
    certificate_element.text = encoded.decode('ascii')

# ################################################################################################################################

def _add_action_binding(parent:'any_', kind:'str', binding_id:'str', action:'str', settings:'AgreementSettings',
    channel_id:'str', other_binding_id:'str') -> 'None':

    element = _add(parent, kind)

    this_party = _add(element, 'ThisPartyActionBinding')
    _set(this_party, 'id', binding_id)
    _set(this_party, 'action', action)
    _set(this_party, 'packageId', _package_id)

    if settings.is_signed:
        is_non_repudiation_required = _boolean_true
    else:
        is_non_repudiation_required = _boolean_false

    characteristics = _add(this_party, 'BusinessTransactionCharacteristics')
    _set(characteristics, 'isNonRepudiationRequired', is_non_repudiation_required)

    _ = _add(this_party, 'ChannelId', channel_id)
    _ = _add(element, 'OtherPartyActionBinding', other_binding_id)

# ################################################################################################################################

def _services(settings:'AgreementSettings') -> 'service_settings_list':
    """ Returns every service of an agreement, the main one first.
    """
    main = ServiceSettings()
    main.service = settings.service
    main.service_type = settings.service_type
    main.action = settings.action

    out = [main]

    for extra in settings.extra_services:
        out.append(extra)

    return out

# ################################################################################################################################

def _add_collaboration_role(parent:'any_', party:'PartySettings', other:'PartySettings', settings:'AgreementSettings',
    service_settings:'ServiceSettings', index:'int') -> 'None':

    element = _add(parent, 'CollaborationRole')

    process = _add(element, 'ProcessSpecification')
    _set(process, 'name', _process_name)
    _set(process, 'version', _process_version)
    _add_xlink(process, _process_href)

    role = _add(element, 'Role')
    _set(role, 'name', party.role)
    _add_xlink(role, _role_href_prefix + party.role)

    service_binding = _add(element, 'ServiceBinding')
    service = _add(service_binding, 'Service', service_settings.service)

    if service_settings.service_type:
        _set(service, 'type', service_settings.service_type)

    channel_id = f'{party.name}-business'
    action = service_settings.action

    # The schema has every CanSend before every CanReceive.
    if party.can_send:
        binding_id = f'{party.name}-send-{index}'
        other_binding_id = f'{other.name}-receive-{index}'
        _add_action_binding(service_binding, 'CanSend', binding_id, action, settings, channel_id, other_binding_id)

    if party.can_receive:
        binding_id = f'{party.name}-receive-{index}'
        other_binding_id = f'{other.name}-send-{index}'
        _add_action_binding(service_binding, 'CanReceive', binding_id, action, settings, channel_id, other_binding_id)

# ################################################################################################################################

def _add_delivery_channel(parent:'any_', channel_id:'str', transport_id:'str', exchange_id:'str',
    channel:'ChannelSettings') -> 'None':

    element = _add(parent, 'DeliveryChannel')
    _set(element, 'channelId', channel_id)
    _set(element, 'transportId', transport_id)
    _set(element, 'docExchangeId', exchange_id)

    characteristics = _add(element, 'MessagingCharacteristics')
    _set(characteristics, 'syncReplyMode', channel.sync_reply_mode)
    _set(characteristics, 'ackRequested', channel.ack_requested)
    _set(characteristics, 'ackSignatureRequested', channel.ack_signature_requested)
    _set(characteristics, 'duplicateElimination', channel.duplicate_elimination)
    _set(characteristics, 'actor', channel.actor)

# ################################################################################################################################

def _add_transport(parent:'any_', party:'PartySettings') -> 'None':

    element = _add(parent, 'Transport')
    _set(element, 'transportId', f'{party.name}-transport')

    sender = _add(element, 'TransportSender')
    _add_protocol(sender, 'TransportProtocol', _transport_protocol, _transport_protocol_version)

    receiver = _add(element, 'TransportReceiver')
    _add_protocol(receiver, 'TransportProtocol', _transport_protocol, _transport_protocol_version)

    endpoint = _add(receiver, 'Endpoint')
    _set(endpoint, 'uri', party.endpoint)

# ################################################################################################################################

def _add_non_repudiation(parent:'any_', name:'str', settings:'AgreementSettings') -> 'any_':

    out = _add(parent, name)
    _add_protocol(out, 'NonRepudiationProtocol', _non_repudiation_protocol)
    _ = _add(out, 'HashFunction', settings.hash_function)

    algorithm = _add(out, 'SignatureAlgorithm', settings.signature_algorithm)
    _set(algorithm, 'w3c', settings.signature_algorithm)

    return out

# ################################################################################################################################

def _add_doc_exchange(parent:'any_', party:'PartySettings', exchange_id:'str', settings:'AgreementSettings', *,
    is_signed:'bool', is_reliable:'bool') -> 'None':

    element = _add(parent, 'DocExchange')
    _set(element, 'docExchangeId', exchange_id)

    for binding_name, non_repudiation_name in _exchange_bindings:

        binding = _add(element, binding_name)
        _set(binding, 'version', _ebms_version)

        if is_reliable:
            retries = str(settings.retries)
            reliable = _add(binding, 'ReliableMessaging')
            _ = _add(reliable, 'Retries', retries)
            _ = _add(reliable, 'RetryInterval', settings.retry_interval)
            _ = _add(reliable, 'MessageOrderSemantics', settings.message_order)

        _ = _add(binding, 'PersistDuration', settings.persist_duration)

        if is_signed:
            non_repudiation = _add_non_repudiation(binding, non_repudiation_name, settings)

            if non_repudiation_name == 'SenderNonRepudiation':
                _add_reference(non_repudiation, 'SigningCertificateRef', 'certId', f'{party.name}-signing')
            else:
                _add_reference(non_repudiation, 'SigningSecurityDetailsRef', 'securityId', f'{party.name}-trust')

# ################################################################################################################################

def _add_party(parent:'any_', party:'PartySettings', other:'PartySettings', settings:'AgreementSettings') -> 'None':

    msh_channel_id = f'{party.name}-msh'
    business_channel_id = f'{party.name}-business'
    transport_id = f'{party.name}-transport'
    msh_exchange_id = f'{party.name}-msh-exchange'
    business_exchange_id = f'{party.name}-business-exchange'

    element = _add(parent, 'PartyInfo')
    _set(element, 'partyName', party.name)
    _set(element, 'defaultMshChannelId', msh_channel_id)
    _set(element, 'defaultMshPackageId', _package_id)

    party_id = _add(element, 'PartyId', party.party_id)

    if party.party_id_type:
        _set(party_id, 'type', party.party_id_type)

    party_ref = _add(element, 'PartyRef')
    _add_xlink(party_ref, _party_ref_prefix + party.name)

    services = _services(settings)

    for index, service_settings in enumerate(services):
        _add_collaboration_role(element, party, other, settings, service_settings, index)

    _add_certificate(element, f'{party.name}-signing', party.certificate)
    _add_certificate(element, f'{party.name}-ca', settings.ca_certificate)

    details = _add(element, 'SecurityDetails')
    _set(details, 'securityId', f'{party.name}-trust')

    anchors = _add(details, 'TrustAnchors')
    _add_reference(anchors, 'AnchorCertificateRef', 'certId', f'{party.name}-ca')

    _add_delivery_channel(element, business_channel_id, transport_id, business_exchange_id, settings.business_channel)
    _add_delivery_channel(element, msh_channel_id, transport_id, msh_exchange_id, settings.msh_channel)

    _add_transport(element, party)

    _add_doc_exchange(element, party, business_exchange_id, settings, is_signed=settings.is_signed, is_reliable=True)
    _add_doc_exchange(element, party, msh_exchange_id, settings, is_signed=settings.is_msh_signed, is_reliable=False)

# ################################################################################################################################

def _add_packaging(parent:'any_') -> 'None':

    for part_id, media_type in _parts:
        part = _add(parent, 'SimplePart')
        _set(part, 'id', part_id)
        _set(part, 'mimetype', media_type)

    packaging = _add(parent, 'Packaging')
    _set(packaging, 'id', _package_id)

    capabilities = _add(packaging, 'ProcessingCapabilities')
    _set(capabilities, 'parse', _boolean_true)
    _set(capabilities, 'generate', _boolean_true)

    composite_list = _add(packaging, 'CompositeList')
    composite = _add(composite_list, 'Composite')
    _set(composite, 'id', _composite_id)
    _set(composite, 'mimetype', _multipart_media_type)

    for part_id, _ in _parts:
        constituent = _add(composite, 'Constituent')
        _set(constituent, 'idref', part_id)

# ################################################################################################################################
# ################################################################################################################################

def build_cpa_element(settings:'AgreementSettings') -> 'any_':
    """ Returns a CPP/A 2.0 agreement between the two parties of the settings, as the root element of the document.
    """
    root_tag = qname(NS.CPA, 'CollaborationProtocolAgreement')

    out = Element(root_tag, nsmap=_nsmap)
    _set(out, 'cpaid', settings.cpa_id)
    _set(out, 'version', _cpa_version)

    status = _add(out, 'Status')
    _set(status, 'value', _status_agreed)

    start = to_timestamp(settings.start)
    end = to_timestamp(settings.end)

    _ = _add(out, 'Start', start)
    _ = _add(out, 'End', end)

    _add_party(out, settings.sender, settings.receiver, settings)
    _add_party(out, settings.receiver, settings.sender, settings)

    _add_packaging(out)

    return out

# ################################################################################################################################

def build_cpa(settings:'AgreementSettings') -> 'bytes':
    """ Returns a CPP/A 2.0 agreement between the two parties of the settings.
    """
    root = build_cpa_element(settings)

    out = tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    return out

# ################################################################################################################################
# ################################################################################################################################
