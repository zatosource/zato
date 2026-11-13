# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# HAProxy in front of the pair - restarted under traffic, and measured for how long clients take to reach
# the active node after each takeover.

# stdlib
import logging
import time

# Zato
from ha_checks import check_copies
from ha_traffic import TimedPublisher

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.haproxy')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs around each event, in seconds
    Traffic_Seconds = 10

    # How many takeovers the test measures
    Takeover_Count = 2

    # How long clients may take to reach the active node after HAProxy restarts, in seconds
    Restart_Recovery_Limit = 10

    # How long clients may take to reach the new active node after a takeover, in seconds
    Takeover_Recovery_Limit = 180

    # How often the test checks whether clients reach the active node, in seconds
    Poll_Interval = 0.2

    # How long the former active node may take to join again as the standby in sync, in seconds
    Rejoin_Timeout = 300

    # The role of a standby in sync
    Standby_In_Sync = ['StandbyInSync']

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_acknowledgment(publisher:'TimedPublisher', start:'float', limit:'float') -> 'float':
    """ Waits until a publication sent after the given time is acknowledged, and returns how long it took, in seconds.
    """
    while True:
        acknowledged = publisher.get_acknowledged_between(start, time.time())

        if acknowledged:
            out = time.time() - start
            return out

        elapsed = time.time() - start
        assert elapsed < limit, f'No publication acknowledged within {limit}s'

        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def test_haproxy(ha_pair:'HAEnvironment') -> 'None':
    """ Clients reach the active node again shortly after HAProxy restarts, and after each takeover within the time
    of the takeover and of the start of the new server.
    """
    env = ha_pair

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    # HAProxy restarts under traffic ..
    restarted_at = time.time()
    env.haproxy.restart()

    restart_recovery = _wait_for_acknowledgment(publisher, restarted_at, ModuleCtx.Restart_Recovery_Limit)
    logger.info('Clients reached the active node %.2fs after HAProxy restarted', restart_recovery)

    # .. and the active node is killed, once per takeover.
    for _ in range(ModuleCtx.Takeover_Count):

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        # The time is taken once the kill returns, since the node still acknowledges publications until then.
        active.kill()
        killed_at = time.time()

        takeover_recovery = _wait_for_acknowledgment(publisher, killed_at, ModuleCtx.Takeover_Recovery_Limit)
        logger.info('Clients reached %s %.2fs after %s was killed', standby.node_name, takeover_recovery, active.node_name)

        env.point_database_at(standby)

        active.resume()
        _ = active.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Rejoin_Timeout)

    publisher.stop()

    active = env.get_active()
    assert active is not None, 'No active node'

    check_copies(env, active)

# ################################################################################################################################
# ################################################################################################################################
