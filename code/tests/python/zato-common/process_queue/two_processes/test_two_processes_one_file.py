# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The worker and the config process of one server write to one SQLite file of the Zato database at the same time.
# The worker publishes, pulls and acknowledges messages, which records their audit events in the same transactions,
# and writes the audit events of a REST channel. The config process renames and then deletes a topic that holds
# many messages, in batches, while it writes audit events of its own. No message and no audit event is lost
# or written twice, no write waits past its deadline, SQLite reports no lock, and the longest time that a write
# of the worker took during the batches of the config process is recorded.

# stdlib
import json
import os
import sqlite3
import time
from time import monotonic
from typing import NamedTuple

# gevent
from gevent import joinall, sleep, spawn
from gevent.event import Event

# Zato
from server_processes import ModuleCtx as ProcessesCtx, receive, ServerProcesses
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import AuditEvent, AuditSource
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import ModuleCtx as PubSubConfigCtx
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from zato.common.typing_ import any_, anydict, anylist, callable_, strintdict, strlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    callable_ = callable_
    Connection = Connection
    strintdict = strintdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The topics of the worker, each with one subscriber, and the publishers of each topic
    Topic_Count = 4
    Publishers_Per_Topic = 4

    # How many greenlets of the worker write the audit events of a REST channel
    REST_Writer_Count = 4

    # How many messages one pull leases at most
    Pull_Max_Messages = 100

    # The topic that the config process renames and deletes, its new name, its subscriber and how many messages it holds
    Seeded_Topic = 'test.two-processes.seeded'
    Renamed_Topic = 'test.two-processes.renamed'
    Seeded_Sub_Key = 'sk.two-processes.seeded'
    Seeded_Count = 5000

    # How many greenlets of the config process publish the messages of its topic
    Seed_Publisher_Count = 50

    # How many rows one batch of the rename and of the delete touches, which leaves many batches
    # between which the writes of the worker take their turns
    Batch_Size = '250'

    # The object names of the audit events of the REST channel and of the configuration
    Channel_Name = 'test.two-processes.channel'
    Config_Object_Name = 'test.two-processes.config'

    # The data of each message
    Message_Data = 'two-processes'

    # The reports that the processes and the test process exchange
    Report_Running = 'running'
    Report_Seeded = 'seeded'
    Report_Done = 'done'
    Request_Begin = 'begin'
    Request_Stop = 'stop'

    # How long the test waits for each report, in seconds
    Seed_Timeout = 300.0
    Run_Timeout = 600.0

    # How often a process checks for a request of the test process and a puller for new messages, in seconds
    Poll_Interval = 0.05

# ################################################################################################################################
# ################################################################################################################################

class _WindowWrites(NamedTuple):
    """ How many writes of the worker took place during the rename and the delete, and how long the longest took.
    """
    count: 'int'
    longest: 'float'

# ################################################################################################################################
# ################################################################################################################################

def _get_topic_name(index:'int') -> 'str':
    out = f'test.two-processes.topic.{index}'
    return out

# ################################################################################################################################

def _get_sub_key(index:'int') -> 'str':
    out = f'sk.two-processes.{index}'
    return out

# ################################################################################################################################

def _wait_for_request(conn:'Connection') -> 'any_':
    """ Waits for the next request of the test process while the other greenlets of the process run.
    """
    while not conn.poll():
        sleep(ModuleCtx.Poll_Interval)

    out = conn.recv()
    return out

# ################################################################################################################################
# ################################################################################################################################

class _ProcessRun:
    """ The writes of the greenlets of one process - what each of them wrote, how long each write took and their errors.
    """

    def __init__(self, backend:'SQLPubSubBackend', audit_log:'AuditLog') -> 'None':
        self.backend = backend
        self.audit_log = audit_log

        # Set once the test process asks the writers to stop, and once the publishers stopped
        self.is_stopping = Event()
        self.is_published = Event()

        self.published:'strlist' = []
        self.pulled:'strlist' = []
        self.cids:'strlist' = []

        # The start and the duration of each write, in seconds
        self.writes:'anylist' = []

        self.errors:'strlist' = []

    def run_safely(self, func:'callable_', *args:'any_') -> 'None':
        """ Runs one writer and records its exception, which ends the writer.
        """
        try:
            func(*args)
        except Exception as exception:
            error = f'{type(exception).__name__}: {exception}'
            self.errors.append(error)

    def _record_write(self, started:'float') -> 'None':
        elapsed = monotonic() - started
        write = (started, elapsed)
        self.writes.append(write)

    def publish(self, topic_name:'str') -> 'None':
        """ Publishes to a topic until the test process asks the writers to stop.
        """
        while not self.is_stopping.is_set():
            started = monotonic()
            result = self.backend.publish(topic_name, ModuleCtx.Message_Data)
            self._record_write(started)
            self.published.append(result.msg_id)

    def pull(self, sub_key:'str') -> 'None':
        """ Pulls and acknowledges the messages of a subscriber until none is left after the publishers stopped.
        """
        while True:

            started = monotonic()
            messages = self.backend.pull_messages(sub_key, ModuleCtx.Pull_Max_Messages)

            # Nothing to pull ends the puller only once nothing more is published ..
            if not messages:
                if self.is_published.is_set():
                    return
                sleep(ModuleCtx.Poll_Interval)
                continue

            self._record_write(started)

            # .. while each message pulled is acknowledged at once.
            msg_ids:'strlist' = []

            for message in messages:
                msg_ids.append(message['msg_id'])

            started = monotonic()
            _ = self.backend.ack_pulled(sub_key, msg_ids)
            self._record_write(started)

            self.pulled.extend(msg_ids)

    def write_events(self, source:'str', event_type:'str', object_name:'str') -> 'None':
        """ Writes audit events, each under a correlation ID of its own, until the test process asks the writers to stop.
        """
        while not self.is_stopping.is_set():
            cid = CryptoManager.generate_hex_string()
            started = monotonic()
            _ = self.audit_log.insert(source, event_type, object_name, cid=cid)
            self._record_write(started)
            self.cids.append(cid)

    def get_report(self) -> 'anydict':
        out = {
            'published': self.published,
            'pulled': self.pulled,
            'cids': self.cids,
            'writes': self.writes,
            'errors': self.errors,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_run() -> '_ProcessRun':
    audit_log = AuditLog(ProcessesCtx.Server_Name)
    backend = SQLPubSubBackend(audit_log=audit_log)

    out = _ProcessRun(backend, audit_log)
    return out

# ################################################################################################################################

def _write_report(report_path:'str', report:'anydict') -> 'None':
    """ Stores the report of a process in a file, which, unlike the connection of the process, has no limit on its size.
    """
    with open(report_path, 'w') as report_file:
        json.dump(report, report_file)

# ################################################################################################################################

def _read_report(conn:'Connection', report_path:'str') -> 'anydict':
    """ Waits until a process stored its report and returns the report.
    """
    assert receive(conn, ModuleCtx.Run_Timeout) == ModuleCtx.Report_Done

    with open(report_path) as report_file:
        out = json.load(report_file)

    return out

# ################################################################################################################################

def _run_worker(conn:'Connection', report_path:'str') -> 'None':
    """ Publishes, pulls and writes the audit events of a REST channel until the test process asks the worker to stop,
    then pulls what is left and reports what it wrote.
    """
    run = _new_run()

    # Each topic has one subscriber ..
    for index in range(ModuleCtx.Topic_Count):
        topic_name = _get_topic_name(index)
        sub_key = _get_sub_key(index)
        run.backend.subscribe(sub_key, topic_name)

    # .. its publishers and its puller run at the same time ..
    publishers:'anylist' = []
    others:'anylist' = []

    for index in range(ModuleCtx.Topic_Count):
        topic_name = _get_topic_name(index)
        sub_key = _get_sub_key(index)

        for _ in range(ModuleCtx.Publishers_Per_Topic):
            publisher = spawn(run.run_safely, run.publish, topic_name)
            publishers.append(publisher)

        puller = spawn(run.run_safely, run.pull, sub_key)
        others.append(puller)

    # .. as do the writers of the audit events of the REST channel ..
    for _ in range(ModuleCtx.REST_Writer_Count):
        writer = spawn(run.run_safely, run.write_events, AuditSource.REST_Channel, AuditEvent.Request_Received,
            ModuleCtx.Channel_Name)
        others.append(writer)

    conn.send(ModuleCtx.Report_Running)

    # .. until the test process asks the worker to stop ..
    _ = _wait_for_request(conn)
    run.is_stopping.set()

    _ = joinall(publishers)
    run.is_published.set()

    # .. after which the pullers take what is left.
    _ = joinall(others)

    report = run.get_report()
    _write_report(report_path, report)

    conn.send(ModuleCtx.Report_Done)

# ################################################################################################################################

def _seed(run:'_ProcessRun') -> 'None':
    """ Publishes the messages of the topic that the config process renames and deletes.
    """
    count = ModuleCtx.Seeded_Count // ModuleCtx.Seed_Publisher_Count
    publishers:'anylist' = []

    for _ in range(ModuleCtx.Seed_Publisher_Count):
        publisher = spawn(run.run_safely, _seed_messages, run, count)
        publishers.append(publisher)

    _ = joinall(publishers)

# ################################################################################################################################

def _seed_messages(run:'_ProcessRun', count:'int') -> 'None':
    for _ in range(count):
        result = run.backend.publish(ModuleCtx.Seeded_Topic, ModuleCtx.Message_Data)
        run.published.append(result.msg_id)

# ################################################################################################################################

def _run_config(conn:'Connection', report_path:'str') -> 'None':
    """ Publishes the messages of a topic, then renames and deletes it while it writes audit events of the configuration,
    and reports what it wrote and when the rename and the delete began and ended.
    """
    run = _new_run()

    # The topic holds many messages of its subscriber ..
    run.backend.subscribe(ModuleCtx.Seeded_Sub_Key, ModuleCtx.Seeded_Topic)
    _seed(run)

    conn.send(ModuleCtx.Report_Seeded)

    # .. and once the worker runs ..
    _ = _wait_for_request(conn)

    writer = spawn(run.run_safely, run.write_events, AuditSource.Config, AuditEvent.Config_Edited,
        ModuleCtx.Config_Object_Name)

    # .. the topic is renamed and deleted, in batches, while the audit events of the configuration are written.
    window_start = monotonic()

    run.run_safely(run.backend.rename_topic, ModuleCtx.Seeded_Topic, ModuleCtx.Renamed_Topic)
    run.run_safely(run.backend.delete_topic, ModuleCtx.Renamed_Topic)

    window_end = monotonic()

    run.is_stopping.set()
    writer.join()

    report = run.get_report()
    report['window_start'] = window_start
    report['window_end'] = window_end

    _write_report(report_path, report)

    conn.send(ModuleCtx.Report_Done)

# ################################################################################################################################
# ################################################################################################################################

def _read_counts(db_path:'str', query:'str') -> 'strintdict':
    """ Returns how many rows a grouping query counted for each key.
    """
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.execute(query)
        rows = cursor.fetchall()
    finally:
        connection.close()

    out:'strintdict' = {}

    for key, count in rows:
        out[key] = count

    return out

# ################################################################################################################################

def _get_event_counts(db_path:'str', column:'str', source:'str', event_type:'str') -> 'strintdict':
    query = f"select {column}, count(*) from event where source = '{source}' and event_type = '{event_type}' " + \
        f'group by {column}'

    out = _read_counts(db_path, query)
    return out

# ################################################################################################################################

def _get_repeated_or_missing(expected:'strlist', counts:'strintdict') -> 'strlist':
    """ Returns each key that the counts lack, have more than once, or have with no expected key behind it.
    """
    out:'strlist' = []
    expected_keys = set(expected)

    for key in expected:
        if counts.get(key) != 1:
            out.append(key)

    for key in counts:
        if key not in expected_keys:
            out.append(key)

    return out

# ################################################################################################################################

def _get_window_writes(writes:'anylist', window_start:'float', window_end:'float') -> '_WindowWrites':
    """ Returns how many writes of the worker took place during the rename and the delete, and how long the longest took.
    """
    count = 0
    longest = 0.0

    for started, elapsed in writes:
        ended = started + elapsed

        if ended >= window_start and started <= window_end:
            count += 1
            longest = max(longest, elapsed)

    out = _WindowWrites(count, longest)
    return out

# ################################################################################################################################

def _write_wait_report(write_count:'int', window_count:'int', longest:'float', window:'float') -> 'None':
    """ Appends the longest wait of a write of the worker during the batches of the config process to the report of the suite.
    """
    directory = os.path.join(get_runtime_dir(), 'reports')
    os.makedirs(directory, exist_ok=True)

    line = f'two processes | {time.strftime("%H:%M:%S")} | worker writes {write_count} | ' + \
        f'during rename and delete {window_count} | rename and delete {window:.3f}s | longest worker write {longest:.3f}s\n'

    report_path = os.path.join(directory, 'two-processes-wait.txt')

    with open(report_path, 'a') as report_file:
        _ = report_file.write(line)

# ################################################################################################################################
# ################################################################################################################################

def test_worker_and_config_process_on_one_file(database_path:'str', monkeypatch:'any_') -> 'None':
    monkeypatch.setenv(PubSubConfigCtx.Env_Batch_Size, ModuleCtx.Batch_Size)

    report_dir = os.path.dirname(database_path)
    config_report_path = os.path.join(report_dir, 'config-report.json')
    worker_report_path = os.path.join(report_dir, 'worker-report.json')

    processes = ServerProcesses()

    # The config process publishes the messages of its topic first ..
    config_conn = processes.start(ProcessesCtx.Role_Config, _run_config, config_report_path)
    assert receive(config_conn, ModuleCtx.Seed_Timeout) == ModuleCtx.Report_Seeded

    # .. then the worker starts its traffic ..
    worker_conn = processes.start(ProcessesCtx.Role_Worker, _run_worker, worker_report_path)
    assert receive(worker_conn, ModuleCtx.Seed_Timeout) == ModuleCtx.Report_Running

    # .. the config process renames and deletes the topic while the traffic runs ..
    config_conn.send(ModuleCtx.Request_Begin)
    config_report = _read_report(config_conn, config_report_path)

    # .. and the worker stops once that completed.
    worker_conn.send(ModuleCtx.Request_Stop)
    worker_report = _read_report(worker_conn, worker_report_path)

    processes.join()

    # No write reported an error, which includes waiting past its deadline and a lock of SQLite ..
    errors:'strlist' = []
    errors.extend(config_report['errors'])
    errors.extend(worker_report['errors'])

    assert not errors, errors

    # .. every message that the worker published was pulled once ..
    published = sorted(worker_report['published'])
    pulled = sorted(worker_report['pulled'])

    assert published, 'Nothing published'
    assert pulled == published, (len(pulled), len(published))

    # .. the topic of the config process held every message it published, and none of them is left ..
    assert len(config_report['published']) == ModuleCtx.Seeded_Count

    topic_names = f"'{ModuleCtx.Seeded_Topic}', '{ModuleCtx.Renamed_Topic}'"
    query = f'select topic_name, count(*) from pubsub_message where topic_name in ({topic_names}) group by topic_name'
    left = _read_counts(database_path, query)

    assert not left, left

    # .. each publication has one audit event, of either process ..
    all_published:'strlist' = []
    all_published.extend(worker_report['published'])
    all_published.extend(config_report['published'])

    counts = _get_event_counts(database_path, 'msg_id', AuditSource.PubSub, AuditEvent.Published)
    assert not _get_repeated_or_missing(all_published, counts)

    # .. each message pulled has one audit event of its reception ..
    counts = _get_event_counts(database_path, 'msg_id', AuditSource.PubSub, AuditEvent.Received)
    assert not _get_repeated_or_missing(worker_report['pulled'], counts)

    # .. and each audit event of the REST channel and of the configuration was written once.
    counts = _get_event_counts(database_path, 'cid', AuditSource.REST_Channel, AuditEvent.Request_Received)
    assert worker_report['cids']
    assert not _get_repeated_or_missing(worker_report['cids'], counts)

    counts = _get_event_counts(database_path, 'cid', AuditSource.Config, AuditEvent.Config_Edited)
    assert config_report['cids']
    assert not _get_repeated_or_missing(config_report['cids'], counts)

    # The longest time that a write of the worker took during the rename and the delete is recorded.
    window_start = config_report['window_start']
    window_end = config_report['window_end']

    writes = worker_report['writes']
    write_count = len(writes)
    window_writes = _get_window_writes(writes, window_start, window_end)

    assert window_writes.count > 0, 'No write of the worker took place during the rename and the delete'

    window = window_end - window_start
    _write_wait_report(write_count, window_writes.count, window_writes.longest, window)

# ################################################################################################################################
# ################################################################################################################################
