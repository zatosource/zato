# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.sample.agreements import Agreements, Registrations
from zato.common.b2b.portal.sample.common import action, cell, chip, choice, column, counted, days_from_now, fields, href, id_column, item, \
    mono, Path_CPAs, Path_Messages, Path_Partners, Path_Registrations, section, tab, table, timestamp, typed
from zato.common.b2b.portal.sample.parties import DUNS_Type, endpoint, Partner_Role, Partners
from zato.common.b2b.portal.sample.section_messages import state_chip
from zato.common.b2b.portal.sample.traffic import Messages

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.portal.sample.parties import Partner
    from zato.common.typing_ import anydict, anylist, dictlist
    Partner = Partner

# ################################################################################################################################
# ################################################################################################################################


# A certificate is reported as expiring this many days before its end of validity
_expiry_warning_days = 30

# How many of the most recent messages of a partner its detail pane lists
_recent_message_count = 8

_categories = sorted({partner.category for partner in Partners})

# ################################################################################################################################
# ################################################################################################################################

def _certificate(name:'str', usage:'str', days_left:'int') -> 'anylist':

    if days_left < _expiry_warning_days:
        state = chip('Expires soon', tip=counted(days_left, 'day left', 'days left'))
    else:
        state = chip('Valid')

    out = [mono(name), usage, typed(days_from_now(days_left), 'date'), state]
    return out

# ################################################################################################################################

def _overview(partner:'Partner') -> 'anylist':

    rows = [
        ('Name', partner.name),
        ('State', chip(partner.state, role='state')),
        ('PartyId', mono(partner.duns)),
        ('Role', mono(Partner_Role)),
        ('Category', choice(partner.category, _categories)),
        ('Endpoint', typed(endpoint(partner), 'url', is_mono=True)),
        ('Contact', partner.contact),
        ('Email', typed(partner.email, 'email', is_mono=True)),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _identifiers(partner:'Partner') -> 'anylist':

    rows = [
        [mono(partner.duns), mono(DUNS_Type), mono(Partner_Role)],
        [mono(partner.host), mono('urn:lorem-ipsum:partyid-type:host'), mono(Partner_Role)],
    ]

    out = [table('', ['PartyId', 'Type', 'Role'], rows, is_editable=True)]
    return out

# ################################################################################################################################

def _certificates(partner:'Partner') -> 'anylist':

    rows = [
        _certificate(f'{partner.key}-signing-2026', 'Signing', partner.signing_days_left),
        _certificate(f'{partner.key}-tls-2026', 'TLS client', partner.tls_days_left),
    ]

    out = [
        table('', ['Name', 'Usage', 'Valid to', 'State'], rows, is_editable=True),
        fields('', [('Subject', mono(f'CN={partner.host}, O={partner.name}, C=US'))], is_editable=True),
    ]
    return out

# ################################################################################################################################

def _agreements(partner:'Partner') -> 'anylist':

    agreement_rows:'anylist' = []

    for agreement in Agreements:
        if agreement.partner_key == partner.key:
            agreement_rows.append([
                mono(agreement.cpa_id, href=href(Path_CPAs, agreement.cpa_id)),
                days_from_now(agreement.end_days),
                chip(agreement.state),
            ])

    registration_rows:'anylist' = []

    for registration in Registrations:
        if registration.partner_key == partner.key:
            registration_rows.append([
                mono(registration.number, href=href(Path_Registrations, registration.number)),
                registration.product,
                chip(registration.state),
            ])

    out:'anylist' = []

    if agreement_rows:
        out.append(table('CPAs', [id_column('CPAId'), 'Valid to', 'State'], agreement_rows))

    if registration_rows:
        out.append(table('Registrations', ['Registration', 'Product', 'State'], registration_rows))

    return out

# ################################################################################################################################

def _messages(partner:'Partner') -> 'anylist':

    rows:'anylist' = []

    for message in Messages:
        if message['partner_key'] == partner.key:
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

    if state == 'Active':
        out.append(action('Suspend', state='Suspended'))
    elif state == 'Suspended':
        out.append(action('Resume', state='Active', is_primary=True))
    elif state == 'Onboarding':
        out.append(action('Activate', state='Active', is_primary=True))

    return out

# ################################################################################################################################

def _item(partner:'Partner') -> 'anydict':

    agreement_count = 0

    for agreement in Agreements:
        if agreement.partner_key == partner.key:
            agreement_count += 1

    out = item(
        partner.key,
        title=partner.name,
        cells=[
            cell(partner.name),
            mono(partner.duns),
            cell(partner.category),
            mono(endpoint(partner)),
            cell(str(agreement_count)),
            chip(partner.state, role='state'),
        ],
        attributes={
            'state': partner.state,
        },
        search=[partner.name, partner.duns, partner.host, partner.contact, partner.category],
        tabs=[
            tab('overview', 'Overview', _overview(partner)),
            tab('identifiers', 'Identifiers', _identifiers(partner)),
            tab('certificates', 'Certificates', _certificates(partner)),
            tab('agreements', 'Agreements', _agreements(partner)),
            tab('messages', 'Messages', _messages(partner)),
        ],
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def build() -> 'anydict':

    items:'dictlist' = []

    for partner in Partners:
        items.append(_item(partner))

    out = section(
        slug='partners',
        path=Path_Partners,
        title='Trading partners',
        columns=[
            column('Name'),
            column('PartyId', is_narrow=True),
            column('Category', is_narrow=True),
            column('Endpoint'),
            column('CPAs', is_narrow=True),
            column('State', is_narrow=True),
        ],
        items=items,
        actions_of=_actions,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################
