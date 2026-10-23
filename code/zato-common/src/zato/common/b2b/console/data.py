# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, dictlist, strlist
    anydict = anydict
    anylist = anylist
    dictlist = dictlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class Pill:
    """ The kinds of state marks a cell of a listing may have.
    """
    No_Pill = ''
    Good    = 'good'
    Warning = 'warning'
    Info    = 'info'

# ################################################################################################################################
# ################################################################################################################################

def _cell(text:'str', pill:'str'=Pill.No_Pill) -> 'anydict':
    out = {'text': text, 'pill': pill}
    return out

# ################################################################################################################################

def _cells(*texts:'str') -> 'anylist':

    out:'anylist' = []

    for text in texts:
        cell = _cell(text)
        out.append(cell)

    return out

# ################################################################################################################################

def _text(label:'str') -> 'anydict':
    out = {'label': label, 'kind': 'text', 'options': []}
    return out

# ################################################################################################################################

def _number(label:'str') -> 'anydict':
    out = {'label': label, 'kind': 'number', 'options': []}
    return out

# ################################################################################################################################

def _select(label:'str', options:'strlist') -> 'anydict':
    out = {'label': label, 'kind': 'select', 'options': options}
    return out

# ################################################################################################################################

def _checkbox(label:'str') -> 'anydict':
    out = {'label': label, 'kind': 'checkbox', 'options': []}
    return out

# ################################################################################################################################
# ################################################################################################################################

# A column is centered under its header when none of its values is longer than this
_centered_max_length = 10

_protocols = ['ebMS 2.0', 'AS2', 'AS4']
_partner_names = ['Acme Medical Supply', 'Northwind Logistics', 'Riverside Pharmacy Group']
_local_party_names = ['Lakeside Health']
_profile_names = ['Reliable, signed, asynchronous', 'Signals in the HTTP response', 'Unsigned, best effort']

# ################################################################################################################################
# ################################################################################################################################

agreements = {
    'slug': 'agreements',
    'title': 'Agreements',
    'columns': ['Name', 'Protocol', 'Partner', 'Valid until', 'State'],
    'items': [
        {
            'id': 'lakeside-acme-orders',
            'title': 'lakeside-acme-orders',
            'cells': _cells('lakeside-acme-orders', 'ebMS 2.0', 'Acme Medical Supply', '2027-06-30') + [_cell('Active', Pill.Good)],
            'fields': [
                ('CPAId', 'urn:lakeside-health:cpa:acme-orders'),
                ('Protocol', 'ebMS 2.0'),
                ('Status', 'agreed'),
                ('Local party', 'Lakeside Health'),
                ('Partner', 'Acme Medical Supply'),
                ('Start', '2026-01-01 00:00 UTC'),
                ('End', '2027-06-30 23:59 UTC'),
                ('Signals', 'Signals in the HTTP response'),
            ],
            'tables': [
                {
                    'title': 'Services and actions',
                    'columns': ['Service', 'Action', 'Direction', 'Channel profile', 'Zato service'],
                    'rows': [
                        ['urn:lakeside-health:orders', 'Submit', 'Send', 'Reliable, signed, asynchronous', 'orders.submit'],
                        ['urn:lakeside-health:orders', 'Confirm', 'Receive', 'Reliable, signed, asynchronous',
                            'orders.submit-received'],
                        ['urn:lakeside-health:invoices', 'Invoice', 'Receive', 'Signals in the HTTP response',
                            'invoices.invoice-received'],
                    ],
                },
            ],
        },
        {
            'id': 'lakeside-northwind-shipping',
            'title': 'lakeside-northwind-shipping',
            'cells': _cells('lakeside-northwind-shipping', 'AS2', 'Northwind Logistics', '2026-12-31') + [
                _cell('Active', Pill.Good)],
            'fields': [
                ('Protocol', 'AS2'),
                ('Local party', 'Lakeside Health'),
                ('Partner', 'Northwind Logistics'),
                ('Start', '2026-03-01 00:00 UTC'),
                ('End', '2026-12-31 23:59 UTC'),
                ('Signing', 'SHA-256'),
                ('Encryption', 'AES-256-CBC'),
                ('MDN', 'Synchronous, signed'),
                ('Zato service', 'shipping.notice-received'),
            ],
            'tables': [],
        },
        {
            'id': 'lakeside-riverside-claims',
            'title': 'lakeside-riverside-claims',
            'cells': _cells('lakeside-riverside-claims', 'AS4', 'Riverside Pharmacy Group', '2026-11-15') + [
                _cell('Expiring', Pill.Warning)],
            'fields': [
                ('AgreementRef', 'urn:riverside:agreements:claims'),
                ('Protocol', 'AS4'),
                ('Local party', 'Lakeside Health'),
                ('Partner', 'Riverside Pharmacy Group'),
                ('Start', '2025-11-15 00:00 UTC'),
                ('End', '2026-11-15 23:59 UTC'),
            ],
            'tables': [
                {
                    'title': 'P-Modes',
                    'columns': ['P-Mode', 'Service', 'Action', 'Direction', 'Retries'],
                    'rows': [
                        ['claims-submit', 'urn:riverside:claims', 'Submit', 'Send', '4 every 15 min'],
                        ['claims-status', 'urn:riverside:claims', 'Status', 'Receive', '4 every 15 min'],
                    ],
                },
            ],
        },
    ],
    'form': [
        _text('Name'),
        _select('Protocol', _protocols),
        _select('Local party', _local_party_names),
        _select('Partner', _partner_names),
        _text('CPAId'),
        _text('Start'),
        _text('End'),
        _select('Signals', _profile_names),
        _checkbox('Active'),
    ],
}

# ################################################################################################################################
# ################################################################################################################################

partners = {
    'slug': 'partners',
    'title': 'Trading partners',
    'columns': ['Name', 'Party ID', 'Endpoint', 'Agreements'],
    'items': [
        {
            'id': 'acme-medical',
            'title': 'Acme Medical Supply',
            'cells': _cells('Acme Medical Supply', 'urn:acme-medical:b2b', 'https://b2b.acme-medical.example.com/ebms', '1'),
            'fields': [
                ('Endpoint', 'https://b2b.acme-medical.example.com/ebms'),
                ('Signing certificate', 'acme-signing-2026'),
                ('Encryption certificate', 'acme-encryption-2026'),
                ('TLS trust anchors', 'acme-tls-ca'),
                ('Contact', 'John Smith'),
            ],
            'tables': [
                {
                    'title': 'Party identifiers',
                    'columns': ['Value', 'Type'],
                    'rows': [
                        ['urn:acme-medical:b2b', 'urn:acme-medical:party-id'],
                        ['0614727000013', 'urn:oasis:names:tc:ebcore:partyid-type:iso6523:0088'],
                    ],
                },
            ],
        },
        {
            'id': 'northwind-logistics',
            'title': 'Northwind Logistics',
            'cells': _cells('Northwind Logistics', 'NORTHWIND-AS2', 'https://as2.northwind.example.com/receive', '1'),
            'fields': [
                ('Endpoint', 'https://as2.northwind.example.com/receive'),
                ('Signing certificate', 'northwind-as2-2026'),
                ('Encryption certificate', 'northwind-as2-2026'),
                ('TLS trust anchors', 'northwind-tls-ca'),
                ('Contact', 'Maria Johnson'),
            ],
            'tables': [],
        },
        {
            'id': 'riverside-pharmacy',
            'title': 'Riverside Pharmacy Group',
            'cells': _cells('Riverside Pharmacy Group', 'urn:riverside:pharmacy', 'https://as4.riverside.example.com/msh', '1'),
            'fields': [
                ('Endpoint', 'https://as4.riverside.example.com/msh'),
                ('Signing certificate', 'riverside-as4-2025'),
                ('Encryption certificate', 'riverside-as4-2025'),
                ('TLS trust anchors', 'riverside-tls-ca'),
                ('Contact', 'Anna Miller'),
            ],
            'tables': [],
        },
    ],
    'form': [
        _text('Name'),
        _text('Party ID'),
        _text('Party ID type'),
        _text('Endpoint'),
        _select('Signing certificate', ['acme-signing-2026', 'northwind-as2-2026', 'riverside-as4-2025']),
        _select('Encryption certificate', ['northwind-as2-2026', 'riverside-as4-2025']),
        _text('Contact'),
        _checkbox('Active'),
    ],
}

# ################################################################################################################################
# ################################################################################################################################

local_parties = {
    'slug': 'local-parties',
    'title': 'Local parties',
    'columns': ['Name', 'Party ID', 'Channel'],
    'items': [
        {
            'id': 'lakeside-health',
            'title': 'Lakeside Health',
            'cells': _cells('Lakeside Health', 'urn:lakeside-health:b2b', '/b2b/lakeside-health'),
            'fields': [
                ('Channel', '/b2b/lakeside-health'),
                ('Signing key', 'lakeside-signing-2026'),
                ('Decryption key', 'lakeside-encryption-2026'),
                ('TLS client key', 'lakeside-tls-client'),
            ],
            'tables': [
                {
                    'title': 'Party identifiers',
                    'columns': ['Value', 'Type'],
                    'rows': [
                        ['urn:lakeside-health:b2b', 'urn:lakeside-health:party-id'],
                        ['LAKESIDE-AS2', 'AS2-From'],
                    ],
                },
            ],
        },
    ],
    'form': [
        _text('Name'),
        _text('Party ID'),
        _text('Party ID type'),
        _text('Channel'),
        _select('Signing key', ['lakeside-signing-2026']),
        _select('Decryption key', ['lakeside-encryption-2026']),
        _checkbox('Active'),
    ],
}

# ################################################################################################################################
# ################################################################################################################################

certificates = {
    'slug': 'certificates',
    'title': 'Certificates',
    'columns': ['Name', 'Owner', 'Subject', 'Valid until', 'State'],
    'items': [
        {
            'id': 'lakeside-signing-2026',
            'title': 'lakeside-signing-2026',
            'cells': _cells('lakeside-signing-2026', 'Local', 'CN=Lakeside Health B2B', '2027-02-01') + [
                _cell('Valid', Pill.Good)],
            'fields': [
                ('Subject', 'CN=Lakeside Health B2B, O=Lakeside Health, C=US'),
                ('Issuer', 'CN=Lakeside Health Issuing CA, O=Lakeside Health, C=US'),
                ('Not before', '2026-02-01 00:00 UTC'),
                ('Not after', '2027-02-01 00:00 UTC'),
                ('SHA-256 fingerprint', '7d0cb83ffc2aeca0d6469e306098a58640ada9e9d24a43c4ba8344610bb76e22'),
                ('Private key', 'Yes'),
            ],
            'tables': [],
        },
        {
            'id': 'acme-signing-2026',
            'title': 'acme-signing-2026',
            'cells': _cells('acme-signing-2026', 'Acme Medical Supply', 'CN=b2b.acme-medical.example.com', '2026-12-01') + [
                _cell('Valid', Pill.Good)],
            'fields': [
                ('Subject', 'CN=b2b.acme-medical.example.com, O=Acme Medical Supply, C=US'),
                ('Issuer', 'CN=Acme Medical Issuing CA, O=Acme Medical Supply, C=US'),
                ('Not before', '2025-12-01 00:00 UTC'),
                ('Not after', '2026-12-01 00:00 UTC'),
                ('SHA-256 fingerprint', '9bb21eac7358e200876cc7ee7499b314bad0ef6122837c4de299d06d83043e56'),
                ('Private key', 'No'),
            ],
            'tables': [],
        },
        {
            'id': 'riverside-as4-2025',
            'title': 'riverside-as4-2025',
            'cells': _cells('riverside-as4-2025', 'Riverside Pharmacy Group', 'CN=as4.riverside.example.com', '2026-11-20') + [
                _cell('Expires in 28 days', Pill.Warning)],
            'fields': [
                ('Subject', 'CN=as4.riverside.example.com, O=Riverside Pharmacy Group, C=US'),
                ('Issuer', 'CN=Riverside Issuing CA, O=Riverside Pharmacy Group, C=US'),
                ('Not before', '2025-11-20 00:00 UTC'),
                ('Not after', '2026-11-20 00:00 UTC'),
                ('SHA-256 fingerprint', '3f6a1c92e04b7d58a1f0c3e9b2d47a6e815c0f93d2b6e4a7c18f5d02e9b3a7c4'),
                ('Private key', 'No'),
            ],
            'tables': [],
        },
    ],
    'form': [
        _text('Name'),
        _select('Owner', ['Local'] + _partner_names),
        _text('PEM'),
    ],
}

# ################################################################################################################################
# ################################################################################################################################

channel_profiles = {
    'slug': 'channel-profiles',
    'title': 'Channel profiles',
    'columns': ['Name', 'Acknowledgment', 'Duplicates', 'Retries', 'Signed'],
    'items': [
        {
            'id': 'reliable-signed-async',
            'title': 'Reliable, signed, asynchronous',
            'cells': _cells('Reliable, signed, asynchronous', 'always', 'always', '3 every 1 min', 'Yes'),
            'fields': [
                ('Reply mode', 'none'),
                ('Acknowledgment', 'always'),
                ('Signed acknowledgment', 'always'),
                ('Duplicate elimination', 'always'),
                ('Retries', '3'),
                ('Retry interval', '60 s'),
                ('Persist duration', '1 day'),
                ('Message order', 'NotGuaranteed'),
                ('Signature algorithm', 'RSA-SHA256'),
            ],
            'tables': [],
        },
        {
            'id': 'sync-signals',
            'title': 'Signals in the HTTP response',
            'cells': _cells('Signals in the HTTP response', 'always', 'perMessage', 'None', 'Yes'),
            'fields': [
                ('Reply mode', 'mshSignalsOnly'),
                ('Acknowledgment', 'always'),
                ('Signed acknowledgment', 'never'),
                ('Duplicate elimination', 'perMessage'),
                ('Signature algorithm', 'RSA-SHA256'),
            ],
            'tables': [],
        },
        {
            'id': 'unsigned-best-effort',
            'title': 'Unsigned, best effort',
            'cells': _cells('Unsigned, best effort', 'never', 'never', 'None', 'No'),
            'fields': [
                ('Reply mode', 'none'),
                ('Acknowledgment', 'never'),
                ('Duplicate elimination', 'never'),
            ],
            'tables': [],
        },
    ],
    'form': [
        _text('Name'),
        _select('Reply mode', ['none', 'mshSignalsOnly', 'signalsOnly', 'responseOnly', 'signalsAndResponse']),
        _select('Acknowledgment', ['perMessage', 'always', 'never']),
        _select('Signed acknowledgment', ['perMessage', 'always', 'never']),
        _select('Duplicate elimination', ['perMessage', 'always', 'never']),
        _number('Retries'),
        _number('Retry interval, seconds'),
        _number('Persist duration, seconds'),
        _select('Message order', ['NotGuaranteed', 'Guaranteed']),
        _checkbox('Signed'),
    ],
}

# ################################################################################################################################
# ################################################################################################################################

def _message(
    message_id:'str',
    time:'str',
    direction:'str',
    partner:'str',
    action:'str',
    state:'str',
    pill:'str',
    attempts:'anylist',
    signals:'anylist',
    ) -> 'anydict':

    cells = _cells(time, direction, partner, action)
    cells.append(_cell(state, pill))

    # The attempts take the shape of the signals below them - the long text first, then the time, then the short value
    attempt_rows = [[outcome, started, attempt] for attempt, started, outcome in attempts]

    out = {
        'id': message_id,
        'title': message_id,
        'cells': cells,
        'fields': [
            ('MessageId', message_id),
            ('Direction', direction),
            ('Partner', partner),
            ('Action', action),
            ('Created', time),
            ('State', state),
        ],
        'tables': [
            {'title': 'Delivery attempts', 'columns': ['Outcome', 'Started', 'Attempt'], 'rows': attempt_rows},
            {'title': 'Signals', 'columns': ['Kind', 'Received', 'Signed'], 'rows': signals},
        ],
    }

    return out

# ################################################################################################################################

messages = {
    'slug': 'messages',
    'title': 'Messages',
    'columns': ['Time', 'Direction', 'Partner', 'Action', 'State'],
    'items': [
        _message('20261023101502.4821@lakeside-health', '2026-10-23 10:15:02', 'Send', 'Acme Medical Supply', 'Submit',
            'Delivered', Pill.Good,
            [['1', '10:15:02', 'HTTP 200']],
            [['Acknowledgment', '10:15:03', 'Yes']]),
        _message('20261023101144.9930@lakeside-health', '2026-10-23 10:11:44', 'Send', 'Acme Medical Supply', 'Submit',
            'Retrying', Pill.Warning,
            [['1', '10:11:44', 'HTTP 503 Service Unavailable'], ['2', '10:12:44', 'Connection timed out']],
            []),
        _message('8c1f0e2a7b@acme-medical', '2026-10-23 10:09:31', 'Receive', 'Acme Medical Supply', 'Confirm',
            'Delivered', Pill.Good,
            [],
            [['Acknowledgment', '10:09:31', 'Yes']]),
        _message('8c1f0e2a7b-2@acme-medical', '2026-10-23 10:09:58', 'Receive', 'Acme Medical Supply', 'Confirm',
            'Duplicate', Pill.Info,
            [],
            [['Acknowledgment', '10:09:58', 'Yes']]),
        _message('NW-20261023-0042', '2026-10-23 09:58:12', 'Receive', 'Northwind Logistics', 'Shipping notice',
            'Delivered', Pill.Good,
            [],
            [['MDN', '09:58:12', 'Yes']]),
        _message('20261023094007.1177@lakeside-health', '2026-10-23 09:40:07', 'Send', 'Riverside Pharmacy Group', 'Submit',
            'Failed', Pill.Warning,
            [['1', '09:40:07', 'No receipt'], ['2', '09:55:07', 'No receipt'], ['3', '10:10:07', 'No receipt']],
            [['Error EBMS:0301 MissingReceipt', '10:10:09', 'No']]),
    ],
    'form': [],
}

# ################################################################################################################################
# ################################################################################################################################

def _centered(rows:'anylist') -> 'anylist':

    out:'anylist' = []

    for index in range(len(rows[0])):
        lengths = [len(row[index]) for row in rows]
        if max(lengths) <= _centered_max_length:
            out.append(index)

    return out

# ################################################################################################################################
# ################################################################################################################################

sections:'dictlist' = [agreements, partners, local_parties, certificates, channel_profiles, messages]

for section in sections:

    section_rows = [[cell['text'] for cell in item['cells']] for item in section['items']]
    section['centered'] = _centered(section_rows)

    # Tables of the same title are measured together, so that one column is centered in all of them or in none
    table_rows:'anydict' = {}

    for item in section['items']:
        for table in item['tables']:
            table_rows.setdefault(table['title'], []).extend(table['rows'])

    for item in section['items']:
        for table in item['tables']:
            table['centered'] = _centered(table_rows[table['title']])

# ################################################################################################################################
# ################################################################################################################################
