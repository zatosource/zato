# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from threading import Thread

# Zato
from _support import wait_for_no_unconfirmed, yaml_add_second_topic
from live_containers.ready import wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_worker_kill(environment:'any_', pickup:'any_', runtime:'any_', names:'any_', client:'any_') -> 'None':
    """ After SIGKILL of the worker the new worker rebuilds the subscription list and the reconciler commits.
    """
    holder = Thread(target=runtime.hold_locks, args=(names.topic_pull, 15.0), daemon=True)
    holder.start()

    pickup.apply('add-before-kill', yaml_add_second_topic(names))

    try:
        runtime.kill_worker()
    except Exception:
        pass

    holder.join(timeout=5)
    time.sleep(2)

    def _server_ready() -> 'bool':
        try:
            _ = client.invoke('zato.ping', {})
            return True
        except Exception:
            return False

    wait_until(_server_ready, 'server after worker kill', timeout=120)
    wait_for_no_unconfirmed(runtime)

    pairs = runtime.governed_pairs()
    found = False

    for _sub_key, topic_name in pairs:
        if topic_name == names.topic_second.lower():
            found = True
            break

    assert found

# ################################################################################################################################
# ################################################################################################################################
