# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.sample.agreements import AS2MDNMode, AS4_Default_MPC, AS4Profile, AS4TokenType
from zato.common.b2b.portal.sample.common import days_from_now, Duration_Units, Path_Agreements, Path_Partners, \
    Path_Registrations
from zato.common.b2b.portal.sample.parties import DUNS_Type, ISO6523_DUNS_Type, Partner_Role, Partners, Services
from zato.common.b2b.portal.sample.protocol.common import Protocol, Protocols
from zato.common.b2b.portal.sample.section_alerts import Path_Alert_Rules, Rules

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

_signature_algorithms = ['rsa-sha256', 'rsa-sha384', 'rsa-sha512']
_digest_algorithms    = ['sha256', 'sha384', 'sha512']
_tls_versions         = ['TLS 1.3', 'TLS 1.2']
_channels             = ['Portal', 'Email', 'Webhook']
_sync_reply_modes     = ['mshSignalsOnly', 'none', 'signalsOnly']

_as2_sign_algorithms       = ['SHA-256', 'SHA-384', 'SHA-512']
_as2_encryption_algorithms = ['AES-128-CBC', 'AES-256-CBC', 'AES-128-GCM', 'AES-256-GCM']
_as2_mdn_modes             = [AS2MDNMode.Sync, AS2MDNMode.Async, AS2MDNMode.Not_Requested]
_as2_content_types         = ['application/xml', 'application/edi-x12', 'application/edifact']
_as2_transfer_encodings    = ['binary', 'base64']

_as4_profiles    = [AS4Profile.EDelivery2, AS4Profile.EDelivery1, AS4Profile.Peppol, AS4Profile.ICS2]
_as4_token_types = [AS4TokenType.X509v3, AS4TokenType.PKIPath, AS4TokenType.SAML20]
_as4_meps        = ['One-Way/Push', 'Two-Way/Sync']

# An AS2 identifier is printable ASCII without spaces
_as2_id_pattern = '^[!-~]{1,128}$'
_as2_id_message = 'Enter up to 128 characters without spaces'

# The times of day a select offers are in steps of half an hour
_hours_per_day   = 24
_minutes_of_hour = [0, 30]

# A DUNS number is nine digits
_duns_pattern = '^[0-9]{9}$'
_duns_message = 'Enter the nine digits of the DUNS number'

# ################################################################################################################################
# ################################################################################################################################

def _option(value:'str', label:'str'='', note:'str'='') -> 'anydict':
    if not label:
        label = value
    out = {'value': value, 'label': label, 'note': note}
    return out

# ################################################################################################################################

def _options(values:'strlist') -> 'anylist':
    out:'anylist' = []

    for value in values:
        out.append(_option(value))

    return out

# ################################################################################################################################

def _partner_options() -> 'anylist':
    out:'anylist' = []

    for partner in Partners:
        out.append(_option(partner.key, partner.name, partner.duns))

    return out

# ################################################################################################################################

def _service_options() -> 'anylist':
    out:'anylist' = []

    for service in Services:
        out.append(_option(service.name, service.name, service.label))

    return out

# ################################################################################################################################
# ################################################################################################################################

def _text(
    name:'str',
    label:'str',
    value:'str'='',
    *,
    is_mono:'bool'=False,
    input_type:'str'='text',
    is_required:'bool'=True,
    ) -> 'anydict':
    """ A text field, required unless is_required is False. Its input type is also what its value is checked
    against - an email address, an https URL, a date or a time.
    """
    out = {
        'kind': 'text',
        'name': name,
        'label': label,
        'value': value,
        'is_mono': is_mono,
        'input_type': input_type,
        'is_required': is_required,
        'is_list': False,
        'required_when': [],
        'pattern': '',
        'pattern_message': '',
        'after': '',
        'after_label': '',
        'shown_when': [],
    }
    return out

# ################################################################################################################################

def _patterned(field:'anydict', pattern:'str', message:'str') -> 'anydict':
    """ A text field whose value must match the regular expression, with the message that says what it expects.
    """
    field['pattern'] = pattern
    field['pattern_message'] = message
    return field

# ################################################################################################################################

def _after(field:'anydict', other:'anydict') -> 'anydict':
    """ A date field whose value must be later than the one of the other field.
    """
    field['after'] = other['name']
    field['after_label'] = other['label']
    return field

# ################################################################################################################################

def _required_when(field:'anydict', name:'str', value:'str') -> 'anydict':
    """ A text field that is required only while the list field of the given name holds the given value.
    """
    field['is_required'] = False
    field['required_when'] = [name, value]
    return field

# ################################################################################################################################

def _listed(field:'anydict') -> 'anydict':
    """ A text field holding a comma-separated list, each item of which is checked on its own.
    """
    field['is_list'] = True
    return field

# ################################################################################################################################

def _shown_when(lines:'anylist', name:'str', value:'str') -> 'anylist':
    """ Lines shown and checked only while the line of the given name holds the given value.
    """
    for line in lines:
        line['shown_when'] = [name, value]

    return lines

# ################################################################################################################################

def _number(name:'str', label:'str', value:'int', one:'str', many:'str') -> 'anydict':
    """ A count, with the words for what it counts that a summary reads it with.
    """
    out = {'kind': 'number', 'name': name, 'label': label, 'value': value, 'unit': '', 'one': one, 'many': many}
    return out

# ################################################################################################################################

def _duration(name:'str', label:'str', amount:'int', unit:'str') -> 'anydict':
    """ An amount of time with the unit it is counted in, the units being the ones of every other duration.
    """
    out = {'kind': 'duration', 'name': name, 'label': label, 'value': {'amount': amount, 'unit': unit}, 'units': Duration_Units}
    return out

# ################################################################################################################################

def _select(name:'str', label:'str', values:'strlist', value:'str'='') -> 'anydict':
    if not value:
        value = values[0]
    out = {'kind': 'select', 'name': name, 'label': label, 'value': value, 'options': _options(values), 'shown_when': []}
    return out

# ################################################################################################################################

def _switch(name:'str', label:'str', value:'bool') -> 'anydict':
    out = {'kind': 'switch', 'name': name, 'label': label, 'value': value, 'shown_when': []}
    return out

# ################################################################################################################################

def _chips(name:'str', label:'str', values:'strlist', picked:'strlist') -> 'anydict':
    out = {'kind': 'chips', 'name': name, 'label': label, 'value': picked, 'options': _options(values), 'is_required': True}
    return out

# ################################################################################################################################

def _pick(name:'str', label:'str', options:'anylist') -> 'anydict':
    out = {'kind': 'pick', 'name': name, 'label': label, 'value': '', 'options': options, 'has_filter': True,
        'is_required': True, 'shown_when': []}
    return out

# ################################################################################################################################

def _pick_many(name:'str', label:'str', options:'anylist', values:'strlist', empty:'str', *, is_required:'bool') -> 'anydict':
    out = {'kind': 'pick-many', 'name': name, 'label': label, 'value': values, 'options': options, 'empty': empty,
        'has_filter': True, 'is_required': is_required, 'shown_when': []}
    return out

# ################################################################################################################################

def _form(name:'str', label:'str', summary:'str', rows:'anylist') -> 'anydict':
    """ A line whose answer is a summary link opening a popover form, the summary naming the fields in braces.
    """
    out = {'kind': 'form', 'name': name, 'label': label, 'summary': summary, 'form': {'title': label, 'rows': rows},
        'shown_when': []}
    return out

# ################################################################################################################################

def _step(title:'str', lines:'anylist') -> 'anydict':
    out = {'title': title, 'lines': lines, 'is_review': False}
    return out

# ################################################################################################################################

def _wizard(title:'str', list_path:'str', done_label:'str', steps:'anylist') -> 'anydict':

    review = {'title': 'Review', 'lines': [], 'is_review': True}
    steps.append(review)

    out = {'title': title, 'list_path': list_path, 'done_label': done_label, 'steps': steps}
    return out

# ################################################################################################################################

def _times() -> 'strlist':
    """ The times of day in steps of half an hour.
    """
    out:'strlist' = []

    for hour in range(_hours_per_day):
        for minute in _minutes_of_hour:
            out.append(f'{hour:02}:{minute:02}')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _ebxml_messaging() -> 'anylist':

    lines = [
        _form('reliability', 'Reliable messaging', 'Persist for {persist_duration}', [
            [_switch('ack_requested', 'Acknowledgment', True), _switch('ack_signed', 'Signed acknowledgment', True)],
            [_switch('duplicate_elimination', 'Duplicate elimination', True)],
            [_duration('persist_duration', 'Persist duration', 7, 'days')],
        ]),
        _select('sync_reply', 'SyncReplyMode', _sync_reply_modes),
        _form('time_limits', 'Time limits', 'Receipt within {receipt_time}, response within {perform_time}', [
            [_duration('receipt_time', 'timeToAcknowledgeReceipt', 0, 'seconds')],
            [_duration('perform_time', 'timeToPerform', 2, 'minutes')],
        ]),
        _form('ebxml_security', 'Security', '{signature_algorithm}, {digest_algorithm}', [
            [_select('signature_algorithm', 'Signature', _signature_algorithms),
                _select('digest_algorithm', 'Digest', _digest_algorithms)],
            [_switch('non_repudiation', 'Non-repudiation', True)],
        ]),
    ]

    out = _shown_when(lines, 'protocol', Protocol.ebXML)
    return out

# ################################################################################################################################

def _as2_messaging() -> 'anylist':

    lines = [
        _form('as2_security', 'Security', '{sign_algorithm}, {encryption_algorithm}', [
            [_select('sign_algorithm', 'Signature', _as2_sign_algorithms),
                _select('encryption_algorithm', 'Encryption', _as2_encryption_algorithms)],
            [_switch('is_compressed', 'Compression', True), _switch('compress_before_signing', 'Compress before signing', True)],
        ]),
        _form('mdn', 'MDN', '{mdn_mode}, overdue after {mdn_overdue}', [
            [_select('mdn_mode', 'Mode', _as2_mdn_modes), _switch('is_mdn_signed', 'Signed MDN', True)],
            [_text('async_mdn_url', 'Asynchronous MDN URL', is_mono=True, input_type='url', is_required=False)],
            [_duration('mdn_overdue', 'Overdue after', 30, 'minutes')],
        ]),
        _form('as2_payload', 'Payload', '{content_type}, {transfer_encoding}', [
            [_select('content_type', 'Content type', _as2_content_types)],
            [_select('transfer_encoding', 'Content-Transfer-Encoding', _as2_transfer_encodings)],
        ]),
    ]

    out = _shown_when(lines, 'protocol', Protocol.AS2)
    return out

# ################################################################################################################################

def _as4_messaging() -> 'anylist':

    lines = [
        _select('profile', 'Profile', _as4_profiles),
        _form('pmode', 'P-Mode', '{mep}, {mpc}', [
            [_select('mep', 'MEP', _as4_meps)],
            [_text('mpc', 'MPC', AS4_Default_MPC, is_mono=True)],
            [_switch('four_corner', 'Original sender and final recipient', False)],
        ]),
        _form('reception_awareness', 'Reception awareness', 'Missing receipt after {missing_receipt}', [
            [_switch('duplicate_detection', 'Duplicate detection', True)],
            [_duration('missing_receipt', 'Missing receipt', 24, 'hours')],
        ]),
        _form('as4_security', 'Security', '{token_type}', [
            [_select('token_type', 'Token', _as4_token_types)],
            [_switch('is_receipt_signed', 'Signed receipt', True), _switch('is_encrypted', 'Encryption', True)],
        ]),
    ]

    out = _shown_when(lines, 'protocol', Protocol.AS4)
    return out

# ################################################################################################################################

def agreement_wizard() -> 'anydict':

    valid_from = _text('valid_from', 'Valid from', days_from_now(7), input_type='date')
    valid_to = _after(_text('valid_to', 'Valid to', days_from_now(372), input_type='date'), valid_from)

    parties = _step('Parties', [
        _pick('partner', 'Partner', _partner_options()),
        _select('protocol', 'Protocol', Protocols),
        _text('agreement_id', 'Agreement', is_mono=True),
        valid_from,
        valid_to,
        _pick_many('services', 'Services', _service_options(), ['SubmitOrderv2', 'NotifyOfOrderStatusv2'], 'None',
            is_required=True),
    ])

    messaging_lines:'anylist' = []
    messaging_lines.extend(_ebxml_messaging())
    messaging_lines.extend(_as2_messaging())
    messaging_lines.extend(_as4_messaging())

    messaging_lines.append(_form('delivery', 'Delivery', '{retries} every {retry_interval}, {tls_version}', [
        [_number('retries', 'Retries', 3, 'retry', 'retries'), _duration('retry_interval', 'Retry interval', 5, 'minutes')],
        [_select('tls_version', 'TLS', _tls_versions), _switch('client_auth', 'Client authentication', True)],
    ]))
    messaging_lines.append(_text('endpoint', 'Endpoint', is_mono=True, input_type='url'))

    messaging = _step('Messaging', messaging_lines)

    out = _wizard('New agreement', Path_Agreements, 'Create', [parties, messaging])
    return out

# ################################################################################################################################

def partner_wizard() -> 'anydict':

    details_lines = [
        _text('name', 'Name'),
        _patterned(_text('duns', 'PartyId', is_mono=True), _duns_pattern, _duns_message),
        _select('protocol', 'Protocol', Protocols),
    ]

    details_lines.extend(_shown_when([
        _select('role', 'Role', [Partner_Role, 'WholesaleProvider']),
    ], 'protocol', Protocol.ebXML))

    details_lines.extend(_shown_when([
        _patterned(_text('as2_id', 'AS2 identifier', is_mono=True), _as2_id_pattern, _as2_id_message),
    ], 'protocol', Protocol.AS2))

    details_lines.extend(_shown_when([
        _select('party_id_type', 'PartyId type', [ISO6523_DUNS_Type, DUNS_Type]),
    ], 'protocol', Protocol.AS4))

    details_lines.append(_select('category', 'Category', ['Tier 1', 'Tier 2', 'Tier 3']))
    details_lines.append(_form('contact', 'Contact', '{contact_name}, {contact_email}', [
        [_text('contact_name', 'Name')],
        [_text('contact_email', 'Email', is_mono=True, input_type='email')],
        [_text('contact_phone', 'Phone', is_mono=True, input_type='tel', is_required=False)],
    ]))

    details = _step('Partner', details_lines)

    connectivity_lines = [
        _text('endpoint', 'Endpoint', is_mono=True, input_type='url'),
        _form('transport', 'Transport', '{tls_version}, timeout {timeout}', [
            [_select('tls_version', 'TLS', _tls_versions), _switch('client_auth', 'Client authentication', True)],
            [_duration('timeout', 'Timeout', 30, 'seconds')],
        ]),
    ]

    connectivity_lines.extend(_shown_when([
        _text('soap_action', 'SOAPAction', '"ebXML"', is_mono=True),
    ], 'protocol', Protocol.ebXML))

    connectivity_lines.append(_form('certificates', 'Certificates', '{signing_certificate}', [
        [_text('signing_certificate', 'Signing certificate', is_mono=True)],
        [_text('tls_certificate', 'TLS certificate', is_mono=True)],
    ]))
    connectivity_lines.append(_select('state', 'State', ['Onboarding', 'Active']))

    connectivity = _step('Connectivity', connectivity_lines)

    out = _wizard('New partner', Path_Partners, 'Create', [details, connectivity])
    return out

# ################################################################################################################################

def registration_wizard() -> 'anydict':

    request = _step('Request', [
        _pick('partner', 'Partner', _partner_options()),
        _pick_many('services', 'Services', _service_options(), ['SubmitOrderv2'], 'None', is_required=True),
        _text('note', 'Note', is_required=False),
    ])

    out = _wizard('New registration', Path_Registrations, 'Submit', [request])
    return out

# ################################################################################################################################

def rule_wizard() -> 'anydict':

    events:'strlist' = []

    for rule in Rules:
        if rule.event not in events:
            events.append(rule.event)

    recipients = _listed(_text('recipients', 'Recipients', is_mono=True, input_type='email'))
    webhook = _text('webhook', 'Webhook', is_mono=True, input_type='url')
    times = _times()

    trigger = _step('Trigger', [
        _text('name', 'Name'),
        _select('event', 'Event', events),
        _select('level', 'Level', ['Warning', 'Error', 'Information']),
        _pick_many('partners', 'Partners', _partner_options(), [], 'All partners', is_required=False),
    ])

    notification = _step('Notification', [
        _form('condition', 'Condition', 'After {threshold} within {window}', [
            [_number('threshold', 'Occurrences', 1, 'occurrence', 'occurrences'), _duration('window', 'Within', 15, 'minutes')],
        ]),
        _form('notify', 'Channels', '{channels}', [
            [_chips('channels', 'Channels', _channels, ['Portal'])],
            [_required_when(recipients, 'channels', 'Email')],
            [_required_when(webhook, 'channels', 'Webhook')],
        ]),
        _form('quiet_hours', 'Quiet hours', '{quiet_from} - {quiet_to}', [
            [_switch('quiet_enabled', 'Quiet hours', False)],
            [_select('quiet_from', 'From', times, '22:00'), _select('quiet_to', 'To', times, '06:00')],
        ]),
        _switch('enabled', 'Enabled', True),
    ])

    out = _wizard('New alert rule', Path_Alert_Rules, 'Create', [trigger, notification])
    return out

# ################################################################################################################################
# ################################################################################################################################
