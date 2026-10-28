# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.config import Local_Organization, Local_Party_ID, Local_Role
from zato.common.b2b.portal.sample.agreements import Agreement_By_ID
from zato.common.b2b.portal.sample.common import action, aside, cell, chip, code, column, counted, delta, directed, envelope_timestamp, \
    fields, href, id_column, item, link, mono, Now, Path_CPAs, Path_Messages, Path_Partners, section, size_text, tab, table, \
    timestamp, yes_no
from zato.common.b2b.portal.sample.parties import DUNS_Type, endpoint, Partner_By_Key, Partner_Role, Services
from zato.common.b2b.portal.sample.payloads import envelope, payload, raw_message
from zato.common.b2b.portal.sample.traffic import Conversation_By_ID, Kind, Messages

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

_states = ['Received', 'Delivered', 'Waiting', 'Retrying', 'Failed', 'Refused', 'Duplicate']

_directions = ['Inbound', 'Outbound']

# The periods a search may be limited to, in minutes
_periods = [
    ('',      'Any time'),
    ('60',    'Last hour'),
    ('120',   'Last 2 hours'),
    ('360',   'Last 6 hours'),
    ('1440',  'Last 24 hours'),
    ('10080', 'Last 7 days'),
]

# ################################################################################################################################
# ################################################################################################################################

def _by_key(conversation:'anydict') -> 'anydict':
    out:'anydict' = {}

    for message in conversation['messages']:
        out[message['id']] = message

    return out

# ################################################################################################################################

# What a chip says of the state of a message, by the direction of the message
_Phrases = {
    'Outbound': {
        'Delivered': 'Delivered to',
        'Waiting':   'Queued for',
        'Retrying':  'Retrying to',
        'Failed':    'Failed to',
        'Refused':   'Refused by',
        'Duplicate': 'Resent to',
    },
    'Inbound': {
        'Received':  'Received from',
        'Refused':   'Refused from',
        'Duplicate': 'Duplicate from',
        'Failed':    'Failed from',
    },
}

# ##############################################################################################################################

def state_chip(message:'anydict', *, role:'str'='') -> 'anydict':
    """ The state of a message, led by the triangle of its direction and saying whether it went to the partner
    or came from it.
    """
    tip = message['error'] if message['error'] else message['tip']

    out = directed(chip(message['state'], tip=tip, role=role), message['direction'])
    out['text'] = _Phrases[message['direction']][message['state']]

    return out

# ##############################################################################################################################

def _state_chip(message:'anydict') -> 'anydict':
    out = state_chip(message, role='state')
    return out

# ################################################################################################################################

def _summary(message:'anydict', conversation:'anydict') -> 'anylist':

    partner = Partner_By_Key[message['partner_key']]
    by_id = _by_key(conversation)

    action_cells = [mono(message['action'])]

    # A signal names its kind in its action already
    if message['kind'] != message['action']:
        action_cells.append(aside(message['kind']))

    rows = [
        ('MessageId', mono(message['id'])),
        ('State', [
            _state_chip(message),
            link(partner.name, href(Path_Partners, partner.key)),
            aside(timestamp(message['moment'])),
        ]),
        ('Action', action_cells),
        ('Service', mono(message['service'])),
        ('Reference', mono(message['reference'])),
        ('CPAId', mono(message['cpa_id'], href=href(Path_CPAs, message['cpa_id']))),
        ('ConversationId', mono(message['conversation_id'])),
    ]

    if ref_to := message['ref_to']:
        answered = by_id[ref_to]
        rows.append(('RefToMessageId', mono(ref_to, href=href(Path_Messages, answered['key']))))

    out = [fields('', rows)]

    if message['error']:
        out.append(fields('Error', [
            ('Code', mono(message['error_code'])),
            ('Description', message['error']),
        ]))

    return out

# ################################################################################################################################

def _transaction(message:'anydict', conversation:'anydict') -> 'anylist':

    rows:'anylist' = []
    previous = None

    for each in conversation['messages']:
        if each is message:
            id_cell = mono(each['id'])
        else:
            id_cell = mono(each['id'], href=href(Path_Messages, each['key']))
        moment = each['moment']
        rows.append([id_cell, timestamp(moment), delta(moment, previous), state_chip(each), mono(each['action']), each['kind']])
        previous = moment

    out = [table('', [id_column('MessageId'), 'Time', 'Delta', 'State', 'Action', 'Kind'], rows)]
    return out

# ################################################################################################################################

def _envelope(message:'anydict') -> 'anylist':

    partner = Partner_By_Key[message['partner_key']]
    agreement = Agreement_By_ID[message['cpa_id']]

    if message['direction'] == 'Inbound':
        from_id, from_role, to_id, to_role = partner.duns, Partner_Role, Local_Party_ID, Local_Role
    else:
        from_id, from_role, to_id, to_role = Local_Party_ID, Local_Role, partner.duns, Partner_Role

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
        ('Signed acknowledgment', yes_no(agreement.is_signed_ack)),
        ('DuplicateElimination', yes_no(not is_messaging)),
        ('SyncReplyMode', mono(agreement.sync_reply)),
    ])

    out = [header, reliability]
    return out

# ##############################################################################################################################

def _parts(message:'anydict', body:'str') -> 'anylist':

    header = envelope(message)
    header_size = len(header.encode('utf8'))

    parts = [['ebXML_Message_Header', 'text/xml', size_text(header_size)]]

    if body:
        body_size = len(body.encode('utf8'))
        parts.append(['payload-1', 'application/xml', size_text(body_size)])

    out = [table('', ['Content-ID', 'Content-Type', 'Size'], parts)]
    return out

# ##############################################################################################################################

def _attempts(message:'anydict') -> 'anylist':

    rows:'anylist' = []
    previous = None

    for attempt in message['attempts']:
        moment = attempt['moment']
        rows.append([
            str(attempt['number']),
            timestamp(moment),
            delta(moment, previous),
            cell(attempt['outcome'], attempt['tone'], tip=attempt['tip']),
        ])
        previous = moment

    out = [table('', ['Attempt', 'Started', 'Delta', 'Outcome'], rows)]
    return out

# ##############################################################################################################################

def _transport(message:'anydict') -> 'anylist':

    partner = Partner_By_Key[message['partner_key']]
    agreement = Agreement_By_ID[message['cpa_id']]

    if message['direction'] == 'Outbound':
        out = [fields('', [
            ('Endpoint', mono(endpoint(partner))),
            ('TLS', agreement.tls_version),
            ('SOAPAction', mono('"ebXML"')),
            ('Retries', f'{counted(agreement.retries, "retry", "retries")} every {counted(agreement.retry_minutes, "minute", "minutes")}'),
        ])]

    else:
        is_verified = message['error_code'] != 'SecurityFailure'
        signature = 'Verified' if is_verified else 'Not verified'

        out = [fields('', [
            ('Channel', mono('/exchange/' + Local_Party_ID)),
            ('TLS', agreement.tls_version),
            ('Client certificate', mono(f'CN={partner.host}, O={partner.name}')),
            ('Signature', chip(signature)),
            ('Received by', Local_Organization),
        ])]

    return out

# ##############################################################################################################################
# ##############################################################################################################################

def _actions(state:'str') -> 'anylist':

    out:'anylist' = []

    if state in ('Failed', 'Retrying'):
        out.append(action('Resend', state='Waiting', text=_Phrases['Outbound']['Waiting'], is_primary=True))

    return out

# ##############################################################################################################################

def _item(message:'anydict') -> 'anydict':

    conversation = Conversation_By_ID[message['conversation_id']]
    partner = Partner_By_Key[message['partner_key']]
    body = payload(message)

    age = Now - message['moment']
    age_minutes = int(age.total_seconds() // 60)

    is_outbound = message['direction'] == 'Outbound'

    tabs = [
        tab('summary', 'Summary', _summary(message, conversation)),
        tab('transaction', 'Transaction', _transaction(message, conversation)),
    ]

    if body:
        tabs.append(tab('payload', 'Payload', [code('', body)]))

    if is_outbound:
        tabs.append(tab('delivery', 'Delivery', _attempts(message)))

    transport_label = 'Transport' if is_outbound else 'Reception'

    details = [
        tab('envelope', 'Envelope', _envelope(message)),
        tab('soap', 'SOAP envelope', [code('', envelope(message))]),
        tab('parts', 'MIME parts', _parts(message, body)),
        tab('transport', transport_label, _transport(message)),
        tab('raw', 'Raw message', [code('', raw_message(message))]),
    ]

    out = item(
        message['key'],
        title=message['action'],
        cells=[
            cell(timestamp(message['moment'])),
            _state_chip(message),
            cell(partner.name),
            mono(message['service']),
            mono(message['action']),
        ],
        attributes={
            'state': message['state'],
            'direction': message['direction'],
            'partner': partner.key,
            'service': message['service'],
            'action': message['action'],
            'cpa': message['cpa_id'],
            'transaction': conversation['state'],
            'message-id': message['id'],
            'conversation-id': message['conversation_id'],
            'age': str(age_minutes),
        },
        search=[message['id'], message['action'], message['service'], partner.name, message['reference']],
        tabs=tabs,
    )
    out['details_label'] = 'Show message details'
    out['details'] = details

    return out

# ################################################################################################################################

def _options(values:'strlist') -> 'anylist':
    out:'anylist' = [{'value': '', 'label': 'Any'}]

    for value in values:
        out.append({'value': value, 'label': value})

    return out

# ################################################################################################################################

def _select(name:'str', label:'str', options:'anylist', match:'str'='equals') -> 'anydict':
    out = {'name': name, 'label': label, 'kind': 'select', 'options': options, 'match': match}
    return out

# ################################################################################################################################

def _text(name:'str', label:'str') -> 'anydict':
    out = {'name': name, 'label': label, 'kind': 'text', 'input_type': 'text', 'is_mono': True, 'match': 'contains'}
    return out

# ################################################################################################################################

def _search() -> 'anydict':
    """ The search form of the message log and the searches that are one click away.
    """
    partners:'anylist' = [{'value': '', 'label': 'Any'}]

    for partner in Partner_By_Key.values():
        partners.append({'value': partner.key, 'label': partner.name})

    service_names:'strlist' = []

    for service in Services:
        service_names.append(service.name)

    periods:'anylist' = []

    for value, label in _periods:
        periods.append({'value': value, 'label': label})

    form = {
        'title': 'Search messages',
        'rows': [
            [_select('partner', 'Partner', partners)],
            [
                _select('direction', 'Direction', _options(_directions)),
                _select('state', 'State', _options(_states)),
            ],
            [_select('service', 'Service', _options(service_names))],
            [_text('action', 'Action')],
            [_text('message-id', 'MessageId')],
            [_text('conversation-id', 'ConversationId')],
            [_text('cpa', 'CPAId')],
            [
                _select('transaction', 'Transaction', _options(['Sent', 'Acknowledged', 'Answered', 'Failed'])),
                _select('age', 'Period', periods, 'at-most'),
            ],
        ],
    }

    out = {'form': form}
    return out

# ################################################################################################################################
# ################################################################################################################################

def build() -> 'anydict':

    items:'dictlist' = []

    for message in sorted(Messages, key=_moment, reverse=True):
        items.append(_item(message))

    out = section(
        slug='messages',
        path=Path_Messages,
        title='Message log',
        columns=[
            column('Time'),
            column('State', is_narrow=True),
            column('Partner'),
            column('Service'),
            column('Action'),
        ],
        items=items,
        actions_of=_actions,
        is_bulk=False,
    )
    out['search'] = _search()

    return out

# ################################################################################################################################

def _moment(message:'anydict') -> 'str':
    out = timestamp(message['moment'])
    return out

# ################################################################################################################################
# ################################################################################################################################
