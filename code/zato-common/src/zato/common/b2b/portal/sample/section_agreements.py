# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.sample.agreements import Agreements
from zato.common.b2b.portal.sample.common import action, cell, chip, column, days_from_now, direction_cell, fields, fixed, \
    href, id_column, item, link, mono, number_value, Path_Agreements, Path_Messages, Path_Partners, section, seconds_value, \
    tab, table, timestamp, typed
from zato.common.b2b.portal.sample.parties import duration, endpoint, Partner_By_Key, Service_By_Name
from zato.common.b2b.portal.sample.protocol.common import Vocabularies
from zato.common.b2b.portal.sample.protocol.views import Views_By_Protocol
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

# How many of the most recent messages of an agreement its detail pane lists
_recent_message_count = 8

# ################################################################################################################################
# ################################################################################################################################

def _overview(agreement:'Agreement') -> 'anylist':

    partner = Partner_By_Key[agreement.partner_key]
    vocabulary = Vocabularies[agreement.protocol]
    views = Views_By_Protocol[agreement.protocol]

    rows = [
        (vocabulary.agreement_label, mono(agreement.agreement_id)),
        ('Protocol', fixed(agreement.protocol)),
        ('State', chip(agreement.state, role='state')),
        ('Version', number_value(agreement.version)),
        ('Valid from', typed(days_from_now(agreement.start_days), 'date')),
        ('Valid to', typed(days_from_now(agreement.end_days), 'date')),
        ('Partner', link(partner.name, href(Path_Partners, partner.key))),
        ('Endpoint', typed(endpoint(partner), 'url', is_mono=True)),
    ]

    out = [fields('', rows, is_editable=True)]
    out.extend(views.agreement_parties(agreement))

    return out

# ################################################################################################################################

def _transactions(agreement:'Agreement') -> 'anylist':

    vocabulary = Vocabularies[agreement.protocol]
    rows:'anylist' = []

    # The protocols with business signals have a receipt acknowledgement of their own, under AS2 the MDN is the receipt
    columns = ['Service', 'Action', 'Direction', 'Response']

    if vocabulary.has_business_signals:
        columns.append('Receipt')
        columns.append('Acceptance')

    columns.append('Time to perform')

    for name in agreement.services:

        service = Service_By_Name[name]

        # A notification is sent by us, a request by the partner
        direction = 'Outbound' if service.is_notification else 'Inbound'
        response = mono(service.response) if service.response else cell('None')

        row = [mono(service.name), mono(service.request), direction_cell(direction), response]

        if vocabulary.has_business_signals:
            if service.receipt_seconds:
                row.append(chip('Required', tip='timeToAcknowledgeReceipt ' + duration(service.receipt_seconds)))
            else:
                row.append(chip('Not required'))

            if service.acceptance_seconds:
                acceptance_tip = 'timeToAcknowledgeAcceptance ' + duration(service.acceptance_seconds)
                row.append(chip('Required', tip=acceptance_tip))
            else:
                row.append(chip('Not required'))

        row.append(seconds_value(service.perform_seconds))
        rows.append(row)

    out = [table('', columns, rows, is_editable=True)]
    return out

# ################################################################################################################################

def _messages(agreement:'Agreement') -> 'anylist':

    rows:'anylist' = []

    for message in Messages:
        if message['agreement_id'] == agreement.agreement_id:
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
    views = Views_By_Protocol[agreement.protocol]
    service_count = len(agreement.services)

    tabs = [
        tab('overview', 'Overview', _overview(agreement)),
        tab('transactions', 'Transactions', _transactions(agreement)),
    ]

    tabs.extend(views.agreement_tabs(agreement))
    tabs.append(tab('messages', 'Messages', _messages(agreement)))

    out = item(
        agreement.agreement_id,
        title=agreement.agreement_id,
        cells=[
            mono(agreement.agreement_id),
            cell(partner.name),
            cell(agreement.protocol),
            cell(agreement.product),
            cell(str(service_count)),
            cell(days_from_now(agreement.end_days)),
            chip(agreement.state, role='state'),
        ],
        attributes={
            'state': agreement.state,
            'partner': partner.key,
            'protocol': agreement.protocol,
        },
        search=[agreement.agreement_id, partner.name, partner.duns, agreement.protocol, *agreement.services],
        tabs=tabs,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def build() -> 'anydict':

    items:'dictlist' = []

    for agreement in Agreements:
        items.append(_item(agreement))

    out = section(
        slug='agreements',
        path=Path_Agreements,
        title='Agreements',
        columns=[
            column('Agreement'),
            column('Partner'),
            column('Protocol', is_narrow=True),
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
