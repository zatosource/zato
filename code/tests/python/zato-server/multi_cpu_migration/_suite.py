# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# Zato
from zato.common.api import PubSub
from zato.common.hl7.mllp.haproxy import Env_Port_Name as MLLP_Port_Env
from zato.common.test.conftest_base_multi_cpu import enmasse_import, MultiCPUTestConfig
from zato.common.test.conftest_base_pubsub import find_free_port, start_server_process
from zato.common.worker_count import get_affinity_count, get_auto_worker_count, ServerWorkers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import dictlist, intnone, list_

    receiverlist = list_[WebhookReceiver]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_migration')

# ################################################################################################################################
# ################################################################################################################################

class MigrationConfig:
    """ The subscribers of the suite, the receivers of their push deliveries and the session of the server,
    which the tests start again with another number of workers.
    """

    # How many push subscribers the topic has, which gives every slot of up to eight workers keys of its own
    Subscriber_Count = 32

    Topic_Name     = 'multi.cpu.migration'
    Publisher_Name = 'test.multi-cpu.migration.publisher'

    # The number of workers of the server that the suite starts first
    Single_Worker_Count = 1

    receivers:'receiverlist' = []

    state:'SessionState'

# ################################################################################################################################
# ################################################################################################################################

def get_subscriber_name(index:'int') -> 'str':
    out = f'test.multi-cpu.migration.sub.{index:02d}'
    return out

# ################################################################################################################################

def get_endpoint_name(index:'int') -> 'str':
    subscriber_name = get_subscriber_name(index)

    out = f'{subscriber_name}.out'
    return out

# ################################################################################################################################
# ################################################################################################################################

def set_delivery_active(is_active:'bool') -> 'None':
    """ Turns the push delivery of every subscription of the suite on or off through enmasse. The messages of a subscription
    whose delivery is off wait in its queue.
    """
    subscriptions:'dictlist' = []

    for index in range(MigrationConfig.Subscriber_Count):
        subscriptions.append({
            'security': get_subscriber_name(index),
            'delivery_type': PubSub.Delivery_Type.Push,
            'push_rest_endpoint': get_endpoint_name(index),
            'topic_list': [MigrationConfig.Topic_Name],
            'is_delivery_active': is_active,
        })

    enmasse_import({'pubsub_subscription': subscriptions})

# ################################################################################################################################

def restart_server(worker_count:'intnone') -> 'None':
    """ Terminates the server and starts it again in the same directory and on the same port with the given number
    of workers, or with no number in its environment when it is None. The server inherits the environment
    of the test process, so the number is set there.
    """
    state = MigrationConfig.state
    state.kill_server()

    # The server reads its worker count from server.conf when its environment has none ..
    if worker_count is None:
        if ServerWorkers.Env_Key in os.environ:
            del os.environ[ServerWorkers.Env_Key]

        affinity_count = get_affinity_count()
        MultiCPUTestConfig.worker_count = get_auto_worker_count(affinity_count, ServerWorkers.CPU_Max_Path)

    # .. or else from its environment.
    else:
        os.environ[ServerWorkers.Env_Key] = str(worker_count)
        MultiCPUTestConfig.worker_count = worker_count

    # The broker of the new process listens on a port of its own ..
    broker_port = find_free_port()

    extra_server_env = {
        MLLP_Port_Env: str(MultiCPUTestConfig.mllp_port),
    }

    # .. and the server itself comes back on the port that the tests already use.
    _ = start_server_process(
        state=state,
        logger=logger,
        zato_bin=MultiCPUTestConfig.zato_bin,
        server_directory=MultiCPUTestConfig.server_directory,
        server_port=MultiCPUTestConfig.port,
        broker_port=broker_port,
        extra_server_env=extra_server_env,
        patch_server_conf_bind=True,
    )

    logger.info('Server started again with %s workers', MultiCPUTestConfig.worker_count)

# ################################################################################################################################

def get_server_conf_path() -> 'str':
    out = os.path.join(MultiCPUTestConfig.server_directory, 'config', 'repo', 'server.conf')
    return out

# ################################################################################################################################
# ################################################################################################################################
