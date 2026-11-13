# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The configuration of a server that runs under the active-standby node, which starts the server only on the active host
# and passes it the location of the replication barrier, the referee generation and the name of the node.

# stdlib
import os

# Zato
from zato.common.defaults import default_env_base_dir

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The mode of the environment, set to the active-standby mode on both hosts of a pair
    Env_Mode = 'Zato_HA_Mode'

    # The path to the Unix socket of the replication barrier
    Env_Barrier_Socket = 'Zato_HA_Barrier_Socket'

    # The name of the socket of the replication barrier in the environment directory, unless the node is told otherwise
    Default_Barrier_Socket_Name = 'ha-barrier.sock'

    # The referee generation under which the node started the server
    Env_Generation = 'Zato_HA_Generation'

    # The name of the node that started the server
    Env_Node_Name = 'Zato_HA_Node_Name'

    # The value of the mode variable that turns the active-standby mode on
    Mode_Active_Standby = 'active-standby'

    # The type of the pub/sub database, which selects the storage mode of the node
    Env_PubSub_DB_Type = 'Zato_PubSub_DB_Type'

    # The type of the pub/sub database under which both hosts of a pair use one PostgreSQL database
    PubSub_DB_Type_PostgreSQL = 'postgresql'

# ################################################################################################################################
# ################################################################################################################################

# The names under which the node replicates each database.
Database_PubSub = 'pubsub'
Database_Common = 'common'
Database_Audit  = 'audit'

# The name of a database that the node does not replicate.
Not_Replicated = ''

# The databases whose commits return only once the standby has stored them.
Synchronous_Databases = (Database_PubSub, Database_Common)

# ################################################################################################################################
# ################################################################################################################################

def is_active_standby() -> 'bool':
    """ Returns whether this process runs in an environment of an active-standby pair.
    """
    mode = os.environ.get(ModuleCtx.Env_Mode, '')

    out = mode == ModuleCtx.Mode_Active_Standby
    return out

# ################################################################################################################################

def is_shared_storage() -> 'bool':
    """ Returns whether both hosts of the pair use one PostgreSQL database, in which case the node replicates
    no database of its host.
    """
    db_type = os.environ.get(ModuleCtx.Env_PubSub_DB_Type, '')

    out = db_type == ModuleCtx.PubSub_DB_Type_PostgreSQL
    return out

# ################################################################################################################################

def get_barrier_socket_path() -> 'str':
    """ Returns the path to the Unix socket of the replication barrier. The node passes it to the server it starts,
    and the other processes of the environment use the default location under the environment directory.
    """
    out = os.environ.get(ModuleCtx.Env_Barrier_Socket)

    if out is None:
        out = os.path.join(default_env_base_dir, ModuleCtx.Default_Barrier_Socket_Name)

    return out

# ################################################################################################################################

def get_generation() -> 'int':
    """ Returns the referee generation under which the node started this server.
    """
    generation = os.environ[ModuleCtx.Env_Generation]

    out = int(generation)
    return out

# ################################################################################################################################

def get_node_name() -> 'str':
    """ Returns the name of the node that started this server.
    """
    out = os.environ[ModuleCtx.Env_Node_Name]
    return out

# ################################################################################################################################
# ################################################################################################################################
