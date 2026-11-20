# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The checks of every run applied to a pair in Kubernetes, the report of how long the Service listed no pod,
# the placement of the active role on a given pod, and the readers of the output of a pod and of the answers
# that a client of the Service received.

# stdlib
import logging
import re
import time
from datetime import datetime

# Zato
from ha_checks import check_scheduler, check_workload
from kube_cluster import kubectl, ModuleCtx as ClusterCtx
from kube_env import ModuleCtx as EnvCtx
from kube_faults import delete_pod
from kube_traffic import ModuleCtx as TrafficCtx
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment, KubeNode
    from kube_traffic import FailoverClient, RequestRecord
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

log_entry = tuple[float, str]
log_entry_list = list[log_entry]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.checks')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before a fault, in seconds
    Traffic_Seconds = 5

    # How long the pair may take to recover once a fault is removed, in seconds, which includes pods that start again
    Recovery_Timeout = 600

    # How long the endpoints of the Service may take to follow the label of the new active pod, in seconds
    Propagation_Limit = 2.0

    # How many claims of each scheduler job an active pod that a fault ends between a claim and its run may leave without a run
    Unrun_Claims_After_Fault = 1

    # How often the requests of a client are read while a test waits for an answer, in seconds
    Poll_Interval = 0.1

    # A line of the output of a pod, with the time at which the kubelet received it
    Timestamped_Line = re.compile(r'^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(\.\d+)?Z (.*)$')

    # The digits of a fraction of a second that datetime reads
    Fraction_Digits = 6

# ################################################################################################################################
# ################################################################################################################################

def place_active(env:'KubeEnvironment', ordinal:'int') -> 'KubeNode':
    """ Moves the active role to the pod of the given ordinal, deleting the active pod while the role is on the other one,
    and returns the active pod once the other one is its standby.
    """
    pod_name = EnvCtx.Pod_Names[ordinal]
    deadline = time.monotonic() + ModuleCtx.Recovery_Timeout

    while True:
        remaining = deadline - time.monotonic()
        active = env.wait_for_pair(remaining)

        if active.pod_name == pod_name:
            logger.info('Active role on %s', pod_name)
            return active

        # The pod of the given ordinal takes over from the deleted one, which then becomes its standby.
        _ = delete_pod(active.pod_name)

        target = env.get_node(pod_name)
        remaining = deadline - time.monotonic()
        _ = target.wait_for_role([EnvCtx.Role_Active], remaining)

# ################################################################################################################################

def start_workload(env:'KubeEnvironment') -> 'Workload':
    """ Starts the shared workload against the Service of the pair and lets it run before a fault.
    """
    out = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    out.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    return out

# ################################################################################################################################

def get_pair(env:'KubeEnvironment') -> 'tuple[KubeNode, KubeNode]':
    """ Returns the active pod and its standby, each with the node it runs on.
    """
    active = env.get_active()
    assert active is not None, 'No active pod'

    standby = env.get_other(active)

    active.locate()
    standby.locate()

    out = (active, standby)
    return out

# ################################################################################################################################

def finish(env:'KubeEnvironment', workload:'Workload', fault_started:'float', unrun_claims:'int'=0) -> 'KubeNode':
    """ Waits for the pair, reports how long the Service listed no pod after the fault and applies the checks of every run.
    Each job may count the given number of claims that an active pod ended by the fault did not run.
    """
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

    for period_start, period_end in env.watcher.get_empty_periods_after(fault_started):
        logger.info('Service listed no pod for %.1fs, from %.3f', period_end - period_start, period_start)

    check_workload(cast_('any_', env), workload)

    _ = check_scheduler(cast_('any_', env), unrun_claims)

    return active

# ################################################################################################################################

def read_pod_log(pod_name:'str', path:'str'='') -> 'log_entry_list':
    """ Returns each line of the output of the Zato container of a pod with the time at which the kubelet received it,
    from the pod itself or, given a path, from a file of that output that a follower of the pod wrote.
    """
    if path:
        with open(path) as log_file:
            text = log_file.read()
    else:
        result = kubectl('logs', pod_name, '-n', ClusterCtx.Namespace, '-c', EnvCtx.Zato_Container, '--timestamps')
        text = result.stdout

    out:'log_entry_list' = []

    for line in text.splitlines():
        match = ModuleCtx.Timestamped_Line.match(line)
        if not match:
            continue

        # The kubelet writes nine digits of a fraction of a second, of which datetime reads six.
        seconds, fraction, text = match.groups()
        if fraction is None:
            fraction = '.0'
        fraction = fraction[:ModuleCtx.Fraction_Digits + 1]

        moment = datetime.fromisoformat(f'{seconds}{fraction}+00:00').timestamp()
        out.append((moment, text))

    return out

# ################################################################################################################################

def find_moment(entries:'log_entry_list', after:'float', pattern:'re.Pattern[str]', description:'str') -> 'float':
    """ Returns the time of the first line after a moment that matches a pattern.
    """
    for moment, text in entries:
        if moment >= after:
            if pattern.search(text):
                return moment

    raise Exception(f'No line of {description} after {after}')

# ################################################################################################################################

def wait_for_ok(client:'FailoverClient', after:'float', timeout:'float') -> 'RequestRecord':
    """ Waits for the first request sent after a moment that the Service answered, and returns it.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        for record in client.get_records():
            if record.sent >= after:
                if record.outcome == TrafficCtx.Outcome_OK:
                    return record

        time.sleep(ModuleCtx.Poll_Interval)

    raise Exception(f'No answer from the Service after {after} within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################
