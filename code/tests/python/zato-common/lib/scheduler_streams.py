# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
from uuid import uuid4

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable that the servers and the scheduler binary read the prefix of the scheduler streams from
    Stream_Prefix_Variable = 'Zato_Scheduler_Stream_Prefix'

    # The prefixes of the test processes are outside the zato: namespace, which quickstart clears,
    # so that a quickstart of another environment does not remove the streams of a running server
    Prefix_Root = 'zato-test:scheduler:'

    # The Redis of the scheduler, unless the environment says otherwise
    Redis_Host_Variable = 'Zato_Scheduler_Redis_Host'
    Redis_Port_Variable = 'Zato_Scheduler_Redis_Port'
    Default_Redis_Host = 'localhost'
    Default_Redis_Port = '6379'

# ################################################################################################################################
# ################################################################################################################################

def delete_streams(prefix:'str') -> 'None':
    """ Removes every stream and the sequence of the scheduler under the prefix of a test process from Redis.
    """
    # The client is imported only at exit, because importing it when this module loads would precede the patch of gevent
    from redis import Redis

    host = ModuleCtx.Default_Redis_Host
    if host_from_env := os.environ.get(ModuleCtx.Redis_Host_Variable):
        host = host_from_env

    port = ModuleCtx.Default_Redis_Port
    if port_from_env := os.environ.get(ModuleCtx.Redis_Port_Variable):
        port = port_from_env

    redis_connection = Redis(host=host, port=int(port), decode_responses=True)

    keys = list(redis_connection.scan_iter(match=prefix + ':*'))

    if keys:
        _ = redis_connection.delete(*keys)

    redis_connection.close()

# ################################################################################################################################

def use_own_streams() -> 'None':
    """ Gives the scheduler streams of this test process and its servers a prefix of their own, so that a quickstart
    of another environment does not remove the streams of a running server, and removes the streams at exit.
    """
    variable = ModuleCtx.Stream_Prefix_Variable

    # A prefix given from outside, e.g. by the test process that started this one, belongs to the process that set it
    if variable in os.environ:
        return

    prefix = ModuleCtx.Prefix_Root + uuid4().hex
    os.environ[variable] = prefix

    # The handler is registered before those of the environments of the run, so it runs after their servers stopped
    _ = atexit.register(delete_streams, prefix)

# ################################################################################################################################
# ################################################################################################################################
