# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import re
import unittest
from http.client import HTTPConnection

# Zato
from zato.common.test.conftest_base_multi_cpu import MultiCPUTestConfig, new_connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, intset, strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_rest.distribution')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many connections a test opens, which makes it certain that the kernel assigns one to every worker
    Connection_Count = 64

    # How many requests each keep-alive connection sends
    Requests_Per_Connection = 3

    Slot_Path = '/test/multi-cpu/worker-slot'
    Error_Path = '/test/multi-cpu/worker-error'

    # The headers whose values differ from one response to another by design
    Volatile_Headers = {'date', 'x-zato-cid', 'content-length'}

    Error_Slot_Pattern = re.compile(r'Raised by the worker of slot (\d+)')

# ################################################################################################################################
# ################################################################################################################################

def _get(connection:'HTTPConnection', path:'str') -> 'tuple[int, strset, bytes]':
    """ Sends one request over an open connection and returns its status, the names of its stable headers and its body.
    """
    connection.request('GET', path)
    response = connection.getresponse()
    body = response.read()

    header_names:'strset' = set()

    for name, _ in response.getheaders():
        name = name.lower()
        if name not in ModuleCtx.Volatile_Headers:
            header_names.add(name)

    out = (response.status, header_names, body)
    return out

# ################################################################################################################################

def _all_slots() -> 'intset':
    out = set(range(MultiCPUTestConfig.worker_count))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTDistribution(unittest.TestCase):
    """ Requests reach every worker, and every worker answers them as a server with one process does.
    """

    def test_new_connections_reach_every_worker(self) -> 'None':
        """ Requests sent over connections of their own are spread across all the workers.
        """
        slots:'intset' = set()

        for _ in range(ModuleCtx.Connection_Count):
            connection = new_connection()
            status, _, body = _get(connection, ModuleCtx.Slot_Path)
            connection.close()

            self.assertEqual(status, 200)

            response:'anydict' = json.loads(body)
            slots.add(response['slot'])

        logger.info('Slots that served new connections: %s', sorted(slots))
        self.assertEqual(slots, _all_slots())

# ################################################################################################################################

    def test_keep_alive_connections_reach_every_worker(self) -> 'None':
        """ Every keep-alive connection stays with one worker, and the connections together reach all the workers.
        """
        slots:'intset' = set()

        for _ in range(ModuleCtx.Connection_Count):
            connection = new_connection()
            connection_slots:'intset' = set()

            for _ in range(ModuleCtx.Requests_Per_Connection):
                status, _, body = _get(connection, ModuleCtx.Slot_Path)
                self.assertEqual(status, 200)

                response:'anydict' = json.loads(body)
                connection_slots.add(response['slot'])

            connection.close()

            self.assertEqual(len(connection_slots), 1)
            slots.update(connection_slots)

        logger.info('Slots that served keep-alive connections: %s', sorted(slots))
        self.assertEqual(slots, _all_slots())

# ################################################################################################################################

    def test_response_headers_are_identical_on_every_worker(self) -> 'None':
        """ Every worker returns the same set of response headers for the same channel.
        """
        headers_by_slot:'dict[int, strset]' = {}

        for _ in range(ModuleCtx.Connection_Count):
            connection = new_connection()
            status, header_names, body = _get(connection, ModuleCtx.Slot_Path)
            connection.close()

            self.assertEqual(status, 200)

            response:'anydict' = json.loads(body)
            headers_by_slot[response['slot']] = header_names

        self.assertEqual(set(headers_by_slot), _all_slots())

        expected = headers_by_slot[0]

        for slot, header_names in headers_by_slot.items():
            self.assertEqual(header_names, expected, f'Slot {slot}')

# ################################################################################################################################

    def test_error_response_is_identical_on_every_worker(self) -> 'None':
        """ Every worker returns the same status, headers and error text, as return_tracebacks configures it.
        """
        responses_by_slot:'dict[int, tuple[int, strset]]' = {}

        for _ in range(ModuleCtx.Connection_Count):
            connection = new_connection()
            status, header_names, body = _get(connection, ModuleCtx.Error_Path)
            connection.close()

            match = ModuleCtx.Error_Slot_Pattern.search(body.decode('utf8'))

            if match is None:
                self.fail(f'No slot in the error response {body!r}')

            slot = int(match.group(1))
            responses_by_slot[slot] = (status, header_names)

        self.assertEqual(set(responses_by_slot), _all_slots())

        expected_status, expected_headers = responses_by_slot[0]
        self.assertEqual(expected_status, 500)

        for slot, (status, header_names) in responses_by_slot.items():
            self.assertEqual(status, expected_status, f'Slot {slot}')
            self.assertEqual(header_names, expected_headers, f'Slot {slot}')

# ################################################################################################################################
# ################################################################################################################################
