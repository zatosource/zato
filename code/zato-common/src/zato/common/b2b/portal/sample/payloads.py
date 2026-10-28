# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.config import Local_Host, Local_Party_ID, Local_Role
from zato.common.b2b.portal.sample.common import envelope_timestamp
from zato.common.b2b.portal.sample.parties import Complaints_Product, DUNS_Type, Partner_By_Key, Partner_Role, Service_By_Name
from zato.common.b2b.portal.sample.traffic import Kind

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist, strtuple

# ################################################################################################################################
# ################################################################################################################################

_business_namespace = 'urn:pinecrest-telecom:b2b:v2'
_signals_namespace  = 'http://www.ebxml.org/bpss/signals'

# HTTP and MIME end each line with a carriage return and a line feed
_crlf = '\r\n'

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

def _parties(message:'anydict') -> 'strtuple':
    """ The party IDs and the roles of the sender and of the receiver of a message.
    """
    partner = Partner_By_Key[message['partner_key']]

    if message['direction'] == 'Inbound':
        out = (partner.duns, Partner_Role, Local_Party_ID, Local_Role)
    else:
        out = (Local_Party_ID, Local_Role, partner.duns, Partner_Role)

    return out

# ################################################################################################################################

def envelope(message:'anydict') -> 'str':
    """ The SOAP envelope of a message, with its ebXML message header and, when it has one, its manifest.
    """
    from_id, from_role, to_id, to_role = _parties(message)
    stamp = envelope_timestamp(message['moment'])
    kind = message['kind']

    lines:'strlist' = [
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"',
        '    xmlns:eb="http://www.oasis-open.org/committees/ebxml-msg/schema/msg-header-2_0.xsd">',
        '  <soap:Header>',
        '    <eb:MessageHeader eb:version="2.0" soap:mustUnderstand="1">',
        '      <eb:From>',
        f'        <eb:PartyId eb:type="{DUNS_Type}">{from_id}</eb:PartyId>',
        f'        <eb:Role>{from_role}</eb:Role>',
        '      </eb:From>',
        '      <eb:To>',
        f'        <eb:PartyId eb:type="{DUNS_Type}">{to_id}</eb:PartyId>',
        f'        <eb:Role>{to_role}</eb:Role>',
        '      </eb:To>',
        f'      <eb:CPAId>{message["cpa_id"]}</eb:CPAId>',
        f'      <eb:ConversationId>{message["conversation_id"]}</eb:ConversationId>',
        f'      <eb:Service eb:type="string">{message["service"]}</eb:Service>',
        f'      <eb:Action>{message["action"]}</eb:Action>',
        '      <eb:MessageData>',
        f'        <eb:MessageId>{message["id"]}</eb:MessageId>',
        f'        <eb:Timestamp>{stamp}</eb:Timestamp>',
    ]

    if message['ref_to']:
        lines.append(f'        <eb:RefToMessageId>{message["ref_to"]}</eb:RefToMessageId>')

    lines.append('      </eb:MessageData>')

    if kind == Kind.Ack:
        lines.append('    </eb:MessageHeader>')
        lines.append('    <eb:Acknowledgment eb:version="2.0" soap:mustUnderstand="1">')
        lines.append(f'      <eb:Timestamp>{stamp}</eb:Timestamp>')
        lines.append(f'      <eb:RefToMessageId>{message["ref_to"]}</eb:RefToMessageId>')
        lines.append('    </eb:Acknowledgment>')

    elif kind == Kind.Error:
        lines.append('    </eb:MessageHeader>')
        lines.append('    <eb:ErrorList eb:version="2.0" eb:highestSeverity="Error" soap:mustUnderstand="1">')
        lines.append(f'      <eb:Error eb:errorCode="{message["error_code"]}" eb:severity="Error">')
        lines.append(f'        <eb:Description xml:lang="en-US">{message["error"]}</eb:Description>')
        lines.append('      </eb:Error>')
        lines.append('    </eb:ErrorList>')

    else:
        lines.append('      <eb:DuplicateElimination/>')
        lines.append('    </eb:MessageHeader>')
        lines.append('    <eb:AckRequested eb:version="2.0" eb:signed="true" soap:mustUnderstand="1"/>')

    lines.append('  </soap:Header>')

    if kind in (Kind.Ack, Kind.Error):
        lines.append('  <soap:Body/>')
    else:
        lines.append('  <soap:Body>')
        lines.append('    <eb:Manifest eb:version="2.0">')
        lines.append('      <eb:Reference xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="cid:payload-1"/>')
        lines.append('    </eb:Manifest>')
        lines.append('  </soap:Body>')

    lines.append('</soap:Envelope>')

    out = '\n'.join(lines)
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
    from_id, _, to_id, _ = _parties(message)
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

def raw_message(message:'anydict') -> 'str':
    """ The HTTP request of a message as it went over the wire - the request line, the HTTP headers and the MIME parts
    of the SOAP envelope and of the payload, if the message has one.
    """
    partner = Partner_By_Key[message['partner_key']]

    # An inbound message was posted to the local endpoint, an outbound one to the partner's
    if message['direction'] == 'Inbound':
        host, party_id = Local_Host, Local_Party_ID
    else:
        host, party_id = partner.host, partner.duns

    boundary = f'MIMEBoundary_{message["key"]}_{party_id}'
    header_id = f'ebxml-header-{message["key"]}@{host}'

    parts = [(header_id, 'text/xml', envelope(message))]

    if body := payload(message):
        parts.append(('payload-1', 'application/xml', body))

    lines:'strlist' = []

    for content_id, content_type, text in parts:
        lines.append(f'--{boundary}')
        lines.append(f'Content-ID: <{content_id}>')
        lines.append(f'Content-Type: {content_type}; charset=UTF-8')
        lines.append('')
        lines.append(text.replace('\n', _crlf))

    lines.append(f'--{boundary}--')
    lines.append('')

    content = _crlf.join(lines)
    content_length = len(content.encode('utf8'))

    head = [
        f'POST /exchange/{party_id} HTTP/1.1',
        f'Host: {host}',
        f'Content-Type: multipart/related; type="text/xml"; boundary="{boundary}"; start="<{header_id}>"',
        'SOAPAction: "ebXML"',
        f'Content-Length: {content_length}',
        '',
        '',
    ]

    out = _crlf.join(head) + content
    return out

# ################################################################################################################################
# ################################################################################################################################
