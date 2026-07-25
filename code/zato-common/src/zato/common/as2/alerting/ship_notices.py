# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The business-document timing guard - an order that arrived from a partner with a ship notice window
raises a finding when the window passed without a notice going back, because the expensive failure
is the document that did not happen.
"""

# stdlib
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.as2.alerting.common import get_ship_notice_window_hours, is_opted_out, Kind_Ship_Notice_Missing, \
    new_finding
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.defaults import default_cluster_id
from zato.common.json_internal import loads
from zato.edi.reconcile import Reconciler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.alerting.common import finding_list
    from zato.common.typing_ import anydict, dictlist
    anydict = anydict
    dictlist = dictlist
    finding_list = finding_list

# ################################################################################################################################
# ################################################################################################################################

# The X12 document types the guard watches - an order that arrived
# and the ship notice that must answer it.
_document_type_order       = '850'
_document_type_ship_notice = '856'

# How an hour is spelled in a digest line, depending on how many of them the window holds.
_one_hour = 'hour'
_many_hours = 'hours'

# ################################################################################################################################
# ################################################################################################################################

def _load_x12_events(event_type:'str', server_name:'str') -> 'dictlist':
    """ Reads all the X12 reconciliation events of one type, oldest first,
    with their JSON data parsed - what the timing guard runs on.
    """
    conditions = and_(
        event_table.c.source == AuditSource.X12,
        event_table.c.event_type == event_type,
    )

    statement = select(
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.event_time_iso,
        event_table.c.data,
    ).where(conditions).order_by(event_table.c.id)

    reconciler = Reconciler(server_name)

    with reconciler.engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.fetchall()

    # Our response to produce
    out:'dictlist' = []

    for object_name, msg_id, event_time_iso, data in rows:

        sender, receiver = object_name.split(':', 1)

        # Events recorded without JSON data have no document type to speak of.
        if data:
            details = loads(data)
        else:
            details = {}

        document_type = details.get('document_type')

        # An event recorded before document types were extracted names none.
        if document_type is None:
            document_type = ''

        item = {
            'sender': sender,
            'receiver': receiver,
            'control_number': msg_id,
            'event_time_iso': event_time_iso,
            'document_type': document_type,
        }

        out.append(item)

    return out

# ################################################################################################################################

def _index_documents_by_partner(events:'dictlist', document_type:'str', partner_key:'str') -> 'anydict':
    """ Groups the events of one document type by the partner named under the given key,
    so one partner's documents are reachable without walking everyone else's.
    """
    out:'anydict' = {}

    for event in events:

        if event['document_type'] != document_type:
            continue

        partner = event[partner_key]

        # The first document of a partner starts that partner's list off.
        if partner not in out:
            out[partner] = []

        partner_documents = out[partner]
        partner_documents.append(event)

    return out

# ################################################################################################################################

def _index_latest_time_by_partner(events:'dictlist', document_type:'str', partner_key:'str') -> 'anydict':
    """ Returns the most recent moment one document type went to or came from each partner.
    A single moment is all the timing guard needs - the question it asks is whether any
    document of the type is newer than an order, which the newest one answers for all of them.
    """
    out:'anydict' = {}

    for event in events:

        if event['document_type'] != document_type:
            continue

        partner = event[partner_key]
        event_time = datetime.fromisoformat(event['event_time_iso'])

        # A partner not seen yet is described by this event alone ..
        if partner not in out:
            out[partner] = event_time
            continue

        # .. and a later one replaces what the partner was described by so far.
        latest_so_far = out[partner]

        if event_time > latest_so_far:
            out[partner] = event_time

    return out

# ################################################################################################################################

def _get_guarded_configs(configs:'dictlist') -> 'dictlist':
    """ Returns the partners the guard applies to - those with a window configured
    that have not opted out of alerting.
    """

    # Our response to produce
    out:'dictlist' = []

    for config in configs:

        if not get_ship_notice_window_hours(config):
            continue

        if is_opted_out(config):
            continue

        out.append(config)

    return out

# ################################################################################################################################

def collect_missing_ship_notices(configs:'dictlist', now:'datetime', server_name:'str') -> 'finding_list':
    """ The business-document timing guard - an order that arrived from a partner
    with a ship notice window raises a finding when the window passed without
    a ship notice going back, because the expensive failure is the document
    that did not happen.
    """

    # Our response to produce
    out:'finding_list' = []

    # Only partners with a configured window take part at all.
    guarded_configs = _get_guarded_configs(configs)

    if not guarded_configs:
        return out

    # Everything received and sent, read once for all the partners, then indexed by the partner
    # it belongs to - the guard is otherwise every partner times every order times every notice.
    received = _load_x12_events(AuditEvent.Interchange_Received, server_name)
    sent = _load_x12_events(AuditEvent.Interchange_Sent, server_name)

    orders_by_sender = _index_documents_by_partner(received, _document_type_order, 'sender')
    latest_notice_by_receiver = _index_latest_time_by_partner(sent, _document_type_ship_notice, 'receiver')

    for config in guarded_configs:

        isa_id = config['isa_id']
        window_hours = get_ship_notice_window_hours(config)
        window = timedelta(hours=window_hours)

        orders = orders_by_sender.get(isa_id)

        # This partner has sent us no orders at all.
        if orders is None:
            continue

        # The most recent ship notice that went back to this partner - any order placed before it
        # is answered, because a notice only ever answers orders that came before it.
        latest_notice_time = latest_notice_by_receiver.get(isa_id)

        for order in orders:

            # An order still inside its window raises nothing yet ..
            order_time = datetime.fromisoformat(order['event_time_iso'])
            deadline = order_time + window

            if now < deadline:
                continue

            # .. and a ship notice sent back to the partner after the order answers it.
            if latest_notice_time is not None:
                if latest_notice_time >= order_time:
                    continue

            order_sender = order['sender']
            order_receiver = order['receiver']
            pair = f'{order_sender}:{order_receiver}'

            name = config['name']
            control_number = order['control_number']
            received_iso = order['event_time_iso']

            if window_hours == 1:
                hour_suffix = _one_hour
            else:
                hour_suffix = _many_hours

            message = f'No ship notice sent to `{name}` within {window_hours} {hour_suffix}'
            message += f' of order `{control_number}`, received {received_iso}'
            link = f'/zato/audit-log/?source=x12&object_name={pair}&cluster={default_cluster_id}'

            finding = new_finding(Kind_Ship_Notice_Missing, AuditSource.X12, pair, message, link)
            out.append(finding)

    return out

# ################################################################################################################################
# ################################################################################################################################
