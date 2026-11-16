# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Two servers of the pub/sub failover suite, each in a container, sharing one PostgreSQL pub/sub database,
# with the relay of the exactly-once tests deployed on both.

# stdlib
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass

# Zato
from failover import build_server_env, ContainerServer, create_container, remove_container, run_container, \
    save_container_logs, wait_until_up
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, patch_server_conf, run_quickstart_and_enmasse, \
    SessionState
from zato.common.test.exactly_once.control import create_control_dir, Env_Dir
from zato.common.test.pubsub_database import get_db_mode, get_runtime_dir, start_pubsub_database, stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_exactly_once_takeover.server_pair')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The label of the pub/sub database container
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

def _new_server(pair:'ServerPair', name:'str', rendered_yaml:'str', invoke_password:'str',
    services_source:'str') -> 'ContainerServer':
    """ Creates the quickstart environment of one server, with the definitions and the services of the relay.
    """
    state = SessionState(f'zato.test.pubsub_exactly_once_takeover.{name}', f'server-logs-exactly-once-takeover-{name}.txt')
    pair.states.append(state)

    # The environment is under the work directory, which the container of the server mounts ..
    server_directory = run_quickstart_and_enmasse(
        state=state,
        logger=logger,
        zato_bin=ModuleCtx.Zato_Binary,
        invoke_password=invoke_password,
        rendered_yaml=rendered_yaml,
        quickstart_prefix=f'zato_exactly_once_takeover_{name}_',
        quickstart_parent_dir=pair.work_dir,
    )

    # .. the server deploys the services of the relay from its pickup directory as it starts ..
    pickup_dir = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    _ = shutil.copy(services_source, pickup_dir)

    out = ContainerServer(
        name=name,
        container_name=f'zato-exactly-once-takeover-{name}',
        server_directory=server_directory,
        port=find_free_port(),
        broker_port=find_free_port(),
    )

    # .. and it reads the control files of the relay from the directory that the test process writes them to.
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

    out.database = start_pubsub_database(ModuleCtx.Database_Label, get_db_mode())
    out.work_dir = tempfile.mkdtemp(prefix='zato_exactly_once_takeover_', dir=get_runtime_dir())

    out.control_dir = os.path.join(out.work_dir, 'control')
    create_control_dir(out.control_dir)

    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

    out.active = _new_server(out, 'a', rendered_yaml, invoke_password, services_source)
    out.standby = _new_server(out, 'b', rendered_yaml, invoke_password, services_source)

    run_container(out.active)
    _ = wait_until_up(out.active)
    create_container(out.standby)

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
