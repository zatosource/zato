# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from zato.common.b2b.portal.sample.agreements import Agreements
from zato.common.b2b.portal.sample.common import action, aside, cell, chip, choice, choices, column, fields, href, item, link, \
    minutes_ago, mono, Path_Agreements, Path_Alerts, Path_Messages, Path_Partners, Path_Registrations, section, tab, table, \
    timestamp
from zato.common.b2b.portal.sample.parties import Partner_By_Key
from zato.common.b2b.portal.sample.protocol.common import Vocabularies
from zato.common.b2b.portal.sample.section_messages import state_chip
from zato.common.b2b.portal.sample.traffic import Messages

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

Path_Alert_Rules = '/alert-rules'

# ################################################################################################################################
# ################################################################################################################################

class Alert(NamedTuple):
    number: str
    level: str
    state: str
    minutes_ago: int
    event: str
    rule: str
    partner_key: str
    text: str
    message_match: str
    agreement_product: str
    registration: str

# ################################################################################################################################

class Rule(NamedTuple):
    key: str
    name: str
    event: str
    level: str
    state: str
    condition: str
    channels: 'strlist'
    recipients: 'strlist'

# ################################################################################################################################
# ################################################################################################################################

Rules = [
    Rule('delivery-failed', 'Undelivered messages', 'Delivery failed', 'Error', 'Enabled',
        'All retries of the agreement exhausted', ['Portal', 'Email', 'Webhook'],
        ['b2b-operations@pinecrest-telecom.example.com', 'https://hooks.pinecrest-telecom.example.com/b2b']),
    Rule('delivery-retrying', 'Retried deliveries', 'Delivery retrying', 'Warning', 'Enabled',
        'Second attempt failed', ['Portal'], []),
    Rule('signature', 'Signature verification', 'Signature verification failed', 'Error', 'Enabled',
        'Any message', ['Portal', 'Email'], ['b2b-security@pinecrest-telecom.example.com']),
    Rule('receipt-overdue', 'Overdue receipts', 'Receipt overdue', 'Warning', 'Enabled',
        'timeToAcknowledgeReceipt exceeded', ['Portal', 'Email'], ['b2b-operations@pinecrest-telecom.example.com']),
    Rule('signal-exception', 'Business signal exceptions', 'Business signal exception', 'Warning', 'Enabled',
        'ReceiptAcknowledgementException or AcceptanceAcknowledgementException', ['Portal'], []),
    Rule('certificate-expiry', 'Certificate expiry', 'Certificate expiring', 'Warning', 'Enabled',
        '30 days before the end of validity', ['Portal', 'Email'], ['pki@pinecrest-telecom.example.com']),
    Rule('agreement-expiry', 'Agreement expiry', 'Agreement expiring', 'Warning', 'Enabled',
        '30 days before the end of validity', ['Portal', 'Email'], ['b2b-onboarding@pinecrest-telecom.example.com']),
    Rule('duplicate', 'Duplicate messages', 'Duplicate eliminated', 'Information', 'Enabled',
        'Any message', ['Portal'], []),
    Rule('registration', 'Registration requests', 'Registration submitted', 'Information', 'Enabled',
        'Any registration', ['Portal', 'Email'], ['b2b-onboarding@pinecrest-telecom.example.com']),
    Rule('response-overdue', 'Overdue responses', 'Response overdue', 'Warning', 'Disabled',
        'timeToPerform exceeded', ['Portal'], []),
]

Rule_By_Key = {}

for _rule in Rules:
    Rule_By_Key[_rule.key] = _rule

_events = [rule.event for rule in Rules]

_channels = ['Portal', 'Email', 'Webhook']

_partner_scopes = ['All'] + [partner.name for partner in Partner_By_Key.values()]

# ################################################################################################################################

Alerts = [
    Alert('10442', 'Error',       'Open',         253, 'Delivery failed', 'delivery-failed', 'redwood',
        'No receipt for NotifyOfOrderStatusv2 after 3 retries', 'EBMS:0202', '', ''),
    Alert('10447', 'Warning',     'Open',         17,  'Delivery retrying', 'delivery-retrying', 'lakeshore',
        'NotifyOfOrderStatusv2 failed twice, next retry scheduled', 'Retrying', '', ''),
    Alert('10445', 'Error',       'Open',         75,  'Signature verification failed', 'signature', 'prairie',
        'rqSubmitOrder refused, the signature does not verify', 'authentication-failed', '', ''),
    Alert('10439', 'Warning',     'Open',         895, 'Receipt overdue', 'receipt-overdue', 'harborlight',
        'No ReceiptAcknowledgement for NotifyOfComplaintStatus within 5 minutes', 'TimeToAcknowledgeReceipt', '', ''),
    Alert('10444', 'Warning',     'Acknowledged', 38,  'Business signal exception', 'signal-exception', 'redwood',
        'AcceptanceAcknowledgementException sent for rqCancelOrder', 'OrderNotCancellable', '', ''),
    Alert('10441', 'Warning',     'Open',         140, 'Business signal exception', 'signal-exception', 'harborlight',
        'ReceiptAcknowledgementException sent for rqFileComplaint', 'InvalidContent', '', ''),
    Alert('10436', 'Warning',     'Open',         1310, 'Certificate expiring', 'certificate-expiry', 'redwood',
        'Signing certificate redwood-signing-2026 expires in 9 days', '', '', ''),
    Alert('10431', 'Warning',     'Acknowledged', 2650, 'Certificate expiring', 'certificate-expiry', 'coppercreek',
        'Signing certificate coppercreek-signing-2026 expires in 27 days', '', '', ''),
    Alert('10433', 'Warning',     'Open',         1890, 'Agreement expiring', 'agreement-expiry', 'lakeshore',
        'Partnership version 1 of Lakeshore Communications expires in 18 days', '', 'Orders', ''),
    Alert('10443', 'Information', 'Acknowledged', 95,  'Duplicate eliminated', 'duplicate', 'harborlight',
        'rqChangeOrder received twice with the same MessageId', 'DuplicateElimination', '', ''),
    Alert('10446', 'Information', 'Open',         1440, 'Registration submitted', 'registration', 'lakeshore',
        '2026-0121 submitted for review', '', '', '2026-0121'),
]

# ################################################################################################################################
# ################################################################################################################################

def _message(partner_key:'str', match:'str') -> 'anydict':
    """ The most recent message of a partner with the given error code or, if no message has one, in the given state.
    """
    for message in Messages:
        if message['partner_key'] == partner_key:
            if message['error_code'] == match:
                out = message
                break
            if message['state'] == match:
                out = message
                break
    else:
        raise Exception(f'No message of `{partner_key}` matching `{match}`')

    return out

# ################################################################################################################################

def _agreement_id(partner_key:'str', product:'str') -> 'str':

    for agreement in Agreements:
        if agreement.partner_key == partner_key:
            if agreement.product == product:
                out = agreement.agreement_id
                break
    else:
        raise Exception(f'No agreement of `{partner_key}` for `{product}`')

    return out

# ################################################################################################################################

def _subject(alert:'Alert') -> 'anylist':
    """ The field naming what the alert was raised about and the field of its partner, which for a message
    is led by the state of the message, as that names the partner in words of its own.
    """
    partner = Partner_By_Key[alert.partner_key]
    partner_link = link(partner.name, href(Path_Partners, partner.key))

    if alert.message_match:
        message = _message(alert.partner_key, alert.message_match)
        subject = ('MessageId', mono(message['id'], href=href(Path_Messages, message['key'])))
        partner_row = ('Partner', [state_chip(message), partner_link])

    elif alert.agreement_product:
        vocabulary = Vocabularies[partner.protocol]
        agreement_id = _agreement_id(alert.partner_key, alert.agreement_product)
        subject = (vocabulary.agreement_label, mono(agreement_id, href=href(Path_Agreements, agreement_id)))
        partner_row = ('Partner', partner_link)

    else:
        subject = ('Registration', mono(alert.registration, href=href(Path_Registrations, alert.registration)))
        partner_row = ('Partner', partner_link)

    out = [subject, partner_row]
    return out

# ################################################################################################################################

def _alert_actions(state:'str') -> 'anylist':

    out:'anylist' = []

    if state == 'Open':
        out.append(action('Acknowledge', state='Acknowledged', is_primary=True))

    out.append(action('Delete', is_remove=True))

    return out

# ##############################################################################################################################

def _alert_item(alert:'Alert') -> 'anydict':

    partner = Partner_By_Key[alert.partner_key]
    rule = Rule_By_Key[alert.rule]
    raised = timestamp(minutes_ago(alert.minutes_ago))

    subject, partner_row = _subject(alert)

    overview = fields('', [
        ('Alert', [mono(alert.number), chip(alert.level), chip(alert.state, role='state'), aside(raised)]),
        subject,
        ('Description', alert.text),
        ('Rule', link(rule.name, href(Path_Alert_Rules, rule.key))),
        partner_row,
    ])

    out = item(
        alert.number,
        title=alert.event,
        cells=[
            mono(alert.number),
            chip(alert.level),
            chip(alert.state, role='state'),
            cell(raised),
            cell(alert.event),
            cell(partner.name),
            cell(alert.text),
        ],
        attributes={
            'level': alert.level,
            'state': alert.state,
        },
        search=[alert.number, alert.event, alert.text, partner.name],
        tabs=[
            tab('overview', 'Overview', [overview]),
        ],
    )
    return out

# ################################################################################################################################

def _rule_actions(state:'str') -> 'anylist':

    if state == 'Enabled':
        out = [action('Disable', state='Disabled')]
    else:
        out = [action('Enable', state='Enabled', is_primary=True)]

    out.append(action('Delete', is_remove=True))

    return out

# ##############################################################################################################################

def _recipients(rule:'Rule') -> 'anylist':
    """ Each address the rule notifies, or a single None if it notifies no one but the portal itself.
    """
    out:'anylist' = []

    for recipient in rule.recipients:
        out.append(mono(recipient))

    if not out:
        out.append('None')

    return out

# ##############################################################################################################################

def _rule_item(rule:'Rule') -> 'anydict':

    raised:'anylist' = []

    for alert in Alerts:
        if alert.rule == rule.key:
            raised.append([
                mono(alert.number, href=href(Path_Alerts, alert.number)),
                timestamp(minutes_ago(alert.minutes_ago)),
                chip(alert.state),
            ])

    overview = fields('', [
        ('Rule', rule.name),
        ('Level', chip(rule.level)),
        ('State', chip(rule.state, role='state')),
        ('Event', choice(rule.event, _events)),
        ('Condition', rule.condition),
        ('Partners', choice('All', _partner_scopes)),
        ('Channels', choices(rule.channels, _channels)),
        ('Recipients', _recipients(rule)),
    ], is_editable=True)

    if raised:
        history = [table('', ['Alert', 'Raised', 'State'], raised)]
    else:
        history = [fields('', [('Alerts', 'None')])]

    out = item(
        rule.key,
        title=rule.name,
        cells=[
            cell(rule.name),
            cell(rule.event),
            chip(rule.level),
            chip(rule.state, role='state'),
            cell(', '.join(rule.channels)),
        ],
        attributes={
            'level': rule.level,
            'state': rule.state,
        },
        search=[rule.name, rule.event, rule.condition],
        tabs=[
            tab('overview', 'Overview', [overview]),
            tab('alerts', 'Alerts', history),
        ],
    )
    return out

# ################################################################################################################################
# ################################################################################################################################

def _by_minutes(alert:'Alert') -> 'int':
    return alert.minutes_ago

# ################################################################################################################################

def build_alerts() -> 'anydict':

    items:'dictlist' = []

    for alert in sorted(Alerts, key=_by_minutes):
        items.append(_alert_item(alert))

    out = section(
        slug='alerts',
        path=Path_Alerts,
        title='Alerts',
        columns=[
            column('Alert', is_narrow=True),
            column('Level', is_narrow=True),
            column('State', is_narrow=True),
            column('Raised', is_narrow=True),
            column('Event'),
            column('Partner'),
            column('Description'),
        ],
        items=items,
        actions_of=_alert_actions,
    )
    return out

# ################################################################################################################################

def build_rules() -> 'anydict':

    items:'dictlist' = []

    for rule in Rules:
        items.append(_rule_item(rule))

    out = section(
        slug='alert-rules',
        path=Path_Alert_Rules,
        title='Alert rules',
        columns=[
            column('Rule'),
            column('Event'),
            column('Level', is_narrow=True),
            column('State', is_narrow=True),
            column('Channels'),
        ],
        items=items,
        actions_of=_rule_actions,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################
