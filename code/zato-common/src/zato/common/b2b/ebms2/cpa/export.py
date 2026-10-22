# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding

# lxml
from lxml.etree import Element, SubElement, tostring

# Zato
from zato.common.b2b.ebms2.agreement import ActionBindingKind
from zato.common.b2b.ebms2.common import NS
from zato.common.b2b.ebms2.cpa.xml_ import tag
from zato.common.util.xml_.core import qname, to_timestamp

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.agreement import ActionBinding, Agreement, CollaborationRole, CPACertificate, DeliveryChannel, \
        DocExchange, DocExchangeBinding, NonRepudiation, Party, Protocol, Transport, TransportSecurity
    from zato.common.b2b.ebms2.agreement_packaging import Packaging
    from zato.common.typing_ import any_, strstrdict
    ActionBinding = ActionBinding
    Agreement = Agreement
    any_ = any_
    CollaborationRole = CollaborationRole
    CPACertificate = CPACertificate
    DeliveryChannel = DeliveryChannel
    DocExchange = DocExchange
    DocExchangeBinding = DocExchangeBinding
    NonRepudiation = NonRepudiation
    Packaging = Packaging
    Party = Party
    Protocol = Protocol
    strstrdict = strstrdict
    Transport = Transport
    TransportSecurity = TransportSecurity

# ################################################################################################################################
# ################################################################################################################################

_nsmap = {
    'tns':   NS.CPA,
    'xlink': NS.XLINK,
    'ds':    NS.DS,
}

_xlink_href = qname(NS.XLINK, 'href')
_xlink_type = qname(NS.XLINK, 'type')
_xlink_role = qname(NS.XLINK, 'role')
_xml_lang = qname(NS.XML, 'lang')

_ds_key_info = qname(NS.DS, 'KeyInfo')
_ds_x509_data = qname(NS.DS, 'X509Data')
_ds_x509_certificate = qname(NS.DS, 'X509Certificate')

# The fixed value of xlink:type in a CPP/A document.
_xlink_type_simple = 'simple'

# ################################################################################################################################
# ################################################################################################################################

def _add(parent:'any_', name:'str', text:'str'='') -> 'any_':
    """ Appends a child element of the CPP/A namespace, with the given text if there is any.
    """
    child_tag = tag(name)

    out = SubElement(parent, child_tag)

    if text:
        out.text = text

    return out

# ################################################################################################################################

def _set(element:'any_', name:'str', value:'str') -> 'None':
    """ Sets an attribute of the CPP/A namespace, unless the value is empty.
    """
    if value:
        attribute_name = tag(name)
        element.set(attribute_name, value)

# ################################################################################################################################

def _add_protocol(parent:'any_', name:'str', protocol:'Protocol') -> 'None':
    element = _add(parent, name, protocol.name)
    _set(element, 'version', protocol.version)

# ################################################################################################################################

def _add_reference(parent:'any_', name:'str', attribute:'str', value:'str') -> 'None':
    """ Appends a reference element, such as a CertificateRef, if the reference is set.
    """
    if value:
        element = _add(parent, name)
        _set(element, attribute, value)

# ################################################################################################################################
# ################################################################################################################################

def _add_action_binding(parent:'any_', binding:'ActionBinding') -> 'None':

    element = _add(parent, binding.kind)

    this_party = _add(element, 'ThisPartyActionBinding')
    _set(this_party, 'id', binding.binding_id)
    _set(this_party, 'action', binding.action)
    _set(this_party, 'packageId', binding.package_id)

    characteristics = _add(this_party, 'BusinessTransactionCharacteristics')

    for name, value in binding.characteristics.items():
        _set(characteristics, name, value)

    for channel_id in binding.channel_ids:
        _ = _add(this_party, 'ChannelId', channel_id)

    if binding.other_party_binding_id:
        _ = _add(element, 'OtherPartyActionBinding', binding.other_party_binding_id)

    for nested in binding.nested:
        _add_action_binding(element, nested)

# ################################################################################################################################

def _add_collaboration_role(parent:'any_', role:'CollaborationRole') -> 'None':

    element = _add(parent, 'CollaborationRole')

    process = _add(element, 'ProcessSpecification')
    _set(process, 'name', role.process_name)
    _set(process, 'version', role.process_version)
    process.set(_xlink_type, _xlink_type_simple)
    process.set(_xlink_href, role.process_href)
    _set(process, 'uuid', role.process_uuid)

    role_element = _add(element, 'Role')
    _set(role_element, 'name', role.role_name)
    role_element.set(_xlink_type, _xlink_type_simple)
    role_element.set(_xlink_href, role.role_href)

    for cert_id in role.application_certificate_ids:
        _add_reference(element, 'ApplicationCertificateRef', 'certId', cert_id)

    _add_reference(element, 'ApplicationSecurityDetailsRef', 'securityId', role.application_security_details_id)

    service_binding = role.service_binding
    service_binding_element = _add(element, 'ServiceBinding')
    service = _add(service_binding_element, 'Service', service_binding.service)
    _set(service, 'type', service_binding.service_type)

    # The schema has every CanSend before every CanReceive.
    for kind in (ActionBindingKind.Can_Send, ActionBindingKind.Can_Receive):
        for binding in service_binding.bindings:
            if binding.kind == kind:
                _add_action_binding(service_binding_element, binding)

# ################################################################################################################################

def _add_certificate(parent:'any_', certificate:'CPACertificate') -> 'None':

    element = _add(parent, 'Certificate')
    _set(element, 'certId', certificate.cert_id)

    key_info = SubElement(element, _ds_key_info)
    x509_data = SubElement(key_info, _ds_x509_data)

    for item in certificate.chain:
        der = item.public_bytes(Encoding.DER)
        encoded = b64encode(der)

        certificate_element = SubElement(x509_data, _ds_x509_certificate)
        certificate_element.text = encoded.decode('ascii')

# ################################################################################################################################

def _add_delivery_channel(parent:'any_', channel:'DeliveryChannel') -> 'None':

    element = _add(parent, 'DeliveryChannel')
    _set(element, 'channelId', channel.channel_id)
    _set(element, 'transportId', channel.transport_id)
    _set(element, 'docExchangeId', channel.doc_exchange_id)

    characteristics = channel.characteristics
    characteristics_element = _add(element, 'MessagingCharacteristics')
    _set(characteristics_element, 'syncReplyMode', characteristics.sync_reply_mode)
    _set(characteristics_element, 'ackRequested', characteristics.ack_requested)
    _set(characteristics_element, 'ackSignatureRequested', characteristics.ack_signature_requested)
    _set(characteristics_element, 'duplicateElimination', characteristics.duplicate_elimination)
    _set(characteristics_element, 'actor', characteristics.actor)

# ################################################################################################################################

def _add_transport_security(
    parent:'any_',
    name:'str',
    security:'TransportSecurity',
    certificate_name:'str',
    details_name:'str',
    ) -> 'None':

    element = _add(parent, name)
    _add_protocol(element, 'TransportSecurityProtocol', security.protocol)
    _add_reference(element, certificate_name, 'certId', security.certificate_id)
    _add_reference(element, details_name, 'securityId', security.security_details_id)

# ################################################################################################################################

def _add_transport(parent:'any_', transport:'Transport') -> 'None':

    element = _add(parent, 'Transport')
    _set(element, 'transportId', transport.transport_id)

    if transport.sender_protocol:

        sender = _add(element, 'TransportSender')
        _add_protocol(sender, 'TransportProtocol', transport.sender_protocol)

        if transport.client_security:
            _add_transport_security(
                sender, 'TransportClientSecurity', transport.client_security, 'ClientCertificateRef', 'ServerSecurityDetailsRef')

    if transport.receiver_protocol:

        receiver = _add(element, 'TransportReceiver')
        _add_protocol(receiver, 'TransportProtocol', transport.receiver_protocol)

        for endpoint in transport.endpoints:
            endpoint_element = _add(receiver, 'Endpoint')
            _set(endpoint_element, 'uri', endpoint.uri)
            _set(endpoint_element, 'type', endpoint.endpoint_type)

        if transport.server_security:
            _add_transport_security(
                receiver, 'TransportServerSecurity', transport.server_security, 'ServerCertificateRef', 'ClientSecurityDetailsRef')

# ################################################################################################################################

def _add_non_repudiation(parent:'any_', name:'str', non_repudiation:'NonRepudiation') -> 'None':

    element = _add(parent, name)
    _add_protocol(element, 'NonRepudiationProtocol', non_repudiation.protocol)
    _ = _add(element, 'HashFunction', non_repudiation.hash_function)

    for algorithm in non_repudiation.signature_algorithms:
        algorithm_element = _add(element, 'SignatureAlgorithm', algorithm)
        _set(algorithm_element, 'w3c', algorithm)

    _add_reference(element, 'SigningCertificateRef', 'certId', non_repudiation.signing_certificate_id)
    _add_reference(element, 'SigningSecurityDetailsRef', 'securityId', non_repudiation.signing_security_details_id)

# ################################################################################################################################

def _add_doc_exchange_binding(parent:'any_', name:'str', binding:'DocExchangeBinding', non_repudiation_name:'str') -> 'None':

    element = _add(parent, name)
    _set(element, 'version', binding.version)

    if reliable := binding.reliable_messaging:

        reliable_element = _add(element, 'ReliableMessaging')

        if reliable.retries is not None:
            retries = str(reliable.retries)
            _ = _add(reliable_element, 'Retries', retries)

        if reliable.retry_interval:
            _ = _add(reliable_element, 'RetryInterval', reliable.retry_interval.text)

        _ = _add(reliable_element, 'MessageOrderSemantics', reliable.message_order)

    if binding.persist_duration:
        _ = _add(element, 'PersistDuration', binding.persist_duration.text)

    if binding.non_repudiation:
        _add_non_repudiation(element, non_repudiation_name, binding.non_repudiation)

# ################################################################################################################################

def _add_doc_exchange(parent:'any_', doc_exchange:'DocExchange') -> 'None':

    element = _add(parent, 'DocExchange')
    _set(element, 'docExchangeId', doc_exchange.doc_exchange_id)

    if doc_exchange.sender_binding:
        _add_doc_exchange_binding(element, 'ebXMLSenderBinding', doc_exchange.sender_binding, 'SenderNonRepudiation')

    if doc_exchange.receiver_binding:
        _add_doc_exchange_binding(element, 'ebXMLReceiverBinding', doc_exchange.receiver_binding, 'ReceiverNonRepudiation')

# ################################################################################################################################

def _add_party(parent:'any_', party:'Party') -> 'None':

    element = _add(parent, 'PartyInfo')
    _set(element, 'partyName', party.party_name)
    _set(element, 'defaultMshChannelId', party.default_msh_channel_id)
    _set(element, 'defaultMshPackageId', party.default_msh_package_id)

    for party_id in party.party_ids:
        party_id_element = _add(element, 'PartyId', party_id.value)
        _set(party_id_element, 'type', party_id.id_type)

    for party_ref in party.party_refs:
        party_ref_element = _add(element, 'PartyRef')
        party_ref_element.set(_xlink_type, _xlink_type_simple)
        party_ref_element.set(_xlink_href, party_ref.href)
        _set(party_ref_element, 'type', party_ref.ref_type)
        _set(party_ref_element, 'schemaLocation', party_ref.schema_location)

    for role in party.roles:
        _add_collaboration_role(element, role)

    for certificate in party.certificates:
        _add_certificate(element, certificate)

    for details in party.security_details:
        details_element = _add(element, 'SecurityDetails')
        _set(details_element, 'securityId', details.security_id)
        if details.anchor_certificate_ids:
            anchors = _add(details_element, 'TrustAnchors')
            for cert_id in details.anchor_certificate_ids:
                _add_reference(anchors, 'AnchorCertificateRef', 'certId', cert_id)

    for channel in party.delivery_channels:
        _add_delivery_channel(element, channel)

    for transport in party.transports:
        _add_transport(element, transport)

    for doc_exchange in party.doc_exchanges:
        _add_doc_exchange(element, doc_exchange)

    for override in party.overrides:
        override_element = _add(element, 'OverrideMshActionBinding')
        _set(override_element, 'action', override.action)
        _set(override_element, 'channelId', override.channel_id)

# ################################################################################################################################

def _add_packaging(parent:'any_', packaging:'Packaging') -> 'None':

    element = _add(parent, 'Packaging')
    _set(element, 'id', packaging.packaging_id)

    capabilities = _add(element, 'ProcessingCapabilities')
    _set(capabilities, 'parse', packaging.parse)
    _set(capabilities, 'generate', packaging.generate)

    for items in packaging.composite_lists:

        composite_list = _add(element, 'CompositeList')

        for item in items:

            item_element = _add(composite_list, item.kind)
            _set(item_element, 'id', item.item_id)
            _set(item_element, 'mimetype', item.mime_type)
            _set(item_element, 'mimeparameters', item.mime_parameters)

            for constituent in item.constituents:
                constituent_element = _add(item_element, 'Constituent')
                _set(constituent_element, 'idref', constituent.idref)
                _set(constituent_element, 'excludedFromSignature', constituent.excluded_from_signature)
                _set(constituent_element, 'minOccurs', constituent.min_occurs)
                _set(constituent_element, 'maxOccurs', constituent.max_occurs)

# ################################################################################################################################
# ################################################################################################################################

def export_cpa_element(agreement:'Agreement') -> 'any_':
    """ Returns an agreement as the root element of a CPP/A 2.0 document.
    """
    root_tag = tag('CollaborationProtocolAgreement')

    out = Element(root_tag, nsmap=_nsmap)
    _set(out, 'cpaid', agreement.cpa_id)
    _set(out, 'version', agreement.version)

    status = _add(out, 'Status')
    _set(status, 'value', agreement.status)

    start = to_timestamp(agreement.start)
    end = to_timestamp(agreement.end)

    _ = _add(out, 'Start', start)
    _ = _add(out, 'End', end)

    # The conversation constraints are written only if the agreement has at least one of them.
    constraints:'strstrdict' = {}

    if agreement.invocation_limit is not None:
        constraints['invocationLimit'] = str(agreement.invocation_limit)

    if agreement.concurrent_conversations is not None:
        constraints['concurrentConversations'] = str(agreement.concurrent_conversations)

    if constraints:
        constraints_element = _add(out, 'ConversationConstraints')
        for name, value in constraints.items():
            _set(constraints_element, name, value)

    for party in agreement.parties:
        _add_party(out, party)

    for simple_part in agreement.simple_parts:
        part_element = _add(out, 'SimplePart')
        _set(part_element, 'id', simple_part.part_id)
        _set(part_element, 'mimetype', simple_part.mime_type)
        _set(part_element, 'mimeparameters', simple_part.mime_parameters)
        if simple_part.role:
            part_element.set(_xlink_role, simple_part.role)

    for packaging in agreement.packagings:
        _add_packaging(out, packaging)

    for comment in agreement.comments:
        comment_element = _add(out, 'Comment', comment.text)
        if comment.language:
            comment_element.set(_xml_lang, comment.language)

    return out

# ################################################################################################################################

def export_cpa(agreement:'Agreement') -> 'bytes':
    """ Returns an agreement as a CPP/A 2.0 document.
    """
    root = export_cpa_element(agreement)

    out = tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    return out

# ################################################################################################################################
# ################################################################################################################################
