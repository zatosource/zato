# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test import rand_int, rand_string
from zato.common.events.client import Client as EventsClient
from zato.common.events.common import EventInfo
from zato.server.connection.stats import ServiceStatsClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.events.common import PushCtx

    PushCtx = PushCtx

# ################################################################################################################################
# ################################################################################################################################

class TestImplClass(EventsClient):
    def __init__(self, host, port):
        # type: (str, int) -> None
        super().__init__(host, port)

        self.host = host
        self.port = port

        self.push_counter      = 0
        self.is_run_called     = False
        self.is_connect_called = False

# ################################################################################################################################

    def connect(self):
        self.is_connect_called = True

# ################################################################################################################################

    def run(self):
        self.is_run_called = True

# ################################################################################################################################

    def push(self, *args, **kwargs):
        self.push_counter += 1

# ################################################################################################################################

    def close(self):
        pass

# ################################################################################################################################

    def send(self, *args, **kwargs):
        pass

# ################################################################################################################################
# ################################################################################################################################

class ServiceStatsClientTestCase(TestCase):

# ################################################################################################################################

    def test_init(self):

        host = rand_string()
        port = rand_int()

        stats_client = ServiceStatsClient(impl_class=TestImplClass)
        stats_client.init(host, port)

        self.assertTrue(stats_client.impl.is_connect_called)
        self.assertEqual(stats_client.host, host)
        self.assertEqual(stats_client.port, port)

# ################################################################################################################################

    def test_run(self):

        host = rand_string()
        port = rand_int()

        stats_client = ServiceStatsClient(impl_class=TestImplClass)

        stats_client.init(host, port)
        stats_client.run()

        self.assertTrue(stats_client.impl.is_run_called)

# ################################################################################################################################

    def test_push_id_is_given(self):

        cid = rand_string()
        timestamp = None
        service_name = None
        is_request = True
        total_time_ms = None
        id = rand_string(prefix='id')

        stats_client = ServiceStatsClient()
        stats_client.push(
            cid,
            timestamp,
            service_name,
            is_request,
            total_time_ms,
            id,
        )
        self.assertEqual(1, len(stats_client.backlog))

        ctx1 = stats_client.backlog[0] # type: PushCtx

        self.assertEqual(ctx1.id, id)
        self.assertEqual(ctx1.cid, cid)

# ################################################################################################################################

    def test_push_id_is_not_given(self):

        cid = rand_string()
        timestamp = None
        service_name = None
        is_request = True
        total_time_ms = None

        stats_client = ServiceStatsClient()
        stats_client.push(
            cid,
            timestamp,
            service_name,
            is_request,
            total_time_ms,
        )
        self.assertEqual(1, len(stats_client.backlog))

        ctx1 = stats_client.backlog[0] # type: PushCtx

        self.assertTrue(len(ctx1.id) >= 23) # The ID is built using new_cid which defaults to at least 23 characters.
        self.assertEqual(ctx1.cid, cid)

# ################################################################################################################################

    def test_push_is_request_true(self):

        cid = None
        timestamp = None
        service_name = None
        is_request = True
        total_time_ms = None
        id = None

        stats_client = ServiceStatsClient()
        stats_client.push(
            cid,
            timestamp,
            service_name,
            is_request,
            total_time_ms,
            id,
        )

        ctx1 = stats_client.backlog[0] # type: PushCtx
        self.assertEqual(ctx1.event_type, EventInfo.EventType.service_request)

# ################################################################################################################################

    def test_push_is_request_false(self):

        cid = None
        timestamp = None
        service_name = None
        is_request = False
        total_time_ms = None
        id = None

        stats_client = ServiceStatsClient()
        stats_client.push(
            cid,
            timestamp,
            service_name,
            is_request,
            total_time_ms,
            id,
        )

        ctx1 = stats_client.backlog[0] # type: PushCtx
        self.assertEqual(ctx1.event_type, EventInfo.EventType.service_response)

# ################################################################################################################################

    def test_push_no_impl(self):

        # The client has no self.impl so it should have only enqueued the messages
        # without actually invoking the implementation.

        cid1 = rand_string()
        timestamp1 = rand_string()
        service_name1 = rand_string()
        is_request1 = True
        total_time_ms1 = rand_int()
        id1 = rand_string(prefix='id1')

        cid2 = rand_string()
        timestamp2 = rand_string()
        service_name2 = rand_string()
        is_request2 = True
        total_time_ms2 = rand_int()
        id2 = rand_string(prefix='id2')

        request1 = {
            'cid': cid1,
            'timestamp': timestamp1,
            'service_name': service_name1,
            'is_request': is_request1,
            'total_time_ms': total_time_ms1,
            'id': id1,
        }

        request2 = {
            'cid': cid2,
            'timestamp': timestamp2,
            'service_name': service_name2,
            'is_request': is_request2,
            'total_time_ms': total_time_ms2,
            'id': id2,
        }

        stats_client = ServiceStatsClient()
        stats_client.push(**request1)
        stats_client.push(**request2)

        ctx1 = stats_client.backlog[0] # type: PushCtx
        ctx2 = stats_client.backlog[1] # type: PushCtx

        self.assertEqual(ctx1.cid, cid1)
        self.assertEqual(ctx1.timestamp, timestamp1)
        self.assertEqual(ctx1.object_id, service_name1)
        self.assertEqual(ctx1.event_type, EventInfo.EventType.service_request)
        self.assertEqual(ctx1.total_time_ms, total_time_ms1)

        self.assertEqual(ctx2.cid, cid2)
        self.assertEqual(ctx2.timestamp, timestamp2)
        self.assertEqual(ctx2.object_id, service_name2)
        self.assertEqual(ctx2.event_type, EventInfo.EventType.service_request)
        self.assertEqual(ctx2.total_time_ms, total_time_ms2)

# ################################################################################################################################

    def test_push_has_impl(self):

        # The client has self.impl so there should be no enqueued messages. Moreover, the implementation
        # should be called twice because there are two requests.

        host = rand_string()
        port = rand_int()

        cid1 = rand_string()
        timestamp1 = rand_string()
        service_name1 = rand_string()
        is_request1 = True
        total_time_ms1 = rand_int()
        id1 = rand_string(prefix='id1')

        cid2 = rand_string()
        timestamp2 = rand_string()
        service_name2 = rand_string()
        is_request2 = True
        total_time_ms2 = rand_int()
        id2 = rand_string(prefix='id2')

        request1 = {
            'cid': cid1,
            'timestamp': timestamp1,
            'service_name': service_name1,
            'is_request': is_request1,
            'total_time_ms': total_time_ms1,
            'id': id1,
        }

        request2 = {
            'cid': cid2,
            'timestamp': timestamp2,
            'service_name': service_name2,
            'is_request': is_request2,
            'total_time_ms': total_time_ms2,
            'id': id2,
        }

        stats_client = ServiceStatsClient(impl_class=TestImplClass)
        stats_client.init(host, port)

        stats_client.push(**request1)
        stats_client.push(**request2)

        self.assertEqual(len(stats_client.backlog), 0)
        self.assertEqual(stats_client.impl.push_counter, 2)

# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
