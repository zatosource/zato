# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import socket
import subprocess
import unittest
from time import monotonic, sleep

# requests
import requests

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.ownership import get_owner_slot
from zato.common.test.client import AdminClient, PublishClient
from zato.common.test.conftest_base_multi_cpu import enmasse_import, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, WorkerControl
from zato.common.test.config_multi_cpu_pubsub import PubSubConfig
from zato.common.test.receiver import wait_until_receivers_quiet

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import any_, anydict, intlist, intset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_pubsub.subscriber_faults')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Subscription_List_Service = 'zato.pubsub.subscription.get-list'
    Outgoing_Invoke_Service = 'test.multi-cpu.outgoing-invoke'
    Subscriber_Name_Pattern = 'test.multi-cpu.sub.{:02d}'

    Host = '127.0.0.1'
    Toxiproxy_Image = 'ghcr.io/shopify/toxiproxy:2.12.0'

    # How long the API of Toxiproxy may take to start and to answer one call, in seconds
    Toxiproxy_Start_Timeout = 60.0
    Toxiproxy_API_Timeout = 30.0

    # The slot that owns the faulty subscribers needs one subscriber of each kind of fault and a healthy one
    Faulty_Kind_Count = 3
    Min_Subscribers_Per_Slot = 4

    # How long the slow endpoint delays each response, in milliseconds
    Slow_Latency_Ms = 2000

    # How many messages the test publishes
    Message_Count = 10

    # How long the healthy subscribers have to receive every message, which is well below the time
    # the slow subscriber needs, and how long the faulty ones have after their endpoints recover, in seconds
    Healthy_Deadline = 15.0
    Recovery_Deadline = 120.0

    # How long the endpoints refuse and sever connections before they recover, in seconds
    Fault_Duration = 10.0

    # How long the owning worker has to apply the address of an outgoing connection, in seconds
    Redirect_Deadline = 30.0

    Received_Bytes_Metric = 'toxiproxy_proxy_received_bytes_total'

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((ModuleCtx.Host, 0))
        out = probe.getsockname()[1]

    return out

# ################################################################################################################################

def _get_seq(message:'anydict') -> 'int':
    data:'any_' = message['data']

    if isinstance(data, str):
        data = json.loads(data)

    out = data['seq']
    return out

# ################################################################################################################################

def _get_seqs(receiver:'WebhookReceiver') -> 'intset':
    out:'intset' = set()

    for message in receiver.get_delivered_messages():
        out.add(_get_seq(message))

    return out

# ################################################################################################################################

def _outgoing_config(index:'int', port:'int') -> 'anydict':
    """ Returns the enmasse definition of the outgoing connection of a subscriber, pointed at a port of the host.
    """
    out = {
        'name': ModuleCtx.Subscriber_Name_Pattern.format(index) + '.out',
        'host': f'http://{ModuleCtx.Host}:{port}',
        'url_path': f'/webhook/{index:02d}',
        'data_format': 'json',
        'timeout': 30,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class _Toxiproxy:
    """ A container of Toxiproxy on the network of the host, with one proxy for each faulty subscriber.
    """

    def __init__(self) -> 'None':
        self.name = f'zato-multi-cpu-toxiproxy-{os.getpid()}'
        self.api_port = _find_free_port()
        self.address = f'http://{ModuleCtx.Host}:{self.api_port}'

    def call(self, method:'str', path:'str', body:'anydict | None'=None) -> 'requests.Response':
        out = requests.request(method, self.address + path, json=body, timeout=ModuleCtx.Toxiproxy_API_Timeout)
        out.raise_for_status()
        return out

    def start(self) -> 'None':
        command = ['docker', 'run', '-d', '--rm', '--name', self.name, '--network', 'host', ModuleCtx.Toxiproxy_Image,
            f'-host={ModuleCtx.Host}', f'-port={self.api_port}', '-proxy-metrics']
        _ = subprocess.run(command, check=True, capture_output=True)

        deadline = monotonic() + ModuleCtx.Toxiproxy_Start_Timeout

        while True:
            try:
                _ = self.call('GET', '/version')
                return
            except requests.ConnectionError:
                if monotonic() > deadline:
                    raise
                sleep(MultiCPUCtx.Poll_Interval)

    def stop(self) -> 'None':
        _ = subprocess.run(['docker', 'rm', '-f', self.name], check=True, capture_output=True)

    def add_proxy(self, name:'str', upstream_port:'int') -> 'int':
        out = _find_free_port()
        body = {
            'name': name,
            'listen': f'{ModuleCtx.Host}:{out}',
            'upstream': f'{ModuleCtx.Host}:{upstream_port}',
            'enabled': True,
        }
        _ = self.call('POST', '/proxies', body)
        return out

    def add_toxic(self, proxy:'str', toxic_type:'str', stream:'str', attributes:'anydict') -> 'None':
        body = {
            'name': f'{toxic_type}-{stream}',
            'type': toxic_type,
            'stream': stream,
            'toxicity': 1.0,
            'attributes': attributes,
        }
        _ = self.call('POST', f'/proxies/{proxy}/toxics', body)

    def remove_toxic(self, proxy:'str', toxic_type:'str', stream:'str') -> 'None':
        _ = self.call('DELETE', f'/proxies/{proxy}/toxics/{toxic_type}-{stream}')

    def set_enabled(self, proxy:'str', is_enabled:'bool') -> 'None':
        _ = self.call('POST', f'/proxies/{proxy}', {'enabled': is_enabled})

    def read_received_bytes(self, proxy:'str') -> 'int':
        response = self.call('GET', '/metrics')
        proxy_label = f'proxy="{proxy}"'
        out = 0

        for line in response.text.splitlines():
            if line.startswith(ModuleCtx.Received_Bytes_Metric):
                if proxy_label in line:
                    out += int(float(line.rsplit(' ', 1)[1]))

        return out

# ################################################################################################################################
# ################################################################################################################################

class TestSlowAndFailingSubscribers(unittest.TestCase):
    """ A slow endpoint, an endpoint that refuses connections and an endpoint whose connections are severed,
    each behind a TCP proxy, do not block the other subscribers owned by the same slot, and each receives every message
    under its retry policy once it recovers.
    """

    def setUp(self) -> 'None':
        self.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        _ = self.control.wait_for_all_ready()

        self.toxiproxy = _Toxiproxy()
        self.toxiproxy.start()
        self.addCleanup(self.toxiproxy.stop)

# ################################################################################################################################

    def _get_subscribers_by_slot(self) -> 'dict[int, intlist]':
        """ Returns the indexes of the subscribers whose push subscription each slot owns.
        """
        admin = AdminClient(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        items, _ = admin.get_list(ModuleCtx.Subscription_List_Service)

        sub_keys:'anydict' = {}

        for item in items:
            if item['delivery_type'] == PubSub.Delivery_Type.Push:
                sub_keys[item['sec_name']] = item['sub_key']

        out:'dict[int, intlist]' = {}

        for index in range(PubSubConfig.Subscriber_Count):
            sub_key = sub_keys[ModuleCtx.Subscriber_Name_Pattern.format(index)]
            slot = get_owner_slot(sub_key, MultiCPUTestConfig.worker_count)
            out.setdefault(slot, []).append(index)

        return out

# ################################################################################################################################

    def _redirect(self, slot:'int', index:'int', proxy:'str', port:'int') -> 'None':
        """ Points the outgoing connection of a subscriber at its proxy and waits until the owning worker sends through it.
        """
        enmasse_import({'outgoing_rest': [_outgoing_config(index, port)]})

        receiver_port = PubSubConfig.receivers[index].port
        self.addCleanup(enmasse_import, {'outgoing_rest': [_outgoing_config(index, receiver_port)]})

        outconn_name = ModuleCtx.Subscriber_Name_Pattern.format(index) + '.out'
        deadline = monotonic() + ModuleCtx.Redirect_Deadline

        while True:
            received_before = self.toxiproxy.read_received_bytes(proxy)
            _ = invoke_on_slot(slot, ModuleCtx.Outgoing_Invoke_Service, {'outconn_name': outconn_name})

            if self.toxiproxy.read_received_bytes(proxy) > received_before:
                return

            if monotonic() > deadline:
                raise Exception(f'Slot {slot} does not send to {outconn_name} through {proxy}')

            sleep(MultiCPUCtx.Poll_Interval)

# ################################################################################################################################

    def _wait_for_all(self, indexes:'intlist', expected:'intset', deadline:'float') -> 'None':
        deadline_at = monotonic() + deadline

        for index in indexes:
            received = _get_seqs(PubSubConfig.receivers[index])

            while not expected <= received:
                if monotonic() > deadline_at:
                    break

                sleep(MultiCPUCtx.Poll_Interval)
                received = _get_seqs(PubSubConfig.receivers[index])

            missing = expected - received
            self.assertEqual(missing, set(), f'Subscriber {index} did not receive {len(missing)} messages')

# ################################################################################################################################

    def test_faulty_subscribers_do_not_block_their_slot(self) -> 'None':

        # The slot with the most subscribers holds the faulty ones and at least one healthy one ..
        subscribers_by_slot = self._get_subscribers_by_slot()
        slot = 0
        indexes:'intlist' = []

        for candidate_slot, candidate_indexes in subscribers_by_slot.items():
            if len(candidate_indexes) > len(indexes):
                slot = candidate_slot
                indexes = candidate_indexes

        self.assertGreaterEqual(len(indexes), ModuleCtx.Min_Subscribers_Per_Slot)

        slow, refusing, severed = indexes[:ModuleCtx.Faulty_Kind_Count]
        healthy_in_slot = indexes[ModuleCtx.Faulty_Kind_Count:]
        logger.info('Slot %s -> slow %s, refusing %s, severed %s, healthy %s', slot, slow, refusing, severed, healthy_in_slot)

        # .. each faulty subscriber is reached through a proxy of its own ..
        for index in (slow, refusing, severed):
            proxy = f'sub-{index:02d}'
            port = self.toxiproxy.add_proxy(proxy, PubSubConfig.receivers[index].port)
            self._redirect(slot, index, proxy, port)

        PubSubConfig.receivers[slow].clear_output()
        PubSubConfig.receivers[refusing].clear_output()
        PubSubConfig.receivers[severed].clear_output()

        # .. which delays its responses, refuses its connections or resets them ..
        self.toxiproxy.add_toxic(f'sub-{slow:02d}', 'latency', 'downstream', {'latency': ModuleCtx.Slow_Latency_Ms})
        self.toxiproxy.set_enabled(f'sub-{refusing:02d}', False)
        self.toxiproxy.add_toxic(f'sub-{severed:02d}', 'reset_peer', 'upstream', {'timeout': 0})

        publisher = PublishClient(MultiCPUTestConfig.base_url, PubSubConfig.Publisher_Name, MultiCPUTestConfig.sec_password)
        expected:'intset' = set()

        for seq in range(ModuleCtx.Message_Count):
            _ = publisher.publish(PubSubConfig.Push_Topic, {'seq': seq})
            expected.add(seq)

        # .. every other subscriber, including those of the same slot, receives every message ..
        healthy:'intlist' = []

        for index in range(PubSubConfig.Subscriber_Count):
            if index not in (slow, refusing, severed):
                healthy.append(index)

        self._wait_for_all(healthy, expected, ModuleCtx.Healthy_Deadline)

        # .. while the slow subscriber is still receiving them and the others have received none ..
        self.assertLess(len(_get_seqs(PubSubConfig.receivers[slow])), ModuleCtx.Message_Count)
        self.assertEqual(_get_seqs(PubSubConfig.receivers[refusing]), set())
        self.assertEqual(_get_seqs(PubSubConfig.receivers[severed]), set())

        # .. and once the endpoints recover, each faulty subscriber receives every message after repeated attempts.
        sleep(ModuleCtx.Fault_Duration)

        self.toxiproxy.set_enabled(f'sub-{refusing:02d}', True)
        self.toxiproxy.remove_toxic(f'sub-{severed:02d}', 'reset_peer', 'upstream')

        self._wait_for_all([slow, refusing, severed], expected, ModuleCtx.Recovery_Deadline)

        for index in (refusing, severed):
            attempts:'intlist' = []

            for record in PubSubConfig.receivers[index].get_request_records():
                attempts.append(record['delivery_attempt'])

            self.assertGreater(max(attempts), 1, f'Subscriber {index}')

        wait_until_receivers_quiet(PubSubConfig.receivers)

# ################################################################################################################################
# ################################################################################################################################
