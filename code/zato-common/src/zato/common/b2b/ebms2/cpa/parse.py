# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.ebms2.agreement import ActionBindingKind, Agreement
from zato.common.b2b.ebms2.agreement_packaging import Comment, CompositeItem, Constituent, Packaging, SimplePart
from zato.common.b2b.ebms2.common import CPAException, CPAUnsupportedException, NS
from zato.common.b2b.ebms2.cpa.parse_party import parse_party
from zato.common.b2b.ebms2.cpa.xml_ import children, local_name, optional_attribute, optional_child, require_attribute, \
    require_child, require_text, tag
from zato.common.util.xml_.core import from_timestamp, parse_xml, qname, XMLException

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.ebms2.agreement import action_binding_list, Party
    from zato.common.typing_ import any_, strset
    action_binding_list = action_binding_list
    any_ = any_
    Party = Party
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

_root_tag = tag('CollaborationProtocolAgreement')

_xlink_role = qname(NS.XLINK, 'role')
_xml_lang = qname(NS.XML, 'lang')

# The number of parties an agreement is between.
_party_count = 2

# The elements of the CPP/A namespace that are valid but outside what this implementation supports.
_unsupported_elements:'strset' = {
    'ActionContext',
    'NamespaceSupported',
    'AccessAuthentication',
    'EncryptionAlgorithm',
    'SenderDigitalEnvelope',
    'ReceiverDigitalEnvelope',
    'SignatureTransforms',
    'EncryptionTransforms',
    'SecurityPolicy',
    'Signature',
}

# The two kinds of item of a composite list.
_composite_item_kinds = ('Composite', 'Encapsulation')

# ################################################################################################################################
# ################################################################################################################################

def _reject_unsupported(root:'any_') -> 'None':
    """ Rejects a document that uses a construct this implementation has no model for, so that
    nothing the document says is silently ignored.
    """
    cpa_prefix = f'{{{NS.CPA}}}'

    for element in root.iter():

        if not isinstance(element.tag, str):
            continue

        if not element.tag.startswith(cpa_prefix):
            continue

        name = local_name(element)

        if name in _unsupported_elements:
            raise CPAUnsupportedException(name, 'Element is not supported')

        if name == 'ProcessSpecification':
            if len(element):
                raise CPAUnsupportedException(name, 'References in a process specification are not supported')

# ################################################################################################################################

def _parse_timestamp(element:'any_') -> 'any_':
    text = require_text(element)

    try:
        out = from_timestamp(text)
    except XMLException:
        name = local_name(element)
        raise CPAException(name, f'Not a timestamp -> `{text}`')

    return out

# ################################################################################################################################

def _parse_int(element:'any_', name:'str') -> 'int | None':
    """ Returns an optional xsd:int attribute.
    """
    if not (value := optional_attribute(element, name)):
        out = None
    else:
        try:
            out = int(value)
        except ValueError:
            element_name = local_name(element)
            raise CPAException(element_name, f'Attribute `{name}` is not an integer -> `{value}`')

    return out

# ################################################################################################################################

def _parse_composite_item(element:'any_', kind:'str') -> 'CompositeItem':

    out = CompositeItem()
    out.kind = kind
    out.item_id = require_attribute(element, 'id')
    out.mime_type = require_attribute(element, 'mimetype')
    out.mime_parameters = optional_attribute(element, 'mimeparameters')

    for constituent_element in children(element, 'Constituent'):
        constituent = Constituent()
        constituent.idref = require_attribute(constituent_element, 'idref')
        constituent.excluded_from_signature = optional_attribute(constituent_element, 'excludedFromSignature')
        constituent.min_occurs = optional_attribute(constituent_element, 'minOccurs')
        constituent.max_occurs = optional_attribute(constituent_element, 'maxOccurs')
        out.constituents.append(constituent)

    return out

# ################################################################################################################################

def _parse_packaging(element:'any_') -> 'Packaging':

    capabilities = require_child(element, 'ProcessingCapabilities')

    out = Packaging()
    out.packaging_id = require_attribute(element, 'id')
    out.parse = require_attribute(capabilities, 'parse')
    out.generate = require_attribute(capabilities, 'generate')

    composite_kind_tags = {}

    for kind in _composite_item_kinds:
        kind_tag = tag(kind)
        composite_kind_tags[kind_tag] = kind

    for composite_list_element in children(element, 'CompositeList'):

        items = []

        for item_element in composite_list_element:
            if kind := composite_kind_tags.get(item_element.tag):
                item = _parse_composite_item(item_element, kind)
                items.append(item)

        out.composite_lists.append(items)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _collect_binding_ids(bindings:'action_binding_list', out:'strset') -> 'None':
    for binding in bindings:
        out.add(binding.binding_id)
        _collect_binding_ids(binding.nested, out)

# ################################################################################################################################

def _require_reference(value:'str', known:'strset', element:'str', kind:'str') -> 'None':
    """ Rejects an IDREF that names nothing of the kind it is to name.
    """
    if value not in known:
        raise CPAException(element, f'IDREF `{value}` names no {kind}')

# ################################################################################################################################

def _resolve_bindings(
    party:'Party',
    bindings:'action_binding_list',
    package_ids:'strset',
    other_binding_ids:'strset',
    ) -> 'None':
    """ Resolves the channels, the packaging and the other party's binding of each action binding, at any depth.
    """
    for binding in bindings:

        _require_reference(binding.package_id, package_ids, 'ThisPartyActionBinding', 'Packaging')

        if binding.other_party_binding_id:
            _require_reference(binding.other_party_binding_id, other_binding_ids, 'OtherPartyActionBinding', 'action binding')

        for channel_id in binding.channel_ids:

            for channel in party.delivery_channels:
                if channel.channel_id == channel_id:
                    break
            else:
                raise CPAException('ChannelId', f'IDREF `{channel_id}` names no DeliveryChannel of `{party.party_name}`')

            # A channel that messages are received on is to say where they are sent to.
            if binding.kind == ActionBindingKind.Can_Receive:
                if channel.transport.receiver_protocol is None:
                    raise CPAException(
                        'Transport', f'Transport `{channel.transport_id}` of channel `{channel_id}` has no TransportReceiver')

            binding.channels.append(channel)

        _resolve_bindings(party, binding.nested, package_ids, other_binding_ids)

# ################################################################################################################################

def _resolve_party(party:'Party', other:'Party', certificate_ids:'strset', details_ids:'strset', package_ids:'strset') -> 'None':
    """ Resolves every IDREF of one party.
    """

    # Delivery channels name their transport and document exchange in the same party ..
    for channel in party.delivery_channels:

        for transport in party.transports:
            if transport.transport_id == channel.transport_id:
                channel.transport = transport
                break
        else:
            raise CPAException('DeliveryChannel', f'IDREF `{channel.transport_id}` names no Transport of `{party.party_name}`')

        for doc_exchange in party.doc_exchanges:
            if doc_exchange.doc_exchange_id == channel.doc_exchange_id:
                channel.doc_exchange = doc_exchange
                break
        else:
            raise CPAException(
                'DeliveryChannel', f'IDREF `{channel.doc_exchange_id}` names no DocExchange of `{party.party_name}`')

    # .. the message service handler defaults name a channel of the party and a packaging ..
    channel_ids:'strset' = set()

    for channel in party.delivery_channels:
        channel_ids.add(channel.channel_id)

    _require_reference(party.default_msh_channel_id, channel_ids, 'PartyInfo', 'DeliveryChannel')
    _require_reference(party.default_msh_package_id, package_ids, 'PartyInfo', 'Packaging')

    for override in party.overrides:
        _require_reference(override.channel_id, channel_ids, 'OverrideMshActionBinding', 'DeliveryChannel')

    # .. certificate and security details references name ones declared anywhere in the document ..
    for role in party.roles:
        for cert_id in role.application_certificate_ids:
            _require_reference(cert_id, certificate_ids, 'ApplicationCertificateRef', 'Certificate')
        if role.application_security_details_id:
            _require_reference(role.application_security_details_id, details_ids, 'ApplicationSecurityDetailsRef', 'SecurityDetails')

    for details in party.security_details:
        for cert_id in details.anchor_certificate_ids:
            _require_reference(cert_id, certificate_ids, 'AnchorCertificateRef', 'Certificate')

    for transport in party.transports:
        for security in (transport.client_security, transport.server_security):
            if security:
                if security.certificate_id:
                    _require_reference(security.certificate_id, certificate_ids, 'CertificateRef', 'Certificate')
                if security.security_details_id:
                    _require_reference(security.security_details_id, details_ids, 'SecurityDetailsRef', 'SecurityDetails')

    for doc_exchange in party.doc_exchanges:
        for binding in (doc_exchange.sender_binding, doc_exchange.receiver_binding):
            if binding:
                if non_repudiation := binding.non_repudiation:
                    if non_repudiation.signing_certificate_id:
                        _require_reference(
                            non_repudiation.signing_certificate_id, certificate_ids, 'SigningCertificateRef', 'Certificate')
                    if non_repudiation.signing_security_details_id:
                        _require_reference(
                            non_repudiation.signing_security_details_id, details_ids, 'SigningSecurityDetailsRef',
                            'SecurityDetails')

    # .. and action bindings name channels, packagings and the other party's bindings.
    other_binding_ids:'strset' = set()

    for role in other.roles:
        _collect_binding_ids(role.service_binding.bindings, other_binding_ids)

    for role in party.roles:
        _resolve_bindings(party, role.service_binding.bindings, package_ids, other_binding_ids)

# ################################################################################################################################

def _resolve(agreement:'Agreement') -> 'None':
    """ Resolves every IDREF of an agreement.
    """
    certificate_ids:'strset' = set()
    details_ids:'strset' = set()
    package_ids:'strset' = set()
    part_ids:'strset' = set()

    for party in agreement.parties:
        for certificate in party.certificates:
            certificate_ids.add(certificate.cert_id)
        for details in party.security_details:
            details_ids.add(details.security_id)

    for packaging in agreement.packagings:
        package_ids.add(packaging.packaging_id)

    for simple_part in agreement.simple_parts:
        part_ids.add(simple_part.part_id)

    for packaging in agreement.packagings:
        for items in packaging.composite_lists:
            for item in items:
                part_ids.add(item.item_id)

    for packaging in agreement.packagings:
        for items in packaging.composite_lists:
            for item in items:
                for constituent in item.constituents:
                    _require_reference(constituent.idref, part_ids, 'Constituent', 'SimplePart, Composite or Encapsulation')

    first, second = agreement.parties

    _resolve_party(first, second, certificate_ids, details_ids, package_ids)
    _resolve_party(second, first, certificate_ids, details_ids, package_ids)

# ################################################################################################################################
# ################################################################################################################################

def parse_cpa(data:'bytes') -> 'Agreement':
    """ Parses a CPP/A 2.0 collaboration protocol agreement, resolving every IDREF it holds.
    """
    try:
        root = parse_xml(data)
    except XMLException as e:
        raise CPAException('CollaborationProtocolAgreement', f'Document is not well-formed -> {e}')

    if root.tag != _root_tag:
        root_name = local_name(root)
        raise CPAException(root_name, 'Document is not a CPP/A 2.0 collaboration protocol agreement')

    _reject_unsupported(root)

    status = require_child(root, 'Status')
    start = require_child(root, 'Start')
    end = require_child(root, 'End')

    out = Agreement()
    out.cpa_id = require_attribute(root, 'cpaid')
    out.version = require_attribute(root, 'version')
    out.status = require_attribute(status, 'value')
    out.start = _parse_timestamp(start)
    out.end = _parse_timestamp(end)

    if (constraints := optional_child(root, 'ConversationConstraints')) is not None:
        out.invocation_limit = _parse_int(constraints, 'invocationLimit')
        out.concurrent_conversations = _parse_int(constraints, 'concurrentConversations')

    party_elements = children(root, 'PartyInfo')
    party_count = len(party_elements)

    if party_count != _party_count:
        raise CPAException('CollaborationProtocolAgreement', f'Expected {_party_count} PartyInfo elements, found {party_count}')

    for party_element in party_elements:
        party = parse_party(party_element)
        out.parties.append(party)

    for part_element in children(root, 'SimplePart'):
        simple_part = SimplePart()
        simple_part.part_id = require_attribute(part_element, 'id')
        simple_part.mime_type = require_attribute(part_element, 'mimetype')
        simple_part.mime_parameters = optional_attribute(part_element, 'mimeparameters')
        if role := part_element.get(_xlink_role):
            simple_part.role = role
        out.simple_parts.append(simple_part)

    for packaging_element in children(root, 'Packaging'):
        packaging = _parse_packaging(packaging_element)
        out.packagings.append(packaging)

    for comment_element in children(root, 'Comment'):
        comment = Comment()
        comment.text = require_text(comment_element)
        if language := comment_element.get(_xml_lang):
            comment.language = language
        out.comments.append(comment)

    _resolve(out)

    return out

# ################################################################################################################################
# ################################################################################################################################
