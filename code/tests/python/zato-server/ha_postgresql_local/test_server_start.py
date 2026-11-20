# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The start of a server under the generation of an active-standby node, by the command that the node runs, measured
# from the spawn of the command to the first answer of /zato/ping, together with the stages of the start that the log
# of the server reports. A node labels its pod only after that answer, so this time is part of every failover.

# stdlib
import logging

# Zato
from local_server import create_local_server, start_local_server, stop_local_server, wait_for_stages
from zato.common.test.client import AdminClient
from zato.common.test.ha_limits import HALimits
from zato.common.test.perf_report import report_result, start_measurement
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from local_server import stage_list
    from zato.common.test.pubsub_database import PubSubDatabase

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

strfloatdict = dict[str, float]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the start may take, from the spawn of the command to the first answer of /zato/ping
    Start_Limit = HALimits.Server_Start

    # The name under which the figures of the start are recorded
    Result_Name = 'Server start'

# ################################################################################################################################
# ################################################################################################################################

def _stage_figures(stages:'stage_list') -> 'strfloatdict':
    """ Returns how long after the spawn each stage was reported, by the name of the stage.
    """
    out:'strfloatdict' = {}

    for stage in stages:
        out[stage.name] = cast_('float', stage.elapsed)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_server_start(pubsub_database:'PubSubDatabase') -> 'None':
    """ A server started by `zato start <dir> --fg` with a node's generation answers /zato/ping within Start_Limit,
    and its log reports every stage of its start.
    """
    server = create_local_server(pubsub_database)

    try:

        # The server is started by the command of the node, and the time to its first answer
        # is what a node waits for before it labels its pod ..
        answered_after = start_local_server(server)
        answered_at_epoch = server.spawned_at_epoch + answered_after

        # .. every stage is reported ..
        wait_for_stages(server)

        for stage in server.stages:
            logger.info('Server start stage %s -> %.3fs', stage.name, stage.elapsed)

        logger.info('Server start first answer -> %.3fs', answered_after)

        # .. the figures of the start are recorded with the settings of the server, which are known once it answers ..
        client = AdminClient(server.base_url, server.invoke_password)
        measurement = start_measurement(client, pubsub_database)

        figures = {
            'stages': _stage_figures(server.stages),
            'first_answer': answered_after,
            'spawned_at_monotonic': server.spawned_at,
            'window_start': server.spawned_at_epoch,
            'window_end': answered_at_epoch,
        }

        _ = report_result(measurement, ModuleCtx.Result_Name, figures)

        # .. and the answer came within the limit.
        assert answered_after < ModuleCtx.Start_Limit, answered_after

    finally:
        stop_local_server(server)

# ################################################################################################################################
# ################################################################################################################################
