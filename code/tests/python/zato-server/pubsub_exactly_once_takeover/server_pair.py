# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Two servers of the pub/sub failover suite, each in a container, sharing one PostgreSQL database,
# with the relay of the exactly-once tests deployed on both.

# stdlib
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass

# Zato
from failover import build_server_env, ContainerServer, copy_server_environment, create_container, remove_container, \
    run_container, save_container_logs, wait_until_up
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, patch_server_conf, run_quickstart_and_enmasse, \
    SessionState
from zato.common.test.exactly_once.control import create_control_dir, Env_Dir
from zato.common.test.pubsub_database import get_db_mode, get_runtime_dir, start_pubsub_database, stop_pubsub_database
from zato_container import build_image

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import strlist

    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_exactly_once_takeover.server_pair')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The label of the Zato database container
    Database_Label = 'exactly-once-takeover'

    # The zato command of the current tree
    Zato_Binary = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ServerPair:
    """ The server that is active, the one that waits as a stopped container, and the database they share.
    """
    database: 'PubSubDatabase'
    active: 'ContainerServer'
    standby: 'ContainerServer'

    # The directory under the runtime directory, which the containers mount, with the environments and the logs
    work_dir: 'str'

    # The control directory of the relay
    control_dir: 'str'

    # The sessions of the quickstart environments of both servers
    states: 'list[SessionState]'

# ################################################################################################################################
# ################################################################################################################################

def _new_state(pair:'ServerPair', name:'str') -> 'SessionState':
    out = SessionState(f'zato.test.pubsub_exactly_once_takeover.{name}', f'server-logs-exactly-once-takeover-{name}.txt')
    pair.states.append(out)

    return out

# ################################################################################################################################

def _create_environments(pair:'ServerPair', rendered_yaml:'str', invoke_password:'str', services_source:'str') -> 'strlist':
    """ Creates the quickstart environment of the active server in the shared database, with the definitions
    and the services of the relay, and a copy of it for the standby, and returns the server directories of both.
    """
    state_active = _new_state(pair, 'a')
    state_standby = _new_state(pair, 'b')

    # The environment is under the work directory, which the containers of the servers mount ..
    server_directory = run_quickstart_and_enmasse(
        state=state_active,
        logger=logger,
        zato_bin=ModuleCtx.Zato_Binary,
        invoke_password=invoke_password,
        rendered_yaml=rendered_yaml,
        quickstart_prefix='zato_exactly_once_takeover_a_',
        extra_env=pair.database.env,
        quickstart_parent_dir=pair.work_dir,
    )

    # .. the server deploys the services of the relay from its pickup directory as it starts ..
    pickup_dir = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    _ = shutil.copy(services_source, pickup_dir)

    # .. and the standby has a copy of the environment, because both servers share the configuration of the database.
    standby_directory = copy_server_environment(state_active, state_standby, 'zato_exactly_once_takeover_b_',
        pair.work_dir)

    out = [server_directory, standby_directory]
    return out

# ################################################################################################################################

def _new_server(pair:'ServerPair', name:'str', server_directory:'str') -> 'ContainerServer':
    """ Returns one server of the pair in its quickstart environment.
    """
    out = ContainerServer(
        name=name,
        container_name=f'zato-exactly-once-takeover-{name}',
        server_directory=server_directory,
        port=find_free_port(),
        broker_port=find_free_port(),
    )

    # The server reads the control files of the relay from the directory that the test process writes them to
    patch_server_conf(server_directory, out.port, False)
    build_server_env(out, pair.database)
    out.env[Env_Dir] = pair.control_dir

    return out

# ################################################################################################################################

def create_server_pair(rendered_yaml:'str', services_source:'str') -> 'ServerPair':
    """ Starts the database and the active server, and creates the stopped container of the standby.
    """
    out = ServerPair()
    out.states = []

    # The image of the containers takes only as long to build as the layers that changed since the previous build ..
    build_image()

    out.database = start_pubsub_database(ModuleCtx.Database_Label, get_db_mode())
    out.work_dir = tempfile.mkdtemp(prefix='zato_exactly_once_takeover_', dir=get_runtime_dir())

    out.control_dir = os.path.join(out.work_dir, 'control')
    create_control_dir(out.control_dir)

    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()
    active_directory, standby_directory = _create_environments(out, rendered_yaml, invoke_password, services_source)

    out.active = _new_server(out, 'a', active_directory)
    out.standby = _new_server(out, 'b', standby_directory)

    # .. and a pair whose servers do not start is removed here, because no fixture receives it to remove it later.
    try:
        run_container(out.active)
        _ = wait_until_up(out.active)
        create_container(out.standby)
    except Exception:
        remove_server_pair(out)
        raise

    return out

# ################################################################################################################################

def remove_server_pair(pair:'ServerPair') -> 'None':
    """ Keeps the logs of both containers in the work directory and removes the containers, the environments
    and the database.
    """
    for server in (pair.active, pair.standby):
        save_container_logs(server, pair.work_dir)
        remove_container(server)

    for state in pair.states:
        state.cleanup()

    stop_pubsub_database(pair.database)

# ################################################################################################################################
# ################################################################################################################################
