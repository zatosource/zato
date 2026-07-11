# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.as2.audit import record_message_received
from zato.common.as2.reconcile import MDNReconciler
from zato.common.audit_log.api import AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.reports import ack_discipline_csv, get_ack_discipline, get_outcomes, get_volume, outcomes_csv, \
    volume_csv, Range_Day, Range_Week
from zato.common.json_internal import dumps
from zato.common.util.api import utcnow
from zato.edi.reconcile import Reconciler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The store all the tests write to and the reports read from.
_server_name = 'test-server'

# The AS2 identities of both sides
_as2_from = 'ZatoRetail'
_as2_to   = 'PartnerCorp'
_pair     = f'{_as2_from}:{_as2_to}'

# The X12 identifiers of both sides
_our_isa_id     = 'ZATORETAIL'
_partner_isa_id = 'PARTNERCORP'
_x12_pair       = f'{_our_isa_id}:{_partner_isa_id}'

# ################################################################################################################################
# ################################################################################################################################

def _mdn_data(modifier:'str') -> 'str':
    """ The JSON data of one MDN arrival, the way the live pipelines record it.
    """
    if modifier:
        disposition = 'processed'
        modifier_kind = 'error'
    else:
        disposition = 'processed'
        modifier_kind = ''

    out = dumps({'disposition': disposition, 'modifier_kind': modifier_kind, 'modifier': modifier, 'mic': '',
        'raw_mime': ''})

    return out

# ################################################################################################################################

def _rows_for_partner(rows:'anylist', partner:'str') -> 'anylist':
    """ Filters report rows down to one partner pair.
    """
    out:'anylist' = []

    for row in rows:
        if row.partner == partner:
            out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestVolume:

    def test_counts_per_partner_and_document_type(self) -> 'None':

        # Two AS2 messages left and one arrived, all for the same partner ..
        mdn_reconciler = MDNReconciler(_server_name)
        mdn_reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', mic='abc, sha-256')
        mdn_reconciler.record_message_sent(_as2_from, _as2_to, 'msg-2@zato', mic='abc, sha-256')

        audit_log = AuditLog(_server_name)
        record_message_received(audit_log, _as2_from, _as2_to, 'msg-3@zato', payload='Inbound test payload')

        # .. two orders left as X12 interchanges and one invoice arrived.
        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000002', document_type='850')
        reconciler.record_interchange_received(_partner_isa_id, _our_isa_id, '000000101', document_type='810')

        rows = get_volume(utcnow(), Range_Week)

        assert len(rows) == 3

        as2_rows = _rows_for_partner(rows, _pair)
        assert len(as2_rows) == 1

        as2_row = as2_rows[0]
        assert as2_row.source == AuditSource.AS2
        assert as2_row.document_type == ''
        assert as2_row.sent == 2
        assert as2_row.received == 1

        order_rows = _rows_for_partner(rows, _x12_pair)
        assert len(order_rows) == 1

        order_row = order_rows[0]
        assert order_row.source == AuditSource.X12
        assert order_row.document_type == '850'
        assert order_row.sent == 2
        assert order_row.received == 0

        invoice_rows = _rows_for_partner(rows, f'{_partner_isa_id}:{_our_isa_id}')
        assert len(invoice_rows) == 1

        invoice_row = invoice_rows[0]
        assert invoice_row.document_type == '810'
        assert invoice_row.sent == 0
        assert invoice_row.received == 1

# ################################################################################################################################

    def test_the_day_range_buckets_by_hour_and_the_week_range_by_day(self) -> 'None':

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')

        now = utcnow()

        # One bucket per hour for the day range - 'YYYY-MM-DDTHH' is 13 characters ..
        day_rows = get_volume(now, Range_Day)

        assert len(day_rows) == 1
        assert len(day_rows[0].period) == 13
        assert day_rows[0].period.startswith(now.isoformat()[:10])

        # .. and one per day for the week range - 'YYYY-MM-DD' is 10 characters.
        week_rows = get_volume(now, Range_Week)

        assert len(week_rows) == 1
        assert len(week_rows[0].period) == 10

# ################################################################################################################################

    def test_the_partner_filter_narrows_the_rows(self) -> 'None':

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')
        reconciler.record_interchange_sent(_our_isa_id, 'OTHERPARTNER', '000000002', document_type='850')

        # The filter matches anywhere inside the identity pair.
        rows = get_volume(utcnow(), Range_Week, partner=_partner_isa_id)

        assert len(rows) == 1
        assert rows[0].partner == _x12_pair

# ################################################################################################################################

    def test_the_range_cutoff_excludes_older_events(self) -> 'None':

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')

        # A report run more than a week later no longer sees the event.
        now = utcnow() + timedelta(days=8)
        rows = get_volume(now, Range_Week)

        assert rows == []

# ################################################################################################################################

    def test_each_row_links_to_the_filtered_audit_log(self) -> 'None':

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')

        rows = get_volume(utcnow(), Range_Week)

        link = rows[0].link

        assert 'source=x12' in link
        assert f'object_name={_x12_pair}' in link

# ################################################################################################################################
# ################################################################################################################################

class TestOutcomes:

    def test_delivered_and_failed_mdns_count_per_partner(self) -> 'None':

        reconciler = MDNReconciler(_server_name)

        # One exchange completed cleanly ..
        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', mic='abc, sha-256')
        reconciler.record_mdn_received('msg-1@zato', data=_mdn_data(''))

        # .. and another one came back with an integrity failure.
        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-2@zato', mic='abc, sha-256')
        reconciler.record_mdn_received('msg-2@zato', outcome=AuditOutcome.Error, data=_mdn_data('integrity-check-failed'))

        rows = get_outcomes(utcnow(), Range_Week)

        assert len(rows) == 1

        row = rows[0]

        assert row.source == AuditSource.AS2
        assert row.partner == _pair
        assert row.document_type == ''
        assert row.delivered == 1
        assert row.failed == 1
        assert row.failure_breakdown == 'integrity-check-failed: 1'

# ################################################################################################################################

    def test_inbound_failures_report_their_error(self) -> 'None':

        audit_log = AuditLog(_server_name)

        # One message arrived cleanly and another could not be decrypted.
        record_message_received(audit_log, _as2_from, _as2_to, 'msg-1@zato', payload='Inbound test payload')
        record_message_received(audit_log, _as2_from, _as2_to, 'msg-2@zato',
            error='decryption-failed', outcome=AuditOutcome.Error)

        rows = get_outcomes(utcnow(), Range_Week)

        assert len(rows) == 1

        row = rows[0]

        assert row.delivered == 1
        assert row.failed == 1
        assert row.failure_breakdown == 'decryption-failed: 1'

# ################################################################################################################################

    def test_acknowledgments_inherit_the_document_type_of_their_interchange(self) -> 'None':

        reconciler = Reconciler(_server_name)

        # An order was accepted and an invoice was rejected.
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')
        reconciler.record_ack_received(_our_isa_id, _partner_isa_id, '000000001')

        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000002', document_type='810')
        reconciler.record_ack_received(_our_isa_id, _partner_isa_id, '000000002', outcome=AuditOutcome.Error,
            data=dumps({'modifier': 'transaction-set-rejected'}))

        rows = get_outcomes(utcnow(), Range_Week)

        assert len(rows) == 2

        # Rows sort by source, partner and document type, so the 810 invoice comes before the 850 order.
        invoice_row = rows[0]
        order_row = rows[1]

        assert invoice_row.document_type == '810'
        assert invoice_row.delivered == 0
        assert invoice_row.failed == 1
        assert invoice_row.failure_breakdown == 'transaction-set-rejected: 1'

        assert order_row.document_type == '850'
        assert order_row.delivered == 1
        assert order_row.failed == 0
        assert order_row.failure_breakdown == ''

# ################################################################################################################################

    def test_failures_without_a_modifier_report_unspecified(self) -> 'None':

        reconciler = MDNReconciler(_server_name)

        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', mic='abc, sha-256')
        reconciler.record_mdn_received('msg-1@zato', outcome=AuditOutcome.Error, data=_mdn_data(''))

        rows = get_outcomes(utcnow(), Range_Week)

        assert len(rows) == 1
        assert rows[0].failure_breakdown == 'unspecified: 1'

# ################################################################################################################################
# ################################################################################################################################

class TestAckDiscipline:

    def test_turnaround_outstanding_and_rejected_count_per_partner(self) -> 'None':

        reconciler = Reconciler(_server_name)

        # One interchange was acknowledged cleanly ..
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')
        reconciler.record_ack_received(_our_isa_id, _partner_isa_id, '000000001')

        # .. another one is still waiting ..
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000002', document_type='850')

        # .. and a third one was rejected.
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000003', document_type='850')
        reconciler.record_ack_received(_our_isa_id, _partner_isa_id, '000000003', outcome=AuditOutcome.Error)

        rows = get_ack_discipline(utcnow(), Range_Week)

        assert len(rows) == 1

        row = rows[0]

        assert row.partner == _x12_pair
        assert row.acknowledged == 2
        assert row.average_seconds >= 0.0
        assert row.max_seconds >= row.average_seconds
        assert row.outstanding == 1
        assert row.rejected == 1

# ################################################################################################################################

    def test_each_partner_gets_its_own_row(self) -> 'None':

        reconciler = Reconciler(_server_name)

        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')
        reconciler.record_interchange_sent(_our_isa_id, 'OTHERPARTNER', '000000002', document_type='850')

        rows = get_ack_discipline(utcnow(), Range_Week)

        assert len(rows) == 2

        # Rows sort by partner pair.
        assert rows[0].partner == f'{_our_isa_id}:OTHERPARTNER'
        assert rows[1].partner == _x12_pair

# ################################################################################################################################

    def test_the_row_links_to_the_audit_log_and_its_outstanding_view(self) -> 'None':

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')

        rows = get_ack_discipline(utcnow(), Range_Week)

        row = rows[0]

        assert 'source=x12' in row.link
        assert f'object_name={_x12_pair}' in row.link
        assert 'status=outstanding' not in row.link

        assert 'status=outstanding' in row.outstanding_link
        assert f'object_name={_x12_pair}' in row.outstanding_link

# ################################################################################################################################
# ################################################################################################################################

class TestCSVExport:

    def test_the_volume_table_renders_as_csv(self) -> 'None':

        reconciler = Reconciler(_server_name)
        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')

        rows = get_volume(utcnow(), Range_Week)
        content = volume_csv(rows)

        lines = content.strip().splitlines()

        assert lines[0] == 'period,source,partner,document_type,sent,received'
        assert len(lines) == 2
        assert _x12_pair in lines[1]
        assert lines[1].endswith('850,1,0')

# ################################################################################################################################

    def test_the_outcomes_table_renders_as_csv(self) -> 'None':

        reconciler = MDNReconciler(_server_name)

        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', mic='abc, sha-256')
        reconciler.record_mdn_received('msg-1@zato', outcome=AuditOutcome.Error, data=_mdn_data('integrity-check-failed'))

        rows = get_outcomes(utcnow(), Range_Week)
        content = outcomes_csv(rows)

        lines = content.strip().splitlines()

        assert lines[0] == 'source,partner,document_type,delivered,failed,failure_breakdown'
        assert len(lines) == 2
        assert _pair in lines[1]
        assert 'integrity-check-failed: 1' in lines[1]

# ################################################################################################################################

    def test_the_ack_discipline_table_renders_as_csv(self) -> 'None':

        reconciler = Reconciler(_server_name)

        reconciler.record_interchange_sent(_our_isa_id, _partner_isa_id, '000000001', document_type='850')
        reconciler.record_ack_received(_our_isa_id, _partner_isa_id, '000000001')

        rows = get_ack_discipline(utcnow(), Range_Week)
        content = ack_discipline_csv(rows)

        lines = content.strip().splitlines()

        assert lines[0] == 'partner,acknowledged,average_seconds,max_seconds,outstanding,rejected'
        assert len(lines) == 2
        assert _x12_pair in lines[1]

# ################################################################################################################################
# ################################################################################################################################
