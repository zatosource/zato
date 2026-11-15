# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import unittest
from base64 import b64encode
from time import monotonic, sleep, time

# Zato
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_multi_cpu import MultiCPUTestConfig, new_connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, intset, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_rate_limiting')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Bucket_Path     = '/test/multi-cpu/rate/bucket'
    Window_Path     = '/test/multi-cpu/rate/window'
    Sec_Window_Path = '/test/multi-cpu/rate/sec-window'

    Channel_Window_Name = 'test.multi-cpu.rate.window'
    Sec_Name            = 'test.multi-cpu.rate.sec'

    Channel_List_Service = 'zato.http-soap.get-list'
    Sec_List_Service     = 'zato.security.basic-auth.get-list'

    Channel_Clear_Service = 'zato.http-soap.rate-limiting.clear-counters'
    Sec_Clear_Service     = 'zato.security.basic-auth.rate-limiting.clear-counters'

    # The token bucket of the bucket channel, as its rule in the enmasse template configures it
    Bucket_Rate  = 1
    Bucket_Burst = 10

    # The limit of the fixed window rules, per minute, as the enmasse template configures them
    Window_Limit  = 15
    Window_Period = 60

    # A test of a fixed window starts early enough in a window that all its requests fall into that window, in seconds
    Window_Latest_Start = 30
    Window_Start_Margin = 1

    # How many requests each test sends, which exceeds every limit above more than twice
    Request_Count = 40

    Status_OK = 200
    Status_Too_Many_Requests = 429

    Rule_Index = 0

# ################################################################################################################################
# ################################################################################################################################

class _Result:
    """ The responses to a series of requests, each sent over a connection of its own.
    """

    def __init__(self) -> 'None':
        self.allowed = 0
        self.rejected = 0
        self.slots:'intset' = set()

# ################################################################################################################################

def _send(path:'str', count:'int', headers:'strdict') -> '_Result':
    """ Sends requests over connections of their own, which the kernel spreads over the workers.
    """
    out = _Result()

    for _ in range(count):
        connection = new_connection()
        connection.request('GET', path, headers=headers)
        response = connection.getresponse()
        body = response.read()
        connection.close()

        if response.status == ModuleCtx.Status_OK:
            data:'anydict' = json.loads(body)
            out.allowed += 1
            out.slots.add(data['slot'])

        elif response.status == ModuleCtx.Status_Too_Many_Requests:
            out.rejected += 1

        else:
            raise Exception(f'Unexpected status {response.status} from {path} -> {body!r}')

    return out

# ################################################################################################################################

def _wait_for_window_start() -> 'None':
    """ Waits for the start of the next fixed window unless the current one has enough time left.
    """
    into_window = time() % ModuleCtx.Window_Period

    if into_window > ModuleCtx.Window_Latest_Start:
        sleep(ModuleCtx.Window_Period - into_window + ModuleCtx.Window_Start_Margin)

# ################################################################################################################################

def _get_id(client:'AdminClient', service_name:'str', name:'str') -> 'int':
    """ Returns the ID of an object that the enmasse template created, by its name.
    """
    items, _ = client.get_list(service_name)

    for item in items:
        if item['name'] == name:
            return item['id']

    raise Exception(f'Object {name} not found through {service_name}')

# ################################################################################################################################
# ################################################################################################################################

class TestRateLimitingAcrossWorkers(unittest.TestCase):
    """ The limits of a rule apply to the requests of all workers in total, not to each worker on its own.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = AdminClient(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

        credentials = f'{ModuleCtx.Sec_Name}:{MultiCPUTestConfig.sec_password}'
        class_.sec_headers = {
            'Authorization': 'Basic ' + b64encode(credentials.encode()).decode(),
        }

# ################################################################################################################################

    def _assert_full_window(self, result:'_Result') -> 'None':
        self.assertEqual(result.allowed, ModuleCtx.Window_Limit)
        self.assertEqual(result.rejected, ModuleCtx.Request_Count - ModuleCtx.Window_Limit)
        self.assertGreater(len(result.slots), 1)

# ################################################################################################################################

    def test_token_bucket_is_shared(self) -> 'None':
        """ Requests spread over every worker are permitted at the rate and burst of the rule in total.
        """
        started_at = monotonic()
        result = _send(ModuleCtx.Bucket_Path, ModuleCtx.Request_Count, {})
        elapsed = monotonic() - started_at

        logger.info('Token bucket -> allowed %s, rejected %s, slots %s, elapsed %.2fs',
            result.allowed, result.rejected, sorted(result.slots), elapsed)

        # .. at most the burst and what the rate refilled while the requests were sent ..
        refilled = int(elapsed * ModuleCtx.Bucket_Rate) + 1
        self.assertLessEqual(result.allowed, ModuleCtx.Bucket_Burst + refilled)

        # .. at least the burst, and from more than one worker.
        self.assertGreaterEqual(result.allowed, ModuleCtx.Bucket_Burst)
        self.assertGreater(len(result.slots), 1)

# ################################################################################################################################

    def test_channel_fixed_window_and_clear(self) -> 'None':
        """ The fixed window of a channel permits its limit in total, and a clear of its counters through one worker
        permits the full limit again on every worker.
        """
        _wait_for_window_start()

        first = _send(ModuleCtx.Window_Path, ModuleCtx.Request_Count, {})
        self._assert_full_window(first)

        channel_id = _get_id(self.client, ModuleCtx.Channel_List_Service, ModuleCtx.Channel_Window_Name)
        _ = self.client.invoke(ModuleCtx.Channel_Clear_Service, {'id': channel_id, 'rule_index': ModuleCtx.Rule_Index})

        second = _send(ModuleCtx.Window_Path, ModuleCtx.Request_Count, {})
        self._assert_full_window(second)

# ################################################################################################################################

    def test_security_fixed_window_and_clear(self) -> 'None':
        """ The fixed window of a security definition permits its limit in total, and a clear of its counters
        through one worker permits the full limit again on every worker.
        """
        _wait_for_window_start()

        first = _send(ModuleCtx.Sec_Window_Path, ModuleCtx.Request_Count, self.sec_headers)
        self._assert_full_window(first)

        sec_def_id = _get_id(self.client, ModuleCtx.Sec_List_Service, ModuleCtx.Sec_Name)
        _ = self.client.invoke(ModuleCtx.Sec_Clear_Service, {'id': sec_def_id, 'rule_index': ModuleCtx.Rule_Index})

        second = _send(ModuleCtx.Sec_Window_Path, ModuleCtx.Request_Count, self.sec_headers)
        self._assert_full_window(second)

# ################################################################################################################################
# ################################################################################################################################
