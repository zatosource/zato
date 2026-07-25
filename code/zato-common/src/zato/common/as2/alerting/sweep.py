# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

One alerting sweep from end to end - every guard run in turn, the findings turned into the digest
email of the run, and each of them written as an alert-raised event so the reports page can count
alerting history per partner.
"""

# Zato
from zato.common.as2.alerting.certificates import collect_expiring_certificates
from zato.common.as2.alerting.common import Default_Server_Name
from zato.common.as2.alerting.overdue import collect_overdue_acks, collect_overdue_mdns
from zato.common.as2.alerting.ship_notices import collect_missing_ship_notices
from zato.common.audit_log.api import AuditEvent
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.as2.alerting.common import finding_list
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import dictlist, strlist, strtuple
    datetime = datetime
    dictlist = dictlist
    finding_list = finding_list
    strlist = strlist
    strtuple = strtuple
    AuditLog = AuditLog

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

    overdue_mdns = collect_overdue_mdns(configs, now, server_name)
    overdue_acks = collect_overdue_acks(configs, now, server_name)
    expiring_certificates = collect_expiring_certificates(configs, now, own_cert_chain)
    missing_ship_notices = collect_missing_ship_notices(configs, now, server_name)

    out.extend(overdue_mdns)
    out.extend(overdue_acks)
    out.extend(expiring_certificates)
    out.extend(missing_ship_notices)

    return out

# ################################################################################################################################

def build_digest(findings:'finding_list', dashboard_url:'str' = '') -> 'strtuple':
    """ Turns the findings of one sweep into the subject and body of the digest email,
    one line per finding, each linking to the filtered audit log page or the partner form.
    """
    count = len(findings)

    if count == 1:
        suffix = 'finding'
    else:
        suffix = 'findings'

    subject = f'Zato B2B alert digest - {count} {suffix}'

    lines:'strlist' = []

    for finding in findings:
        link = f'{dashboard_url}{finding.link}'
        lines.append(f'* {finding.message}\n  {link}')

    body = '\n\n'.join(lines)

    out = subject, body
    return out

# ################################################################################################################################

def record_alerts(audit_log:'AuditLog', findings:'finding_list', cid:'str' = '') -> 'None':
    """ Writes each finding as an alert-raised audit event, filed under the partner
    it is about, so the reports page can count alerting history per partner.
    """
    for finding in findings:

        details = {'kind': finding.kind, 'message': finding.message}
        data = dumps(details)

        audit_log.insert(finding.source, AuditEvent.Alert_Raised, finding.partner, cid=cid, data=data)

# ################################################################################################################################
# ################################################################################################################################
