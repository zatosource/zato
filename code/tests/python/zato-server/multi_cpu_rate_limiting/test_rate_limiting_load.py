# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import unittest
from threading import Lock, Thread
from time import monotonic, sleep, time

# Zato
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_multi_cpu import MultiCPUTestConfig, new_connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, intset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_rate_limiting.load')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Bucket_Path = '/test/multi-cpu/rate/bucket'
    Window_Path = '/test/multi-cpu/rate/window'

    Channel_Window_Name = 'test.multi-cpu.rate.window'
    Channel_List_Service = 'zato.http-soap.get-list'
    Channel_Clear_Service = 'zato.http-soap.rate-limiting.clear-counters'

    # The token bucket and the fixed window of the enmasse template
    Bucket_Rate  = 1
    Bucket_Burst = 10
    Window_Limit  = 15
    Window_Period = 60

    # How long the bucket is given to refill to its burst before a test, in seconds
    Bucket_Refill_Wait = Bucket_Burst / Bucket_Rate + 1

    # A test of the fixed window starts early enough in a window that all its requests fall into that window, in seconds
    Window_Latest_Start = 30
    Window_Start_Margin = 1

    # How many clients send requests at the same time and how many requests each of them sends
    Client_Count = 32
    Requests_Per_Client = 10

    Status_OK = 200
    Status_Too_Many_Requests = 429

    Rule_Index = 0

# ################################################################################################################################
# ################################################################################################################################

class LoadResult:
    """ The responses to the requests of every client together.
    """

    def __init__(self) -> 'None':
        self.allowed = 0
        self.rejected = 0
        self.slots:'intset' = set()
        self.errors:'anylist' = []
        self.lock = Lock()

# ################################################################################################################################

    def record(self, status:'int', body:'bytes') -> 'None':

        with self.lock:
            if status == ModuleCtx.Status_OK:
                data:'anydict' = json.loads(body)
                self.allowed += 1
                self.slots.add(data['slot'])

            elif status == ModuleCtx.Status_Too_Many_Requests:
                self.rejected += 1

            else:
                self.errors.append((status, body))

# ################################################################################################################################
# ################################################################################################################################

def _run_clients(path:'str') -> 'LoadResult':
    """ Runs every client at once, each sending its requests over connections of their own.
    """
    out = LoadResult()

    def _client() -> 'None':
        for _ in range(ModuleCtx.Requests_Per_Client):
            connection = new_connection()
            connection.request('GET', path)
            response = connection.getresponse()
            out.record(response.status, response.read())
            connection.close()

    threads:'anylist' = []

    for _ in range(ModuleCtx.Client_Count):
        thread = Thread(target=_client, daemon=True)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRateLimitingUnderLoad(unittest.TestCase):
    """ Many concurrent clients spread over every worker are permitted no more than one limit allows in total.
    """

    def test_token_bucket_under_load(self) -> 'None':
        """ The requests that the bucket permits stay within its burst and what its rate refilled during the run.
        """
        sleep(ModuleCtx.Bucket_Refill_Wait)

        started_at = monotonic()
        result = _run_clients(ModuleCtx.Bucket_Path)
        elapsed = monotonic() - started_at

        logger.info('Token bucket under load -> allowed %s, rejected %s, slots %s, elapsed %.2fs',
            result.allowed, result.rejected, sorted(result.slots), elapsed)

        self.assertEqual(result.errors, [])

        refilled = int(elapsed * ModuleCtx.Bucket_Rate) + 1
        self.assertLessEqual(result.allowed, ModuleCtx.Bucket_Burst + refilled)
        self.assertGreaterEqual(result.allowed, ModuleCtx.Bucket_Burst)

# ################################################################################################################################

    def test_fixed_window_under_load(self) -> 'None':
        """ The requests that the fixed window permits are exactly its limit.
        """
        into_window = time() % ModuleCtx.Window_Period

        if into_window > ModuleCtx.Window_Latest_Start:
            sleep(ModuleCtx.Window_Period - into_window + ModuleCtx.Window_Start_Margin)

        # The counters that an earlier test left in this window are cleared ..
        client = AdminClient(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        items, _ = client.get_list(ModuleCtx.Channel_List_Service)

        channel_id = 0

        for item in items:
            if item['name'] == ModuleCtx.Channel_Window_Name:
                channel_id = item['id']

        _ = client.invoke(ModuleCtx.Channel_Clear_Service, {'id': channel_id, 'rule_index': ModuleCtx.Rule_Index})

        # .. and the clients together receive exactly the limit.
        result = _run_clients(ModuleCtx.Window_Path)

        logger.info('Fixed window under load -> allowed %s, rejected %s, slots %s',
            result.allowed, result.rejected, sorted(result.slots))

        total = ModuleCtx.Client_Count * ModuleCtx.Requests_Per_Client

        self.assertEqual(result.errors, [])
        self.assertEqual(result.allowed, ModuleCtx.Window_Limit)
        self.assertEqual(result.rejected, total - ModuleCtx.Window_Limit)

# ################################################################################################################################
# ################################################################################################################################
