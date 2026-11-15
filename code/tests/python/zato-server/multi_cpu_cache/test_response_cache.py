# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import unittest
from threading import Thread
from time import sleep
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import enmasse_import, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, request_on_slot, wait_for_every_slot
from zato.common.test.config_multi_cpu_cache import CacheConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_cache.response_cache')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many identical requests each slot receives at once
    Requests_Per_Slot = 4

    # How long a test waits after it starts a slow invocation before it acts, in seconds,
    # which is well within the duration of the invocation
    Action_Delay = 1.0

    # How long every slot has to apply a configuration change, in seconds
    Change_Deadline = 90.0

    Marker_Path_Prefix = '/test/multi-cpu/cache/marker'

# ################################################################################################################################
# ################################################################################################################################

def _get(slot:'int', path:'str', key:'str') -> 'anydict':
    """ Sends a request with the key through the worker of a slot and returns its JSON response.
    """
    status, body = request_on_slot(slot, 'GET', f'{path}?key={key}', '', {})

    if status != MultiCPUCtx.Status_OK:
        raise Exception(f'Status {status} from {path} in slot {slot} -> {body!r}')

    out = json.loads(body)
    return out

# ################################################################################################################################

def _invocation_ids(key:'str') -> 'strlist':
    """ The IDs of the invocations of the cached service with the key, recorded by every worker.
    """
    out:'strlist' = []

    with open(os.environ[CacheConfig.Invocation_Log_Env]) as invocation_log:
        for line in invocation_log.read().splitlines():
            line_key, invocation_id, _ = line.split()
            if line_key == key:
                out.append(invocation_id)

    return out

# ################################################################################################################################
# ################################################################################################################################

class SlowRequest:
    """ One request to a cached channel, sent in a thread of its own so that a test acts while the invocation is in progress.
    """

    def __init__(self, slot:'int', path:'str', key:'str') -> 'None':
        self.slot = slot
        self.path = path
        self.key = key
        self.response:'anydict' = {}
        self.thread = Thread(target=self._send, daemon=True)

    def _send(self) -> 'None':
        self.response = _get(self.slot, self.path, self.key)

    def start(self) -> 'None':
        self.thread.start()

    def join(self) -> 'anydict':
        self.thread.join()
        out = self.response
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestResponseCacheAcrossWorkers(unittest.TestCase):
    """ The response cache is shared by every worker, and a change or an invalidation made in one worker
    is respected by all of them.
    """

    def _assert_invoked_once(self, path:'str') -> 'None':
        """ Identical requests sent at once through every slot invoke the service once and receive its response.
        """
        key = uuid4().hex
        requests:'anylist' = []

        for slot in range(MultiCPUTestConfig.worker_count):
            for _ in range(ModuleCtx.Requests_Per_Slot):
                requests.append(SlowRequest(slot, path, key))

        for request in requests:
            request.start()

        responses:'anylist' = []

        for request in requests:
            responses.append(request.join())

        invocation_ids = _invocation_ids(key)
        self.assertEqual(len(invocation_ids), 1, f'{path} invoked {len(invocation_ids)} times')

        for response in responses:
            self.assertEqual(response['invocation_id'], invocation_ids[0])

# ################################################################################################################################

    def test_concurrent_requests_cache_on_first_request(self) -> 'None':
        self._assert_invoked_once(CacheConfig.First_Channel_Path)

# ################################################################################################################################

    def test_concurrent_requests_cache_on_second_request(self) -> 'None':
        self._assert_invoked_once(CacheConfig.Second_Channel_Path)

# ################################################################################################################################

    def _assert_no_response_from_before(self, key:'str', previous:'anydict') -> 'None':
        """ Every slot answers the key with a response of an invocation other than the one in progress before the action.
        """
        for slot in range(MultiCPUTestConfig.worker_count):
            response = _get(slot, CacheConfig.First_Channel_Path, key)
            self.assertNotEqual(response['invocation_id'], previous['invocation_id'], f'Slot {slot} served the response from before')

# ################################################################################################################################

    def test_configuration_change_during_an_invocation(self) -> 'None':
        """ A change of the channel made while an invocation is in progress makes every slot discard the response of that invocation.
        """
        key = uuid4().hex
        marker_path = f'{ModuleCtx.Marker_Path_Prefix}/{key}'

        slow = SlowRequest(0, CacheConfig.First_Channel_Path, key)
        slow.start()
        sleep(ModuleCtx.Action_Delay)

        # The channel is changed, and a marker channel created in the same import is served by every slot
        # only after the change that precedes it ..
        enmasse_import({
            'channel_rest': [{
                'name': CacheConfig.First_Channel_Name,
                'service': CacheConfig.Cached_Service,
                'url_path': CacheConfig.First_Channel_Path,
                'data_format': 'json',
                'response_cache': {
                    'is_enabled': True,
                    'ttl': 601,
                    'ttl_unit': 'seconds',
                    'cache_on_second_request': False,
                },
            }, {
                'name': f'test.multi-cpu.cache.marker.{key}',
                'service': MultiCPUCtx.Worker_Slot_Service,
                'url_path': marker_path,
                'data_format': 'json',
            }],
        })

        def _has_marker(slot:'int') -> 'bool':
            status, _ = request_on_slot(slot, 'GET', marker_path, '', {})
            out = status == MultiCPUCtx.Status_OK
            return out

        wait_for_every_slot(_has_marker, marker_path, ModuleCtx.Change_Deadline)

        # .. and once the invocation from before the change completes, no slot serves its response.
        previous = slow.join()
        self._assert_no_response_from_before(key, previous)

# ################################################################################################################################

    def test_invalidation_during_an_invocation(self) -> 'None':
        """ An invalidation made through one slot while an invocation is in progress in another makes every slot
        discard the response of that invocation.
        """
        key = uuid4().hex
        last_slot = MultiCPUTestConfig.worker_count - 1

        slow = SlowRequest(0, CacheConfig.First_Channel_Path, key)
        slow.start()
        sleep(ModuleCtx.Action_Delay)

        status, body = invoke_on_slot(last_slot, CacheConfig.Invalidate_Service, {'channel_name': CacheConfig.First_Channel_Name})
        self.assertEqual(status, MultiCPUCtx.Status_OK, body)

        previous = slow.join()
        self._assert_no_response_from_before(key, previous)

# ################################################################################################################################
# ################################################################################################################################
