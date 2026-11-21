# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.test.pubsub_database import get_db_mode, is_postgresql_mode

from _support import wait_for_no_unconfirmed, yaml_add_second_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_network_faults(environment:'any_', pickup:'any_', runtime:'any_', names:'any_') -> 'None':
    """ Network faults on PostgreSQL during a reload end with rows equal to the subscription list.
    """
    if not is_postgresql_mode(get_db_mode()):
        pytest.skip('Network faults of the suite apply to PostgreSQL')

    pickup.apply('add-on-postgresql', yaml_add_second_topic(names))
    wait_for_no_unconfirmed(runtime)

    pairs = runtime.governed_pairs()
    statuses = runtime.statuses()

    pair_set = set()

    for sub_key, topic_name in pairs:
        pair_set.add((sub_key, topic_name))

    for sub_key, topic_name, status in statuses:
        assert status == 'confirmed'
        assert (sub_key, topic_name) in pair_set

# ################################################################################################################################
# ################################################################################################################################
