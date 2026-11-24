# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The SQLite file of the Zato database of a running server is removed or replaced, as a restore script or a remount
# of a volume does. The server answers publications with 503, stops its push deliveries, writes no audit events
# and creates no new file in place of the one that was removed.

# stdlib
import os
import shutil
import threading
import time
from http.client import OK, SERVICE_UNAVAILABLE
from typing import NamedTuple

# pytest
import pytest

# Zato
from environment import DatabaseFileEnvironment, get_digest, wait_until
from zato.common.test.sql_conformance.disk import get_disk_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intlist

    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the tests
    Dir_Name = 'database-file-sqlite'

    # The name of the server
    Server_Name = 'database-file'

    # How many messages wait for their push delivery when the file is removed
    Pending_Count = 20

    # How long the first push delivery and the first rejected push may take, in seconds
    Delivery_Timeout = 60

    # How long the endpoint is observed for pushes after the removal, in seconds, which spans several retries of a push
    Observation_Seconds = 20

    # How long the log of the server may take to record the removal, in seconds
    Log_Timeout = 10

    # How long the replacement file is observed for writes, in seconds, which spans many WAL checkpoint intervals
    Replacement_Observation_Seconds = 5

    # How many clients publish at the same time, and for how long before and after the removal, in seconds
    Publisher_Count = 4
    Publish_Seconds_Before = 3
    Publish_Seconds_After = 5

    # The suffix of the copy of the database that replaces it
    Copy_Suffix = '.copy'

    # The message that the server logs once a process finds the file removed or replaced
    Removal_Log_Text = 'was removed or replaced while the process was running'

    # How many processes of a server use the database, the worker and the config process
    Database_Process_Count = 2

    # The status that a client records for a request that received no response
    No_Response_Status = 0

# ################################################################################################################################
# ################################################################################################################################

class PublicationRecord(NamedTuple):
    """ When a publication was sent and the status code that the server answered it with.
    """
    started_at: 'float'
    status_code: 'int'

publication_record_list = list[PublicationRecord]
thread_list             = list[threading.Thread]

# ################################################################################################################################
# ################################################################################################################################

class Publishers:
    """ Clients that publish at the same time, each recording when it sent each publication and how it was answered.
    """

    def __init__(self, environment:'DatabaseFileEnvironment') -> 'None':
        self.environment = environment
        self.records:'publication_record_list' = []
        self.lock = threading.Lock()
        self.is_running = threading.Event()
        self.threads:'thread_list' = []

    def _publish_loop(self, publisher_index:'int') -> 'None':

        counter = 0

        while self.is_running.is_set():
            counter += 1
            correl_id = f'publisher.{publisher_index}.{counter}'
            started_at = time.monotonic()

            try:
                result = self.environment.publish(correl_id)
                status_code = result.status_code
            except Exception:
                status_code = ModuleCtx.No_Response_Status

            record = PublicationRecord(started_at, status_code)

            with self.lock:
                self.records.append(record)

    def start(self) -> 'None':
        self.is_running.set()

        for publisher_index in range(ModuleCtx.Publisher_Count):
            thread = threading.Thread(target=self._publish_loop, args=(publisher_index,), daemon=True)
            thread.start()
            self.threads.append(thread)

    def stop(self) -> 'None':
        self.is_running.clear()

        for thread in self.threads:
            thread.join()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def environment() -> 'any_':
    """ A running server on SQLite with the endpoint that it pushes to.
    """
    base_dir = get_disk_dir(ModuleCtx.Dir_Name)
    shutil.rmtree(base_dir)
    os.makedirs(base_dir)

    out = DatabaseFileEnvironment(ModuleCtx.Server_Name, base_dir, extra_server_env={})

    try:
        out.start()
        yield out
    finally:
        out.stop()
        shutil.rmtree(base_dir)

# ################################################################################################################################
# ################################################################################################################################

def _has_rejected_push(environment:'DatabaseFileEnvironment') -> 'bool':
    """ Whether the endpoint rejected at least one push.
    """
    for record in environment.receiver.get_request_records():
        if record['status_code'] == SERVICE_UNAVAILABLE:
            return True

    return False

# ################################################################################################################################

def _wait_for_removal_log(environment:'DatabaseFileEnvironment') -> 'int':
    """ Waits until the log of the server records the removal and returns how many times it does.
    """
    def is_logged() -> 'bool':
        count = environment.count_log_lines(ModuleCtx.Removal_Log_Text)
        out = count > 0
        return out

    wait_until(is_logged, ModuleCtx.Log_Timeout, 'the log of the removal of the database file')

    out = environment.count_log_lines(ModuleCtx.Removal_Log_Text)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_removal_with_pending_deliveries(environment:'DatabaseFileEnvironment') -> 'None':
    """ Once the file is removed, publications are answered with 503, the messages that wait for their push deliveries
    are not pushed, an audited call writes nothing, no new file is created, and each process logs the removal once.
    """
    # A publication is pushed to the endpoint ..
    result = environment.publish('before-removal')
    assert result.status_code == OK, result

    delivered = environment.receiver.wait_for_delivery(1, ModuleCtx.Delivery_Timeout)
    assert len(delivered) == 1, delivered

    # .. the endpoint starts to reject pushes, so that the next publications wait for their deliveries ..
    environment.receiver.behavior.set_reject_503()

    for idx in range(ModuleCtx.Pending_Count):
        result = environment.publish(f'pending.{idx}')
        assert result.status_code == OK, result

    def has_rejected_push() -> 'bool':
        out = _has_rejected_push(environment)
        return out

    wait_until(has_rejected_push, ModuleCtx.Delivery_Timeout, 'a rejected push')

    # .. the file is removed ..
    environment.remove_database()

    # .. the next publication is refused ..
    result = environment.publish('after-removal')
    assert result.status_code == SERVICE_UNAVAILABLE, result

    # .. and the endpoint that accepts pushes again receives none of the messages that were waiting.
    delivered_count = environment.receiver.delivered_count()
    environment.receiver.behavior.set_accept()

    time.sleep(ModuleCtx.Observation_Seconds)

    delivered_count_after = environment.receiver.delivered_count()
    assert delivered_count_after == delivered_count, (delivered_count, delivered_count_after)

    # An audited call is served without its audit events, which creates no new file ..
    result = environment.call_audited()
    assert result.status_code == OK, result

    assert not os.path.exists(environment.db_path)

    # .. and the processes that found the file removed logged it once each.
    log_count = _wait_for_removal_log(environment)
    assert log_count <= ModuleCtx.Database_Process_Count, log_count

# ################################################################################################################################

def test_replacement(environment:'DatabaseFileEnvironment') -> 'None':
    """ Once another file replaces the file of the database, publications are answered with 503,
    and the server writes nothing into the replacement.
    """
    result = environment.publish('before-replacement')
    assert result.status_code == OK, result

    # Another file is put in place of the database ..
    copy_path = environment.db_path + ModuleCtx.Copy_Suffix

    _ = shutil.copy2(environment.db_path, copy_path)
    os.replace(copy_path, environment.db_path)

    digest = get_digest(environment.db_path)

    # .. publications are refused ..
    result = environment.publish('after-replacement')
    assert result.status_code == SERVICE_UNAVAILABLE, result

    # .. an audited call writes nothing ..
    result = environment.call_audited()
    assert result.status_code == OK, result

    # .. and the replacement stays as it was put in place.
    time.sleep(ModuleCtx.Replacement_Observation_Seconds)

    digest_after = get_digest(environment.db_path)
    assert digest_after == digest

    _ = _wait_for_removal_log(environment)

# ################################################################################################################################

def test_concurrent_publishers(environment:'DatabaseFileEnvironment') -> 'None':
    """ Clients publish while the file is removed. No publication sent after the removal is acknowledged,
    each of them is answered with 503.
    """
    publishers = Publishers(environment)
    publishers.start()

    try:
        time.sleep(ModuleCtx.Publish_Seconds_Before)

        environment.remove_database()
        removed_at = time.monotonic()

        time.sleep(ModuleCtx.Publish_Seconds_After)

    finally:
        publishers.stop()

    acknowledged_before = 0
    statuses_after:'intlist' = []

    for record in publishers.records:
        if record.started_at > removed_at:
            statuses_after.append(record.status_code)
        elif record.status_code == OK:
            acknowledged_before += 1

    assert acknowledged_before > 0
    assert statuses_after

    for status_code in statuses_after:
        assert status_code == SERVICE_UNAVAILABLE, statuses_after

    assert not os.path.exists(environment.db_path)

# ################################################################################################################################
# ################################################################################################################################
