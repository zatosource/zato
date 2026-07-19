# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from common import pubsub_backend_env, Mass_Drain_Backlog_Mass, Mass_Drain_Deadline_Mass, Mass_Drain_Publish_Floor_Mass
from mass_drain import run_mass_drain_scenario

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sql.containers import DatabaseServer
    DatabaseServer = DatabaseServer

# ################################################################################################################################
# ################################################################################################################################

def test_pubsub_backend_perf_mass_mysql(mysql_server:'DatabaseServer') -> 'None':
    """ The mass-recovery scenario at full scale against a plain MySQL server.
    """
    with pubsub_backend_env(mysql_server.details):
        run_mass_drain_scenario(
            backlog_per_subscriber=Mass_Drain_Backlog_Mass,
            deadline_seconds=Mass_Drain_Deadline_Mass,
            min_publish_rate=Mass_Drain_Publish_Floor_Mass,
        )

# ################################################################################################################################
# ################################################################################################################################
