# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import unittest
from random import randrange
from threading import Lock, Thread
from time import monotonic, sleep

# Zato
from zato.common.test.client import AdminClient, PublishClient
from zato.common.test.conftest_base_multi_cpu import get_json, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, new_connection, \
     WorkerControl
from zato.common.test.config_multi_cpu_pubsub import PubSubConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_pubsub.faults_under_load')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the load runs, how many threads publish and send REST requests, and how often a worker is killed, in seconds
    Run_Duration = 60.0
    Publisher_Count = 4
    REST_Client_Count = 8
    Kill_Interval = 8.0

    # How long the subscribers have to receive every acknowledged message after the load ends, in seconds
    Delivery_Timeout = 180.0

    Subscription_List_Service = 'zato.pubsub.subscription.get-list'

# ################################################################################################################################
# ################################################################################################################################

def _get_seq(message:'anydict') -> 'int':
    data:'any_' = message['data']

    if isinstance(data, str):
        data = json.loads(data)

    out = data['seq']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFaultsUnderLoad(unittest.TestCase):
    """ Workers killed at random during sustained publishing and REST traffic lose no acknowledged message
    and leave no subscription key without an owner.
    """

    def test_random_kills_during_load(self) -> 'None':

        control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        _ = control.wait_for_all_ready()

        run_end = monotonic() + ModuleCtx.Run_Duration
        lock = Lock()

        acknowledged:'intset' = set()
        state:'anydict' = {'next_seq': 0, 'publish_failures': 0, 'rest_failures': 0, 'rest_count': 0, 'kills': 0}

        def _next_seq() -> 'int':
            with lock:
                out = state['next_seq']
                state['next_seq'] += 1
            return out

        # Each publisher publishes numbered messages through connections that the kernel spreads over the workers,
        # and a publication that fails with its worker is never counted as acknowledged ..
        def _publish() -> 'None':
            publisher = PublishClient(MultiCPUTestConfig.base_url, PubSubConfig.Publisher_Name, MultiCPUTestConfig.sec_password)

            while monotonic() < run_end:
                seq = _next_seq()

                try:
                    _ = publisher.publish(PubSubConfig.Push_Topic, {'seq': seq})
                except Exception:
                    with lock:
                        state['publish_failures'] += 1
                    continue

                with lock:
                    acknowledged.add(seq)

        # .. the REST clients keep every worker busy ..
        def _rest() -> 'None':
            while monotonic() < run_end:
                try:
                    connection = new_connection()
                    _ = get_json(connection, MultiCPUCtx.Worker_Slot_Path)
                    connection.close()
                except Exception:
                    with lock:
                        state['rest_failures'] += 1
                    continue

                with lock:
                    state['rest_count'] += 1

        threads:'anylist' = []

        for _ in range(ModuleCtx.Publisher_Count):
            threads.append(Thread(target=_publish, daemon=True))

        for _ in range(ModuleCtx.REST_Client_Count):
            threads.append(Thread(target=_rest, daemon=True))

        for thread in threads:
            thread.start()

        # .. and a random worker is killed and replaced, again and again, while they run.
        while monotonic() + ModuleCtx.Kill_Interval < run_end:
            sleep(ModuleCtx.Kill_Interval)

            slot = randrange(MultiCPUTestConfig.worker_count)
            killed = control.kill(slot)
            state['kills'] += 1
            logger.info('Killed slot %s -> %s', slot, killed)

            _ = control.wait_for_respawn(slot, killed['generation'])

        for thread in threads:
            thread.join()

        logger.info('Load completed -> acknowledged %s, %s', len(acknowledged), state)

        # Every subscriber receives every acknowledged message ..
        for index, receiver in enumerate(PubSubConfig.receivers):
            messages = receiver.wait_for_delivery(len(acknowledged), ModuleCtx.Delivery_Timeout)

            received:'intset' = set()

            for message in messages:
                received.add(_get_seq(message))

            missing = acknowledged - received
            self.assertEqual(missing, set(), f'Subscriber {index} did not receive {len(missing)} messages')

        # .. and the keys of every subscription are owned by the workers once more.
        rows = control.wait_for_all_ready()
        admin = AdminClient(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        items, _ = admin.get_list(ModuleCtx.Subscription_List_Service)

        total = 0

        for row in rows:
            total += row['sub_key_count']

        self.assertEqual(total, len(items))

# ################################################################################################################################
# ################################################################################################################################
