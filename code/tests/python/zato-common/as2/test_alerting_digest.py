# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from urllib.parse import quote

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.as2.alerting import build_digest, collect_findings, Kind_MDN_Overdue, record_alerts
from zato.common.as2.reconcile import MDNReconciler
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditSource, event_table, get_audit_engine
from zato.common.json_internal import loads
from zato.common.util.api import utcnow

# Zato
from .alerting_helpers import AS2_From, AS2_To, new_config, Pair, Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

# The Dashboard address every digest line links back to.
_dashboard_url = 'https://dashboard.example.com'

# ################################################################################################################################
# ################################################################################################################################

class TestDigestAndEvents:

    def _collect_one_sweep(self) -> 'anylist':
        """ Seeds the store with one overdue MDN and runs the sweep past the window.
        """
        reconciler = MDNReconciler(Server_Name)
        reconciler.record_message_sent(AS2_From, AS2_To, 'msg-1@zato', mic='abc, sha-256')

        config = new_config(ack_overdue_after=3600)

        now = utcnow() + timedelta(seconds=3700)

        out = collect_findings([config], now, server_name=Server_Name)
        return out

# ################################################################################################################################

    def test_the_digest_has_one_line_per_finding(self) -> 'None':

        findings = self._collect_one_sweep()

        subject, body = build_digest(findings, _dashboard_url)

        assert subject == 'Zato B2B alert digest - 1 finding'
        assert 'msg-1@zato' in body

        # Each line links to the filtered audit log page under the given Dashboard address,
        # with the pair URL-quoted the way the link builder writes it.
        assert f'{_dashboard_url}/zato/audit-log/?source=as2&object_name={quote(Pair)}' in body

# ################################################################################################################################

    def test_each_finding_becomes_an_alert_raised_event(self) -> 'None':

        findings = self._collect_one_sweep()

        audit_log = AuditLog(Server_Name)
        record_alerts(audit_log, findings, cid='cid-alerting')

        # The alerting history is filed under the partner the finding is about.
        statement = select(
            event_table.c.source,
            event_table.c.object_name,
            event_table.c.cid,
            event_table.c.data,
        ).where(event_table.c.event_type == AuditEvent.Alert_Raised)

        engine = get_audit_engine()

        with engine.connect() as connection:
            result = connection.execute(statement)
            rows = result.fetchall()

        assert len(rows) == 1

        source, object_name, cid, data = rows[0]

        assert source == AuditSource.AS2
        assert object_name == Pair
        assert cid == 'cid-alerting'

        details = loads(data)

        assert details['kind'] == Kind_MDN_Overdue
        assert 'msg-1@zato' in details['message']

# ################################################################################################################################
# ################################################################################################################################
