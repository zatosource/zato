# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The takeover of a failed active node by its standby under traffic, shared by the takeover suite and the long runs.

# stdlib
import logging
import time

# Zato
from ha_faults import apply_fault, get_isolation_addresses, ModuleCtx as FaultsCtx, remove_fault
from nodes import ModuleCtx as NodesCtx
from workload import Topic_Name, Workload
from zato.common.pubsub.sql.config import ModuleCtx as PubSubConfigCtx
from zato.common.test.client import PublishClient, PullClient
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from zato.common.typing_ import any_, callable_, strlist

    any_ = any_
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.ha_takeover')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before the fault and after the takeover, in seconds
    Traffic_Seconds = 5

    # STOP_GRACE of the supervisor of the node, after which it sends SIGKILL to the process group of the server, in seconds
    Stop_Grace = 10

    # How long the standby may take to become active after the fault, in seconds
    Takeover_Timeout = 60

    # How long the server of the new active node may take to start, in seconds
    Server_Timeout = 120

    # How long the former active node may take to join again as the standby, in seconds
    Rejoin_Timeout = 300

    # The roles of a node that serves requests and of a standby
    Active_Roles:'strlist' = [NodesCtx.Role_Active]
    Standby_Roles:'strlist' = ['Standby']

    # What the log of a node that resumed after a takeover contains
    Fencing_Text = 'fencing'

    # The faults after which the former active node resumes with its process intact, and is fenced as it does
    Resuming_Faults = (FaultsCtx.Fault_Pause, FaultsCtx.Fault_Partition)

    # The faults of the takeover
    Faults = [FaultsCtx.Fault_Stop, FaultsCtx.Fault_Kill, FaultsCtx.Fault_Pause, FaultsCtx.Fault_Partition]

    # How many claims of each scheduler job an active node that fails between a claim and its run may leave without a run
    Unrun_Claims_After_Takeover = 1

    # The prefix of the message ID that is published again after a takeover
    Repeat_Msg_Id_Prefix = 'zpsm.ha.repeat-across-takeover'

    # How many messages one pull of the puller hands out at most
    Pull_Max_Messages = 100

    # The environment of the retention sweep that removes every fully delivered message
    No_Delivered_Messages = {PubSubConfigCtx.Env_Delivered_Max_Messages: '0'}

# ################################################################################################################################
# ################################################################################################################################

def take_over(env:'HAEnvironment', fault:'str', workload:'Workload') -> 'tuple[Node, Node, float]':
    """ Applies a fault to the active node under traffic, waits for its standby to take over and for the former
    active node to join again, and returns the new active node, the former one and the time of the takeover.
    """
    old_active = env.get_active()
    assert old_active is not None, 'No active node'

    new_active = env.get_other(old_active)

    record = env.referee.read_record()
    assert record is not None
    generation_before = record['generation']

    # The traffic reaches the active node ..
    time.sleep(ModuleCtx.Traffic_Seconds)

    # .. which fails ..
    backend_ips = [ip for backend in env.backends for ip in backend.ips]
    addresses = get_isolation_addresses(new_active, env.referee.ip, backend_ips)

    started = time.monotonic()
    fault_started = apply_fault(old_active, fault, addresses)

    # .. a graceful stop drains the worker before the supervisor would send SIGKILL ..
    if fault == FaultsCtx.Fault_Stop:
        stop_duration = time.monotonic() - started
        logger.info('Stop of %s took %.3fs', old_active.node_name, stop_duration)
        assert stop_duration < ModuleCtx.Stop_Grace, f'Stop of {old_active.node_name} took {stop_duration:.3f}s'

    # .. and its standby takes over ..
    _ = new_active.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Takeover_Timeout)
    takeover_time = time.time()

    record = env.referee.read_record()
    assert record is not None
    assert record['active_node'] == new_active.node_name, record
    assert record['generation'] > generation_before, record

    _ = new_active.wait_until_server_up(ModuleCtx.Server_Timeout)

    # .. the traffic reaches the new active node ..
    time.sleep(ModuleCtx.Traffic_Seconds)

    # .. the former active node resumes and is fenced, if its process remained ..
    remove_fault(old_active, fault)
    workload.fault_windows.append((fault_started, time.time()))

    # .. and it joins again as the standby.
    _ = old_active.wait_for_role(ModuleCtx.Standby_Roles, ModuleCtx.Rejoin_Timeout)

    if fault in ModuleCtx.Resuming_Faults:
        logs = old_active.read_logs()
        assert ModuleCtx.Fencing_Text in logs, f'{old_active.node_name} was not fenced'

    out = (new_active, old_active, takeover_time)
    return out

# ################################################################################################################################

def _pull_msg_ids(env:'HAEnvironment') -> 'strlist':
    """ Pulls and acknowledges the queue of the puller until a pull hands out nothing, and returns the msg_id
    of each message handed out.
    """
    client = PullClient(env.haproxy.base_url, env.puller_username, env.puller_password)

    out:'strlist' = []

    while True:
        result = client.pull(max_messages=ModuleCtx.Pull_Max_Messages, needs_ack=True)

        if not result['messages']:
            break

        for message in result['messages']:
            meta = message['meta']
            out.append(meta['msg_id'])

    return out

# ################################################################################################################################

def check_repeat_across_takeover(env:'HAEnvironment', has_message:'callable_') -> 'None':
    """ Publishes a message, delivers it, lets a retention sweep on the active node remove it, stops the active node,
    and after the takeover publishes the same msg_id again, which is a repeat that stores and delivers nothing.
    The function given tells whether the database of a node holds the message of a msg_id.
    """
    active = env.get_active()
    assert active is not None, 'No active node'

    client = PublishClient(env.haproxy.base_url, env.publisher_username, env.publisher_password)

    msg_id = f'{ModuleCtx.Repeat_Msg_Id_Prefix}.{time.time_ns()}'
    data = {'repeat_across_takeover': msg_id}

    # The message is published and delivered ..
    result = client.publish(Topic_Name, data, msg_id=msg_id)
    assert result['msg_id'] == msg_id, result

    pulled = _pull_msg_ids(env)
    assert msg_id in pulled, f'{msg_id} not delivered'

    # .. a retention sweep on the active node removes it, while its dedup record remains ..
    sweep = active.run_retention_sweep(ModuleCtx.No_Delivered_Messages)
    assert sweep.returncode == 0, f'Sweep failed:\n{sweep.stdout}{sweep.stderr}'
    assert not has_message(active, msg_id), f'{msg_id} not removed'

    # .. the active node stops and its standby takes over ..
    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    new_active, _ignored, _ignored_time = take_over(env, FaultsCtx.Fault_Stop, workload)

    # .. and the same msg_id published again is a repeat, which stores nothing and is delivered to no one.
    result = client.publish(Topic_Name, data, msg_id=msg_id)
    assert result['msg_id'] == msg_id, result

    assert not has_message(new_active, msg_id), f'{msg_id} stored again after the takeover'

    pulled = _pull_msg_ids(env)
    assert msg_id not in pulled, f'{msg_id} delivered again after the takeover'

# ################################################################################################################################
# ################################################################################################################################
