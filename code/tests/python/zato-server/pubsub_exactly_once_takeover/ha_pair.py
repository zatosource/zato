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
from tempfile import TemporaryDirectory

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from ha_env import create_session as create_ha_session, ModuleCtx as EnvCtx
from nodes import Node, NodeHook
from pair import import_jobs
from topology import ModuleCtx as TopologyCtx
from zato.common.test.exactly_once.control import create_control_dir, Env_Dir
from zato.common.test.exactly_once.verify import assert_exactly_once, check_outputs, wait_for_checks

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HASession
    from postgresql_cluster import PostgreSQLCluster
    from zato.common.test.exactly_once.verify import OutputCheck
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The directory of the control files of the relay, under the run directory that both nodes mount
    Control_Dir_Name = 'exactly-once-control'

    # The suffix of the log of a SQLite database file
    WAL_Suffix = '-wal'

    # How long the outputs of the relay may take to settle once the pair serves again, in seconds
    Settle_Timeout = 120.0

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

def _add_relay(node:'Node', server_directory:'str', rendered_yaml:'str', services_source:'str') -> 'None':
    """ Imports the definitions of the relay, offline, into the configuration of a node, and places the services
    of the relay in its pickup directory, from which the server deploys them as it starts.
    """
    quickstart_directory = os.path.dirname(server_directory)
    extra_env = {'HOME': node.home_dir}

    import_jobs(quickstart_directory, server_directory, rendered_yaml, extra_env)

    pickup_dir = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    _ = shutil.copy(services_source, pickup_dir)

# ################################################################################################################################

def create_session(rendered_yaml:'str', services_source:'str') -> 'HASession':
    """ Creates the session of the HA suites, adds the relay to the environment of both nodes, and replaces
    the copy of each environment, from which every test starts its node, with the result.
    """
    out = create_ha_session(TopologyCtx.Single_Control_Plane)

    for short_name in EnvCtx.Node_Names:
        node = Node(short_name=short_name, run_dir=out.run_dir)
        server_directory = out.server_directories[short_name]

        _add_relay(node, server_directory, rendered_yaml, services_source)

        template_path = os.path.join(out.template_dir, os.path.basename(node.directory))
        shutil.rmtree(template_path)
        _ = shutil.copytree(node.directory, template_path, symlinks=True)

    control_dir = get_control_dir(out)
    create_control_dir(control_dir)

    return out

# ################################################################################################################################
# ################################################################################################################################

def _read_copied_check(path:'str', keys:'strlist', prefix:'str') -> 'OutputCheck':
    """ Checks the outputs of the relay in a private copy of the pub/sub database of a node, which the node never waits for.
    """
    with TemporaryDirectory() as copy_dir:
        copy_path = os.path.join(copy_dir, os.path.basename(path))

        # The log is copied before the file, so that frames that a checkpoint moves into the file
        # in the meantime are still in the copied log ..
        try:
            _ = shutil.copyfile(path + ModuleCtx.WAL_Suffix, copy_path + ModuleCtx.WAL_Suffix)

        # .. and a database without a log consists of its file alone.
        except FileNotFoundError:
            pass

        _ = shutil.copyfile(path, copy_path)
        engine = create_engine(f'sqlite:///{copy_path}')

        try:
            out = check_outputs(engine, keys, prefix)
        finally:
            engine.dispose()

    return out

# ################################################################################################################################

def verify_node(node:'Node', prefix:'str', keys:'strlist') -> 'OutputCheck':
    """ Waits until the outputs of the relay settle in the pub/sub database of a node and asserts that each key
    was relayed exactly once and in order.
    """
    path = node.db_path(EnvCtx.PubSub_DB_File)
    read_check = partial(_read_copied_check, path, keys, prefix)

    out = wait_for_checks(read_check, ModuleCtx.Settle_Timeout)
    assert_exactly_once(out, keys)

    return out

# ################################################################################################################################

def get_cluster_env(cluster:'PostgreSQLCluster') -> 'strstrdict':
    """ Returns the settings under which the test process reads the instance of a cluster that accepts writes,
    at its own address rather than under the name of the endpoint that only the nodes resolve.
    """
    out = dict(cluster.node_env)
    out['Zato_PubSub_DB_Host'] = cluster.ip

    return out

# ################################################################################################################################
# ################################################################################################################################
