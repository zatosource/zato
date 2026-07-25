# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

B2B alerting - one sweep over the reconciliation store and the partner configuration, turning
overdue MDNs, overdue X12 acknowledgments, expiring certificates and missing ship notices into
findings, spread over one module per guard.

- common - the finding a sweep produces, and what a partner's configuration says about it
- overdue - the AS2 MDN and the X12 acknowledgment a sent document is owed
- certificates - the certificates an exchange rests on, watched for the day they expire
- ship_notices - the business-document timing guard
- sweep - every guard run in turn, the digest email and the alert-raised events
"""

# Zato
from zato.common.as2.alerting.certificates import get_cert_days_left
from zato.common.as2.alerting.common import Default_Server_Name, Finding, finding_list, Kind_Ack_Overdue, \
    Kind_Cert_Expiry, Kind_MDN_Overdue, Kind_Ship_Notice_Missing, Own_Keystore_Name
from zato.common.as2.alerting.sweep import build_digest, collect_findings, record_alerts

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'build_digest',
    'collect_findings',
    'finding_list',
    'get_cert_days_left',
    'record_alerts',
    'Default_Server_Name',
    'Finding',
    'Kind_Ack_Overdue',
    'Kind_Cert_Expiry',
    'Kind_MDN_Overdue',
    'Kind_Ship_Notice_Missing',
    'Own_Keystore_Name',
)

# ################################################################################################################################
# ################################################################################################################################
