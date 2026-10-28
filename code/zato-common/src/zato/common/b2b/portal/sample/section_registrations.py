# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.config import Local_Organization
from zato.common.b2b.portal.sample.agreements import Agreement_By_ID, Registrations
from zato.common.b2b.portal.sample.common import action, cell, chip, choice, column, days_from_now, delta, direction_cell, \
    fields, fixed, href, item, link, mono, Path_CPAs, Path_Partners, minutes_ago, Path_Registrations, section, tab, table, typed
from zato.common.b2b.portal.sample.parties import cpa_id, endpoint, Partner_By_Key, Partner_Role, Service_By_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.b2b.portal.sample.agreements import Registration
    from zato.common.typing_ import anydict, anylist, dictlist
    Registration = Registration

# ################################################################################################################################
# ################################################################################################################################

_minutes_per_day = 24 * 60

_products = sorted({registration.product for registration in Registrations})

# ################################################################################################################################
# ################################################################################################################################

def _overview(registration:'Registration') -> 'anylist':

    partner = Partner_By_Key[registration.partner_key]
    agreement_id = cpa_id(partner, registration.product, registration.agreement_version)

    if agreement_id in Agreement_By_ID:
        agreement = mono(agreement_id, href=href(Path_CPAs, agreement_id))
    else:
        agreement = cell('Not issued')

    first = registration.events[0]
    last = registration.events[-1]

    rows = [
        ('Registration', mono(registration.number)),
        ('State', chip(registration.state, role='state')),
        ('Partner', link(partner.name, href(Path_Partners, partner.key))),
        ('PartyId', mono(partner.duns)),
        ('Role', mono(Partner_Role)),
        ('Product', choice(registration.product, _products)),
        ('Endpoint', typed(endpoint(partner), 'url', is_mono=True)),
        ('CPAId', agreement),
        ('Requested', fixed(days_from_now(-first.days_ago))),
        ('Last change', fixed(days_from_now(-last.days_ago))),
        ('Requested by', fixed(first.user)),
    ]

    out = [fields('', rows, is_editable=True)]
    return out

# ################################################################################################################################

def _services(registration:'Registration') -> 'anylist':

    rows:'anylist' = []

    for name in registration.services:
        service = Service_By_Name[name]
        direction = 'Outbound' if service.is_notification else 'Inbound'
        rows.append([mono(service.name), service.label, direction_cell(direction)])

    out = [table('', ['Service', 'Business transaction', 'Direction'], rows, is_editable=True)]
    return out

# ################################################################################################################################

def _history(registration:'Registration') -> 'anylist':

    partner = Partner_By_Key[registration.partner_key]
    rows:'anylist' = []
    previous = None

    for event in registration.events:

        # A change is made either by the partner's own contact or by the reviewers of the local organization
        organization = partner.name if event.user == partner.contact else Local_Organization
        person = cell(f'{event.user}, {organization}')

        moment = minutes_ago(event.days_ago * _minutes_per_day)
        rows.append([days_from_now(-event.days_ago), delta(moment, previous), chip(event.state), person, event.note])
        previous = moment

    # The most recent change comes first
    rows.reverse()

    out = [table('', ['Date', 'Delta', 'State', 'Changed by', 'Note'], rows)]
    return out

# ################################################################################################################################

def _actions(state:'str') -> 'anylist':

    out:'anylist' = []

    if state in ('Submitted', 'In review'):
        out.append(action('Approve', state='Approved', is_primary=True))
        out.append(action('Reject', state='Rejected'))
    elif state == 'Approved':
        out.append(action('Activate', state='Active', is_primary=True))
    elif state == 'Active':
        out.append(action('Suspend', state='Suspended'))
    elif state == 'Suspended':
        out.append(action('Resume', state='Active', is_primary=True))
    elif state == 'Draft':
        out.append(action('Submit', state='Submitted', is_primary=True))
        out.append(action('Delete', is_remove=True))

    return out

# ################################################################################################################################

def _item(registration:'Registration') -> 'anydict':

    partner = Partner_By_Key[registration.partner_key]
    first = registration.events[0]

    out = item(
        registration.number,
        title=registration.number,
        cells=[
            mono(registration.number),
            cell(partner.name),
            cell(registration.product),
            cell(days_from_now(-first.days_ago)),
            chip(registration.state, role='state'),
        ],
        attributes={
            'state': registration.state,
            'partner': partner.key,
        },
        search=[registration.number, partner.name, partner.duns, registration.product, *registration.services],
        tabs=[
            tab('overview', 'Overview', _overview(registration)),
            tab('services', 'Services', _services(registration)),
            tab('history', 'History', _history(registration)),
        ],
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def build() -> 'anydict':

    items:'dictlist' = []

    for registration in Registrations:
        items.append(_item(registration))

    out = section(
        slug='registrations',
        path=Path_Registrations,
        title='Registrations',
        columns=[
            column('Registration', is_narrow=True),
            column('Partner'),
            column('Product', is_narrow=True),
            column('Requested', is_narrow=True),
            column('State', is_narrow=True),
        ],
        items=items,
        actions_of=_actions,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################
