# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import Thread

# Zato
from _support import wait_for_no_unconfirmed, yaml_add_second_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_reload_write_failure(environment:'any_', pickup:'any_', runtime:'any_', names:'any_') -> 'None':
    """ An enmasse file applied while writes to the pub/sub database fail is obeyed after recovery.
    """
    holder = Thread(target=runtime.hold_locks, args=(names.topic_pull, 8.0), daemon=True)
    holder.start()

    pickup.apply('add-second-while-locked', yaml_add_second_topic(names))
    holder.join(timeout=30)

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
