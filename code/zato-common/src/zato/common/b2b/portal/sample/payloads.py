# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.config import Local_Party_ID, Local_Role
from zato.common.b2b.portal.sample.common import envelope_timestamp
from zato.common.b2b.portal.sample.parties import Complaints_Product, Partner_By_Key, Partner_Role, Service_By_Name
from zato.common.b2b.portal.sample.traffic import Conversation_By_ID, Kind

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist, strtuple

# ################################################################################################################################
# ################################################################################################################################

# The Content-ID, the Content-Type and the text of each part of a multipart message
mime_part_list = list[tuple[str, str, str]]

# ################################################################################################################################
# ################################################################################################################################

_business_namespace = 'urn:pinecrest-telecom:b2b:v2'
_signals_namespace  = 'http://www.ebxml.org/bpss/signals'

# HTTP and MIME end each line with a carriage return and a line feed
CRLF = '\r\n'

# What each business response and notification reports back, by its service
_outcomes = {
    'SubmitOrderv2':             ('OrderStatus', 'Order Pending'),
    'ChangeOrderv2':             ('OrderStatus', 'Order Change Pending'),
    'CancelOrderv2':             ('OrderStatus', 'Order Cancellation Pending'),
    'ScheduleInstallationv2':    ('InstallationStatus', 'Installation Scheduled'),
    'QueryOrderDetailsv2':       ('OrderStatus', 'Order Confirmed'),
    'NotifyOfOrderStatusv2':     ('OrderStatus', 'Order Confirmed'),
    'FileComplaintv2':           ('ComplaintStatus', 'Complaint Received'),
    'EscalateComplaintv2':       ('ComplaintStatus', 'Complaint Escalated'),
    'NotifyOfComplaintStatusv2': ('ComplaintStatus', 'Technician Assigned'),
}

# ################################################################################################################################
# ################################################################################################################################

def parties(message:'anydict') -> 'strtuple':
    """ The party IDs and the roles of the sender and of the receiver of a message.
    """
    partner = Partner_By_Key[message['partner_key']]

    if message['direction'] == 'Inbound':
        out = (partner.duns, Partner_Role, Local_Party_ID, Local_Role)
    else:
        out = (Local_Party_ID, Local_Role, partner.duns, Partner_Role)

    return out

# ################################################################################################################################

def answered(message:'anydict') -> 'anydict':
    """ The message of the same conversation that the message refers to.
    """
    conversation = Conversation_By_ID[message['conversation_id']]

    for each in conversation['messages']:
        if each['id'] == message['ref_to']:
            out = each
            break
    else:
        raise Exception(f'No message `{message["ref_to"]}` in `{message["conversation_id"]}`')

    return out

# ################################################################################################################################

def _signal(message:'anydict') -> 'str':
    """ The business document of a business signal, which names the message it answers.
    """
    action = message['action']
    stamp = envelope_timestamp(message['moment'])

    lines:'strlist' = [
        f'<bs:{action} xmlns:bs="{_signals_namespace}">',
        f'  <bs:OriginalMessageIdentifier>{message["ref_to"]}</bs:OriginalMessageIdentifier>',
        f'  <bs:ThisMessageDateTime>{stamp}</bs:ThisMessageDateTime>',
    ]

    if message['error']:
        lines.append(f'  <bs:ExceptionType>{message["error_code"]}</bs:ExceptionType>')
        lines.append(f'  <bs:Reason>{message["error"]}</bs:Reason>')

    lines.append(f'</bs:{action}>')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def _business(message:'anydict') -> 'str':
    """ The business document of a request, of a response or of a notification.
    """
    action = message['action']
    from_id, _, to_id, _ = parties(message)
    stamp = envelope_timestamp(message['moment'])

    lines:'strlist' = [
        f'<b2b:{action} xmlns:b2b="{_business_namespace}">',
        '  <b2b:Header>',
        f'    <b2b:SenderDUNS>{from_id}</b2b:SenderDUNS>',
        f'    <b2b:ReceiverDUNS>{to_id}</b2b:ReceiverDUNS>',
        f'    <b2b:Created>{stamp}</b2b:Created>',
        '  </b2b:Header>',
        f'  <b2b:Reference>{message["reference"]}</b2b:Reference>',
    ]

    if message['kind'] == Kind.Document:

        # A complaint describes the problem, an order what is being bought and where it is installed
        if Service_By_Name[message['service']].product == Complaints_Product:
            lines.append('  <b2b:Category>Intermittent connectivity</b2b:Category>')
            lines.append('  <b2b:Severity>Major</b2b:Severity>')
            lines.append('  <b2b:ServiceAddress>')
            lines.append('    <b2b:Line>42 Harbor Street</b2b:Line>')
            lines.append('    <b2b:City>Portland</b2b:City>')
            lines.append('    <b2b:State>OR</b2b:State>')
            lines.append('    <b2b:PostalCode>97201</b2b:PostalCode>')
            lines.append('  </b2b:ServiceAddress>')
            lines.append('  <b2b:Reported>' + stamp[:10] + '</b2b:Reported>')

        else:
            lines.append('  <b2b:Product>Business Fiber 500</b2b:Product>')
            lines.append('  <b2b:InstallationAddress>')
            lines.append('    <b2b:Line>42 Harbor Street</b2b:Line>')
            lines.append('    <b2b:City>Portland</b2b:City>')
            lines.append('    <b2b:State>OR</b2b:State>')
            lines.append('    <b2b:PostalCode>97201</b2b:PostalCode>')
            lines.append('  </b2b:InstallationAddress>')
            lines.append('  <b2b:RequiredDate>' + stamp[:10] + '</b2b:RequiredDate>')

    else:
        element, status = _outcomes[message['service']]
        lines.append(f'  <b2b:{element}>{status}</b2b:{element}>')

    lines.append(f'</b2b:{action}>')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def payload(message:'anydict') -> 'str':
    """ The business document of a message, which is empty for the messages of the messaging layer.
    """
    kind = message['kind']

    if kind in (Kind.Ack, Kind.Error):
        out = ''
    elif kind == Kind.Signal:
        out = _signal(message)
    else:
        out = _business(message)

    return out

# ################################################################################################################################

def mime_message(parts:'mime_part_list', boundary:'str') -> 'str':
    """ The body of a multipart message, each part a triple of its Content-ID, its Content-Type and its text.
    """
    lines:'strlist' = []

    for content_id, content_type, text in parts:
        lines.append(f'--{boundary}')
        lines.append(f'Content-ID: <{content_id}>')
        lines.append(f'Content-Type: {content_type}')
        lines.append('')
        lines.append(text.replace('\n', CRLF))

    lines.append(f'--{boundary}--')
    lines.append('')

    out = CRLF.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################
