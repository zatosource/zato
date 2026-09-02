# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from zato.common.audit_log.common import event_attr_table, event_table, metadata, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.search import last_seen, search_events

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_

    # Dummy assignments to satisfy type checkers
    any_ = any_
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

class SearchEventsTestCase(TestCase):

    def setUp(self) -> 'None':
        self.engine = create_engine('sqlite://')
        metadata.create_all(self.engine)

# ################################################################################################################################

    def _insert_event(self, **values:'any_') -> 'int':
        """ Writes one event row and returns its id.
        """
        statement = event_table.insert()
        statement = statement.values(**values)

        with self.engine.begin() as connection:
            result = connection.execute(statement)

        primary_key = result.inserted_primary_key

        out = primary_key[0]
        return out

# ################################################################################################################################

    def _insert_attr(self, event_id:'int', name:'str', value:'str') -> 'None':
        """ Writes one searchable attribute of one event.
        """
        statement = event_attr_table.insert()
        statement = statement.values(event_id=event_id, name=name, value=value)

        with self.engine.begin() as connection:
            _ = connection.execute(statement)

# ################################################################################################################################

    def _insert_arrivals(self) -> 'None':
        """ Writes the events the tests read - three HL7 arrivals on one channel,
        one of them a failure, and one arrival on another channel.
        """
        _ = self._insert_event(
            cid='cid-adt-1',
            source=AuditSource.MLLP_Channel,
            event_type=AuditEvent.Message_Received,
            object_name='ADT from Registration',
            msg_id='MSG-0001',
            event_time_iso='2026-08-29T10:00:00',
            outcome=AuditOutcome.OK,
            data='MSH|^~\\&|REGISTRATION|MAIN|ZATO|HL7|20260829100000||ADT^A01|MSG-0001|P|2.4',
        )

        _ = self._insert_event(
            cid='cid-adt-2',
            source=AuditSource.MLLP_Channel,
            event_type=AuditEvent.Message_Received,
            object_name='ADT from Registration',
            msg_id='MSG-0002',
            event_time_iso='2026-08-29T11:00:00',
            outcome=AuditOutcome.Error,
            status='Field EVN-2 is missing',
            data='MSH|^~\\&|REGISTRATION|MAIN|ZATO|HL7|20260829110000||ADT^A01|MSG-0002|P|2.4',
        )

        _ = self._insert_event(
            cid='cid-adt-3',
            source=AuditSource.MLLP_Channel,
            event_type=AuditEvent.Message_Received,
            object_name='ADT from Registration',
            msg_id='MSG-0003',
            event_time_iso='2026-08-29T12:00:00',
            outcome=AuditOutcome.OK,
            data='MSH|^~\\&|REGISTRATION|MAIN|ZATO|HL7|20260829120000||ADT^A03|MSG-0003|P|2.4',
        )

        _ = self._insert_event(
            cid='cid-lab-1',
            source=AuditSource.MLLP_Channel,
            event_type=AuditEvent.Message_Received,
            object_name='Results from Lab',
            msg_id='MSG-0004',
            event_time_iso='2026-08-29T11:30:00',
            outcome=AuditOutcome.OK,
            data='MSH|^~\\&|LAB|MAIN|ZATO|HL7|20260829113000||ORU^R01|MSG-0004|P|2.4',
        )

# ################################################################################################################################

    def test_search_all_newest_first(self) -> 'None':
        self._insert_arrivals()

        rows = search_events(self.engine)

        row_count = len(rows)
        self.assertEqual(row_count, 4)

        # Newest first, by the time each event happened
        self.assertEqual(rows[0]['msg_id'], 'MSG-0003')
        self.assertEqual(rows[1]['msg_id'], 'MSG-0004')
        self.assertEqual(rows[2]['msg_id'], 'MSG-0002')
        self.assertEqual(rows[3]['msg_id'], 'MSG-0001')

# ################################################################################################################################

    def test_search_by_object_name(self) -> 'None':
        self._insert_arrivals()

        rows = search_events(self.engine, object_name='Results from Lab')

        row_count = len(rows)
        self.assertEqual(row_count, 1)

        self.assertEqual(rows[0]['msg_id'], 'MSG-0004')
        self.assertEqual(rows[0]['object_name'], 'Results from Lab')

# ################################################################################################################################

    def test_search_by_outcome(self) -> 'None':
        self._insert_arrivals()

        rows = search_events(self.engine, outcome=AuditOutcome.Error)

        row_count = len(rows)
        self.assertEqual(row_count, 1)

        self.assertEqual(rows[0]['msg_id'], 'MSG-0002')
        self.assertEqual(rows[0]['status'], 'Field EVN-2 is missing')

# ################################################################################################################################

    def test_search_filters_accept_lists(self) -> 'None':
        """ Each filter accepts a list of values as well as one value.
        """
        self._insert_arrivals()

        object_names = ['ADT from Registration', 'Results from Lab']
        rows = search_events(self.engine, object_name=object_names, outcome=[AuditOutcome.OK, AuditOutcome.Error])

        row_count = len(rows)
        self.assertEqual(row_count, 4)

        # A one-element list reads the same as one value
        rows = search_events(self.engine, object_name=['Results from Lab'])

        row_count = len(rows)
        self.assertEqual(row_count, 1)

        self.assertEqual(rows[0]['msg_id'], 'MSG-0004')

# ################################################################################################################################

    def test_search_time_window(self) -> 'None':
        self._insert_arrivals()

        rows = search_events(self.engine, time_from='2026-08-29T10:30:00', time_to='2026-08-29T11:45:00')

        row_count = len(rows)
        self.assertEqual(row_count, 2)

        self.assertEqual(rows[0]['msg_id'], 'MSG-0004')
        self.assertEqual(rows[1]['msg_id'], 'MSG-0002')

# ################################################################################################################################

    def test_search_free_text_in_payload(self) -> 'None':
        self._insert_arrivals()

        rows = search_events(self.engine, query='ADT^A03')

        row_count = len(rows)
        self.assertEqual(row_count, 1)

        self.assertEqual(rows[0]['msg_id'], 'MSG-0003')

# ################################################################################################################################

    def test_search_attr_widening(self) -> 'None':
        """ A search by an MRN returns the whole trace the MRN appears in - the attr matches
        one event and every event sharing that event's cid comes back with it.
        """
        self._insert_arrivals()

        # The arrival carries the patient's MRN as a searchable attribute ..
        arrival_id = self._insert_event(
            cid='cid-visit-7',
            source=AuditSource.MLLP_Channel,
            event_type=AuditEvent.Message_Received,
            object_name='ADT from Registration',
            msg_id='MSG-0005',
            event_time_iso='2026-08-29T14:00:00',
            outcome=AuditOutcome.OK,
        )
        self._insert_attr(arrival_id, 'mrn', '12345678')

        # .. and the acknowledgment shares the arrival's cid without carrying the MRN itself.
        _ = self._insert_event(
            cid='cid-visit-7',
            source=AuditSource.MLLP_Channel,
            event_type=AuditEvent.Ack_Sent,
            object_name='ADT from Registration',
            msg_id='MSG-0005',
            event_time_iso='2026-08-29T14:00:01',
            outcome=AuditOutcome.OK,
        )

        rows = search_events(self.engine, source=AuditSource.MLLP_Channel, query='12345678')

        row_count = len(rows)
        self.assertEqual(row_count, 2)

        self.assertEqual(rows[0]['event_type'], 'ack-sent')
        self.assertEqual(rows[1]['event_type'], 'message-received')

        self.assertEqual(rows[0]['cid'], 'cid-visit-7')
        self.assertEqual(rows[1]['cid'], 'cid-visit-7')

# ################################################################################################################################

    def test_search_attrs_need_a_source(self) -> 'None':
        """ The attr-to-cid widening reads the attrs of the source the search names -
        with no source named, the free text covers the event columns alone.
        """
        self._insert_arrivals()

        arrival_id = self._insert_event(
            cid='cid-visit-8',
            source=AuditSource.MLLP_Channel,
            event_type=AuditEvent.Message_Received,
            object_name='ADT from Registration',
            msg_id='MSG-0006',
            event_time_iso='2026-08-29T15:00:00',
            outcome=AuditOutcome.OK,
        )
        self._insert_attr(arrival_id, 'mrn', '87654321')

        rows = search_events(self.engine, query='87654321')

        row_count = len(rows)
        self.assertEqual(row_count, 0)

# ################################################################################################################################

    def test_search_paging(self) -> 'None':
        self._insert_arrivals()

        first_page = search_events(self.engine, page=1, page_size=3)
        second_page = search_events(self.engine, page=2, page_size=3)

        first_page_count = len(first_page)
        second_page_count = len(second_page)

        self.assertEqual(first_page_count, 3)
        self.assertEqual(second_page_count, 1)

        # The second page continues where the first one ended
        self.assertEqual(second_page[0]['msg_id'], 'MSG-0001')

# ################################################################################################################################

    def test_search_like_wildcards_match_literally(self) -> 'None':
        self._insert_arrivals()

        # A percent sign in the query is a character to find, not a wildcard
        rows = search_events(self.engine, query='100%')

        row_count = len(rows)
        self.assertEqual(row_count, 0)

# ################################################################################################################################

    def test_last_seen(self) -> 'None':
        self._insert_arrivals()

        out = last_seen(self.engine, AuditSource.MLLP_Channel)

        object_count = len(out)
        self.assertEqual(object_count, 2)

        self.assertEqual(out['ADT from Registration'], '2026-08-29T12:00:00')
        self.assertEqual(out['Results from Lab'], '2026-08-29T11:30:00')

# ################################################################################################################################

    def test_last_seen_covers_one_source_alone(self) -> 'None':
        self._insert_arrivals()

        _ = self._insert_event(
            cid='cid-fhir-1',
            source=AuditSource.FHIR,
            event_type=AuditEvent.Request_Sent,
            object_name='Patient Registry',
            msg_id='MSG-0007',
            event_time_iso='2026-08-29T16:00:00',
            outcome=AuditOutcome.OK,
        )

        out = last_seen(self.engine, AuditSource.FHIR)

        object_count = len(out)
        self.assertEqual(object_count, 1)

        self.assertEqual(out['Patient Registry'], '2026-08-29T16:00:00')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
