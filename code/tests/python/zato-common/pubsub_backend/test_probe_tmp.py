# -*- coding: utf-8 -*-

import os

from cleanup_lock import run_cleanup_lock_scenario
from common import pubsub_path_env
import scenarios

def test_probe(tmp_path):
    db_path = os.path.join(str(tmp_path), 'zato.db')

    names = ['run_publish_values_scenario', 'run_ack_values_scenario', 'run_fenced_values_scenario',
        'run_attempt_values_scenario', 'run_publish_events_scenario']

    for name in names:
        setattr(scenarios, name, _skip)

    with pubsub_path_env(db_path):
        scenarios.run_common_scenarios()
        run_cleanup_lock_scenario()

def _skip():
    pass
