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
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from http.client import OK
from threading import Event
from time import sleep
from uuid import uuid4

# Zato
from zato.common.test.client import AdminClient, PullClient
from zato.common.test.conftest_base_multi_cpu import basic_auth_header, connection_to_slot, MultiCPUTestConfig, post_json, \
    WorkerControl
from zato.common.typing_ import list_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http.client import HTTPConnection
    from zato.common.typing_ import anydict, anylist, intlist, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_writer')

# ################################################################################################################################
# ################################################################################################################################

publication_list = list_['Publication']
future_list      = list_[Future]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Publish_Path = '/test/multi-cpu/publish-with-id'
    Invoke_Path  = '/zato/api/invoke/{}'

    Admin_User                = 'admin.invoke'
    Subscription_List_Service = 'zato.pubsub.subscription.get-list'
    Browse_Service            = 'zato.pubsub.subscription.browse-queue'
    Browse_State              = 'pending'
    Browse_Page_Size          = 100

    One_Topic        = 'multi.cpu.writer.one'
    Many_Topic       = 'multi.cpu.writer.many.{:02d}'
    Kill_Topic       = 'multi.cpu.writer.kill'
    Duplicate_Topic  = 'multi.cpu.writer.duplicate'
    Browse_Topic     = 'multi.cpu.writer.browse'
    Many_Topic_Count = 10

    One_Subscribers      = ('test.multi-cpu.writer.one-a', 'test.multi-cpu.writer.one-b')
    Many_Subscriber      = 'test.multi-cpu.writer.many'
    Kill_Subscriber      = 'test.multi-cpu.writer.kill'
    Duplicate_Subscriber = 'test.multi-cpu.writer.duplicate'
    Browse_Subscriber    = 'test.multi-cpu.writer.browse'

    # How many messages each worker publishes in the tests of delivery order
    Messages_Per_Worker = 60

    # The priorities that the publications of each worker cycle through
    Priorities = (2, 5, 8)

    # How many messages one pull requests at most
    Pull_Batch = 1000

    # How many times the writer is terminated, how long the workers publish before each termination
    # and after the last restart of the writer, in seconds, and the upper bound of the publications of one worker
    Kill_Count            = 3
    Kill_Interval         = 2.0
    Settle_Time           = 2.0
    Max_Kill_Publications = 1_000_000

    # The exception that a publication raises under a message ID that belongs to another message
    Duplicate_Error = 'PubSubDuplicateMsgID'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Publication:
    msg_id:   'str'
    slot:     'int'
    seq:      'int'
    priority: 'int'

    # The name of the exception of a publication that failed, empty for one that succeeded
    error: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _publish(connection:'HTTPConnection', topic_name:'str', data:'anydict', msg_id:'str', priority:'int') -> 'anydict':
    """ Publishes one message through the worker that accepted the connection.
    """
    payload = {
        'topic_name': topic_name,
        'data': data,
        'msg_id': msg_id,
        'priority': priority,
    }

    out = post_json(connection, ModuleCtx.Publish_Path, payload)
    return out

# ################################################################################################################################

def _publish_from_slot(
    slot:'int',
    run_id:'str',
    topic_names:'strlist',
    max_count:'int',
    stop_event:'Event',
    ) -> 'publication_list':
    """ Publishes through the worker of a slot, each message once the previous one returned, cycling through the topics
    and the priorities, until max_count messages were published or the stop event is set.
    """
    out:'publication_list' = []

    connection = connection_to_slot(slot)
    seq = 0

    while seq < max_count and not stop_event.is_set():

        publication = Publication()
        publication.msg_id = f'{run_id}.{slot}.{seq}'
        publication.slot = slot
        publication.seq = seq
        publication.priority = ModuleCtx.Priorities[seq % len(ModuleCtx.Priorities)]

        topic_name = topic_names[seq % len(topic_names)]
        data = {'slot': slot, 'seq': seq}

        try:
            response = _publish(connection, topic_name, data, publication.msg_id, publication.priority)

        # A request without a response in time leaves the outcome of its publication unknown,
        # and the next one is sent over a new connection to the same worker ..
        except OSError as e:
            publication.error = type(e).__name__
            connection.close()
            connection = connection_to_slot(slot)

        # .. while a response says whether the publication succeeded.
        else:
            publication.error = response['error']

        out.append(publication)
        seq += 1

    connection.close()

    return out

# ################################################################################################################################

def _publish_from_every_slot(
    slots:'intlist',
    topic_names:'strlist',
    max_count:'int',
    stop_event:'Event',
    executor:'ThreadPoolExecutor',
    ) -> 'future_list':
    """ Starts one publisher per slot, all of which publish at the same time.
    """
    run_id = uuid4().hex

    out:'future_list' = []

    for slot in slots:
        future = executor.submit(_publish_from_slot, slot, run_id, topic_names, max_count, stop_event)
        out.append(future)

    return out

# ################################################################################################################################

def _collect(futures:'future_list') -> 'publication_list':
    """ Waits for every publisher and returns the publications of all of them, raising the exception of a publisher
    that ended with one.
    """
    out:'publication_list' = []

    for future in futures:
        publications = future.result()
        out.extend(publications)

    return out

# ################################################################################################################################

def _pull_all(sec_name:'str') -> 'anylist':
    """ Pulls and acknowledges the messages of a subscriber until its queue is empty and returns them in the order pulled.
    """
    puller = PullClient(MultiCPUTestConfig.base_url, sec_name, MultiCPUTestConfig.sec_password)

    out:'anylist' = []

    while True:
        result = puller.pull(max_messages=ModuleCtx.Pull_Batch)

        if result['message_count'] == 0:
            break

        out.extend(result['messages'])

    return out

# ################################################################################################################################

def _drain(sec_name:'str') -> 'None':
    """ Empties the queue of a subscriber, so that a test starts from no messages whichever test ran before it.
    """
    puller = PullClient(MultiCPUTestConfig.base_url, sec_name, MultiCPUTestConfig.sec_password)
    puller.drain()

# ################################################################################################################################
# ################################################################################################################################

class TestWriterProcess(unittest.TestCase):
    """ The workers of a server publish through its one pub/sub writer process, which writes every publication
    of every worker to the one pub/sub database.
    """

    def setUp(self) -> 'None':
        self.control = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        self.admin = AdminClient(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

# ################################################################################################################################

    def _get_slots(self) -> 'intlist':
        """ Returns the slot of every worker once every worker is ready.
        """
        rows = self.control.wait_for_all_ready()

        out:'intlist' = []

        for row in rows:
            out.append(row['slot'])

        return out

# ################################################################################################################################

    def _get_sub_key(self, sec_name:'str') -> 'str':
        items, _ = self.admin.get_list(ModuleCtx.Subscription_List_Service)

        for item in items:
            if item['sec_name'] == sec_name:
                return item['sub_key']

        raise Exception(f'No subscription of {sec_name}')

# ################################################################################################################################

    def _assert_received_once_in_order(self, messages:'anylist', publications:'publication_list') -> 'None':
        """ Confirms that the messages are those of the publications, each once, the higher priorities first,
        and those of one worker and one priority in the order the worker published them.
        """
        received_ids:'strlist' = []

        for message in messages:
            received_ids.append(message['meta']['msg_id'])

        expected_ids:'strset' = set()

        for publication in publications:
            self.assertEqual(publication.error, '', publication.msg_id)
            expected_ids.add(publication.msg_id)

        # Each message arrives once ..
        self.assertEqual(len(received_ids), len(set(received_ids)))
        self.assertEqual(set(received_ids), expected_ids)

        # .. the messages of a higher priority come first ..
        priorities:'intlist' = []

        for message in messages:
            priorities.append(message['meta']['priority'])

        self.assertEqual(priorities, sorted(priorities, reverse=True))

        # .. and within one priority, the messages of one worker come in the order of their publication.
        last_seq:'anydict' = {}

        for message in messages:
            data = message['data']
            key = (data['slot'], message['meta']['priority'])

            if key in last_seq:
                self.assertGreater(data['seq'], last_seq[key], key)

            last_seq[key] = data['seq']

# ################################################################################################################################

    def _run_ordered_publications(self, topic_names:'strlist') -> 'publication_list':
        """ Publishes the same number of messages through every worker at the same time and returns the publications.
        """
        slots = self._get_slots()
        stop_event = Event()

        with ThreadPoolExecutor(max_workers=len(slots)) as executor:
            futures = _publish_from_every_slot(slots, topic_names, ModuleCtx.Messages_Per_Worker, stop_event, executor)
            out = _collect(futures)

        self.assertEqual(len(out), len(slots) * ModuleCtx.Messages_Per_Worker)

        return out

# ################################################################################################################################

    def test_one_topic_delivered_once_and_in_order(self) -> 'None':
        """ Messages that every worker publishes to one topic reach each of its subscribers once and in publication
        order per priority.
        """
        for sec_name in ModuleCtx.One_Subscribers:
            _drain(sec_name)

        publications = self._run_ordered_publications([ModuleCtx.One_Topic])

        for sec_name in ModuleCtx.One_Subscribers:
            messages = _pull_all(sec_name)
            self._assert_received_once_in_order(messages, publications)

# ################################################################################################################################

    def test_many_topics_delivered_once_and_in_order(self) -> 'None':
        """ Messages that every worker publishes to many topics reach their subscriber once and in publication order
        per priority.
        """
        _drain(ModuleCtx.Many_Subscriber)

        topic_names:'strlist' = []

        for index in range(ModuleCtx.Many_Topic_Count):
            topic_names.append(ModuleCtx.Many_Topic.format(index))

        publications = self._run_ordered_publications(topic_names)

        messages = _pull_all(ModuleCtx.Many_Subscriber)
        self._assert_received_once_in_order(messages, publications)

# ################################################################################################################################

    def test_writer_terminated_during_commits(self) -> 'None':
        """ A writer terminated while every worker publishes loses no publication that received a success reply,
        and every publication that it committed is delivered once.
        """
        _drain(ModuleCtx.Kill_Subscriber)

        slots = self._get_slots()
        stop_event = Event()

        with ThreadPoolExecutor(max_workers=len(slots)) as executor:

            futures = _publish_from_every_slot(
                slots, [ModuleCtx.Kill_Topic], ModuleCtx.Max_Kill_Publications, stop_event, executor)

            # The writer is terminated while the workers publish, and each time the arbiter starts another one ..
            for _ in range(ModuleCtx.Kill_Count):
                sleep(ModuleCtx.Kill_Interval)

                writer_pid = self.control.get_writer_pid()
                os.kill(writer_pid, signal.SIGKILL)

                new_writer_pid = self.control.wait_for_writer(writer_pid)
                logger.info('Writer %s terminated, writer %s started', writer_pid, new_writer_pid)

            # .. after which the workers publish through the last one for a while.
            sleep(ModuleCtx.Settle_Time)
            stop_event.set()

            publications = _collect(futures)

        attempted:'strset' = set()
        succeeded:'strset' = set()

        for publication in publications:
            attempted.add(publication.msg_id)
            if not publication.error:
                succeeded.add(publication.msg_id)

        logger.info('Publications: %s, succeeded: %s', len(attempted), len(succeeded))

        received_ids:'strlist' = []

        for message in _pull_all(ModuleCtx.Kill_Subscriber):
            received_ids.append(message['meta']['msg_id'])

        received = set(received_ids)

        # Each committed publication is delivered once ..
        self.assertEqual(len(received_ids), len(received))

        # .. every publication with a success reply is among them ..
        self.assertEqual(succeeded - received, set())

        # .. and none of them is anything but a publication of a worker.
        self.assertEqual(received - attempted, set())

        self.assertGreater(len(succeeded), 0)

# ################################################################################################################################

    def test_repeated_publication_detected_from_any_worker(self) -> 'None':
        """ A publication repeated under its message ID through any worker receives the original result,
        and another message under that ID is rejected by any worker.
        """
        _drain(ModuleCtx.Duplicate_Subscriber)

        slots = self._get_slots()

        msg_id = uuid4().hex
        data = {'order_id': 'ORD-20261116-001', 'customer': 'John Smith'}
        other_data = {'order_id': 'ORD-20261116-002', 'customer': 'Jane Brown'}
        priority = ModuleCtx.Priorities[0]

        # The first publication stores the message ..
        connection = connection_to_slot(slots[0])
        response = _publish(connection, ModuleCtx.Duplicate_Topic, data, msg_id, priority)
        connection.close()

        self.assertEqual(response['error'], '')
        self.assertEqual(response['msg_id'], msg_id)

        for slot in slots[1:]:
            connection = connection_to_slot(slot)

            # .. the same publication through any other worker receives the same result ..
            response = _publish(connection, ModuleCtx.Duplicate_Topic, data, msg_id, priority)

            self.assertEqual(response['slot'], slot)
            self.assertEqual(response['error'], '')
            self.assertEqual(response['msg_id'], msg_id)

            # .. while another message under the same ID is rejected.
            response = _publish(connection, ModuleCtx.Duplicate_Topic, other_data, msg_id, priority)

            self.assertEqual(response['slot'], slot)
            self.assertEqual(response['error'], ModuleCtx.Duplicate_Error)

            connection.close()

        # The subscriber receives the first message alone.
        messages = _pull_all(ModuleCtx.Duplicate_Subscriber)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['meta']['msg_id'], msg_id)
        self.assertEqual(messages[0]['data'], data)

# ################################################################################################################################

    def test_every_worker_browses_the_messages_of_every_worker(self) -> 'None':
        """ The queue browser of the Dashboard, served by any worker, lists the messages that every worker published.
        """
        _drain(ModuleCtx.Browse_Subscriber)

        slots = self._get_slots()
        sub_key = self._get_sub_key(ModuleCtx.Browse_Subscriber)
        run_id = uuid4().hex

        # One message is published through each worker ..
        published:'strset' = set()

        for slot in slots:
            msg_id = f'{run_id}.{slot}'

            connection = connection_to_slot(slot)
            response = _publish(connection, ModuleCtx.Browse_Topic, {'slot': slot}, msg_id, ModuleCtx.Priorities[0])
            connection.close()

            self.assertEqual(response['error'], '')
            published.add(msg_id)

        # .. and each worker lists all of them.
        path = ModuleCtx.Invoke_Path.format(ModuleCtx.Browse_Service)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': basic_auth_header(ModuleCtx.Admin_User, MultiCPUTestConfig.invoke_password),
        }

        payload = {
            'sub_key': sub_key,
            'state': ModuleCtx.Browse_State,
            'page_size': ModuleCtx.Browse_Page_Size,
        }

        for slot in slots:

            connection = connection_to_slot(slot)
            connection.request('POST', path, body=json.dumps(payload), headers=headers)

            response = connection.getresponse()
            body = response.read()
            connection.close()

            self.assertEqual(response.status, OK, body)

            result = json.loads(body)

            listed:'strset' = set()

            for row in result['rows']:
                listed.add(row['msg_id'])

            self.assertEqual(result['total'], len(published), slot)
            self.assertEqual(listed, published, slot)

        _drain(ModuleCtx.Browse_Subscriber)

# ################################################################################################################################
# ################################################################################################################################
