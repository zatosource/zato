# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import glob
import logging
import os
import re
import unittest
from threading import Thread
from time import sleep
from uuid import uuid4

# Zato
from zato.common.test.conftest_base_multi_cpu import invoke_on_slot, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, dict_

    strintdict = dict_[str, int]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_logging.log_rotation')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Log_Records_Service = 'test.multi-cpu.log-records'

    # How many requests each slot receives, how many records each request writes and how long each record is,
    # which together exceed the size limit of the server log several times
    Requests_Per_Slot = 5
    Records_Per_Request = 1000
    Record_Padding = 200

    # How long the arbiter is given to rotate the files that exceed their limit, in seconds,
    # which is more than two of its log checks
    Rotation_Wait = 25.0

    Log_Pattern = os.path.join('logs', 'server.log*')

# ################################################################################################################################
# ################################################################################################################################

class LogRequest:
    """ One request that makes the worker of a slot write records, sent in a thread of its own.
    """

    def __init__(self, slot:'int', prefix:'str') -> 'None':
        self.slot = slot
        self.prefix = prefix
        self.status = 0
        self.thread = Thread(target=self._send, daemon=True)

    def _send(self) -> 'None':
        request = {
            'prefix': self.prefix,
            'count': ModuleCtx.Records_Per_Request,
            'padding': ModuleCtx.Record_Padding,
        }
        self.status, _ = invoke_on_slot(self.slot, ModuleCtx.Log_Records_Service, request)

# ################################################################################################################################
# ################################################################################################################################

class TestLogRotationAcrossWorkers(unittest.TestCase):
    """ The rotations of the server log that the records of every worker cause lose no record and repeat none.
    """

    def test_rotation_loses_no_record(self) -> 'None':

        run_id = uuid4().hex
        requests:'anylist' = []

        for slot in range(MultiCPUTestConfig.worker_count):
            for index in range(ModuleCtx.Requests_Per_Slot):
                requests.append(LogRequest(slot, f'{run_id}-{slot}-{index}'))

        # Every worker writes its records at the same time ..
        for request in requests:
            request.thread.start()

        for request in requests:
            request.thread.join()
            self.assertEqual(request.status, MultiCPUCtx.Status_OK)

        # .. the arbiter rotates the file while and after they are written ..
        sleep(ModuleCtx.Rotation_Wait)

        # .. and the current file together with its backups holds each record exactly once.
        record_pattern = re.compile(f'({run_id}-[0-9]+-[0-9]+-[0-9]+) ')
        counts:'strintdict' = {}

        paths = glob.glob(os.path.join(MultiCPUTestConfig.server_directory, ModuleCtx.Log_Pattern))
        logger.info('Log files after the rotation -> %s', sorted(paths))

        self.assertGreater(len(paths), 1, 'The server log was not rotated')

        for path in paths:
            with open(path, encoding='utf8') as log_file:
                for match in record_pattern.finditer(log_file.read()):
                    marker = match.group(1)
                    if marker in counts:
                        counts[marker] += 1
                    else:
                        counts[marker] = 1

        expected = MultiCPUTestConfig.worker_count * ModuleCtx.Requests_Per_Slot * ModuleCtx.Records_Per_Request
        self.assertEqual(len(counts), expected, f'{expected - len(counts)} records missing')

        for marker, count in counts.items():
            self.assertEqual(count, 1, f'Record {marker} written {count} times')

# ################################################################################################################################
# ################################################################################################################################
