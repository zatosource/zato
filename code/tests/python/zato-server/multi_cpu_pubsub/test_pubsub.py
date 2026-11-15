# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import unittest
from threading import Thread
from time import sleep

# Zato
from zato.common.test.client import AdminClient, PublishClient, PullClient
from zato.common.test.config_multi_cpu_pubsub import PubSubConfig
from zato.common.test.conftest_base_multi_cpu import connection_to_slot, MultiCPUTestConfig, post_json, WorkerControl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, intlist, strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_pubsub')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Pull_Path    = '/test/multi-cpu/blocking-pull'
    Publish_Path = '/test/multi-cpu/publish'

    Subscription_List_Service = 'zato.pubsub.subscription.get-list'

    # How many messages a test publishes
    Message_Count = 20

    # How long a test waits for every delivery, in seconds
    Delivery_Timeout = 120.0

    # How long a blocking pull waits at most, in milliseconds, and the time within which a publication wakes it, in seconds
    Block_Ms = 30_000
    Wake_Deadline = 10.0

    # How long the blocking pull is left waiting before the publication, in seconds
    Pull_Head_Start = 2.0

    # How many pulls of one key run concurrently, and how many messages each requests
    Concurrent_Pulls = 8
    Pull_Batch = 5

# ################################################################################################################################
# ################################################################################################################################

def _get_seq(message:'anydict') -> 'int':
    data:'any_' = message['data']

    # .. a receiver records the data either as it was published or as its JSON form ..
    if isinstance(data, str):
        data = json.loads(data)

    out = data['seq']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubAcrossWorkers(unittest.TestCase):
    """ Publications made through any worker reach subscribers owned by every slot, and pulls served by any worker
    see them.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        class_.admin = AdminClient(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        class_.publisher = PublishClient(MultiCPUTestConfig.base_url, PubSubConfig.Publisher_Name, MultiCPUTestConfig.sec_password)

# ################################################################################################################################

    def _get_sub_key(self, sec_name:'str') -> 'str':
        items, _ = self.admin.get_list(ModuleCtx.Subscription_List_Service)

        for item in items:
            if item['sec_name'] == sec_name:
                return item['sub_key']

        raise Exception(f'No subscription of {sec_name}')

# ################################################################################################################################

    def test_every_slot_owns_subscription_keys(self) -> 'None':
        """ The keys are spread over every slot, and the counts of all slots add up to the number of subscriptions.
        """
        rows = self.control.wait_for_all_ready()
        items, _ = self.admin.get_list(ModuleCtx.Subscription_List_Service)

        total = 0

        for row in rows:
            logger.info('Slot %s owns %s keys', row['slot'], row['sub_key_count'])
            self.assertGreater(row['sub_key_count'], 0, f'Slot {row["slot"]}')
            total += row['sub_key_count']

        self.assertEqual(total, len(items))

# ################################################################################################################################

    def test_push_reaches_every_subscriber_once_and_in_order(self) -> 'None':
        """ Messages published through every worker are delivered to each subscriber once and in publication order.
        """
        for seq in range(ModuleCtx.Message_Count):
            _ = self.publisher.publish(PubSubConfig.Push_Topic, {'seq': seq})

        expected:'intlist' = list(range(ModuleCtx.Message_Count))

        for index, receiver in enumerate(PubSubConfig.receivers):
            messages = receiver.wait_for_delivery(ModuleCtx.Message_Count, ModuleCtx.Delivery_Timeout)

            received:'intlist' = []

            for message in messages:
                received.append(_get_seq(message))

            self.assertEqual(received, expected, f'Subscriber {index}')

# ################################################################################################################################

    def test_blocking_pull_wakes_on_a_publication_of_another_worker(self) -> 'None':
        """ A blocking pull waiting in one worker returns as soon as another worker publishes to its topic.
        """
        sub_key = self._get_sub_key(PubSubConfig.Waiter_Name)
        rows = self.control.wait_for_all_ready()
        pull_slot = rows[0]['slot']

        pull_connection = connection_to_slot(pull_slot, other_than=False)
        publish_connection = connection_to_slot(pull_slot, other_than=True)

        results:'anylist' = []

        def _pull() -> 'None':
            results.append(post_json(pull_connection, ModuleCtx.Pull_Path, {'sub_key': sub_key, 'block_ms': ModuleCtx.Block_Ms}))

        thread = Thread(target=_pull, daemon=True)
        thread.start()

        # .. publish once the pull is waiting, through a worker of another slot ..
        sleep(ModuleCtx.Pull_Head_Start)
        published = post_json(publish_connection, ModuleCtx.Publish_Path, {'topic_name': PubSubConfig.Wake_Topic, 'data': {'seq': 0}})

        thread.join()
        pull_connection.close()
        publish_connection.close()

        result = results[0]
        logger.info('Published through slot %s, pulled through slot %s -> %s', published['slot'], pull_slot, result)

        self.assertNotEqual(published['slot'], result['slot'])
        self.assertEqual(result['count'], 1)
        self.assertLess(result['elapsed'], ModuleCtx.Pull_Head_Start + ModuleCtx.Wake_Deadline)

        # .. the message is consumed so the next run of the test starts with an empty queue.
        waiter = PullClient(MultiCPUTestConfig.base_url, PubSubConfig.Waiter_Name, MultiCPUTestConfig.sec_password)
        waiter.drain()

# ################################################################################################################################

    def test_concurrent_pulls_receive_disjoint_messages(self) -> 'None':
        """ Pulls of one key served concurrently by different workers each receive messages that no other pull received.
        """
        message_count = ModuleCtx.Concurrent_Pulls * ModuleCtx.Pull_Batch

        for seq in range(message_count):
            _ = self.publisher.publish(PubSubConfig.Pull_Topic, {'seq': seq})

        results:'anylist' = []

        def _pull() -> 'None':
            puller = PullClient(MultiCPUTestConfig.base_url, PubSubConfig.Puller_Name, MultiCPUTestConfig.sec_password)
            results.append(puller.pull(max_messages=ModuleCtx.Pull_Batch))

        threads:'list[Thread]' = []

        for _ in range(ModuleCtx.Concurrent_Pulls):
            thread = Thread(target=_pull, daemon=True)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        msg_ids:'strset' = set()
        pulled = 0

        for result in results:
            for message in result['messages']:
                msg_id = message['meta']['msg_id']
                self.assertNotIn(msg_id, msg_ids)
                msg_ids.add(msg_id)
                pulled += 1

        logger.info('Concurrent pulls received %s of %s messages', pulled, message_count)
        self.assertGreater(pulled, 0)

        # .. the rest is consumed so the next run of the test starts with an empty queue.
        puller = PullClient(MultiCPUTestConfig.base_url, PubSubConfig.Puller_Name, MultiCPUTestConfig.sec_password)
        puller.drain()

# ################################################################################################################################
# ################################################################################################################################
