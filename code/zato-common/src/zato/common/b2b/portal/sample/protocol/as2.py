# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.config import Local_AS2_ID, Local_Host, Local_Organization, Local_Party_ID
from zato.common.b2b.portal.sample.agreements import Agreement_By_ID, AS2MDNMode
from zato.common.b2b.portal.sample.common import chip, choice, code, counted, duration_value, fields, href, mono, \
    number_value, Path_Messages, size_text, tab, table, typed, yes_no
from zato.common.b2b.portal.sample.parties import as2_id, endpoint, Partner_By_Key
from zato.common.b2b.portal.sample.payloads import answered, CRLF, payload
from zato.common.b2b.portal.sample.protocol.common import base64_lines, channel_path, digest, is_signature_verified, \
    opaque_bytes, Protocol, ProtocolViews, transport_label
from zato.common.b2b.portal.sample.traffic import Kind
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.portal.sample.agreements import Agreement, AS2Settings
    from zato.common.b2b.portal.sample.parties import Partner
    from zato.common.typing_ import anydict, anylist, strlist, strtuple
    Agreement = Agreement
    AS2Settings = AS2Settings
    Partner = Partner

# ################################################################################################################################
# ################################################################################################################################

_sign_algorithms       = ['SHA-256', 'SHA-384', 'SHA-512', 'SHA-1']
_encryption_algorithms = ['AES-128-CBC', 'AES-256-CBC', 'AES-128-GCM', 'AES-256-GCM', '3DES-CBC']
_mdn_modes             = [AS2MDNMode.Sync, AS2MDNMode.Async, AS2MDNMode.Not_Requested]
_content_types         = ['application/xml', 'application/edi-x12', 'application/edifact', 'application/octet-stream']
_transfer_encodings    = ['base64', 'binary']
_transfer_modes        = ['Content-Length', 'Chunked']
_as2_versions          = ['1.2', '1.1', '1.3']
_tls_versions          = ['TLS 1.2', 'TLS 1.3']

_as2_version = '1.2'

# The micalg names of RFC 5751 by the digest algorithms they stand for
_micalg = {
    'SHA-256': 'sha-256',
    'SHA-384': 'sha-384',
    'SHA-512': 'sha-512',
    'SHA-1':   'sha1',
}

# The path asynchronous MDNs are delivered to
_mdn_path = '/as2/mdn'

_enveloped_type  = 'application/pkcs7-mime; smime-type=enveloped-data'
_compressed_type = 'application/pkcs7-mime; smime-type=compressed-data'
_signature_type  = 'application/pkcs7-signature'
_report_type     = 'multipart/report; report-type=disposition-notification'
_notice_type     = 'message/disposition-notification'

_processed = 'automatic-action/MDN-sent-automatically; processed'

# What the S/MIME layers add to the size of what they enclose, in bytes, and how much compression keeps, in percent
_signature_size      = 1864
_mime_header_size    = 236
_encryption_overhead = 412
_compressed_percent  = 42

# The cipher of the enveloped data works in blocks of this many bytes
_cipher_block_size = 16

# ################################################################################################################################
# ################################################################################################################################

def _settings(agreement:'Agreement') -> 'AS2Settings':
    out = cast_('AS2Settings', agreement.settings)
    return out

# ################################################################################################################################

def _partner_identifiers(partner:'Partner') -> 'anylist':

    rows = [
        ('AS2 identifier', mono(as2_id(partner))),
        ('Local AS2 identifier', mono(Local_AS2_ID)),
        ('DUNS', mono(partner.duns)),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _agreement_parties(agreement:'Agreement') -> 'anylist':

    partner = Partner_By_Key[agreement.partner_key]

    out = [table('Parties', ['Party', 'AS2 identifier', 'DUNS'], [
        [Local_Organization, mono(Local_AS2_ID), mono(Local_Party_ID)],
        [partner.name, mono(as2_id(partner)), mono(partner.duns)],
    ], is_editable=True)]
    return out

# ################################################################################################################################

def _security(agreement:'Agreement') -> 'anylist':

    settings = _settings(agreement)
    name = agreement.partner_key

    rows = [
        ('Signature', chip('Signed')),
        ('Signature algorithm', choice(settings.sign_algorithm, _sign_algorithms)),
        ('Encryption algorithm', choice(settings.encryption_algorithm, _encryption_algorithms)),
        ('Compression', yes_no(settings.is_compressed)),
    ]

    if settings.is_compressed:
        rows.append(('Compress before signing', yes_no(True)))

    rows.append(('TLS', choice(agreement.tls_version, _tls_versions)))
    rows.append(('Partner certificate', mono(f'{name}-signing-2026')))
    rows.append(('Partner TLS certificate', mono(f'{name}-tls-2026')))
    rows.append(('Local signing certificate', mono('pinecrest-signing-2026')))
    rows.append(('Local decryption certificate', mono('pinecrest-decryption-2026')))

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _mdn(agreement:'Agreement') -> 'anylist':

    settings = _settings(agreement)

    rows = [
        ('MDN', choice(settings.mdn_mode, _mdn_modes)),
        ('Signed MDN', yes_no(settings.is_mdn_signed)),
        ('MIC algorithm', mono(_micalg[settings.sign_algorithm])),
    ]

    if settings.mdn_mode == AS2MDNMode.Async:
        rows.append(('Receipt-Delivery-Option', typed(f'https://{Local_Host}{_mdn_path}', 'url', is_mono=True)))

    rows.append(('MDN overdue after', duration_value(settings.mdn_overdue_minutes, 'minutes')))

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _delivery(agreement:'Agreement') -> 'anylist':

    rows = [
        ('AS2 version', choice(_as2_version, _as2_versions)),
        ('Content-Type', choice(_content_types[0], _content_types, is_mono=True)),
        ('Content-Transfer-Encoding', choice(_transfer_encodings[0], _transfer_encodings, is_mono=True)),
        ('HTTP transfer mode', choice(_transfer_modes[0], _transfer_modes)),
        ('Duplicate detection', chip('Required')),
        ('Retries', number_value(agreement.retries)),
        ('Retry interval', duration_value(agreement.retry_minutes, 'minutes')),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _agreement_tabs(agreement:'Agreement') -> 'anylist':

    out = [
        tab('security', 'Security', _security(agreement)),
        tab('mdn', 'MDN', _mdn(agreement)),
        tab('delivery', 'Delivery', _delivery(agreement)),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################

def _is_mdn(message:'anydict') -> 'bool':
    out = message['kind'] in (Kind.Ack, Kind.Error)
    return out

# ################################################################################################################################

def _identifiers(message:'anydict') -> 'strtuple':
    """ The AS2-From and the AS2-To of a message.
    """
    partner = Partner_By_Key[message['partner_key']]
    partner_id = as2_id(partner)

    if message['direction'] == 'Inbound':
        out = (partner_id, Local_AS2_ID)
    else:
        out = (Local_AS2_ID, partner_id)

    return out

# ################################################################################################################################

def _hosts(message:'anydict') -> 'strtuple':
    """ The host of the sender and the host of the receiver of a message.
    """
    partner = Partner_By_Key[message['partner_key']]

    if message['direction'] == 'Inbound':
        out = (partner.host, Local_Host)
    else:
        out = (Local_Host, partner.host)

    return out

# ################################################################################################################################

def _date(message:'anydict') -> 'str':
    out = message['moment'].strftime('%a, %d %b %Y %H:%M:%S +0000')
    return out

# ################################################################################################################################

def _mic(message:'anydict', settings:'AS2Settings') -> 'str':
    """ The Received-Content-MIC of an MDN, the digest of the payload of the message it answers.
    """
    original = answered(message)
    body = payload(original)
    value = digest(body)
    algorithm = _micalg[settings.sign_algorithm]

    out = f'{value}, {algorithm}'
    return out

# ################################################################################################################################

def _disposition(message:'anydict') -> 'str':

    if message['kind'] == Kind.Error:
        out = f'{_processed}/error: {message["error_code"]}'
    else:
        out = _processed

    return out

# ################################################################################################################################

def _signed_type(settings:'AS2Settings') -> 'str':
    algorithm = _micalg[settings.sign_algorithm]

    out = f'multipart/signed; protocol="{_signature_type}"; micalg={algorithm}'
    return out

# ################################################################################################################################

def _mdn_content_type(settings:'AS2Settings') -> 'str':

    if settings.is_mdn_signed:
        out = _signed_type(settings)
    else:
        out = _report_type

    return out

# ################################################################################################################################

def _as2_headers(message:'anydict') -> 'anylist':
    """ The AS2 headers every message and every MDN has, as pairs of a name and a value.
    """
    as2_from, as2_to = _identifiers(message)

    out = [
        ('AS2-Version', _as2_version),
        ('AS2-From', as2_from),
        ('AS2-To', as2_to),
        ('Message-ID', f'<{message["id"]}>'),
        ('Date', _date(message)),
    ]

    if not _is_mdn(message):
        out.append(('Subject', f'{message["action"]} {message["reference"]}'))

    return out

# ################################################################################################################################

def _mdn_request(message:'anydict', settings:'AS2Settings') -> 'anylist':
    """ The headers with which a message asks for its MDN, as pairs of a name and a value.
    """
    sender_host, _ = _hosts(message)
    algorithm = _micalg[settings.sign_algorithm]
    out:'anylist' = []

    if settings.mdn_mode != AS2MDNMode.Not_Requested:
        out.append(('Disposition-Notification-To', f'as2@{sender_host}'))

        if settings.is_mdn_signed:
            options = f'signed-receipt-protocol=optional, pkcs7-signature; signed-receipt-micalg=optional, {algorithm}'
            out.append(('Disposition-Notification-Options', options))

    if settings.mdn_mode == AS2MDNMode.Async:
        out.append(('Receipt-Delivery-Option', f'https://{sender_host}{_mdn_path}'))

    return out

# ################################################################################################################################
# ################################################################################################################################

def _notification(message:'anydict', settings:'AS2Settings') -> 'str':
    """ The message/disposition-notification part of an MDN.
    """
    partner = Partner_By_Key[message['partner_key']]
    mdn_from, _ = _identifiers(message)

    if message['direction'] == 'Outbound':
        reporting_ua = f'{Local_Organization} B2B Gateway'
    else:
        reporting_ua = f'{partner.name} AS2 Gateway'

    lines:'strlist' = [
        f'Reporting-UA: {reporting_ua}',
        f'Original-Recipient: rfc822; {mdn_from}',
        f'Final-Recipient: rfc822; {mdn_from}',
        f'Original-Message-ID: <{message["ref_to"]}>',
        f'Disposition: {_disposition(message)}',
    ]

    if message['kind'] == Kind.Ack:
        lines.append(f'Received-Content-MIC: {_mic(message, settings)}')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def _mdn_layers(message:'anydict', settings:'AS2Settings') -> 'anylist':
    """ The MIME structure of an MDN from the outermost layer in, each layer with its Content-Type and its size.
    """
    notification = _notification(message, settings)
    notification_size = len(notification) + _mime_header_size
    report_size = notification_size + _mime_header_size * 2

    out:'anylist' = []

    if settings.is_mdn_signed:
        out.append(['Signed', _signed_type(settings), report_size + _signature_size])

    out.append(['Report', _report_type, report_size])
    out.append(['Text', 'text/plain', _mime_header_size])
    out.append(['Disposition notification', _notice_type, notification_size])

    if settings.is_mdn_signed:
        out.append(['Signature', _signature_type, _signature_size])

    return out

# ################################################################################################################################

def _message_layers(body:'str', settings:'AS2Settings') -> 'anylist':
    """ The MIME structure of a message from the outermost layer in - the enveloped data, the signed data
    with the compressed data in it if the message is compressed, the payload and the signature.
    """
    payload_size = len(body.encode('utf8'))

    if settings.is_compressed:
        compressed_size = payload_size * _compressed_percent // 100 + _mime_header_size
        signed_size = compressed_size + _signature_size + _mime_header_size
    else:
        compressed_size = 0
        signed_size = payload_size + _signature_size + _mime_header_size

    encrypted_size = signed_size + _encryption_overhead
    encrypted_size += -encrypted_size % _cipher_block_size

    out:'anylist' = [
        ['Encrypted', f'{_enveloped_type}; {settings.encryption_algorithm}', encrypted_size],
        ['Signed', _signed_type(settings), signed_size],
    ]

    if settings.is_compressed:
        out.append(['Compressed', _compressed_type, compressed_size])

    out.append(['Payload', 'application/xml', payload_size])
    out.append(['Signature', _signature_type, _signature_size])

    return out

# ################################################################################################################################

def _headers(message:'anydict', settings:'AS2Settings') -> 'anylist':

    rows:'anylist' = []

    for name, value in _as2_headers(message):
        rows.append((name, mono(value)))

    if _is_mdn(message):
        original = answered(message)

        disposition = [
            ('Original-Message-ID', mono(f'<{message["ref_to"]}>', href=href(Path_Messages, original['key']))),
            ('Disposition', mono(_disposition(message))),
        ]

        if message['kind'] == Kind.Ack:
            disposition.append(('Received-Content-MIC', mono(_mic(message, settings))))

        rows.append(('Content-Type', mono(_mdn_content_type(settings))))
        out = [fields('', rows), fields('Disposition', disposition)]

    else:
        for name, value in _mdn_request(message, settings):
            rows.append((name, mono(value)))

        rows.append(('Content-Type', mono(_enveloped_type)))
        out = [fields('', rows)]

    return out

# ################################################################################################################################

def _smime(message:'anydict', settings:'AS2Settings') -> 'anylist':

    if _is_mdn(message):
        rows:'anylist' = [
            ('Signature', chip('Signed' if settings.is_mdn_signed else 'Unsigned')),
            ('MIC algorithm', mono(_micalg[settings.sign_algorithm])),
        ]
    else:
        rows = [
            ('Signature', chip('Signed')),
            ('Signature algorithm', settings.sign_algorithm),
            ('Encryption algorithm', settings.encryption_algorithm),
            ('Compression', yes_no(settings.is_compressed)),
        ]

    if message['direction'] == 'Inbound':
        signature = 'Verified' if is_signature_verified(message) else 'Not verified'
        rows.append(('Signature verification', chip(signature)))

    out = [fields('', rows)]
    return out

# ################################################################################################################################

def _structure(message:'anydict', body:'str', settings:'AS2Settings') -> 'anylist':

    if _is_mdn(message):
        layers = _mdn_layers(message, settings)
    else:
        layers = _message_layers(body, settings)

    rows:'anylist' = []

    for layer, content_type, size in layers:
        rows.append([layer, mono(content_type), size_text(size)])

    out = [table('', ['Layer', 'Content-Type', 'Size'], rows)]
    return out

# ################################################################################################################################

def _address(message:'anydict', settings:'AS2Settings') -> 'anydict | str':
    """ Where a message was sent to - a synchronous MDN is the HTTP response to the message it answers,
    an asynchronous one goes to an endpoint of its own.
    """
    partner = Partner_By_Key[message['partner_key']]
    is_outbound = message['direction'] == 'Outbound'

    if _is_mdn(message):
        if settings.mdn_mode == AS2MDNMode.Sync:
            out = 'HTTP response'
        elif is_outbound:
            out = mono(f'https://{partner.host}{_mdn_path}')
        else:
            out = mono(_mdn_path)

    elif is_outbound:
        out = mono(endpoint(partner))

    else:
        out = mono(channel_path(Protocol.AS2, Local_Party_ID))

    return out

# ################################################################################################################################

def _transport(message:'anydict', settings:'AS2Settings') -> 'anylist':

    partner = Partner_By_Key[message['partner_key']]
    agreement = Agreement_By_ID[message['agreement_id']]
    address = _address(message, settings)

    if message['direction'] == 'Outbound':
        retries = counted(agreement.retries, 'retry', 'retries')
        interval = counted(agreement.retry_minutes, 'minute', 'minutes')

        out = [fields('', [
            ('Endpoint', address),
            ('TLS', agreement.tls_version),
            ('MDN', settings.mdn_mode),
            ('Retries', f'{retries} every {interval}'),
        ])]

    else:
        out = [fields('', [
            ('Channel', address),
            ('TLS', agreement.tls_version),
            ('Client certificate', mono(f'CN={partner.host}, O={partner.name}')),
            ('Decryption', settings.encryption_algorithm),
            ('Received by', Local_Organization),
        ])]

    return out

# ################################################################################################################################
# ################################################################################################################################

def _http(head:'strlist', content:'str') -> 'str':
    """ An HTTP request or response out of its first lines and its content, which the Content-Length header is computed for.
    """
    content_length = len(content.encode('utf8'))

    head.append(f'Content-Length: {content_length}')
    head.append('')
    head.append('')

    out = CRLF.join(head) + content
    return out

# ################################################################################################################################

def _report(message:'anydict', settings:'AS2Settings', boundary:'str') -> 'str':
    """ The multipart/report body of an MDN, with its human-readable part and its disposition notification.
    """
    notification = _notification(message, settings)
    notification = notification.replace('\n', CRLF)

    if message['kind'] == Kind.Error:
        text = f'The message <{message["ref_to"]}> was not processed. {message["error"]}.'
    else:
        text = f'The message <{message["ref_to"]}> was received and processed.'

    lines = [
        f'--{boundary}',
        'Content-Type: text/plain; charset=us-ascii',
        '',
        text,
        '',
        f'--{boundary}',
        f'Content-Type: {_notice_type}',
        '',
        notification,
        '',
        f'--{boundary}--',
        '',
    ]

    out = CRLF.join(lines)
    return out

# ################################################################################################################################

def _signed_report(message:'anydict', report:'str', report_boundary:'str', boundary:'str') -> 'str':
    """ The report of an MDN inside a multipart/signed, followed by its signature.
    """
    signature = opaque_bytes(message['id'], _signature_size)

    lines = [
        f'--{boundary}',
        f'Content-Type: {_report_type}; boundary="{report_boundary}"',
        '',
        report,
        f'--{boundary}',
        f'Content-Type: {_signature_type}; name="smime.p7s"',
        'Content-Transfer-Encoding: base64',
        'Content-Disposition: attachment; filename="smime.p7s"',
        '',
        *base64_lines(signature),
        f'--{boundary}--',
        '',
    ]

    out = CRLF.join(lines)
    return out

# ################################################################################################################################

def _mdn_raw(message:'anydict', settings:'AS2Settings') -> 'str':
    """ An MDN as it went over the wire - the HTTP response to the message it answers if it is synchronous,
    an HTTP request of its own if it is asynchronous.
    """
    _, receiver_host = _hosts(message)

    report_boundary = f'REPORT_{message["key"]}'
    report = _report(message, settings, report_boundary)

    if settings.is_mdn_signed:
        signed_boundary = f'SIGNED_{message["key"]}'
        content = _signed_report(message, report, report_boundary, signed_boundary)
        content_type = f'{_signed_type(settings)}; boundary="{signed_boundary}"'
    else:
        content = report
        content_type = f'{_report_type}; boundary="{report_boundary}"'

    if settings.mdn_mode == AS2MDNMode.Sync:
        head = ['HTTP/1.1 200 OK']
    else:
        head = [f'POST {_mdn_path} HTTP/1.1', f'Host: {receiver_host}']

    for name, value in _as2_headers(message):
        head.append(f'{name}: {value}')

    head.append('MIME-Version: 1.0')
    head.append(f'Content-Type: {content_type}')

    out = _http(head, content)
    return out

# ################################################################################################################################

def _message_raw(message:'anydict', body:'str', settings:'AS2Settings') -> 'str':
    """ A message as it went over the wire, its enveloped data in base64.
    """
    _, receiver_host = _hosts(message)

    layers = _message_layers(body, settings)
    enveloped = layers[0]
    enveloped_size = enveloped[2]
    enveloped_data = opaque_bytes(message['id'], enveloped_size)
    content_lines = base64_lines(enveloped_data)
    content = CRLF.join(content_lines) + CRLF

    path = channel_path(Protocol.AS2, Local_Party_ID)
    head = [f'POST {path} HTTP/1.1', f'Host: {receiver_host}']

    for name, value in _as2_headers(message):
        head.append(f'{name}: {value}')

    for name, value in _mdn_request(message, settings):
        head.append(f'{name}: {value}')

    head.append('MIME-Version: 1.0')
    head.append(f'Content-Type: {_enveloped_type}; name="smime.p7m"')
    head.append('Content-Disposition: attachment; filename="smime.p7m"')
    head.append('Content-Transfer-Encoding: base64')

    out = _http(head, content)
    return out

# ################################################################################################################################

def _message_details(message:'anydict', body:'str') -> 'anylist':

    agreement = Agreement_By_ID[message['agreement_id']]
    settings = _settings(agreement)
    is_mdn = _is_mdn(message)

    if is_mdn:
        raw = _mdn_raw(message, settings)
    else:
        raw = _message_raw(message, body, settings)

    out = [
        tab('headers', 'AS2 headers', _headers(message, settings)),
        tab('smime', 'S/MIME', _smime(message, settings)),
    ]

    if is_mdn:
        out.append(tab('notification', 'Disposition notification', [code('', _notification(message, settings))]))

    out.append(tab('structure', 'MIME structure', _structure(message, body, settings)))
    out.append(tab('transport', transport_label(message), _transport(message, settings)))
    out.append(tab('raw', 'Raw message', [code('', raw)]))

    return out

# ################################################################################################################################
# ################################################################################################################################

Views = ProtocolViews(
    partner_identifiers=_partner_identifiers,
    certificate_usages=['Signing and encryption', 'TLS client'],
    agreement_parties=_agreement_parties,
    agreement_tabs=_agreement_tabs,
    message_details=_message_details,
)

# ################################################################################################################################
# ################################################################################################################################
