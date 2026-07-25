# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The two receipts a sent document is owed - the AS2 MDN and the X12 functional acknowledgment -
each turned into a finding once the partner's own window has passed without it arriving.
"""

# stdlib
from datetime import datetime, timedelta

# Zato
from zato.common.as2.alerting.common import get_overdue_seconds, index_configs_by_as2_pair, index_configs_by_isa_id, \
    is_opted_out, Kind_Ack_Overdue, Kind_MDN_Overdue, new_finding
from zato.common.as2.reconcile import MDNReconciler
from zato.common.audit_log.api import AuditSource
from zato.common.defaults import default_cluster_id
from zato.edi.reconcile import Reconciler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.alerting.common import finding_list
    from zato.common.typing_ import dictlist
    dictlist = dictlist
    finding_list = finding_list

# ################################################################################################################################
# ################################################################################################################################

def collect_overdue_mdns(configs:'dictlist', now:'datetime', server_name:'str') -> 'finding_list':
    """ Turns every sent message whose MDN is overdue by its partner's window into a finding.
    """

    # Our response to produce
    out:'finding_list' = []

    reconciler = MDNReconciler(server_name)
    configs_by_pair = index_configs_by_as2_pair(configs)

    for pending in reconciler.outstanding(now):

        pair = f'{pending.as2_from}:{pending.as2_to}'
        config = configs_by_pair.get(pair)

        # The partner said not to alert about it.
        if is_opted_out(config):
            continue

        # A message younger than its partner's window is merely pending, not overdue.
        sent_time = datetime.fromisoformat(pending.sent_time_iso)
        overdue_seconds = get_overdue_seconds(config)
        overdue_from = sent_time + timedelta(seconds=overdue_seconds)

        if now < overdue_from:
            continue

        message = f'MDN overdue from `{pair}` for message `{pending.message_id}`, sent {pending.sent_time_iso}'
        link = f'/zato/audit-log/?source=as2&object_name={pair}&status=outstanding&cluster={default_cluster_id}'

        finding = new_finding(Kind_MDN_Overdue, AuditSource.AS2, pair, message, link)
        out.append(finding)

    return out

# ################################################################################################################################

def collect_overdue_acks(configs:'dictlist', now:'datetime', server_name:'str') -> 'finding_list':
    """ Turns every sent interchange whose acknowledgment is overdue by its partner's window
    into a finding - the pair maps back to a partner through the receiver's EDI identifier.
    """

    # Our response to produce
    out:'finding_list' = []

    reconciler = Reconciler(server_name)
    configs_by_isa_id = index_configs_by_isa_id(configs)

    for pending in reconciler.outstanding(now):

        config = configs_by_isa_id.get(pending.receiver)

        # The partner said not to alert about it.
        if is_opted_out(config):
            continue

        # An interchange younger than its partner's window is merely pending, not overdue.
        sent_time = datetime.fromisoformat(pending.sent_time_iso)
        overdue_seconds = get_overdue_seconds(config)
        overdue_from = sent_time + timedelta(seconds=overdue_seconds)

        if now < overdue_from:
            continue

        pair = f'{pending.sender}:{pending.receiver}'
        message = f'Acknowledgment overdue from `{pair}` for interchange `{pending.control_number}`,'
        message += f' sent {pending.sent_time_iso}'
        link = f'/zato/audit-log/?source=x12&object_name={pair}&status=outstanding&cluster={default_cluster_id}'

        finding = new_finding(Kind_Ack_Overdue, AuditSource.X12, pair, message, link)
        out.append(finding)

    return out

# ################################################################################################################################
# ################################################################################################################################
