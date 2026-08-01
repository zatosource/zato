# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from typing import NamedTuple

# pytest
import pytest

# Zato
from zato.common.api import FileTransfer
from zato.common.crypto.api import CryptoManager
from zato.common.test.file_transfer_harness.client import ScheduleClient
from zato.common.test.file_transfer_harness.evidence import Evidence, Service_Store_File

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.test.file_transfer_harness.adapter import FileTransferAdapter
    from zato.common.typing_ import any_, anydict, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# How many bits of randomness go into the name of a schedule that a test creates
_schedule_name_bits = 32

# ################################################################################################################################
# ################################################################################################################################

class Connection(NamedTuple):
    """ One connection that a test created, as the test refers to it afterwards.
    """
    id: int
    name: str

# ################################################################################################################################
# ################################################################################################################################

class Harness:
    """ What a shared test works through - one protocol's adapter, the Zato server behind it
    and the record of what the schedules delivered. Nothing in here knows which protocol it is driving.
    """

    def __init__(self, client:'ScheduleClient', adapter:'FileTransferAdapter', evidence:'Evidence') -> 'None':
        self.client = client
        self.adapter = adapter
        self.evidence = evidence

# ################################################################################################################################

    def require(self, capability:'str') -> 'None':
        """ Skips the test when the protocol under test does not have what the test needs.
        """
        is_supported = getattr(self.adapter, capability)

        if not is_supported:
            pytest.skip(f'`{self.adapter.conn_type}` does not have `{capability}`')

# ################################################################################################################################

    def new_conn(self, **extra:'any_') -> 'Connection':
        """ Creates a connection pointing at this protocol's test server, with anything the test
        says about it replacing what the adapter would have used.
        """
        name = self.adapter.new_conn_name()
        conn_id = self.client.create_conn(name, **extra)

        out = Connection(conn_id, name)
        return out

# ################################################################################################################################

    def new_schedule_name(self, prefix:'str') -> 'str':
        """ A schedule name that no other test uses, so the evidence of two tests never mixes.
        """
        suffix = CryptoManager.generate_hex_string(_schedule_name_bits)

        out = f'{prefix}.{suffix}'
        return out

# ################################################################################################################################

    def make_directory(self) -> 'str':
        """ A fresh remote directory for one test's files.
        """
        out = self.adapter.make_directory()
        return out

# ################################################################################################################################

    def make_subdirectory(self, directory:'str', name:'str') -> 'str':
        out = self.adapter.make_subdirectory(directory, name)
        return out

# ################################################################################################################################

    def move_directory_of(self, directory:'str', name:'str'=_scheduler.Default_Move_Directory) -> 'str':
        """ The remote path a schedule moves its files into.
        """
        out = self.adapter.remote_join(directory, name)
        return out

# ################################################################################################################################

    def write(self, directory:'str', name:'str', data:'str | bytes') -> 'None':
        """ Puts one file on the remote side, out of band.
        """
        payload = data

        if isinstance(payload, str):
            payload = payload.encode('utf8')

        self.adapter.write_file(directory, name, payload)

# ################################################################################################################################

    def append(self, directory:'str', name:'str', data:'str | bytes') -> 'None':
        """ Adds to a file already on the remote side, which is how a test keeps an upload in progress.
        """
        payload = data

        if isinstance(payload, str):
            payload = payload.encode('utf8')

        self.adapter.append_file(directory, name, payload)

# ################################################################################################################################

    def read(self, directory:'str', name:'str') -> 'bytes':
        out = self.adapter.read_file(directory, name)
        return out

# ################################################################################################################################

    def read_text(self, directory:'str', name:'str') -> 'str':
        payload = self.adapter.read_file(directory, name)

        out = payload.decode('utf8')
        return out

# ################################################################################################################################

    def names(self, directory:'str') -> 'strlist':
        """ The sorted names of everything a remote directory holds, read once.
        """
        out = self.adapter.list_names(directory)
        return out

# ################################################################################################################################

    def exists(self, directory:'str', name:'str') -> 'bool':
        out = self.adapter.exists(directory, name)
        return out

# ################################################################################################################################

    def delete(self, directory:'str', name:'str') -> 'None':
        self.adapter.delete_file(directory, name)

# ################################################################################################################################

    def make_symlink(self, directory:'str', name:'str', target:'str') -> 'None':
        self.adapter.make_symlink(directory, name, target)

# ################################################################################################################################

    def assert_names(self, directory:'str', expected:'strlist') -> 'None':
        """ Waits until a remote directory holds exactly the given names, within the protocol's settle timeout,
        so that a protocol whose writes take a moment to become visible does not fail on timing alone.
        """
        expected = sorted(expected)
        deadline = time.monotonic() + self.adapter.settle_timeout

        while True:
            actual = self.names(directory)

            if actual == expected:
                return

            if time.monotonic() >= deadline:
                break

            time.sleep(self.adapter.settle_sleep_time)

        assert actual == expected, f'`{directory}` holds {actual} rather than {expected}'

# ################################################################################################################################

    def create_schedule(self, conn:'Connection', name:'str', directory:'str', **extra:'any_') -> 'anydict':
        """ Creates one schedule and hands back the entry as the connection stores it, which is what
        the dispatch service receives when the schedule fires.
        """
        out = self.client.create_and_get_schedule(conn.id, name, directory, **extra)
        return out

# ################################################################################################################################

    def run(self, conn:'Connection', schedule:'anydict') -> 'None':
        """ One run of a schedule, driven the way a scheduler fire event drives it.
        """
        self.client.invoke_dispatch(conn.id, conn.name, schedule)

# ################################################################################################################################

    def run_once(self, conn:'Connection', schedule:'anydict') -> 'None':
        """ One run of a schedule with no retrying, for when the run itself is expected to fail.
        """
        self.client.invoke_dispatch_once(conn.id, conn.name, schedule)

# ################################################################################################################################

    def delivered(self, schedule_name:'str') -> 'dictlist':
        out = self.evidence.read(schedule_name)
        return out

# ################################################################################################################################

    def delivered_names(self, schedule_name:'str') -> 'strlist':
        out = self.evidence.file_names(schedule_name)
        return out

# ################################################################################################################################

    def job_of(self, conn:'Connection', schedule_name:'str') -> 'anydict':
        """ The scheduler job that mirrors one schedule.
        """
        job_name = self.client.job_name(conn.name, schedule_name)

        out = self.client.get_job(job_name)
        return out

# ################################################################################################################################

    def job_exists(self, conn:'Connection', schedule_name:'str') -> 'bool':
        job_name = self.client.job_name(conn.name, schedule_name)
        job_names = self.client.get_job_names()

        out = job_name in job_names
        return out

# ################################################################################################################################
# ################################################################################################################################

class FileTransferScheduleTestBase:
    """ The fixtures every shared test group needs. A protocol joins the suite by subclassing one
    of the test groups and overriding the adapter fixture with its own.
    """

    @pytest.fixture()
    def adapter(self) -> 'FileTransferAdapter':
        """ Overridden by each protocol's subclass with the adapter for that protocol.
        """
        raise Exception('Each protocol subclass must override the adapter fixture')

# ################################################################################################################################

    @pytest.fixture()
    def harness(
        self,
        admin_client:'AdminClient',
        adapter:'FileTransferAdapter',
        evidence_file:'str',
        ) -> 'Harness':
        """ Everything one test works through, built fresh for each test around a shared server.
        """
        client = ScheduleClient(admin_client, adapter, Service_Store_File)
        evidence = Evidence(evidence_file)

        out = Harness(client, adapter, evidence)
        return out

# ################################################################################################################################

    @pytest.fixture(autouse=True)
    def cleanup(self, harness:'Harness') -> 'any_':
        """ Removes the connections and jobs a test left behind, no matter how the test ended.
        """
        yield

        harness.client.cleanup()

# ################################################################################################################################
# ################################################################################################################################
