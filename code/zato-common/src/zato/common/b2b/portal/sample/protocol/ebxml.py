# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.config import Local_Host, Local_Organization, Local_Party_ID, Local_Role
from zato.common.b2b.portal.sample.agreements import Agreement_By_ID
from zato.common.b2b.portal.sample.common import chip, choice, code, counted, duration_value, envelope_timestamp, fields, mono, \
    number_value, size_text, tab, table, yes_no
from zato.common.b2b.portal.sample.parties import DUNS_Type, endpoint, Partner_By_Key, Partner_Role
from zato.common.b2b.portal.sample.payloads import CRLF, mime_message, parties, payload
from zato.common.b2b.portal.sample.protocol.common import channel_path, is_signature_verified, Protocol, ProtocolViews, \
    transport_label
from zato.common.b2b.portal.sample.traffic import Kind
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.portal.sample.agreements import Agreement, EbXMLSettings
    from zato.common.b2b.portal.sample.parties import Partner
    from zato.common.typing_ import anydict, anylist, strlist
    Agreement = Agreement
    EbXMLSettings = EbXMLSettings
    Partner = Partner

# ################################################################################################################################
# ################################################################################################################################

_signature_algorithm = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
_digest_algorithm    = 'http://www.w3.org/2001/04/xmlenc#sha256'

_signature_algorithms = [_signature_algorithm, 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha512']
_digest_algorithms    = [_digest_algorithm, 'http://www.w3.org/2001/04/xmlenc#sha512']

_tls_versions = ['TLS 1.2', 'TLS 1.3']

_sync_reply_modes = ['mshSignalsOnly', 'signalsOnly', 'responseOnly', 'signalsAndResponse', 'none']

_message_orders = ['Guaranteed', 'NotGuaranteed']

# ################################################################################################################################
# ################################################################################################################################

def _settings(agreement:'Agreement') -> 'EbXMLSettings':
    out = cast_('EbXMLSettings', agreement.settings)
    return out

# ################################################################################################################################

def _partner_identifiers(partner:'Partner') -> 'anylist':

    rows = [
        [mono(partner.duns), mono(DUNS_Type), mono(Partner_Role)],
        [mono(partner.host), mono('urn:pinecrest-telecom:partyid-type:host'), mono(Partner_Role)],
    ]

    out = [table('', ['PartyId', 'Type', 'Role'], rows, is_editable=True)]
    return out

# ################################################################################################################################

def _agreement_parties(agreement:'Agreement') -> 'anylist':

    partner = Partner_By_Key[agreement.partner_key]

    parties_table = table('Parties', ['Party', 'PartyId', 'Role'], [
        [Local_Organization, mono(Local_Party_ID), mono(Local_Role)],
        [partner.name, mono(partner.duns), mono(Partner_Role)],
    ], is_editable=True)

    out = [parties_table, fields('', [('PartyId type', mono(DUNS_Type))], is_editable=True)]
    return out

# ################################################################################################################################

def _reliability(agreement:'Agreement') -> 'anylist':

    settings = _settings(agreement)

    rows = [
        ('Acknowledgment', chip('Required')),
        ('Signed acknowledgment', yes_no(settings.is_signed_ack)),
        ('Duplicate elimination', chip('Required')),
        ('Retries', number_value(agreement.retries)),
        ('Retry interval', duration_value(agreement.retry_minutes, 'minutes')),
        ('Persist duration', duration_value(settings.persist_days, 'days')),
        ('SyncReplyMode', choice(settings.sync_reply, _sync_reply_modes, is_mono=True)),
        ('Message order', choice('NotGuaranteed', _message_orders, is_mono=True)),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _security(agreement:'Agreement') -> 'anylist':

    name = agreement.partner_key

    rows = [
        ('Signature', chip('Signed')),
        ('Signature algorithm', choice(_signature_algorithm, _signature_algorithms, is_mono=True)),
        ('Digest algorithm', choice(_digest_algorithm, _digest_algorithms, is_mono=True)),
        ('Non-repudiation', chip('Required')),
        ('TLS', choice(agreement.tls_version, _tls_versions)),
        ('Client authentication', chip('Required')),
        ('Partner signing certificate', mono(f'{name}-signing-2026')),
        ('Partner TLS certificate', mono(f'{name}-tls-2026')),
        ('Local signing certificate', mono('pinecrest-signing-2026')),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _agreement_tabs(agreement:'Agreement') -> 'anylist':

    out = [
        tab('reliability', 'Reliability', _reliability(agreement)),
        tab('security', 'Security', _security(agreement)),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################

def envelope(message:'anydict') -> 'str':
    """ The SOAP envelope of a message, with its ebXML message header and, when it has one, its manifest.
    """
    from_id, from_role, to_id, to_role = parties(message)
    stamp = envelope_timestamp(message['moment'])
    kind = message['kind']

    lines:'strlist' = [
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"',
        '    xmlns:eb="http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd">',
        '  <soap:Header>',
        '    <eb:MessageHeader eb:version="2.0" soap:mustUnderstand="1">',
        '      <eb:From>',
        f'        <eb:PartyId eb:type="{DUNS_Type}">{from_id}</eb:PartyId>',
        f'        <eb:Role>{from_role}</eb:Role>',
        '      </eb:From>',
        '      <eb:To>',
        f'        <eb:PartyId eb:type="{DUNS_Type}">{to_id}</eb:PartyId>',
        f'        <eb:Role>{to_role}</eb:Role>',
        '      </eb:To>',
        f'      <eb:CPAId>{message["agreement_id"]}</eb:CPAId>',
        f'      <eb:ConversationId>{message["conversation_id"]}</eb:ConversationId>',
        f'      <eb:Service eb:type="string">{message["service"]}</eb:Service>',
        f'      <eb:Action>{message["action"]}</eb:Action>',
        '      <eb:MessageData>',
        f'        <eb:MessageId>{message["id"]}</eb:MessageId>',
        f'        <eb:Timestamp>{stamp}</eb:Timestamp>',
    ]

    if message['ref_to']:
        lines.append(f'        <eb:RefToMessageId>{message["ref_to"]}</eb:RefToMessageId>')

    lines.append('      </eb:MessageData>')

    if kind == Kind.Ack:
        lines.append('    </eb:MessageHeader>')
        lines.append('    <eb:Acknowledgment eb:version="2.0" soap:mustUnderstand="1">')
        lines.append(f'      <eb:Timestamp>{stamp}</eb:Timestamp>')
        lines.append(f'      <eb:RefToMessageId>{message["ref_to"]}</eb:RefToMessageId>')
        lines.append('    </eb:Acknowledgment>')

    elif kind == Kind.Error:
        lines.append('    </eb:MessageHeader>')
        lines.append('    <eb:ErrorList eb:version="2.0" eb:highestSeverity="Error" soap:mustUnderstand="1">')
        lines.append(f'      <eb:Error eb:errorCode="{message["error_code"]}" eb:severity="Error">')
        lines.append(f'        <eb:Description xml:lang="en-US">{message["error"]}</eb:Description>')
        lines.append('      </eb:Error>')
        lines.append('    </eb:ErrorList>')

    else:
        lines.append('      <eb:DuplicateElimination/>')
        lines.append('    </eb:MessageHeader>')
        lines.append('    <eb:AckRequested eb:version="2.0" eb:signed="true" soap:mustUnderstand="1"/>')

    lines.append('  </soap:Header>')

    if kind in (Kind.Ack, Kind.Error):
        lines.append('  <soap:Body/>')
    else:
        lines.append('  <soap:Body>')
        lines.append('    <eb:Manifest eb:version="2.0">')
        lines.append('      <eb:Reference xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="cid:payload-1"/>')
        lines.append('    </eb:Manifest>')
        lines.append('  </soap:Body>')

    lines.append('</soap:Envelope>')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def raw_message(message:'anydict') -> 'str':
    """ The HTTP request of a message as it went over the wire - the request line, the HTTP headers and the MIME parts
    of the SOAP envelope and of the payload, if the message has one.
    """
    partner = Partner_By_Key[message['partner_key']]

    # An inbound message was posted to the local endpoint, an outbound one to the partner's
    if message['direction'] == 'Inbound':
        host, party_id = Local_Host, Local_Party_ID
    else:
        host, party_id = partner.host, partner.duns

    boundary = f'MIMEBoundary_{message["key"]}_{party_id}'
    header_id = f'ebxml-header-{message["key"]}@{host}'

    parts = [(header_id, 'text/xml; charset=UTF-8', envelope(message))]

    if body := payload(message):
        parts.append(('payload-1', 'application/xml; charset=UTF-8', body))

    content = mime_message(parts, boundary)
    content_length = len(content.encode('utf8'))
    path = channel_path(Protocol.ebXML, party_id)

    head = [
        f'POST {path} HTTP/1.1',
        f'Host: {host}',
        f'Content-Type: multipart/related; type="text/xml"; boundary="{boundary}"; start="<{header_id}>"',
        'SOAPAction: "ebXML"',
        f'Content-Length: {content_length}',
        '',
        '',
    ]

    out = CRLF.join(head) + content
    return out

# ################################################################################################################################

def _envelope(message:'anydict') -> 'anylist':

    agreement = Agreement_By_ID[message['agreement_id']]
    settings = _settings(agreement)
    from_id, from_role, to_id, to_role = parties(message)

    is_messaging = message['kind'] in (Kind.Ack, Kind.Error)

    header = fields('Message header', [
        ('From PartyId', mono(from_id)),
        ('From role', mono(from_role)),
        ('To PartyId', mono(to_id)),
        ('To role', mono(to_role)),
        ('PartyId type', mono(DUNS_Type)),
        ('Service type', mono('string')),
        ('Timestamp', mono(envelope_timestamp(message['moment']))),
    ])

    reliability = fields('Reliable messaging', [
        ('AckRequested', yes_no(not is_messaging)),
        ('Signed acknowledgment', yes_no(settings.is_signed_ack)),
        ('DuplicateElimination', yes_no(not is_messaging)),
        ('SyncReplyMode', mono(settings.sync_reply)),
    ])

    out = [header, reliability]
    return out

# ################################################################################################################################

def _parts(message:'anydict', body:'str') -> 'anylist':

    header = envelope(message)
    header_size = len(header.encode('utf8'))

    parts = [['ebXML_Message_Header', 'text/xml', size_text(header_size)]]

    if body:
        body_size = len(body.encode('utf8'))
        parts.append(['payload-1', 'application/xml', size_text(body_size)])

    out = [table('', ['Content-ID', 'Content-Type', 'Size'], parts)]
    return out

# ################################################################################################################################

def _transport(message:'anydict') -> 'anylist':

    partner = Partner_By_Key[message['partner_key']]
    agreement = Agreement_By_ID[message['agreement_id']]

    if message['direction'] == 'Outbound':
        retries = counted(agreement.retries, 'retry', 'retries')
        interval = counted(agreement.retry_minutes, 'minute', 'minutes')

        out = [fields('', [
            ('Endpoint', mono(endpoint(partner))),
            ('TLS', agreement.tls_version),
            ('SOAPAction', mono('"ebXML"')),
            ('Retries', f'{retries} every {interval}'),
        ])]

    else:
        signature = 'Verified' if is_signature_verified(message) else 'Not verified'

        out = [fields('', [
            ('Channel', mono(channel_path(Protocol.ebXML, Local_Party_ID))),
            ('TLS', agreement.tls_version),
            ('Client certificate', mono(f'CN={partner.host}, O={partner.name}')),
            ('Signature', chip(signature)),
            ('Received by', Local_Organization),
        ])]

    return out

# ################################################################################################################################

def _message_details(message:'anydict', body:'str') -> 'anylist':

    out = [
        tab('envelope', 'Envelope', _envelope(message)),
        tab('soap', 'SOAP envelope', [code('', envelope(message))]),
        tab('parts', 'MIME parts', _parts(message, body)),
        tab('transport', transport_label(message), _transport(message)),
        tab('raw', 'Raw message', [code('', raw_message(message))]),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################

Views = ProtocolViews(
    partner_identifiers=_partner_identifiers,
    certificate_usages=['Signing', 'TLS client'],
    agreement_parties=_agreement_parties,
    agreement_tabs=_agreement_tabs,
    message_details=_message_details,
)

# ################################################################################################################################
# ################################################################################################################################
