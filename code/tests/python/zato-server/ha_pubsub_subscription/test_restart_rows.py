# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from _support import wait_for_no_unconfirmed, yaml_add_second_topic, yaml_remove_pull_topic
from conftest import server_environment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_restart_rows(environment:'any_', pickup:'any_', runtime:'any_', names:'any_') -> 'None':
    """ Subscriptions removed from the enmasse file while the server is stopped have no rows after the restart.
    """
    pickup.apply('add-second-before-stop', yaml_add_second_topic(names))
    wait_for_no_unconfirmed(runtime)

    extra_environment = server_environment(None)
    environment._stop_processes()

    remove_yaml = yaml_remove_pull_topic(names)
    file_path = os.path.join(environment.pickup_directory, 'enmasse-before-start-remove.yaml')

    with open(file_path, 'w') as enmasse_file:
        _ = enmasse_file.write(remove_yaml)

    environment.start(extra_environment)
    wait_for_no_unconfirmed(runtime)

    pairs = runtime.governed_pairs()

    for _sub_key, topic_name in pairs:
        assert topic_name != names.topic_pull.lower()

# ################################################################################################################################
# ################################################################################################################################
