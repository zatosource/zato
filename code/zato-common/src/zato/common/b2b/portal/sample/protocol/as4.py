# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.b2b.portal.config import Local_Host, Local_Organization, Local_Party_ID, Local_Role
from zato.common.b2b.portal.sample.agreements import Agreement_By_ID, AS4Profile, AS4TokenType
from zato.common.b2b.portal.sample.common import aside, chip, choice, code, counted, duration_value, envelope_timestamp, \
    fields, mono, number_value, size_text, tab, table, yes_no
from zato.common.b2b.portal.sample.parties import endpoint, ISO6523_DUNS_Type, Partner_By_Key, Partner_Role
from zato.common.b2b.portal.sample.payloads import answered, CRLF, parties, payload
from zato.common.b2b.portal.sample.protocol.common import base64_lines, channel_path, digest, is_signature_verified, \
    opaque_bytes, opaque_text, Protocol, ProtocolViews, transport_label
from zato.common.b2b.portal.sample.traffic import Kind
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.portal.sample.agreements import Agreement, AS4Settings
    from zato.common.b2b.portal.sample.parties import Partner
    from zato.common.typing_ import anydict, anylist, strlist, strtuple
    Agreement = Agreement
    AS4Settings = AS4Settings
    Partner = Partner

# ################################################################################################################################
# ################################################################################################################################

class _CryptoSuite(NamedTuple):
    name: str
    signature_algorithm: str
    key_label: str
    key_algorithm: str

# ################################################################################################################################

_rsa_suite = _CryptoSuite('RSA', 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256', 'Key transport',
    'http://www.w3.org/2009/xmlenc11#rsa-oaep')

_eddsa_suite = _CryptoSuite('EdDSA', 'http://www.w3.org/2021/04/xmldsig-more#eddsa-ed25519', 'Key agreement',
    'http://www.w3.org/2021/04/xmldsig-more#x25519')

# The crypto suite each profile prescribes
_suites = {
    AS4Profile.EDelivery1: _rsa_suite,
    AS4Profile.EDelivery2: _eddsa_suite,
    AS4Profile.Peppol:     _rsa_suite,
    AS4Profile.ICS2:       _rsa_suite,
}

# The ValueType of the BinarySecurityToken of each token type
_token_value_types = {
    AS4TokenType.X509v3:  'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3',
    AS4TokenType.PKIPath: 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509PKIPathv1',
    AS4TokenType.SAML20:  'http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.1#SAMLV2.0',
}

# The short descriptions of the ebMS 3.0 error codes
_error_descriptions = {
    'EBMS:0101': 'FailedAuthentication',
    'EBMS:0202': 'DeliveryFailure',
}

_profiles    = [AS4Profile.EDelivery1, AS4Profile.EDelivery2, AS4Profile.Peppol, AS4Profile.ICS2]
_token_types = [AS4TokenType.X509v3, AS4TokenType.PKIPath, AS4TokenType.SAML20]
_tls_versions = ['TLS 1.2', 'TLS 1.3']

_soap_namespace  = 'http://www.w3.org/2003/05/soap-envelope'
_ebms_namespace  = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/'
_ebbp_namespace  = 'http://docs.oasis-open.org/ebxml-bp/ebbp-signals-2.0'
_wsse_namespace  = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd'
_wsu_namespace   = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'
_ds_namespace    = 'http://www.w3.org/2000/09/xmldsig#'
_xenc_namespace  = 'http://www.w3.org/2001/04/xmlenc#'
_base64_encoding = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary'
_attachment_type = 'http://docs.oasis-open.org/wss/oasis-wss-SwAProfile-1.1#Attachment-Content-Only'

_mep           = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/oneWay'
_mep_binding   = 'http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/push'
_c14n          = 'http://www.w3.org/2001/10/xml-exc-c14n#'
_digest_method = 'http://www.w3.org/2001/04/xmlenc#sha256'
_encryption    = 'http://www.w3.org/2009/xmlenc11#aes128-gcm'
_service_type  = 'urn:pinecrest-telecom:b2b:service'
_compression   = 'application/gzip'
_soap_type     = 'application/soap+xml'

# How much compression keeps of a payload, in percent, and what AES-GCM adds to it, its nonce and its tag, in bytes
_compressed_percent = 42
_gcm_overhead       = 28

# The sizes of the opaque values of the security header, in bytes
_token_size     = 48
_signature_size = 256
_key_size       = 256

# ################################################################################################################################
# ################################################################################################################################

def _settings(agreement:'Agreement') -> 'AS4Settings':
    out = cast_('AS4Settings', agreement.settings)
    return out

# ################################################################################################################################

def _partner_identifiers(partner:'Partner') -> 'anylist':

    rows = [
        [mono(partner.duns), mono(ISO6523_DUNS_Type), mono(Partner_Role)],
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

    out = [parties_table, fields('', [('PartyId type', mono(ISO6523_DUNS_Type))], is_editable=True)]
    return out

# ################################################################################################################################

def _pmode(agreement:'Agreement') -> 'anylist':

    settings = _settings(agreement)

    rows = [
        ('Profile', choice(settings.profile, _profiles)),
        ('MEP', mono(_mep)),
        ('MEP binding', mono(_mep_binding)),
        ('MPC', mono(settings.mpc)),
        ('Service type', mono(_service_type)),
        ('Compression', mono(_compression)),
        ('Original sender', 'None'),
        ('Final recipient', 'None'),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _reception_awareness(agreement:'Agreement') -> 'anylist':

    settings = _settings(agreement)

    rows = [
        ('Receipt', chip('Required')),
        ('Signed receipt', yes_no(settings.is_receipt_signed)),
        ('Duplicate detection', chip('Required')),
        ('Retries', number_value(agreement.retries)),
        ('Retry interval', duration_value(agreement.retry_minutes, 'minutes')),
        ('Missing receipt after', duration_value(settings.missing_receipt_hours, 'hours')),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _security(agreement:'Agreement') -> 'anylist':

    settings = _settings(agreement)
    suite = _suites[settings.profile]
    name = agreement.partner_key

    rows = [
        ('Crypto suite', suite.name),
        ('Signature algorithm', mono(suite.signature_algorithm)),
        ('Digest algorithm', mono(_digest_method)),
        ('Encryption algorithm', mono(_encryption)),
        (suite.key_label, mono(suite.key_algorithm)),
        ('Token type', choice(settings.token_type, _token_types)),
        ('TLS', choice(agreement.tls_version, _tls_versions)),
        ('Client authentication', chip('Required')),
        ('Partner signing certificate', mono(f'{name}-signing-2026')),
        ('Partner encryption certificate', mono(f'{name}-encryption-2026')),
        ('Partner TLS certificate', mono(f'{name}-tls-2026')),
        ('Local signing certificate', mono('pinecrest-signing-2026')),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _agreement_tabs(agreement:'Agreement') -> 'anylist':

    out = [
        tab('pmode', 'P-Mode', _pmode(agreement)),
        tab('reception', 'Reception awareness', _reception_awareness(agreement)),
        tab('security', 'Security', _security(agreement)),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################

def _is_signal(message:'anydict') -> 'bool':
    out = message['kind'] in (Kind.Ack, Kind.Error)
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

def _payload_id(message:'anydict') -> 'str':
    sender_host, _ = _hosts(message)

    out = f'payload-1@{sender_host}'
    return out

# ################################################################################################################################

def _payload_size(body:'str') -> 'int':
    """ The size of a payload once it is compressed and encrypted.
    """
    size = len(body.encode('utf8'))

    out = size * _compressed_percent // 100 + _gcm_overhead
    return out

# ################################################################################################################################

def _message_info(message:'anydict') -> 'strlist':

    out = [
        '        <eb3:MessageInfo>',
        f'          <eb3:Timestamp>{envelope_timestamp(message["moment"])}</eb3:Timestamp>',
        f'          <eb3:MessageId>{message["id"]}</eb3:MessageId>',
    ]

    if message['ref_to']:
        out.append(f'          <eb3:RefToMessageId>{message["ref_to"]}</eb3:RefToMessageId>')

    out.append('        </eb3:MessageInfo>')

    return out

# ################################################################################################################################

def _user_message(message:'anydict', settings:'AS4Settings') -> 'strlist':

    from_id, from_role, to_id, to_role = parties(message)

    out = [f'      <eb3:UserMessage mpc="{settings.mpc}">']
    out.extend(_message_info(message))
    out.extend([
        '        <eb3:PartyInfo>',
        '          <eb3:From>',
        f'            <eb3:PartyId type="{ISO6523_DUNS_Type}">{from_id}</eb3:PartyId>',
        f'            <eb3:Role>{from_role}</eb3:Role>',
        '          </eb3:From>',
        '          <eb3:To>',
        f'            <eb3:PartyId type="{ISO6523_DUNS_Type}">{to_id}</eb3:PartyId>',
        f'            <eb3:Role>{to_role}</eb3:Role>',
        '          </eb3:To>',
        '        </eb3:PartyInfo>',
        '        <eb3:CollaborationInfo>',
        f'          <eb3:AgreementRef>{message["agreement_id"]}</eb3:AgreementRef>',
        f'          <eb3:Service type="{_service_type}">{message["service"]}</eb3:Service>',
        f'          <eb3:Action>{message["action"]}</eb3:Action>',
        f'          <eb3:ConversationId>{message["conversation_id"]}</eb3:ConversationId>',
        '        </eb3:CollaborationInfo>',
        '        <eb3:PayloadInfo>',
        f'          <eb3:PartInfo href="cid:{_payload_id(message)}">',
        '            <eb3:PartProperties>',
        '              <eb3:Property name="MimeType">application/xml</eb3:Property>',
        f'              <eb3:Property name="CompressionType">{_compression}</eb3:Property>',
        '            </eb3:PartProperties>',
        '          </eb3:PartInfo>',
        '        </eb3:PayloadInfo>',
        '      </eb3:UserMessage>',
    ])

    return out

# ################################################################################################################################

def _signal_message(message:'anydict', settings:'AS4Settings') -> 'strlist':

    out = ['      <eb3:SignalMessage>']
    out.extend(_message_info(message))

    if message['kind'] == Kind.Error:
        code_value = message['error_code']
        description = _error_descriptions[code_value]
        out.append(f'        <eb3:Error errorCode="{code_value}" severity="failure" shortDescription="{description}"')
        out.append(f'            refToMessageInError="{message["ref_to"]}">')
        out.append(f'          <eb3:Description xml:lang="en">{message["error"]}</eb3:Description>')
        out.append('        </eb3:Error>')

    elif settings.is_receipt_signed:
        original = answered(message)
        body = payload(original)
        out.extend([
            '        <eb3:Receipt>',
            f'          <ebbp:NonRepudiationInformation xmlns:ebbp="{_ebbp_namespace}">',
            '            <ebbp:MessagePartNRInformation>',
            f'              <ds:Reference URI="cid:{_payload_id(original)}">',
            f'                <ds:DigestMethod Algorithm="{_digest_method}"/>',
            f'                <ds:DigestValue>{digest(body)}</ds:DigestValue>',
            '              </ds:Reference>',
            '            </ebbp:MessagePartNRInformation>',
            '          </ebbp:NonRepudiationInformation>',
            '        </eb3:Receipt>',
        ])

    else:
        out.append('        <eb3:Receipt/>')

    out.append('      </eb3:SignalMessage>')

    return out

# ################################################################################################################################

def _reference(uri:'str', seed:'str') -> 'strlist':
    out = [
        f'          <ds:Reference URI="{uri}">',
        f'            <ds:DigestMethod Algorithm="{_digest_method}"/>',
        f'            <ds:DigestValue>{digest(seed)}</ds:DigestValue>',
        '          </ds:Reference>',
    ]
    return out

# ################################################################################################################################

def _security_header(message:'anydict', settings:'AS4Settings') -> 'strlist':
    """ The WS-Security header - the signing token, the signature over the ebMS header, the body and the payload,
    and for a user message the key its payload is encrypted with.
    """
    suite = _suites[settings.profile]
    value_type = _token_value_types[settings.token_type]
    message_id = message['id']

    token = opaque_text(message_id + '.token', _token_size)
    signature_value = opaque_text(message_id + '.signature', _signature_size)
    key_value = opaque_text(message_id + '.key', _key_size)

    out = [
        '    <wsse:Security env:mustUnderstand="true">',
        f'      <wsse:BinarySecurityToken wsu:Id="signing-token" ValueType="{value_type}"',
        f'          EncodingType="{_base64_encoding}">{token}</wsse:BinarySecurityToken>',
        '      <ds:Signature>',
        '        <ds:SignedInfo>',
        f'          <ds:CanonicalizationMethod Algorithm="{_c14n}"/>',
        f'          <ds:SignatureMethod Algorithm="{suite.signature_algorithm}"/>',
    ]

    out.extend(_reference('#ebms-header', message_id + '.header'))
    out.extend(_reference('#body', message_id + '.body'))

    if not _is_signal(message):
        out.extend(_reference(f'cid:{_payload_id(message)}', message_id + '.payload'))

    out.extend([
        '        </ds:SignedInfo>',
        f'        <ds:SignatureValue>{signature_value}</ds:SignatureValue>',
        '        <ds:KeyInfo>',
        '          <wsse:SecurityTokenReference>',
        '            <wsse:Reference URI="#signing-token"/>',
        '          </wsse:SecurityTokenReference>',
        '        </ds:KeyInfo>',
        '      </ds:Signature>',
    ])

    if not _is_signal(message):
        out.extend([
            f'      <xenc:EncryptedKey xmlns:xenc="{_xenc_namespace}" Id="encrypted-key">',
            f'        <xenc:EncryptionMethod Algorithm="{suite.key_algorithm}"/>',
            '        <xenc:CipherData>',
            f'          <xenc:CipherValue>{key_value}</xenc:CipherValue>',
            '        </xenc:CipherData>',
            '      </xenc:EncryptedKey>',
            f'      <xenc:EncryptedData xmlns:xenc="{_xenc_namespace}" MimeType="{_compression}"',
            f'          Type="{_attachment_type}">',
            f'        <xenc:EncryptionMethod Algorithm="{_encryption}"/>',
            '        <xenc:CipherData>',
            f'          <xenc:CipherReference URI="cid:{_payload_id(message)}"/>',
            '        </xenc:CipherData>',
            '      </xenc:EncryptedData>',
        ])

    out.append('    </wsse:Security>')

    return out

# ################################################################################################################################

def envelope(message:'anydict', settings:'AS4Settings') -> 'str':
    """ The SOAP 1.2 envelope of a message, with its ebMS 3.0 user message or signal message and its WS-Security header.
    """
    lines:'strlist' = [
        f'<env:Envelope xmlns:env="{_soap_namespace}"',
        f'    xmlns:eb3="{_ebms_namespace}"',
        f'    xmlns:wsse="{_wsse_namespace}"',
        f'    xmlns:wsu="{_wsu_namespace}"',
        f'    xmlns:ds="{_ds_namespace}">',
        '  <env:Header>',
        '    <eb3:Messaging env:mustUnderstand="true" wsu:Id="ebms-header">',
    ]

    if _is_signal(message):
        lines.extend(_signal_message(message, settings))
    else:
        lines.extend(_user_message(message, settings))

    lines.append('    </eb3:Messaging>')
    lines.extend(_security_header(message, settings))
    lines.append('  </env:Header>')
    lines.append('  <env:Body wsu:Id="body"/>')
    lines.append('</env:Envelope>')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _envelope(message:'anydict', settings:'AS4Settings') -> 'anylist':

    if _is_signal(message):

        if message['kind'] == Kind.Error:
            code_value = message['error_code']
            signal = [mono('Error'), aside(f'{code_value} {_error_descriptions[code_value]}')]
        else:
            signal = mono('Receipt')

        out = [fields('Signal message', [
            ('Signal', signal),
            ('Non-repudiation', yes_no(settings.is_receipt_signed)),
            ('Timestamp', mono(envelope_timestamp(message['moment']))),
        ])]

    else:
        from_id, from_role, to_id, to_role = parties(message)

        header = fields('User message', [
            ('From PartyId', mono(from_id)),
            ('From role', mono(from_role)),
            ('To PartyId', mono(to_id)),
            ('To role', mono(to_role)),
            ('PartyId type', mono(ISO6523_DUNS_Type)),
            ('Service type', mono(_service_type)),
            ('MPC', mono(settings.mpc)),
            ('Timestamp', mono(envelope_timestamp(message['moment']))),
        ])

        reception = fields('Reception awareness', [
            ('Signed receipt', yes_no(settings.is_receipt_signed)),
            ('Duplicate detection', yes_no(True)),
            ('Compression', mono(_compression)),
        ])

        out = [header, reception]

    return out

# ################################################################################################################################

def _parts(message:'anydict', body:'str', settings:'AS4Settings') -> 'anylist':

    sender_host, _ = _hosts(message)
    soap = envelope(message, settings)
    soap_size = len(soap.encode('utf8'))

    rows = [[mono(f'soap-part@{sender_host}'), mono(_soap_type), mono(_soap_type), size_text(soap_size)]]

    if body:
        rows.append([mono(_payload_id(message)), mono('application/octet-stream'), mono('application/xml'),
            size_text(_payload_size(body))])

    out = [table('', ['Content-ID', 'Content-Type', 'MimeType', 'Size'], rows)]
    return out

# ################################################################################################################################

def _transport(message:'anydict', settings:'AS4Settings') -> 'anylist':

    partner = Partner_By_Key[message['partner_key']]
    agreement = Agreement_By_ID[message['agreement_id']]
    suite = _suites[settings.profile]

    # A signal is the HTTP response to the user message it answers
    if _is_signal(message):
        address = 'HTTP response'
    elif message['direction'] == 'Outbound':
        address = mono(endpoint(partner))
    else:
        address = mono(channel_path(Protocol.AS4, Local_Party_ID))

    if message['direction'] == 'Outbound':
        retries = counted(agreement.retries, 'retry', 'retries')
        interval = counted(agreement.retry_minutes, 'minute', 'minutes')

        out = [fields('', [
            ('Endpoint', address),
            ('TLS', agreement.tls_version),
            ('Profile', settings.profile),
            ('Retries', f'{retries} every {interval}'),
        ])]

    else:
        signature = 'Verified' if is_signature_verified(message) else 'Not verified'

        out = [fields('', [
            ('Channel', address),
            ('TLS', agreement.tls_version),
            ('Client certificate', mono(f'CN={partner.host}, O={partner.name}')),
            ('Signature', chip(signature)),
            ('Crypto suite', suite.name),
            ('Received by', Local_Organization),
        ])]

    return out

# ################################################################################################################################

def _raw(message:'anydict', body:'str', settings:'AS4Settings') -> 'str':
    """ A message as it went over the wire - a user message is a multipart/related request with its SOAP envelope
    and its encrypted payload, a signal is the SOAP envelope of the HTTP response to the user message it answers.
    """
    sender_host, receiver_host = _hosts(message)
    soap = envelope(message, settings)
    soap = soap.replace('\n', CRLF)

    if _is_signal(message):
        head = ['HTTP/1.1 200 OK', f'Content-Type: {_soap_type}; charset=UTF-8']
        content = soap

    else:
        boundary = f'MIMEBoundary_{message["key"]}'
        soap_id = f'soap-part@{sender_host}'
        encrypted = opaque_bytes(message['id'], _payload_size(body))

        lines = [
            f'--{boundary}',
            f'Content-ID: <{soap_id}>',
            f'Content-Type: {_soap_type}; charset=UTF-8',
            '',
            soap,
            f'--{boundary}',
            f'Content-ID: <{_payload_id(message)}>',
            'Content-Type: application/octet-stream',
            'Content-Transfer-Encoding: base64',
            '',
            *base64_lines(encrypted),
            f'--{boundary}--',
            '',
        ]
        content = CRLF.join(lines)

        path = channel_path(Protocol.AS4, Local_Party_ID)
        content_type = f'multipart/related; type="{_soap_type}"; boundary="{boundary}"; start="<{soap_id}>"'
        head = [f'POST {path} HTTP/1.1', f'Host: {receiver_host}', 'MIME-Version: 1.0', f'Content-Type: {content_type}']

    content_length = len(content.encode('utf8'))

    head.append(f'Content-Length: {content_length}')
    head.append('')
    head.append('')

    out = CRLF.join(head) + content
    return out

# ################################################################################################################################

def _message_details(message:'anydict', body:'str') -> 'anylist':

    agreement = Agreement_By_ID[message['agreement_id']]
    settings = _settings(agreement)

    out = [
        tab('envelope', 'Envelope', _envelope(message, settings)),
        tab('soap', 'SOAP envelope', [code('', envelope(message, settings))]),
        tab('parts', 'MIME parts', _parts(message, body, settings)),
        tab('transport', transport_label(message), _transport(message, settings)),
        tab('raw', 'Raw message', [code('', _raw(message, body, settings))]),
    ]
    return out

# ################################################################################################################################
# ################################################################################################################################

Views = ProtocolViews(
    partner_identifiers=_partner_identifiers,
    certificate_usages=['Signing', 'Encryption', 'TLS client'],
    agreement_parties=_agreement_parties,
    agreement_tabs=_agreement_tabs,
    message_details=_message_details,
)

# ################################################################################################################################
# ################################################################################################################################
