# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.b2b.portal.config import Local_Host, Local_Organization, Local_Party_ID, Local_Role
from zato.common.b2b.portal.sample.common import days_from_now
from zato.common.b2b.portal.sample.parties import DUNS_Type, duration, Partner_By_Key, Partner_Role, Service_By_Name
from zato.common.b2b.portal.sample.protocol.common import channel_path, opaque_text, Protocol
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.portal.sample.agreements import Agreement, EbXMLSettings
    from zato.common.b2b.portal.sample.parties import Service
    from zato.common.typing_ import strlist
    Agreement = Agreement
    EbXMLSettings = EbXMLSettings
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

_namespaces = [
    'xmlns:tp="http://www.oasis-open.org/committees/ebxml-cppa/schema/cpp-cpa-2_0.xsd"',
    'xmlns:xlink="http://www.w3.org/1999/xlink"',
    'xmlns:ds="http://www.w3.org/2000/09/xmldsig#"',
]

# The status of a CPA by the state of its agreement, a CPA in use is one both parties have signed
_status_by_state = {
    'Proposed':  'proposed',
    'Agreed':    'agreed',
    'Active':    'signed',
    'Expiring':  'signed',
    'Suspended': 'signed',
}

_package_id = 'package-ebxml'
_process_version = '1.5.0'

_non_repudiation_protocol = 'http://www.w3.org/2000/09/xmldsig#'
_hash_function = 'http://www.w3.org/2001/04/xmlenc#sha256'
_signature_algorithm = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'

# How many bytes of opaque content stand in for the DER form of a certificate
_certificate_size = 96

# ################################################################################################################################
# ################################################################################################################################

class _Party(NamedTuple):
    name: str
    party_id: str
    role: str
    host: str
    prefix: str
    is_local: bool

# ################################################################################################################################
# ################################################################################################################################

def _limits(service:'Service') -> 'str':
    """ The time limits of a business transaction, of which a CPA names only those the transaction has.
    """
    out = ''

    if service.receipt_seconds:
        out += f' tp:timeToAcknowledgeReceipt="{duration(service.receipt_seconds)}"'

    if service.acceptance_seconds:
        out += f' tp:timeToAcknowledgeAcceptance="{duration(service.acceptance_seconds)}"'

    if service.perform_seconds:
        out += f' tp:timeToPerform="{duration(service.perform_seconds)}"'

    return out

# ################################################################################################################################

def _action_binding(lines:'strlist', party:'_Party', element:'str', action:'str', limits:'str') -> 'None':

    characteristics = '                tp:isAuthenticated="persistent" tp:isTamperProof="persistent" tp:isAuthorizationRequired="true"'

    lines.extend([
        f'        <tp:{element}>',
        f'          <tp:ThisPartyActionBinding tp:id="{party.prefix}-{action}" tp:action="{action}"',
        f'              tp:packageId="{_package_id}">',
        '            <tp:BusinessTransactionCharacteristics tp:isNonRepudiationRequired="true"',
        '                tp:isNonRepudiationReceiptRequired="true" tp:isConfidential="transient"',
    ])

    if limits:
        lines.append(characteristics)
        lines.append(f'               {limits}/>')
    else:
        lines.append(characteristics + '/>')

    lines.extend([
        f'            <tp:ChannelId>{party.prefix}-channel</tp:ChannelId>',
        '          </tp:ThisPartyActionBinding>',
        f'        </tp:{element}>',
    ])

# ################################################################################################################################

def _service_binding(lines:'strlist', party:'_Party', service:'Service') -> 'None':

    # .. the local organization sends the notifications and receives the requests, the partner does the opposite ..
    sends_request = party.is_local == service.is_notification

    request_element = 'CanSend' if sends_request else 'CanReceive'
    response_element = 'CanReceive' if sends_request else 'CanSend'

    lines.append('      <tp:ServiceBinding>')
    lines.append(f'        <tp:Service tp:type="string">{service.name}</tp:Service>')

    _action_binding(lines, party, request_element, service.request, _limits(service))

    if service.response:
        _action_binding(lines, party, response_element, service.response, '')

    lines.append('      </tp:ServiceBinding>')

# ################################################################################################################################

def _certificates(lines:'strlist', party:'_Party') -> 'None':

    for usage in ('signing', 'tls'):
        cert_id = f'{party.prefix}-{usage}-2026'
        lines.extend([
            f'    <tp:Certificate tp:certId="{cert_id}">',
            '      <ds:KeyInfo>',
            f'        <ds:KeyName>{cert_id}</ds:KeyName>',
            '        <ds:X509Data>',
            f'          <ds:X509Certificate>{opaque_text(cert_id, _certificate_size)}</ds:X509Certificate>',
            '        </ds:X509Data>',
            '      </ds:KeyInfo>',
            '    </tp:Certificate>',
        ])

# ################################################################################################################################

def _delivery(lines:'strlist', party:'_Party', agreement:'Agreement') -> 'None':

    settings = cast_('EbXMLSettings', agreement.settings)
    prefix = party.prefix

    ack_signature = 'always' if settings.is_signed_ack else 'never'
    tls_version = agreement.tls_version.split(' ')[1]
    address = 'https://' + party.host + channel_path(Protocol.ebXML, party.party_id)

    lines.extend([
        f'    <tp:SecurityDetails tp:securityId="{prefix}-security">',
        '      <tp:TrustAnchors>',
        f'        <tp:AnchorCertificateRef tp:certId="{prefix}-signing-2026"/>',
        '      </tp:TrustAnchors>',
        '    </tp:SecurityDetails>',
        f'    <tp:DeliveryChannel tp:channelId="{prefix}-channel" tp:transportId="{prefix}-transport"',
        f'        tp:docExchangeId="{prefix}-docexchange">',
        f'      <tp:MessagingCharacteristics tp:syncReplyMode="{settings.sync_reply}" tp:ackRequested="always"',
        f'          tp:ackSignatureRequested="{ack_signature}" tp:duplicateElimination="always"/>',
        '    </tp:DeliveryChannel>',
        f'    <tp:Transport tp:transportId="{prefix}-transport">',
        '      <tp:TransportSender>',
        '        <tp:TransportProtocol tp:version="1.1">HTTP</tp:TransportProtocol>',
        '        <tp:TransportClientSecurity>',
        f'          <tp:TransportSecurityProtocol tp:version="{tls_version}">TLS</tp:TransportSecurityProtocol>',
        f'          <tp:ClientCertificateRef tp:certId="{prefix}-tls-2026"/>',
        '        </tp:TransportClientSecurity>',
        '      </tp:TransportSender>',
        '      <tp:TransportReceiver>',
        '        <tp:TransportProtocol tp:version="1.1">HTTP</tp:TransportProtocol>',
        f'        <tp:Endpoint tp:uri="{address}" tp:type="allPurpose"/>',
        '        <tp:TransportServerSecurity>',
        f'          <tp:TransportSecurityProtocol tp:version="{tls_version}">TLS</tp:TransportSecurityProtocol>',
        f'          <tp:ServerCertificateRef tp:certId="{prefix}-tls-2026"/>',
        '        </tp:TransportServerSecurity>',
        '      </tp:TransportReceiver>',
        '    </tp:Transport>',
        f'    <tp:DocExchange tp:docExchangeId="{prefix}-docexchange">',
    ])

    for binding, non_repudiation in (('Sender', 'SenderNonRepudiation'), ('Receiver', 'ReceiverNonRepudiation')):
        lines.extend([
            f'      <tp:ebXML{binding}Binding tp:version="2.0">',
            '        <tp:ReliableMessaging>',
            f'          <tp:Retries>{agreement.retries}</tp:Retries>',
            f'          <tp:RetryInterval>PT{agreement.retry_minutes}M</tp:RetryInterval>',
            '          <tp:MessageOrderSemantics>NotGuaranteed</tp:MessageOrderSemantics>',
            '        </tp:ReliableMessaging>',
            f'        <tp:PersistDuration>P{settings.persist_days}D</tp:PersistDuration>',
            f'        <tp:{non_repudiation}>',
            f'          <tp:NonRepudiationProtocol>{_non_repudiation_protocol}</tp:NonRepudiationProtocol>',
            f'          <tp:HashFunction>{_hash_function}</tp:HashFunction>',
            f'          <tp:SignatureAlgorithm>{_signature_algorithm}</tp:SignatureAlgorithm>',
        ])

        # .. a sender names the certificate it signs with, a receiver the trust anchors it verifies signatures against ..
        if binding == 'Sender':
            lines.append(f'          <tp:SigningCertificateRef tp:certId="{prefix}-signing-2026"/>')
        else:
            lines.append(f'          <tp:SigningSecurityDetailsRef tp:securityId="{prefix}-security"/>')

        lines.append(f'        </tp:{non_repudiation}>')
        lines.append(f'      </tp:ebXML{binding}Binding>')

    lines.append('    </tp:DocExchange>')

# ################################################################################################################################

def _party_info(lines:'strlist', party:'_Party', agreement:'Agreement') -> 'None':

    process = 'urn:pinecrest-telecom:b2b:process:' + agreement.product.lower()

    lines.extend([
        f'  <tp:PartyInfo tp:partyName="{party.name}" tp:defaultMshChannelId="{party.prefix}-channel"',
        f'      tp:defaultMshPackageId="{_package_id}">',
        f'    <tp:PartyId tp:type="{DUNS_Type}">{party.party_id}</tp:PartyId>',
        f'    <tp:PartyRef xlink:type="simple" xlink:href="https://{party.host}/"/>',
        '    <tp:CollaborationRole>',
        f'      <tp:ProcessSpecification tp:version="{_process_version}" tp:name="{agreement.product}"',
        f'          xlink:type="simple" xlink:href="{process}"/>',
        f'      <tp:Role tp:name="{party.role}" xlink:type="simple" xlink:href="{process}#{party.role}"/>',
        f'      <tp:ApplicationCertificateRef tp:certId="{party.prefix}-signing-2026"/>',
    ])

    for name in agreement.services:
        service = Service_By_Name[name]
        _service_binding(lines, party, service)

    lines.append('    </tp:CollaborationRole>')

    _certificates(lines, party)
    _delivery(lines, party, agreement)

    lines.append('  </tp:PartyInfo>')

# ################################################################################################################################
# ################################################################################################################################

def cpa_document(agreement:'Agreement') -> 'str':
    """ The CPA of an ebXML agreement, an XML document of the OASIS ebXML CPPA 2.0 schema with the party information
    of both parties and the packaging of the messages they exchange.
    """
    partner = Partner_By_Key[agreement.partner_key]

    local = _Party(Local_Organization, Local_Party_ID, Local_Role, Local_Host, 'pinecrest', True)
    remote = _Party(partner.name, partner.duns, Partner_Role, partner.host, partner.key, False)

    start = days_from_now(agreement.start_days)
    end = days_from_now(agreement.end_days)
    status = _status_by_state[agreement.state]

    lines:'strlist' = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<tp:CollaborationProtocolAgreement {_namespaces[0]}',
        f'    {_namespaces[1]}',
        f'    {_namespaces[2]}',
        f'    tp:cpaid="{agreement.agreement_id}" tp:version="2_0b">',
        f'  <tp:Status tp:value="{status}"/>',
        f'  <tp:Start>{start}T00:00:00Z</tp:Start>',
        f'  <tp:End>{end}T00:00:00Z</tp:End>',
    ]

    _party_info(lines, local, agreement)
    _party_info(lines, remote, agreement)

    lines.extend([
        '  <tp:SimplePart tp:id="part-header" tp:mimetype="text/xml"/>',
        '  <tp:SimplePart tp:id="part-payload" tp:mimetype="application/xml"/>',
        f'  <tp:Packaging tp:id="{_package_id}">',
        '    <tp:ProcessingCapabilities tp:parse="true" tp:generate="true"/>',
        '    <tp:CompositeList>',
        '      <tp:Composite tp:id="composite-message" tp:mimetype="multipart/related" tp:mimeparameters="type=text/xml">',
        '        <tp:Constituent tp:idref="part-header"/>',
        '        <tp:Constituent tp:idref="part-payload"/>',
        '      </tp:Composite>',
        '    </tp:CompositeList>',
        '  </tp:Packaging>',
        '</tp:CollaborationProtocolAgreement>',
    ])

    out = '\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################
