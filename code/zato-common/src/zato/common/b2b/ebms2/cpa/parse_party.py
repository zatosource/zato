# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from binascii import Error as BinasciiError

# cryptography
from cryptography.x509 import load_der_x509_certificate

# Zato
from zato.common.b2b.ebms2.agreement import ActionBinding, ActionBindingKind, CollaborationRole, CPACertificate, \
    DeliveryChannel, DocExchange, DocExchangeBinding, Endpoint, MessagingCharacteristics, NonRepudiation, \
    OverrideMshActionBinding, Party, PartyRef, Protocol, ReliableMessaging, SecurityDetails, ServiceBinding, Transport, \
    TransportSecurity
from zato.common.b2b.ebms2.common import Actor, CPAException, MessageOrderSemantics, new_party_id, NS, PerMessage, \
    SyncReplyMode
from zato.common.b2b.ebms2.cpa.xml_ import children, get_attribute, local_name, optional_attribute, optional_child, \
    optional_text, parse_duration, require_attribute, require_child, require_text
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strset
    any_ = any_
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

_xlink_href = qname(NS.XLINK, 'href')

_ds_key_info = qname(NS.DS, 'KeyInfo')
_ds_x509_data = qname(NS.DS, 'X509Data')
_ds_x509_certificate = qname(NS.DS, 'X509Certificate')

# The values each enumerated attribute of MessagingCharacteristics may take.
_sync_reply_modes:'strset' = {
    SyncReplyMode.No_Reply,
    SyncReplyMode.MSH_Signals_Only,
    SyncReplyMode.Signals_Only,
    SyncReplyMode.Response_Only,
    SyncReplyMode.Signals_And_Response,
}

_per_message_values:'strset' = {PerMessage.Always, PerMessage.Never, PerMessage.Per_Message}

_actors:'strset' = {Actor.Next_MSH, Actor.To_Party_MSH}

_message_order_values:'strset' = {MessageOrderSemantics.Guaranteed, MessageOrderSemantics.Not_Guaranteed}

# The nested action bindings of each kind of action binding.
_nested_kind = {
    ActionBindingKind.Can_Send:    ActionBindingKind.Can_Receive,
    ActionBindingKind.Can_Receive: ActionBindingKind.Can_Send,
}

# ################################################################################################################################
# ################################################################################################################################

def _enumerated_attribute(element:'any_', name:'str', allowed:'strset', default:'str') -> 'str':
    """ Returns an attribute that takes one of a fixed set of values, or its default when it is absent.
    """
    if (out := get_attribute(element, name)) is None:
        out = default

    if out not in allowed:
        element_name = local_name(element)
        raise CPAException(element_name, f'Attribute `{name}` has an unsupported value `{out}`')

    return out

# ################################################################################################################################

def _xlink_attribute(element:'any_') -> 'str':
    """ Returns the xlink:href an element is required to have.
    """
    if (out := element.get(_xlink_href)) is None:
        element_name = local_name(element)
        raise CPAException(element_name, 'Attribute `xlink:href` is missing')

    return out

# ################################################################################################################################

def _parse_protocol(element:'any_') -> 'Protocol':
    out = Protocol()
    out.name = require_text(element)
    out.version = optional_attribute(element, 'version')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _parse_action_binding(element:'any_', kind:'str', service:'str', service_type:'str', role_name:'str') -> 'ActionBinding':
    """ Parses a CanSend or a CanReceive with the action bindings nested in it.
    """
    this_party = require_child(element, 'ThisPartyActionBinding')
    characteristics = require_child(this_party, 'BusinessTransactionCharacteristics')

    out = ActionBinding()
    out.kind = kind
    out.binding_id = require_attribute(this_party, 'id')
    out.action = require_attribute(this_party, 'action')
    out.package_id = require_attribute(this_party, 'packageId')
    out.service = service
    out.service_type = service_type
    out.role_name = role_name
    out.other_party_binding_id = optional_text(element, 'OtherPartyActionBinding')

    # The attributes of the transaction characteristics are kept as they were written.
    for name, value in characteristics.attrib.items():
        _, _, attribute_name = name.rpartition('}')
        out.characteristics[attribute_name] = value

    for channel_id_element in children(this_party, 'ChannelId'):
        channel_id = require_text(channel_id_element)
        out.channel_ids.append(channel_id)

    if not out.channel_ids:
        raise CPAException('ThisPartyActionBinding', f'Action binding `{out.binding_id}` names no delivery channel')

    nested_kind = _nested_kind[kind]

    for nested_element in children(element, nested_kind):
        nested = _parse_action_binding(nested_element, nested_kind, service, service_type, role_name)
        out.nested.append(nested)

    return out

# ################################################################################################################################

def _parse_collaboration_role(element:'any_') -> 'CollaborationRole':

    process = require_child(element, 'ProcessSpecification')
    role = require_child(element, 'Role')
    service_binding_element = require_child(element, 'ServiceBinding')
    service_element = require_child(service_binding_element, 'Service')

    role_name = require_attribute(role, 'name')

    service_binding = ServiceBinding()
    service_binding.service = require_text(service_element)
    service_binding.service_type = optional_attribute(service_element, 'type')

    for kind in (ActionBindingKind.Can_Send, ActionBindingKind.Can_Receive):
        for binding_element in children(service_binding_element, kind):
            binding = _parse_action_binding(
                binding_element, kind, service_binding.service, service_binding.service_type, role_name)
            service_binding.bindings.append(binding)

    out = CollaborationRole()
    out.process_name = require_attribute(process, 'name')
    out.process_version = require_attribute(process, 'version')
    out.process_href = _xlink_attribute(process)
    out.process_uuid = optional_attribute(process, 'uuid')
    out.role_name = role_name
    out.role_href = _xlink_attribute(role)
    out.service_binding = service_binding

    for reference in children(element, 'ApplicationCertificateRef'):
        cert_id = require_attribute(reference, 'certId')
        out.application_certificate_ids.append(cert_id)

    if (security_reference := optional_child(element, 'ApplicationSecurityDetailsRef')) is not None:
        out.application_security_details_id = require_attribute(security_reference, 'securityId')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _parse_certificate(element:'any_') -> 'CPACertificate':
    """ Parses a Certificate whose KeyInfo holds its chain as X509Certificate elements.
    """
    out = CPACertificate()
    out.cert_id = require_attribute(element, 'certId')
    out.chain = []

    if (key_info := element.find(_ds_key_info)) is None:
        raise CPAException('Certificate', f'Certificate `{out.cert_id}` has no ds:KeyInfo')

    for x509_data in key_info.iter(_ds_x509_data):
        for certificate_element in x509_data.iter(_ds_x509_certificate):

            text = require_text(certificate_element)

            try:
                certificate_bytes = b64decode(text, validate=False)
                certificate = load_der_x509_certificate(certificate_bytes)
            except (BinasciiError, ValueError) as e:
                raise CPAException('X509Certificate', f'Certificate `{out.cert_id}` cannot be loaded -> {e}')

            out.chain.append(certificate)

    if not out.chain:
        raise CPAException('KeyInfo', f'Certificate `{out.cert_id}` has no ds:X509Certificate')

    return out

# ################################################################################################################################

def _parse_security_details(element:'any_') -> 'SecurityDetails':

    out = SecurityDetails()
    out.security_id = require_attribute(element, 'securityId')
    out.anchor_certificate_ids = []

    if (anchors := optional_child(element, 'TrustAnchors')) is not None:
        for reference in children(anchors, 'AnchorCertificateRef'):
            cert_id = require_attribute(reference, 'certId')
            out.anchor_certificate_ids.append(cert_id)

    return out

# ################################################################################################################################

def _parse_delivery_channel(element:'any_') -> 'DeliveryChannel':

    characteristics_element = require_child(element, 'MessagingCharacteristics')

    characteristics = MessagingCharacteristics()
    characteristics.sync_reply_mode = _enumerated_attribute(
        characteristics_element, 'syncReplyMode', _sync_reply_modes, SyncReplyMode.No_Reply)
    characteristics.ack_requested = _enumerated_attribute(
        characteristics_element, 'ackRequested', _per_message_values, PerMessage.Per_Message)
    characteristics.ack_signature_requested = _enumerated_attribute(
        characteristics_element, 'ackSignatureRequested', _per_message_values, PerMessage.Per_Message)
    characteristics.duplicate_elimination = _enumerated_attribute(
        characteristics_element, 'duplicateElimination', _per_message_values, PerMessage.Per_Message)

    if actor := optional_attribute(characteristics_element, 'actor'):
        if actor not in _actors:
            raise CPAException('MessagingCharacteristics', f'Attribute `actor` has an unsupported value `{actor}`')
        characteristics.actor = actor

    out = DeliveryChannel()
    out.channel_id = require_attribute(element, 'channelId')
    out.transport_id = require_attribute(element, 'transportId')
    out.doc_exchange_id = require_attribute(element, 'docExchangeId')
    out.characteristics = characteristics

    return out

# ################################################################################################################################

def _parse_transport_security(element:'any_', certificate_name:'str', details_name:'str') -> 'TransportSecurity':

    protocol_element = require_child(element, 'TransportSecurityProtocol')

    out = TransportSecurity()
    out.protocol = _parse_protocol(protocol_element)

    if (certificate_reference := optional_child(element, certificate_name)) is not None:
        out.certificate_id = require_attribute(certificate_reference, 'certId')

    if (details_reference := optional_child(element, details_name)) is not None:
        out.security_details_id = require_attribute(details_reference, 'securityId')

    return out

# ################################################################################################################################

def _parse_transport(element:'any_') -> 'Transport':

    out = Transport()
    out.transport_id = require_attribute(element, 'transportId')

    if (sender := optional_child(element, 'TransportSender')) is not None:

        protocol_element = require_child(sender, 'TransportProtocol')
        out.sender_protocol = _parse_protocol(protocol_element)

        if (client_security := optional_child(sender, 'TransportClientSecurity')) is not None:
            out.client_security = _parse_transport_security(client_security, 'ClientCertificateRef', 'ServerSecurityDetailsRef')

    if (receiver := optional_child(element, 'TransportReceiver')) is not None:

        protocol_element = require_child(receiver, 'TransportProtocol')
        out.receiver_protocol = _parse_protocol(protocol_element)

        for endpoint_element in children(receiver, 'Endpoint'):
            endpoint = Endpoint()
            endpoint.uri = require_attribute(endpoint_element, 'uri')
            if endpoint_type := optional_attribute(endpoint_element, 'type'):
                endpoint.endpoint_type = endpoint_type
            out.endpoints.append(endpoint)

        if not out.endpoints:
            raise CPAException('TransportReceiver', f'Transport `{out.transport_id}` has no endpoint')

        if (server_security := optional_child(receiver, 'TransportServerSecurity')) is not None:
            out.server_security = _parse_transport_security(server_security, 'ServerCertificateRef', 'ClientSecurityDetailsRef')

    return out

# ################################################################################################################################

def _parse_non_repudiation(element:'any_') -> 'NonRepudiation':

    protocol_element = require_child(element, 'NonRepudiationProtocol')
    hash_function_element = require_child(element, 'HashFunction')

    out = NonRepudiation()
    out.protocol = _parse_protocol(protocol_element)
    out.hash_function = require_text(hash_function_element)
    out.signature_algorithms = []

    for algorithm_element in children(element, 'SignatureAlgorithm'):

        # The algorithm URI is in the w3c attribute or in the element's text.
        if not (algorithm := optional_attribute(algorithm_element, 'w3c')):
            algorithm = require_text(algorithm_element)

        out.signature_algorithms.append(algorithm)

    if not out.signature_algorithms:
        element_name = local_name(element)
        raise CPAException(element_name, 'Element `SignatureAlgorithm` is missing')

    if (certificate_reference := optional_child(element, 'SigningCertificateRef')) is not None:
        out.signing_certificate_id = require_attribute(certificate_reference, 'certId')

    if (details_reference := optional_child(element, 'SigningSecurityDetailsRef')) is not None:
        out.signing_security_details_id = require_attribute(details_reference, 'securityId')

    return out

# ################################################################################################################################

def _parse_doc_exchange_binding(element:'any_', non_repudiation_name:'str') -> 'DocExchangeBinding':

    out = DocExchangeBinding()
    out.version = require_attribute(element, 'version')

    if (reliable_element := optional_child(element, 'ReliableMessaging')) is not None:

        reliable = ReliableMessaging()

        if retries := optional_text(reliable_element, 'Retries'):
            if not retries.isdigit():
                raise CPAException('Retries', f'Not a non-negative integer -> `{retries}`')
            reliable.retries = int(retries)

        if (interval_element := optional_child(reliable_element, 'RetryInterval')) is not None:
            reliable.retry_interval = parse_duration(interval_element)

        order_element = require_child(reliable_element, 'MessageOrderSemantics')
        reliable.message_order = require_text(order_element)

        if reliable.message_order not in _message_order_values:
            raise CPAException('MessageOrderSemantics', f'Unsupported value `{reliable.message_order}`')

        out.reliable_messaging = reliable

    if (persist_element := optional_child(element, 'PersistDuration')) is not None:
        out.persist_duration = parse_duration(persist_element)

    if (non_repudiation_element := optional_child(element, non_repudiation_name)) is not None:
        out.non_repudiation = _parse_non_repudiation(non_repudiation_element)

    return out

# ################################################################################################################################

def _parse_doc_exchange(element:'any_') -> 'DocExchange':

    out = DocExchange()
    out.doc_exchange_id = require_attribute(element, 'docExchangeId')

    if (sender := optional_child(element, 'ebXMLSenderBinding')) is not None:
        out.sender_binding = _parse_doc_exchange_binding(sender, 'SenderNonRepudiation')

    if (receiver := optional_child(element, 'ebXMLReceiverBinding')) is not None:
        out.receiver_binding = _parse_doc_exchange_binding(receiver, 'ReceiverNonRepudiation')

    return out

# ################################################################################################################################
# ################################################################################################################################

def parse_party(element:'any_') -> 'Party':
    """ Parses one PartyInfo. The IDREFs it holds are resolved once both parties are parsed.
    """
    out = Party()
    out.party_name = require_attribute(element, 'partyName')
    out.default_msh_channel_id = require_attribute(element, 'defaultMshChannelId')
    out.default_msh_package_id = require_attribute(element, 'defaultMshPackageId')

    for party_id_element in children(element, 'PartyId'):
        value = require_text(party_id_element)
        id_type = optional_attribute(party_id_element, 'type')
        party_id = new_party_id(value, id_type)
        out.party_ids.append(party_id)

    if not out.party_ids:
        raise CPAException('PartyInfo', f'Party `{out.party_name}` has no PartyId')

    for party_ref_element in children(element, 'PartyRef'):
        party_ref = PartyRef()
        party_ref.href = _xlink_attribute(party_ref_element)
        party_ref.ref_type = optional_attribute(party_ref_element, 'type')
        party_ref.schema_location = optional_attribute(party_ref_element, 'schemaLocation')
        out.party_refs.append(party_ref)

    for role_element in children(element, 'CollaborationRole'):
        role = _parse_collaboration_role(role_element)
        out.roles.append(role)

    for certificate_element in children(element, 'Certificate'):
        certificate = _parse_certificate(certificate_element)
        out.certificates.append(certificate)

    for details_element in children(element, 'SecurityDetails'):
        details = _parse_security_details(details_element)
        out.security_details.append(details)

    for channel_element in children(element, 'DeliveryChannel'):
        channel = _parse_delivery_channel(channel_element)
        out.delivery_channels.append(channel)

    for transport_element in children(element, 'Transport'):
        transport = _parse_transport(transport_element)
        out.transports.append(transport)

    for doc_exchange_element in children(element, 'DocExchange'):
        doc_exchange = _parse_doc_exchange(doc_exchange_element)
        out.doc_exchanges.append(doc_exchange)

    for override_element in children(element, 'OverrideMshActionBinding'):
        override = OverrideMshActionBinding()
        override.action = require_attribute(override_element, 'action')
        override.channel_id = require_attribute(override_element, 'channelId')
        out.overrides.append(override)

    return out

# ################################################################################################################################
# ################################################################################################################################
