# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import signal
import unittest
from time import monotonic, sleep

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.ownership import get_owner_slot
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_multi_cpu import basic_auth_header, connection_to_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, WorkerControl
from zato.common.test.config_multi_cpu_pubsub import PubSubConfig
from zato.common.test.receiver import wait_until_receivers_quiet

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http.client import HTTPConnection
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import any_, anydict, intlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_pubsub.delivery_kill')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Subscription_List_Service = 'zato.pubsub.subscription.get-list'
    Subscriber_Name_Pattern = 'test.multi-cpu.sub.{:02d}'

    # The sequence number of the message published in each phase of a delivery in which the owning worker is killed
    Seq_Before_Attempt = 0
    Seq_During_Send = 1
    Seq_Before_Outcome = 2

    # How long the held request and the response of the receiver are waited for, in seconds
    Gate_Timeout = 30.0

    # How long the subscribers have to receive every message of a phase, in seconds
    Delivery_Timeout = 120.0

# ################################################################################################################################
# ################################################################################################################################

def _get_seq(message:'anydict') -> 'int':
    data:'any_' = message['data']

    if isinstance(data, str):
        data = json.loads(data)

    out = data['seq']
    return out

# ################################################################################################################################

def _count_copies(receiver:'WebhookReceiver', seq:'int') -> 'int':
    out = 0

    for message in receiver.get_delivered_messages():
        if _get_seq(message) == seq:
            out += 1

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestKillDuringPushDelivery(unittest.TestCase):
    """ The worker that owns a push subscription, killed before the delivery attempt, during the HTTP send,
    and after the send but before the outcome is recorded, loses no message and repeats only the message in flight.
    """

    def setUp(self) -> 'None':
        self.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        _ = self.control.wait_for_all_ready()

        self.publish_headers = {
            'Authorization': basic_auth_header(PubSubConfig.Publisher_Name, MultiCPUTestConfig.sec_password),
            'Content-Type': 'application/json',
        }

        self.owners = self._get_owners()

# ################################################################################################################################

    def _get_owners(self) -> 'intlist':
        """ Returns the slot that owns the push subscription of each subscriber, in the order of the receivers.
        """
        admin = AdminClient(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        items, _ = admin.get_list(ModuleCtx.Subscription_List_Service)

        sub_keys:'anydict' = {}

        for item in items:
            if item['delivery_type'] == PubSub.Delivery_Type.Push:
                sub_keys[item['sec_name']] = item['sub_key']

        out:'intlist' = []

        for index in range(PubSubConfig.Subscriber_Count):
            name = ModuleCtx.Subscriber_Name_Pattern.format(index)
            sub_key = sub_keys[name]
            out.append(get_owner_slot(sub_key, MultiCPUTestConfig.worker_count))

        return out

# ################################################################################################################################

    def _publish(self, connection:'HTTPConnection', seq:'int') -> 'None':
        """ Publishes one numbered message to the push topic through a connection that a worker already accepted.
        """
        body = json.dumps({'data': {'seq': seq}})
        path = f'/pubsub/topic/{PubSubConfig.Push_Topic}'

        connection.request('POST', path, body=body, headers=self.publish_headers)

        response = connection.getresponse()
        _ = response.read()
        connection.close()

        self.assertEqual(response.status, 200)

# ################################################################################################################################

    def _wait_for_seq(self, seq:'int') -> 'None':
        """ Waits until every receiver holds the message of a phase and no further copy is in flight.
        """
        deadline = monotonic() + ModuleCtx.Delivery_Timeout
        pending = list(range(PubSubConfig.Subscriber_Count))

        while pending:
            if monotonic() > deadline:
                raise Exception(f'Message {seq} not delivered to subscribers {pending}')

            remaining:'intlist' = []

            for index in pending:
                if _count_copies(PubSubConfig.receivers[index], seq) == 0:
                    remaining.append(index)

            pending = remaining

            if pending:
                sleep(MultiCPUCtx.Poll_Interval)

        wait_until_receivers_quiet(PubSubConfig.receivers)

# ################################################################################################################################

    def _check_copies(self, seq:'int', killed_slot:'int', max_repeated:'int') -> 'None':
        """ Confirms that each subscriber holds the message once, or up to max_repeated copies
        if the killed worker owns its subscription.
        """
        for index, receiver in enumerate(PubSubConfig.receivers):
            copies = _count_copies(receiver, seq)
            owner = self.owners[index]

            logger.info('Message %s, subscriber %s, owner %s -> %s copies', seq, index, owner, copies)

            if owner == killed_slot:
                self.assertGreaterEqual(copies, 1, f'Subscriber {index}, message {seq}')
                self.assertLessEqual(copies, max_repeated, f'Subscriber {index}, message {seq}')
            else:
                self.assertEqual(copies, 1, f'Subscriber {index}, message {seq}')

# ################################################################################################################################

    def test_kill_in_each_phase_of_delivery(self) -> 'None':

        gated = PubSubConfig.receivers[0]
        owner = self.owners[0]

        # A worker killed before the attempt has sent nothing, so its replacement delivers the message exactly once ..
        connection = connection_to_slot(owner, other_than=True)
        row = self.control.get_slot(owner)

        os.kill(row['pid'], signal.SIGSTOP)
        self._publish(connection, ModuleCtx.Seq_Before_Attempt)
        os.kill(row['pid'], signal.SIGKILL)

        _ = self.control.wait_for_respawn(owner, row['generation'])
        self._wait_for_seq(ModuleCtx.Seq_Before_Attempt)
        self._check_copies(ModuleCtx.Seq_Before_Attempt, owner, 1)

        # .. a worker killed while the receiver holds its request has no outcome to record, so the message is sent again ..
        gated.behavior.set_gate()

        connection = connection_to_slot(owner, other_than=True)
        self._publish(connection, ModuleCtx.Seq_During_Send)

        self.assertTrue(gated.behavior.request_arrived.wait(ModuleCtx.Gate_Timeout))
        row = self.control.kill(owner)
        gated.behavior.gate_released.set()

        _ = self.control.wait_for_respawn(owner, row['generation'])
        self._wait_for_seq(ModuleCtx.Seq_During_Send)
        self._check_copies(ModuleCtx.Seq_During_Send, owner, 2)

        # .. and a worker killed after the receiver replied, but before the worker read the reply, sends it again as well.
        gated.behavior.set_gate()

        connection = connection_to_slot(owner, other_than=True)
        self._publish(connection, ModuleCtx.Seq_Before_Outcome)

        self.assertTrue(gated.behavior.request_arrived.wait(ModuleCtx.Gate_Timeout))
        row = self.control.stop(owner)
        gated.behavior.gate_released.set()

        self.assertTrue(gated.behavior.response_sent.wait(ModuleCtx.Gate_Timeout))
        os.kill(row['pid'], signal.SIGKILL)

        _ = self.control.wait_for_respawn(owner, row['generation'])
        self._wait_for_seq(ModuleCtx.Seq_Before_Outcome)
        self._check_copies(ModuleCtx.Seq_Before_Outcome, owner, 2)

# ################################################################################################################################
# ################################################################################################################################
