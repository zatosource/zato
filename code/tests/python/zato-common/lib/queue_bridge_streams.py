# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import importlib.util
import os
import sys
from uuid import uuid4

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The module that names the variable of the prefix, loaded from its file, without the packages above it,
    # which import modules that the suites patching gevent must import only after the patch
    Module_Name = 'zato_test_queue_bridge'
    Module_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..',
        'zato-common', 'src', 'zato', 'common', 'queue_bridge.py')

    # The prefixes of the test processes are outside the zato: namespace, which quickstart clears,
    # so that a quickstart of another environment does not remove the streams of a running server
    Prefix_Root = 'zato-test:queue_bridge:'

    # The Redis of the queue bridge, unless the environment says otherwise
    Redis_Host_Variable = 'Zato_Queue_Bridge_Redis_Host'
    Redis_Port_Variable = 'Zato_Queue_Bridge_Redis_Port'

    Default_Redis_Host = 'localhost'
    Default_Redis_Port = '6379'

# ################################################################################################################################
# ################################################################################################################################

def delete_streams(prefix:'str') -> 'None':
    """ Removes every stream of the queue bridge under the prefix of a test process from Redis.
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
    """ Gives the queue bridge of this test process, its servers and its bridges a stream prefix of their own,
    so that test processes sharing one Redis never read each other's streams, and removes the streams at exit.
    """
    spec = importlib.util.spec_from_file_location(ModuleCtx.Module_Name, ModuleCtx.Module_Path)
    queue_bridge = importlib.util.module_from_spec(spec) # type: ignore
    sys.modules[ModuleCtx.Module_Name] = queue_bridge
    spec.loader.exec_module(queue_bridge) # type: ignore

    variable = queue_bridge.Stream_Prefix_Variable

    # A prefix given from outside, e.g. by the test process that started this one, belongs to the process that set it
    if variable in os.environ:
        return

    prefix = ModuleCtx.Prefix_Root + uuid4().hex
    os.environ[variable] = prefix

    # The handler is registered before those of the environments of the run, so it runs after their servers stopped
    _ = atexit.register(delete_streams, prefix)

# ################################################################################################################################
# ################################################################################################################################
