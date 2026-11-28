# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The limits that the suites of the active-standby pair apply to the steps of a failover.

# Zato
from zato.common.ha.common import ModuleCtx as HACtx

# ################################################################################################################################
# ################################################################################################################################

class HALimits:

    # How long a server started with the generation of a node may take, from the spawn of its command to the first answer
    # of /zato/ping, in seconds. The start measures 2.9 s in breakdowns/ha-start/03.md of private-zato-perf
    # and 4.3 s while eight other suites run.
    Server_Start = 5.0

    # How often the node sends /zato/ping to a server that has answered, and how long each ping may take, in seconds,
    # the same as SERVER_PING_INTERVAL and SERVER_PING_TIMEOUT of zato_ha_core/src/config.rs. The slowest ping measures
    # 55 ms in test_ping_under_load.py under 16 publishers and 16 subscribers on the local build of PostgreSQL.
    Server_Ping_Interval = 1.0
    Server_Ping_Timeout  = 2.0

    # How long a server that has answered may remain without an answer before its node resigns, in seconds,
    # the default of the node. It spans five pings that time out, and it is below the 30 s after which the arbiter
    # of the server replaces a worker without a heartbeat.
    Server_Liveness_Timeout = HACtx.Default_Server_Liveness_Timeout

    # How many exits of the server within the window make its node resign, the default of the node.
    Server_Exit_Limit = HACtx.Default_Server_Exit_Limit

    # How long a server whose configuration cannot be read may take to exit, from the spawn of its command, in seconds.
    # The exit measures 0.15 s in test_server_liveness.py on the local build of PostgreSQL, and the limit leaves room
    # for the start of the interpreter in a pod, which takes up to 2.1 s in the Kubernetes suite.
    Server_Bad_Start = 3.0

    # How long the stop of the server of an active node may take, from the SIGTERM of its node to the exit of the server,
    # in seconds. The longest stop of breakdowns/ha-handover/01.md of private-zato-perf is 0.4 seconds, and the limit
    # is five times that, which stays below HA_Stop_Grace of zato/server/arbiter_config.py, the longest stop that the node permits.
    Server_Stop = 2.0

# ################################################################################################################################
# ################################################################################################################################
