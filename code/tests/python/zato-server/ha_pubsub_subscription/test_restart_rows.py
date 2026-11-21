# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.crypto.api import CryptoManager

# Local
from _support import assert_rows_equal_list, publish_accepted, publish_client, wait_for, wait_for_no_unconfirmed, \
    yaml_subscription

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable that points a starting server at the directory of the files that it deploys
    Env_Deploy_From = 'Zato_Deploy_From'

    # The directories of the deployment, the enmasse files of which the server imports once it has started
    Deploy_Directory = 'deploy'
    Enmasse_Directory = 'enmasse'

    File_Name = 'enmasse-remove-pull.yaml'

# ################################################################################################################################
# ################################################################################################################################

def test_restart_rows(environment:'any_', pickup:'any_', runtime:'any_', names:'any_', server_env:'any_') -> 'None':
    """ A topic removed from a subscription by an enmasse file deployed during the start of the server has no row
    and no queued messages after the restart.
    """
    sub_key = runtime.sub_key(names.security_pull)
    removed_pair = (sub_key, names.topic_pull.lower())

    # The subscriber has a message queued from the topic that the file removes ..
    publisher = publish_client(environment, names)
    _ = publish_accepted(publisher, names.topic_pull, 'restart.' + CryptoManager.generate_hex_string(32))

    def _is_queued() -> 'bool':
        out = runtime.queue_depth(sub_key) == 1
        return out

    wait_for(_is_queued, 'The queueing of the message')

    # .. the file is in the deployment that the server reads when it starts ..
    deploy_directory = os.path.join(environment.directory, ModuleCtx.Deploy_Directory)
    enmasse_directory = os.path.join(deploy_directory, ModuleCtx.Enmasse_Directory)
    os.makedirs(enmasse_directory)

    file_path = os.path.join(enmasse_directory, ModuleCtx.File_Name)

    with open(file_path, 'w') as enmasse_file:
        _ = enmasse_file.write(yaml_subscription(names.security_pull, [names.topic_second]))

    restart_env = dict(server_env)
    restart_env[ModuleCtx.Env_Deploy_From] = deploy_directory

    # .. the server restarts and imports the file ..
    _, completed_before, failed_before = pickup.count_markers()

    environment.restart(restart_env)
    pickup.wait_for_import(completed_before, failed_before, ModuleCtx.File_Name)

    wait_for_no_unconfirmed(runtime)

    # .. after which the pair has no row ..
    assert removed_pair not in runtime.governed_pairs()
    assert_rows_equal_list(runtime)

    # .. and its queue is emptied.
    def _is_emptied() -> 'bool':
        out = runtime.queue_depth(sub_key) == 0
        return out

    wait_for(_is_emptied, 'The removal of the queued message')

# ################################################################################################################################
# ################################################################################################################################
