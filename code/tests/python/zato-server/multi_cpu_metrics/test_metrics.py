# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import unittest
from base64 import b64encode

# Prometheus
from prometheus_client.parser import text_string_to_metric_families

# Zato
from zato.common.test.conftest_base_multi_cpu import get_json, ModuleCtx as MultiCPUCtx, MultiCPUTestConfig, new_connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intset, list_, strdict
    floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_metrics')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Slot_Path    = '/test/multi-cpu/worker-slot'
    Metrics_Path = '/metrics'

    Channel_Name = 'test.multi-cpu.metrics.worker-slot'

    # The parser names a counter family without the suffix that each of its samples carries
    Family_Name = 'zato_rest_channel_requests'
    Sample_Name = 'zato_rest_channel_requests_total'

    # How many requests the channel receives, and how many times the metrics are read afterwards
    Request_Count = 64
    Read_Count    = 32

# ################################################################################################################################
# ################################################################################################################################

def _get_metrics_headers() -> 'strdict':
    credentials = f'{MultiCPUCtx.Metrics_Username}:{MultiCPUTestConfig.sec_password}'

    out = {
        'Authorization': 'Basic ' + b64encode(credentials.encode()).decode(),
    }
    return out

# ################################################################################################################################

def _read_channel_total(headers:'strdict') -> 'float':
    """ Returns the number of requests of the test channel that one read of the metrics endpoint reports.
    """
    connection = new_connection()
    connection.request('GET', ModuleCtx.Metrics_Path, headers=headers)
    response = connection.getresponse()
    body = response.read()
    connection.close()

    if response.status != MultiCPUCtx.Status_OK:
        raise Exception(f'Status {response.status} from {ModuleCtx.Metrics_Path} -> {body!r}')

    out = 0.0

    for family in text_string_to_metric_families(body.decode('utf8')):
        if family.name == ModuleCtx.Family_Name:
            for sample in family.samples:
                if sample.name == ModuleCtx.Sample_Name and sample.labels['channel_name'] == ModuleCtx.Channel_Name:
                    out += sample.value

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMetricsAcrossWorkers(unittest.TestCase):
    """ The metrics endpoint served by any worker reports the activity of all workers.
    """

    def test_totals_are_the_sum_of_all_workers(self) -> 'None':
        """ Every read of the metrics endpoint, whichever worker serves it, reports the requests of every worker.
        """
        headers = _get_metrics_headers()
        before = _read_channel_total(headers)

        # .. requests that the kernel spreads over all the workers ..
        slots:'intset' = set()

        for _ in range(ModuleCtx.Request_Count):
            connection = new_connection()
            response = get_json(connection, ModuleCtx.Slot_Path)
            connection.close()
            slots.add(response['slot'])

        self.assertEqual(slots, set(range(MultiCPUTestConfig.worker_count)))

        # .. each read reports all of them.
        totals:'floatlist' = []

        for _ in range(ModuleCtx.Read_Count):
            totals.append(_read_channel_total(headers))

        logger.info('Channel totals: before %s, after %s', before, sorted(set(totals)))

        expected = before + ModuleCtx.Request_Count

        for total in totals:
            self.assertEqual(total, expected)

# ################################################################################################################################
# ################################################################################################################################
