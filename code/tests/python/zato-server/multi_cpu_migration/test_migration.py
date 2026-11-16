# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import re
import sqlite3
import unittest
from http.client import OK
from time import monotonic, sleep

# Zato
from zato.common.pubsub.sql.schema import delivery_table, mcp_session_table, message_table, topic_sub_table
from zato.common.test.client import PublishClient
from zato.common.test.conftest_base_multi_cpu import MultiCPUTestConfig, WorkerControl
from zato.common.test.receiver import wait_until_receivers_quiet
from zato.common.worker_count import ServerWorkers

# Test helpers
from _suite import get_server_conf_path, MigrationConfig, restart_server, set_delivery_active

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import any_, anydict, dictlist, intlist, strintdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_migration')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The number of workers of a server with several of them, and the number that the server changes to
    Several_Worker_Count = 4
    Changed_Worker_Count = 3

    # How many messages a test publishes
    Message_Count = 20

    # How long a test waits for every delivery, in seconds
    Delivery_Timeout = 120.0

    # How many attempts the rejecting receiver answers before the server is terminated
    Attempts_Before_Restart = 2

    # How long the attempts before the restart, and the ownership of the keys after it, may take, in seconds
    Wait_Deadline = 60.0

    Poll_Interval = 0.25

    # The line of server.conf that holds the worker count
    Worker_Count_Line = re.compile(rf'^{ServerWorkers.Config_Key}\s*=.*\n', re.MULTILINE)

    # The tables whose rows hold the messages, their deliveries and the subscriptions of the topics
    Data_Tables = (message_table.name, delivery_table.name, topic_sub_table.name)

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

def _get_pubsub_db_path() -> 'str':
    out = os.environ['Zato_PubSub_DB_Path']
    return out

# ################################################################################################################################

def _count_rows(connection:'sqlite3.Connection') -> 'strintdict':
    """ Returns the number of rows of each table that holds the data of the topic.
    """
    out:'strintdict' = {}

    for table_name in ModuleCtx.Data_Tables:
        cursor = connection.execute(f'select count(*) from {table_name}')
        row = cursor.fetchone()
        out[table_name] = row[0]

    return out

# ################################################################################################################################

def _has_table(table_name:'str') -> 'bool':
    """ Whether the pub/sub database has a table of the given name.
    """
    connection = sqlite3.connect(_get_pubsub_db_path())

    try:
        cursor = connection.execute('select name from sqlite_master where type = ? and name = ?', ('table', table_name))
        row = cursor.fetchone()
    finally:
        connection.close()

    out = row is not None
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMigrationToSeveralWorkers(unittest.TestCase):
    """ A server that ran with one process, and a server whose number of workers changes, starts again with the messages,
    the attempts and the database that it had. Each test starts the server with the number of workers it needs.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(MultiCPUTestConfig.base_url, MigrationConfig.Publisher_Name,
            MultiCPUTestConfig.sec_password)

# ################################################################################################################################

    def _get_control(self) -> 'WorkerControl':
        out = WorkerControl(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)
        return out

# ################################################################################################################################

    def _publish(self, count:'int') -> 'None':
        for seq in range(count):
            _ = self.publisher.publish(MigrationConfig.Topic_Name, {'seq': seq})

        logger.info('Published %d messages to %s', count, MigrationConfig.Topic_Name)

# ################################################################################################################################

    def _start_with_pending(self, worker_count:'int') -> 'None':
        """ Starts the server with the given number of workers and every delivery off, and publishes the messages
        of the test, which wait in the queue of each subscription.
        """
        set_delivery_active(False)
        restart_server(worker_count)
        self._publish(ModuleCtx.Message_Count)

# ################################################################################################################################

    def _assert_delivered_once_in_order(self, count:'int') -> 'None':
        """ Every receiver receives each message once and in the order of publication.
        """
        expected:'intlist' = list(range(count))

        for index, receiver in enumerate(MigrationConfig.receivers):
            messages = receiver.wait_for_delivery(count, ModuleCtx.Delivery_Timeout)

            received:'intlist' = []

            for message in messages:
                received.append(_get_seq(message))

            self.assertEqual(received, expected, f'Subscriber {index}')

        # .. and no copy arrives after the last message.
        wait_until_receivers_quiet(MigrationConfig.receivers)

        for index, receiver in enumerate(MigrationConfig.receivers):
            self.assertEqual(receiver.delivered_count(), count, f'Subscriber {index}')

# ################################################################################################################################

    def _wait_for_rejected_attempts(self, receiver:'WebhookReceiver') -> 'dictlist':
        """ Waits until the receiver rejected the number of attempts that precede the restart and returns their records.
        """
        deadline = monotonic() + ModuleCtx.Wait_Deadline

        while monotonic() < deadline:
            out = receiver.get_request_records()

            if len(out) >= ModuleCtx.Attempts_Before_Restart:
                return out

            sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'Fewer than {ModuleCtx.Attempts_Before_Restart} attempts within {ModuleCtx.Wait_Deadline}s')

# ################################################################################################################################

    def _wait_for_key_ownership(self) -> 'None':
        """ Waits until every slot owns subscription keys and the keys of all slots add up to the subscriptions of the suite.
        """
        control = self._get_control()
        deadline = monotonic() + ModuleCtx.Wait_Deadline

        while monotonic() < deadline:
            rows = control.wait_for_all_ready()

            counts:'intlist' = []

            for row in rows:
                counts.append(row['sub_key_count'])

            logger.info('Subscription keys by slot -> %s', counts)

            if sum(counts) == MigrationConfig.Subscriber_Count:
                if min(counts) > 0:
                    return

            sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'Subscription keys not owned by every slot within {ModuleCtx.Wait_Deadline}s')

# ################################################################################################################################

    def test_pending_messages_of_one_process(self) -> 'None':
        """ The messages that a server of one process left pending are delivered once and in order
        after it starts again with several workers.
        """
        self._start_with_pending(MigrationConfig.Single_Worker_Count)

        restart_server(ModuleCtx.Several_Worker_Count)
        set_delivery_active(True)

        self._assert_delivered_once_in_order(ModuleCtx.Message_Count)

# ################################################################################################################################

    def test_attempts_of_one_process(self) -> 'None':
        """ A message whose delivery a server of one process attempted and that its subscriber rejected stays
        in the queue under its retry policy and is delivered once after the server starts again with several workers.
        SQLite counts the attempts of a message in memory, so their numbers start again with the new server.
        """
        set_delivery_active(True)
        restart_server(MigrationConfig.Single_Worker_Count)

        # The first receiver rejects each attempt until the server starts again ..
        receiver = MigrationConfig.receivers[0]
        receiver.behavior.set_reject_503()

        _ = self.publisher.publish(MigrationConfig.Topic_Name, {'seq': 0})

        records_before = self._wait_for_rejected_attempts(receiver)
        logger.info('Attempts before the restart -> %s', records_before)

        restart_server(ModuleCtx.Several_Worker_Count)
        receiver.behavior.set_accept()

        # .. every receiver receives the message once ..
        self._assert_delivered_once_in_order(1)

        # .. and the first receiver accepted it in an attempt of the new server, after the attempts of the previous one.
        records = receiver.get_request_records()
        logger.info('Attempts of the message -> %s', records)

        attempt_count = len(records)
        self.assertGreater(attempt_count, len(records_before))

        last_record = records[-1]
        self.assertEqual(last_record['status_code'], OK)

        for record in records:
            self.assertEqual(record['msg_id'], last_record['msg_id'])

# ################################################################################################################################

    def test_worker_count_change(self) -> 'None':
        """ A server that starts again with another number of workers spreads the subscription keys over the new slots
        and delivers each pending message once.
        """
        self._start_with_pending(ModuleCtx.Several_Worker_Count)

        restart_server(ModuleCtx.Changed_Worker_Count)
        set_delivery_active(True)

        self._wait_for_key_ownership()
        self._assert_delivered_once_in_order(ModuleCtx.Message_Count)

# ################################################################################################################################

    def test_session_table_created_at_startup(self) -> 'None':
        """ A pub/sub database without the session table receives the table when the server starts,
        and its messages remain as they were.
        """
        self._start_with_pending(ModuleCtx.Several_Worker_Count)

        # The table is removed while the server is not running, as in a database of a server that predates it ..
        MigrationConfig.state.kill_server()

        connection = sqlite3.connect(_get_pubsub_db_path())

        try:
            counts_before = _count_rows(connection)
            _ = connection.execute(f'drop table {mcp_session_table.name}')
            connection.commit()
        finally:
            connection.close()

        self.assertFalse(_has_table(mcp_session_table.name))

        # .. the server creates it as it starts ..
        restart_server(ModuleCtx.Several_Worker_Count)
        self.assertTrue(_has_table(mcp_session_table.name))

        connection = sqlite3.connect(_get_pubsub_db_path())

        try:
            counts_after = _count_rows(connection)
        finally:
            connection.close()

        # .. with every message still in place ..
        self.assertEqual(counts_after, counts_before)

        # .. and delivered once its delivery is on.
        set_delivery_active(True)
        self._assert_delivered_once_in_order(ModuleCtx.Message_Count)

# ################################################################################################################################

    def test_server_conf_without_worker_count(self) -> 'None':
        """ A server.conf written before the worker count existed starts the number of workers that auto resolves to.
        """
        server_conf_path = get_server_conf_path()

        with open(server_conf_path) as server_conf_file:
            server_conf = server_conf_file.read()

        server_conf, removed_count = ModuleCtx.Worker_Count_Line.subn('', server_conf)
        self.assertEqual(removed_count, 1)

        with open(server_conf_path, 'w') as server_conf_file:
            _ = server_conf_file.write(server_conf)

        restart_server(None)

        rows = self._get_control().wait_for_all_ready()
        logger.info('Slots without a worker count -> %d, auto -> %d', len(rows), MultiCPUTestConfig.worker_count)

        self.assertEqual(len(rows), MultiCPUTestConfig.worker_count)

# ################################################################################################################################
# ################################################################################################################################
