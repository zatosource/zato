# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from json import loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The names of the services the harness hot-deploys for schedules to invoke
Service_Store_File = 'file-transfer-scheduler-test.store-file'
Service_Always_Raise = 'file-transfer-scheduler-test.always-raise'
Service_Fail_Selected = 'file-transfer-scheduler-test.fail-selected'
Service_Slow_Store = 'file-transfer-scheduler-test.slow-store'

# A file whose name holds this is the one that Service_Fail_Selected refuses to accept
Failing_File_Token = 'refused'

# How long Service_Slow_Store spends on one file, in seconds - long enough for the next fire
# of a one-second schedule to arrive while this one is still working.
Slow_Store_Delay = 3

# Payloads larger than this are recorded by their length and digest only, never in full
Max_Recorded_Payload_Size = 4096

# ################################################################################################################################
# ################################################################################################################################

# Source code of the services that the schedules under test invoke, rendered with the evidence file's path
# and the service names embedded. Every one of them records what it received before deciding what to do,
# except the one that refuses everything.
Test_Services_Template = '''# -*- coding: utf-8 -*-

# stdlib
from hashlib import sha256
from json import dumps

# gevent
from gevent import sleep

# Zato
from zato.server.service import Service

_evidence_file = '{evidence_file}'
_failing_file_token = '{failing_file_token}'
_slow_store_delay = {slow_store_delay}
_max_recorded_payload_size = {max_recorded_payload_size}


def _record(item):
    """ Appends one line describing the file that was received to the evidence file.
    """
    data = item.data

    # The remote side hands over bytes and the digest is taken over exactly those ..
    payload = data
    if isinstance(payload, str):
        payload = payload.encode('utf8')

    data_length = len(payload)
    digest = sha256(payload).hexdigest()

    # .. while the readable form is kept only for payloads small enough to be worth comparing in full.
    if data_length > _max_recorded_payload_size:
        text = ''
    else:
        text = payload.decode('utf8', errors='replace')

    line = dumps({{
        'conn_type': item.conn_type,
        'conn_name': item.conn_name,
        'schedule_name': item.schedule_name,
        'directory': item.directory,
        'file_name': item.file_name,
        'full_path': item.full_path,
        'size': item.size,
        'last_modified': item.last_modified,
        'data': text,
        'data_length': data_length,
        'data_digest': digest,
    }})

    with open(_evidence_file, 'a') as evidence:
        _ = evidence.write(line + '\\n')


class StoreFileTransferItem(Service):
    """ Records each file received on input.
    """
    name = '{service_store_file}'

    def handle(self):

        # The dispatch service hands us the item object itself
        item = self.request.raw_request
        _record(item)


class AlwaysRaiseFileTransfer(Service):
    """ Fails on purpose so that tests can confirm that files are never lost on errors.
    """
    name = '{service_always_raise}'

    def handle(self):
        raise Exception('This service always raises an error for file transfer tests')


class FailSelectedFileTransfer(Service):
    """ Records every file except the ones whose name marks them as the ones to refuse,
    so that a test can watch a healthy file and a failing one go through the same run.
    """
    name = '{service_fail_selected}'

    def handle(self):

        item = self.request.raw_request

        if _failing_file_token in item.file_name:
            raise Exception('This service refuses the file `{{}}`'.format(item.file_name))

        _record(item)


class SlowStoreFileTransfer(Service):
    """ Takes its time over each file so that a schedule running every second has a run
    still in progress when the next one starts.
    """
    name = '{service_slow_store}'

    def handle(self):

        item = self.request.raw_request
        sleep(_slow_store_delay)

        _record(item)
'''

# ################################################################################################################################
# ################################################################################################################################

def build_test_services_source(evidence_file:'str') -> 'str':
    """ Renders the source code of the services that the schedules under test invoke.
    """
    out = Test_Services_Template.format(
        evidence_file=evidence_file,
        failing_file_token=Failing_File_Token,
        slow_store_delay=Slow_Store_Delay,
        max_recorded_payload_size=Max_Recorded_Payload_Size,
        service_store_file=Service_Store_File,
        service_always_raise=Service_Always_Raise,
        service_fail_selected=Service_Fail_Selected,
        service_slow_store=Service_Slow_Store,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

class Evidence:
    """ What the services invoked by the schedules under test recorded about the files they received.
    """

    def __init__(self, evidence_file:'str') -> 'None':
        self.evidence_file = evidence_file

# ################################################################################################################################

    def read(self, schedule_name:'str') -> 'dictlist':
        """ Returns what one schedule delivered, in the order it was delivered in.
        """
        out:'dictlist' = []

        # The file comes into existence only once the first item was recorded
        if not os.path.exists(self.evidence_file):
            return out

        with open(self.evidence_file) as evidence:
            for line in evidence:
                line = line.strip()
                if line:
                    entry = loads(line)
                    if entry['schedule_name'] == schedule_name:
                        out.append(entry)

        return out

# ################################################################################################################################

    def file_names(self, schedule_name:'str') -> 'strlist':
        """ The sorted names of the files one schedule delivered, duplicates included.
        """
        entries = self.read(schedule_name)

        names:'strlist' = []

        for entry in entries:
            names.append(entry['file_name'])

        out = sorted(names)
        return out

# ################################################################################################################################

    def by_file_name(self, schedule_name:'str') -> 'dict':
        """ What one schedule delivered, keyed by file name.
        """
        entries = self.read(schedule_name)

        out = {}

        for entry in entries:
            out[entry['file_name']] = entry

        return out

# ################################################################################################################################

    def wait_for_count(self, schedule_name:'str', count:'int', timeout:'float') -> 'dictlist':
        """ Waits until one schedule has delivered at least the given number of files, returning
        everything it delivered by then and failing the test if it never got there.
        """
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            out = self.read(schedule_name)
            delivered = len(out)
            if delivered >= count:
                return out
            time.sleep(0.5)

        out = self.read(schedule_name)
        delivered = len(out)

        raise AssertionError(
            f'Schedule `{schedule_name}` delivered {delivered} of {count} files within {timeout}s')

# ################################################################################################################################

    def wait_for_quiet(self, schedule_name:'str', quiet_time:'float') -> 'dictlist':
        """ Lets the given time pass and returns what one schedule delivered by then, which is how a test
        confirms that nothing more arrived after the deliveries it already saw.
        """
        time.sleep(quiet_time)

        out = self.read(schedule_name)
        return out

# ################################################################################################################################
# ################################################################################################################################
