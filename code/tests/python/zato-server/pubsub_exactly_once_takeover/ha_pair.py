# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The active-standby pair of the HA suites with the relay of the exactly-once tests deployed on both nodes.

# stdlib
import os
import shutil
from functools import partial

# Zato
from ha_env import create_session as create_ha_session
from nodes import Node, NodeHook
from pair import import_jobs
from zato.common.test.exactly_once.control import create_control_dir, Env_Dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HASession
    from postgresql_cluster import PostgreSQLCluster
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the control files of the relay, under the run directory that both nodes mount
    Control_Dir_Name = 'exactly-once-control'

# ################################################################################################################################
# ################################################################################################################################

class ControlDirHook(NodeHook):
    """ Gives the server of each node the control directory of the relay.
    """

    def __init__(self, control_dir:'str') -> 'None':
        self.control_dir = control_dir

    def before_start(self, node:'Node') -> 'None':
        node.env[Env_Dir] = self.control_dir

    def after_remove(self, node:'Node') -> 'None':
        """ The control directory belongs to the session, whose run directory contains it.
        """

# ################################################################################################################################
# ################################################################################################################################

def get_control_dir(session:'HASession') -> 'str':
    out = os.path.join(session.run_dir, ModuleCtx.Control_Dir_Name)
    return out

# ################################################################################################################################

def _add_relay(
    node:'Node',
    server_directory:'str',
    database_env:'strstrdict',
    *,
    rendered_yaml:'str',
    services_source:'str',
    ) -> 'None':
    """ Imports the definitions of the relay, offline, into the Zato database of the given settings, and places
    the services of the relay in the pickup directory of a node, from which the server deploys them as it starts.
    """
    quickstart_directory = os.path.dirname(server_directory)

    extra_env = {'HOME': node.home_dir}
    extra_env.update(database_env)

    import_jobs(quickstart_directory, server_directory, rendered_yaml, extra_env)

    pickup_dir = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    _ = shutil.copy(services_source, pickup_dir)

# ################################################################################################################################

def create_session(rendered_yaml:'str', services_source:'str') -> 'HASession':
    """ Creates the session of the HA suites, which adds the relay to the quickstart environment of the first node
    of each test, and thereby to the copy of that environment that the other node starts from.
    """
    out = create_ha_session()

    add_relay = partial(_add_relay, rendered_yaml=rendered_yaml, services_source=services_source)
    out.environment_hooks.append(add_relay)

    control_dir = get_control_dir(out)
    create_control_dir(control_dir)

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_cluster_env(cluster:'PostgreSQLCluster') -> 'strstrdict':
    """ Returns the settings under which the test process reads the instance of a cluster that accepts writes,
    at its own address rather than under the name of the endpoint that only the nodes resolve.
    """
    out = dict(cluster.database.env)
    return out

# ################################################################################################################################
# ################################################################################################################################
