# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# B2B alerting - one sweep over the reconciliation store and the partner configuration,
# turning overdue MDNs, overdue X12 acknowledgments, expiring certificates and missing
# ship notices into findings. Findings become an email digest, one per run, and each one
# is also written as an alert-raised audit event so reports can count alerting history
# per partner.

from __future__ import annotations

# stdlib
from dataclasses import dataclass
from datetime import datetime, timedelta

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.api import AS2
from zato.common.as2.reconcile import MDNReconciler
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.json_internal import dumps, loads
from zato.common.util.xml_.keystore import load_certificates_pem
from zato.edi.reconcile import Reconciler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import anydict, dictlist, intnone, strtuple
    anydict = anydict
    AuditLog = AuditLog
    dictlist = dictlist
    intnone = intnone
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
finding_list = list['Finding']

# ################################################################################################################################
# ################################################################################################################################

# The kinds of findings one alerting sweep can raise.
Kind_MDN_Overdue         = 'mdn-overdue'
Kind_Ack_Overdue         = 'ack-overdue'
Kind_Cert_Expiry         = 'cert-expiry'
Kind_Ship_Notice_Missing = 'ship-notice-missing'

# The server name alerting events are recorded under when none is given.
Default_Server_Name = 'b2b-alerting'

# The object name a finding about our own keystore certificate is filed under.
Own_Keystore_Name = 'as2-keystore'

# The X12 document types the business-document timing guard watches -
# an order that arrived and the ship notice that must answer it.
_doc_type_order       = '850'
_doc_type_ship_notice = '856'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Finding:
    """ One thing the alerting sweep found - a digest line and an alert-raised event in the making.
    """
    # Which of the finding kinds this is.
    kind: str = ''

    # The audit source the finding belongs to - as2 or x12.
    source: str = ''

    # The identity pair or object the finding is about, which is also
    # the object name its alert-raised event is filed under.
    partner: str = ''

    # The human-readable digest line.
    message: str = ''

    # The Dashboard path the digest line links to.
    link: str = ''

# ################################################################################################################################

def _new_finding(kind:'str', source:'str', partner:'str', message:'str', link:'str') -> 'Finding':

    # Our response to produce
    out = Finding()

    out.kind = kind
    out.source = source
    out.partner = partner
    out.message = message
    out.link = link

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_cert_days_left(cert_chain:'str', now:'datetime') -> 'intnone':
    """ Returns how many days are left until the first certificate of a pasted PEM chain
    expires, or None for an empty or unparseable chain.
    """
    if not cert_chain:
        return None

    try:
        certificates = load_certificates_pem(cert_chain.encode('utf8'))
    except ValueError:
        return None

    first_certificate = certificates[0]
    not_after = first_certificate.not_valid_after_utc

    delta = not_after - now

    out = delta.days
    return out

# ################################################################################################################################

def _get_overdue_seconds(config:'anydict | None') -> 'int':
    """ Returns the overdue window of one partner - its own ack_overdue_after
    or the alerting default when the partner does not set one.
    """
    if config:
        if window := config['ack_overdue_after']:
            out = window
            return out

    out = AS2.Alerting.Default_Ack_Overdue_Seconds
    return out

# ################################################################################################################################

def _is_opted_out(config:'anydict | None') -> 'bool':
    """ Tells whether a partner opted out of alerting - no configuration means no opt-out.
    """
    # No matching partner means nothing to opt out of.
    if config is None:
        return False

    # Connections saved before the opt-out existed do not carry the field at all.
    if 'alerting_opt_out' not in config:
        return False

    out = config['alerting_opt_out']
    return out

# ################################################################################################################################

def _get_ship_notice_window_hours(config:'anydict') -> 'int':
    """ Returns the partner's ship notice window in hours - zero means the guard is off,
    and connections saved before the field existed do not carry it at all.
    """
    if 'ship_notice_window_hours' not in config:
        return 0

    out = config['ship_notice_window_hours']
    return out

# ################################################################################################################################

def _find_config_by_as2_pair(configs:'dictlist', as2_from:'str', as2_to:'str') -> 'anydict | None':
    """ Returns the connection whose AS2 identities form the given pair, or None.
    """
    for config in configs:
        if config['as2_from'] == as2_from:
            if config['as2_to'] == as2_to:
                out = config
                break
    else:
        out = None

    return out

# ################################################################################################################################

def _find_config_by_isa_id(configs:'dictlist', isa_id:'str') -> 'anydict | None':
    """ Returns the connection whose partner EDI identifier matches, or None -
    the identifier is how X12 reconciliation pairs map back to partners.
    """
    for config in configs:
        if config['isa_id'] == isa_id:
            out = config
            break
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################

def _collect_overdue_mdns(configs:'dictlist', now:'datetime', server_name:'str') -> 'finding_list':
    """ Turns every sent message whose MDN is overdue by its partner's window into a finding.
    """

    # Our response to produce
    out:'finding_list' = []

    reconciler = MDNReconciler(server_name)

    for pending in reconciler.outstanding(now):

        config = _find_config_by_as2_pair(configs, pending.as2_from, pending.as2_to)

        # The partner said not to alert about it.
        if _is_opted_out(config):
            continue

        # A message younger than its partner's window is merely pending, not overdue.
        sent_time = datetime.fromisoformat(pending.sent_time_iso)
        overdue_from = sent_time + timedelta(seconds=_get_overdue_seconds(config))

        if now < overdue_from:
            continue

        pair = f'{pending.as2_from}:{pending.as2_to}'
        message = f'MDN overdue from `{pair}` for message `{pending.message_id}`, sent {pending.sent_time_iso}'
        link = f'/zato/audit-log/?source=as2&object_name={pair}&status=outstanding&cluster=1'

        finding = _new_finding(Kind_MDN_Overdue, AuditSource.AS2, pair, message, link)
        out.append(finding)

    return out

# ################################################################################################################################

def _collect_overdue_acks(configs:'dictlist', now:'datetime', server_name:'str') -> 'finding_list':
    """ Turns every sent interchange whose acknowledgment is overdue by its partner's window
    into a finding - the pair maps back to a partner through the receiver's EDI identifier.
    """

    # Our response to produce
    out:'finding_list' = []

    reconciler = Reconciler(server_name)

    for pending in reconciler.outstanding(now):

        config = _find_config_by_isa_id(configs, pending.receiver)

        # The partner said not to alert about it.
        if _is_opted_out(config):
            continue

        # An interchange younger than its partner's window is merely pending, not overdue.
        sent_time = datetime.fromisoformat(pending.sent_time_iso)
        overdue_from = sent_time + timedelta(seconds=_get_overdue_seconds(config))

        if now < overdue_from:
            continue

        pair = f'{pending.sender}:{pending.receiver}'
        message = f'Acknowledgment overdue from `{pair}` for interchange `{pending.control_number}`, ' \
            f'sent {pending.sent_time_iso}'
        link = f'/zato/audit-log/?source=x12&object_name={pair}&status=outstanding&cluster=1'

        finding = _new_finding(Kind_Ack_Overdue, AuditSource.X12, pair, message, link)
        out.append(finding)

    return out

# ################################################################################################################################

def _collect_expiring_certificates(configs:'dictlist', now:'datetime', own_cert_chain:'str') -> 'finding_list':
    """ Turns every partner certificate and our own signing certificate inside
    the warning window into a finding.
    """

    # Our response to produce
    out:'finding_list' = []

    # Each partner's pasted certificate is checked against the warning window ..
    for config in configs:

        # The partner said not to alert about it.
        if _is_opted_out(config):
            continue

        days_left = get_cert_days_left(config['as2_partner_cert'], now)

        if days_left is None:
            continue

        if days_left >= AS2.Alerting.Cert_Warning_Days:
            continue

        as2_from = config['as2_from']
        as2_to = config['as2_to']
        pair = f'{as2_from}:{as2_to}'

        name = config['name']
        message = f'Certificate of partner `{name}` ({pair}) expires in {days_left} day(s)'
        link = '/zato/outgoing/as2/?cluster=1&type_=outconn-as2'

        finding = _new_finding(Kind_Cert_Expiry, AuditSource.AS2, pair, message, link)
        out.append(finding)

    # .. and so is our own signing certificate.
    days_left = get_cert_days_left(own_cert_chain, now)

    if days_left is not None:
        if days_left < AS2.Alerting.Cert_Warning_Days:

            message = f'Our own AS2 signing certificate expires in {days_left} day(s)'
            link = '/zato/as2-keystore/?cluster=1'

            finding = _new_finding(Kind_Cert_Expiry, AuditSource.AS2, Own_Keystore_Name, message, link)
            out.append(finding)

    return out

# ################################################################################################################################

def _load_x12_events(event_type:'str', server_name:'str') -> 'dictlist':
    """ Reads all the X12 reconciliation events of one type, oldest first,
    with their JSON data parsed - what the timing guard runs on.
    """
    stmt = select(
        event_table.c.object_name,
        event_table.c.msg_id,
        event_table.c.event_time_iso,
        event_table.c.data,
    ).where(and_(
        event_table.c.source == AuditSource.X12,
        event_table.c.event_type == event_type,
    )).order_by(event_table.c.id)

    reconciler = Reconciler(server_name)

    with reconciler.engine.connect() as connection:
        rows = connection.execute(stmt).fetchall()

    # Our response to produce
    out:'dictlist' = []

    for object_name, msg_id, event_time_iso, data in rows:

        sender, receiver = object_name.split(':', 1)

        # Events recorded without JSON data have no document type to speak of.
        if data:
            details = loads(data)
        else:
            details = {}

        if 'doc_type' in details:
            doc_type = details['doc_type']
        else:
            doc_type = ''

        item = {
            'sender': sender,
            'receiver': receiver,
            'control_number': msg_id,
            'event_time_iso': event_time_iso,
            'doc_type': doc_type,
        }

        out.append(item)

    return out

# ################################################################################################################################

def _collect_missing_ship_notices(configs:'dictlist', now:'datetime', server_name:'str') -> 'finding_list':
    """ The business-document timing guard - an order that arrived from a partner
    with a ship notice window raises a finding when the window passed without
    a ship notice going back, because the expensive failure is the document
    that did not happen.
    """

    # Our response to produce
    out:'finding_list' = []

    # Only partners with a configured window take part at all.
    guarded_configs:'dictlist' = []

    for config in configs:

        if not _get_ship_notice_window_hours(config):
            continue

        if _is_opted_out(config):
            continue

        guarded_configs.append(config)

    if not guarded_configs:
        return out

    # Everything received and sent, read once for all the partners.
    received = _load_x12_events(AuditEvent.Interchange_Received, server_name)
    sent = _load_x12_events(AuditEvent.Interchange_Sent, server_name)

    for config in guarded_configs:

        isa_id = config['isa_id']
        window = timedelta(hours=_get_ship_notice_window_hours(config))

        for order in received:

            # Only this partner's orders are of interest here ..
            if order['doc_type'] != _doc_type_order:
                continue

            if order['sender'] != isa_id:
                continue

            # .. an order still inside its window raises nothing yet ..
            order_time = datetime.fromisoformat(order['event_time_iso'])
            deadline = order_time + window

            if now < deadline:
                continue

            # .. and a ship notice sent back to the partner after the order answers it.
            for notice in sent:

                if notice['doc_type'] != _doc_type_ship_notice:
                    continue

                if notice['receiver'] != isa_id:
                    continue

                notice_time = datetime.fromisoformat(notice['event_time_iso'])

                if notice_time >= order_time:
                    break
            else:
                pair = f'{order["sender"]}:{order["receiver"]}'
                name = config['name']
                control_number = order['control_number']
                window_hours = config['ship_notice_window_hours']

                message = f'No ship notice sent to `{name}` within {window_hours} hour(s) ' \
                    f'of order `{control_number}`, received {order["event_time_iso"]}'
                link = f'/zato/audit-log/?source=x12&object_name={pair}&cluster=1'

                finding = _new_finding(Kind_Ship_Notice_Missing, AuditSource.X12, pair, message, link)
                out.append(finding)

    return out

# ################################################################################################################################
# ################################################################################################################################

def collect_findings(
    configs:'dictlist',
    now:'datetime',
    *,
    own_cert_chain:'str' = '',
    server_name:'str' = Default_Server_Name,
    ) -> 'finding_list':
    """ Runs one full alerting sweep - overdue MDNs, overdue acknowledgments,
    expiring certificates and missing ship notices, in that order.
    """

    # Our response to produce
    out:'finding_list' = []

    out.extend(_collect_overdue_mdns(configs, now, server_name))
    out.extend(_collect_overdue_acks(configs, now, server_name))
    out.extend(_collect_expiring_certificates(configs, now, own_cert_chain))
    out.extend(_collect_missing_ship_notices(configs, now, server_name))

    return out

# ################################################################################################################################

def build_digest(findings:'finding_list', dashboard_url:'str'='') -> 'strtuple':
    """ Turns the findings of one sweep into the subject and body of the digest email,
    one line per finding, each linking to the filtered audit log page or the partner form.
    """
    count = len(findings)
    suffix = 'finding' if count == 1 else 'findings'

    subject = f'Zato B2B alert digest - {count} {suffix}'

    lines = []

    for finding in findings:
        link = f'{dashboard_url}{finding.link}'
        lines.append(f'* {finding.message}\n  {link}')

    body = '\n\n'.join(lines)

    out = subject, body
    return out

# ################################################################################################################################

def record_alerts(audit_log:'AuditLog', findings:'finding_list', cid:'str'='') -> 'None':
    """ Writes each finding as an alert-raised audit event, filed under the partner
    it is about, so the reports page can count alerting history per partner.
    """
    for finding in findings:

        data = dumps({'kind': finding.kind, 'message': finding.message})

        audit_log.insert(finding.source, AuditEvent.Alert_Raised, finding.partner, cid=cid, data=data)

# ################################################################################################################################
# ################################################################################################################################
