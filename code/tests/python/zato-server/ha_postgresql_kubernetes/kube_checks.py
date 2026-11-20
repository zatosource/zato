# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The checks of every run applied to a pair in Kubernetes, the report of how long the Service listed no pod,
# and the readers of the output of a pod and of the answers that a client of the Service received.

# stdlib
import logging
import re
import time
from datetime import datetime

# Zato
from ha_checks import check_scheduler, check_workload
from kube_cluster import kubectl, ModuleCtx as ClusterCtx
from kube_env import ModuleCtx as EnvCtx
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

def read_pod_log(pod_name:'str') -> 'log_entry_list':
    """ Returns each line of the output of the Zato container of a pod with the time at which the kubelet received it.
    """
    result = kubectl('logs', pod_name, '-n', ClusterCtx.Namespace, '-c', EnvCtx.Zato_Container, '--timestamps')
    out:'log_entry_list' = []

    for line in result.stdout.splitlines():
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
