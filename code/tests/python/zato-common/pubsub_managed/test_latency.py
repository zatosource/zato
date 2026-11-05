# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# pytest
import pytest

# Zato
from backbone import run_backbone_scenario
from document_mix import run_document_mix_scenario
from fanout import run_fanout_scenario
from production_mix import run_production_mix_scenario
from push import run_push_delivery_scenario
from runner import get_report_path
from throughput import run_delivery_throughput_scenario, run_publish_throughput_scenario
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.test.pubsub_database import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, strlist

# ################################################################################################################################
# ################################################################################################################################

# The scenarios of the perf suite that are timed at each round-trip time, by their names in the report.
_timed_scenarios = [
    ('push delivery', run_push_delivery_scenario),
    ('fanout', run_fanout_scenario),
    ('document mix', run_document_mix_scenario),
    ('production mix', run_production_mix_scenario),
    ('backbone', run_backbone_scenario),
]

# ################################################################################################################################
# ################################################################################################################################

def test_latency(start_managed:'callable_', round_trip_ms:'float', monkeypatch:'pytest.MonkeyPatch') -> 'None':
    """ The perf scenarios run with the round-trip time of a network within one availability
    zone and across zones, and the report gives their rates and durations at each round-trip time.
    """
    monkeypatch.setenv(ModuleCtx.Env_Round_Trip_Ms, f'{round_trip_ms}')

    _ = start_managed('latency')

    lines:'strlist' = []

    try:
        publish_rate = run_publish_throughput_scenario()
        delivery_rate = run_delivery_throughput_scenario()

        lines.append(f'round trip {round_trip_ms} ms | publish {publish_rate:.1f}/s | delivery {delivery_rate:.1f}/s')

        for name, scenario in _timed_scenarios:
            start = monotonic()
            scenario()
            elapsed = monotonic() - start
            lines.append(f'round trip {round_trip_ms} ms | {name} {elapsed:.1f}s')

    finally:
        get_pubsub_engine().dispose()

        report_path = get_report_path('latency')

        with open(report_path, 'a') as report_file:
            for line in lines:
                _ = report_file.write(line + '\n')
                print(line, flush=True)

# ################################################################################################################################
# ################################################################################################################################
