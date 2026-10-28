# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.config import Local_Organization, Local_Party_ID, Local_Role
from zato.common.b2b.portal.sample.agreements import Agreements
from zato.common.b2b.portal.sample.common import action, cell, chip, choice, column, days_from_now, direction_cell, \
    duration_value, fields, href, id_column, item, link, mono, number_value, Path_CPAs, Path_Messages, Path_Partners, section, \
    seconds_value, tab, table, timestamp, typed, yes_no
from zato.common.b2b.portal.sample.parties import DUNS_Type, duration, endpoint, Partner_By_Key, Partner_Role, \
    Service_By_Name
from zato.common.b2b.portal.sample.section_messages import state_chip
from zato.common.b2b.portal.sample.traffic import Messages

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.portal.sample.agreements import Agreement
    from zato.common.typing_ import anydict, anylist, dictlist
    Agreement = Agreement

# ################################################################################################################################
# ################################################################################################################################


_signature_algorithm = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
_digest_algorithm    = 'http://www.w3.org/2001/04/xmlenc#sha256'

_signature_algorithms = [_signature_algorithm, 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha512']
_digest_algorithms    = [_digest_algorithm, 'http://www.w3.org/2001/04/xmlenc#sha512']

_tls_versions = ['TLS 1.2', 'TLS 1.3']

_sync_reply_modes = ['mshSignalsOnly', 'signalsOnly', 'responseOnly', 'signalsAndResponse', 'none']

_message_orders = ['Guaranteed', 'NotGuaranteed']

# How many of the most recent messages of an agreement its detail pane lists
_recent_message_count = 8

# ################################################################################################################################
# ################################################################################################################################

def _overview(agreement:'Agreement') -> 'anylist':

    partner = Partner_By_Key[agreement.partner_key]

    rows = [
        ('CPAId', mono(agreement.cpa_id)),
        ('State', chip(agreement.state, role='state')),
        ('Version', number_value(agreement.version)),
        ('Valid from', typed(days_from_now(agreement.start_days), 'date')),
        ('Valid to', typed(days_from_now(agreement.end_days), 'date')),
        ('Partner', link(partner.name, href(Path_Partners, partner.key))),
        ('Endpoint', typed(endpoint(partner), 'url', is_mono=True)),
    ]

    parties = table('Parties', ['Party', 'PartyId', 'Role'], [
        [Local_Organization, mono(Local_Party_ID), mono(Local_Role)],
        [partner.name, mono(partner.duns), mono(Partner_Role)],
    ], is_editable=True)

    out = [fields('', rows, is_editable=True), parties, fields('', [('PartyId type', mono(DUNS_Type))], is_editable=True)]
    return out

# ################################################################################################################################

def _transactions(agreement:'Agreement') -> 'anylist':

    rows:'anylist' = []

    for name in agreement.services:

        service = Service_By_Name[name]

        # A notification is sent by us, a request by the partner
        direction = 'Outbound' if service.is_notification else 'Inbound'

        if service.receipt_seconds:
            receipt = chip('Required', tip='timeToAcknowledgeReceipt ' + duration(service.receipt_seconds))
        else:
            receipt = chip('Not required')

        perform = seconds_value(service.perform_seconds)
        response = mono(service.response) if service.response else cell('None')

        rows.append([mono(service.name), mono(service.request), direction_cell(direction), response, receipt, perform])

    out = [table('', ['Service', 'Action', 'Direction', 'Response', 'Receipt', 'Time to perform'], rows, is_editable=True)]
    return out

# ################################################################################################################################

def _reliability(agreement:'Agreement') -> 'anylist':

    rows = [
        ('Acknowledgment', chip('Required')),
        ('Signed acknowledgment', yes_no(agreement.is_signed_ack)),
        ('Duplicate elimination', chip('Required')),
        ('Retries', number_value(agreement.retries)),
        ('Retry interval', duration_value(agreement.retry_minutes, 'minutes')),
        ('Persist duration', duration_value(agreement.persist_days, 'days')),
        ('SyncReplyMode', choice(agreement.sync_reply, _sync_reply_modes, is_mono=True)),
        ('Message order', choice('NotGuaranteed', _message_orders, is_mono=True)),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _security(agreement:'Agreement') -> 'anylist':

    partner = Partner_By_Key[agreement.partner_key]
    name = partner.key

    rows = [
        ('Signature', chip('Signed')),
        ('Signature algorithm', choice(_signature_algorithm, _signature_algorithms, is_mono=True)),
        ('Digest algorithm', choice(_digest_algorithm, _digest_algorithms, is_mono=True)),
        ('Non-repudiation', chip('Required')),
        ('TLS', choice(agreement.tls_version, _tls_versions)),
        ('Client authentication', chip('Required')),
        ('Partner signing certificate', mono(f'{name}-signing-2026')),
        ('Partner TLS certificate', mono(f'{name}-tls-2026')),
        ('Local signing certificate', mono('lorem-signing-2026')),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _messages(agreement:'Agreement') -> 'anylist':

    rows:'anylist' = []

    for message in Messages:
        if message['cpa_id'] == agreement.cpa_id:
            rows.append([
                mono(message['id'], href=href(Path_Messages, message['key'])),
                timestamp(message['moment']),
                state_chip(message),
                mono(message['action']),
            ])

    rows = rows[:_recent_message_count]

    if rows:
        out = [table('', [id_column('MessageId'), 'Time', 'State', 'Action'], rows)]
    else:
        out = [fields('', [('Messages', 'None')])]

    return out

# ################################################################################################################################
# ################################################################################################################################

def _actions(state:'str') -> 'anylist':

    out:'anylist' = []

    if state in ('Active', 'Expiring'):
        out.append(action('Suspend', state='Suspended'))
    elif state == 'Suspended':
        out.append(action('Resume', state='Active', is_primary=True))
    elif state == 'Proposed':
        out.append(action('Agree', state='Agreed', is_primary=True))
        out.append(action('Delete', is_remove=True))
    elif state == 'Agreed':
        out.append(action('Activate', state='Active', is_primary=True))

    return out

# ################################################################################################################################

def _item(agreement:'Agreement') -> 'anydict':

    partner = Partner_By_Key[agreement.partner_key]
    service_count = len(agreement.services)

    out = item(
        agreement.cpa_id,
        title=agreement.cpa_id,
        cells=[
            mono(agreement.cpa_id),
            cell(partner.name),
            cell(agreement.product),
            cell(str(service_count)),
            cell(days_from_now(agreement.end_days)),
            chip(agreement.state, role='state'),
        ],
        attributes={
            'state': agreement.state,
            'partner': partner.key,
        },
        search=[agreement.cpa_id, partner.name, partner.duns, *agreement.services],
        tabs=[
            tab('overview', 'Overview', _overview(agreement)),
            tab('transactions', 'Transactions', _transactions(agreement)),
            tab('reliability', 'Reliability', _reliability(agreement)),
            tab('security', 'Security', _security(agreement)),
            tab('messages', 'Messages', _messages(agreement)),
        ],
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def build() -> 'anydict':

    items:'dictlist' = []

    for agreement in Agreements:
        items.append(_item(agreement))

    out = section(
        slug='cpas',
        path=Path_CPAs,
        title='CPAs',
        columns=[
            column('CPAId'),
            column('Partner'),
            column('Product', is_narrow=True),
            column('Transactions', is_narrow=True),
            column('Valid to', is_narrow=True),
            column('State', is_narrow=True),
        ],
        items=items,
        actions_of=_actions,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################
