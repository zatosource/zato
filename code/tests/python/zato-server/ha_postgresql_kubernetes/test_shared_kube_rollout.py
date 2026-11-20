# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The handover of the active role when its pod is replaced. A rolling update replaces the pod of the highest ordinal
# first, so it hands the active role over once if the role is on ordinal 0 and twice if it is on ordinal 1. In each
# handover, the active node drains its server, releases the referee record and exits, and the standby takes the released
# record over at its next heartbeat. A node that restarts while the other one is unreachable takes over the record
# that it released itself at once.

# stdlib
import json
import math
import os
import re
import time

# pytest
import pytest

# Zato
from kube_checks import find_moment, finish, get_pair, ModuleCtx as ChecksCtx, place_active, read_pod_log, start_workload, \
    wait_for_ok
from kube_cluster import get_pod_uid, kubectl, ModuleCtx as ClusterCtx, wait_for_rollout
from kube_env import ModuleCtx as EnvCtx
from kube_faults import delete_pod, heal_node, isolate_node
from kube_sampler import ModuleCtx as SamplerCtx, PodLogFollower, PodSampler
from kube_traffic import FailoverClient, ModuleCtx as TrafficCtx
from zato.common.test.client import AdminClient
from zato.common.test.ha_limits import HALimits
from zato.common.test.perf_report import ModuleCtx as PerfCtx, report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_checks import log_entry, log_entry_list
    from kube_env import KubeEnvironment, KubeNode
    from kube_sampler import followed_line_list, sample_list
    from kube_traffic import record_list
    from workload import Workload
    from zato.common.typing_ import anydict, floatlist, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

request_run_list = list['record_list']
strfloatdict = dict[str, float]
stage_moment_list = list[tuple[str, float]]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The annotation of the pod template that a rolling update changes
    Restart_Annotation = 'zato.io/restarted-at'

    # How many handovers a rolling update performs with the active role on each ordinal
    Handovers = {0: 1, 1: 2}

    # How much later than the heartbeat time the takeover of a released record may follow the release, in seconds,
    # which covers the write of the release, the read of the record by the other node and the output of both pods
    Release_Margin = 1.0

    # How long the client may take to be served before the update and after it, in seconds
    Served_Timeout = 120

    # How long the client keeps sending requests after the update, in seconds
    Served_Seconds = 5

    # How long the replaced pod may take to report the active role, in seconds
    Takeover_Timeout = 300

    # The roles in which a node may not be Ready
    Not_Ready_Roles:'strlist' = ['Down', 'Fenced']

    # The lines of the nodes that the test reads a handover from
    Takeover_Line = re.compile(r'Taking over at generation \d+ after ')
    Release_Line = re.compile(r'Released the active role at generation \d+')
    Standby_Line = re.compile(r'Starting as Standby at generation ')
    Released_By = 'after the release by {}'
    Released_By_Any = 'after the release by '

    # The lines of a node that stops its server and that removes and applies the label of its own pod
    Server_Stop_Line   = re.compile(r'Stopping the Zato server with PID ')
    Label_Removed_Line = re.compile(r'labeled as serving: false')
    Label_Applied_Line = re.compile(r'labeled as serving: true')

    # The stages of a handover that a performance suite records, each by the line that ends it
    Stage_Patterns = (
        ('server_stop', Server_Stop_Line),
        ('label_removed', Label_Removed_Line),
        ('drain', re.compile(r'Worker is draining')),
        ('worker_exit', re.compile(r'Worker, PID \d+, terminated')),
        ('config_exit', re.compile(r'Config process, PID \d+, terminated')),
        ('release', re.compile(r'Released the active role at generation \d+')),
        ('takeover', re.compile(r'Taking over at generation \d+ after the release by ')),
        ('server_start', re.compile(r'Zato server started with PID ')),
        ('first_answer', re.compile(r'Zato server answers at generation ')),
        ('label_applied', Label_Applied_Line),
    )

    # The name under which the figures of a handover are recorded
    Result_Name = 'Handover'

# ################################################################################################################################
# ################################################################################################################################

def _get_handover_limit(env:'KubeEnvironment') -> 'float':
    """ Returns how long the client may fail in one handover - the stop of the server, one heartbeat, the start
    of the next server and the propagation of the endpoints.
    """
    out = HALimits.Server_Stop + env.timers.heartbeat + HALimits.Server_Start + ChecksCtx.Propagation_Limit
    return out

# ################################################################################################################################

def _read_generation(env:'KubeEnvironment') -> 'int':
    record = env.referee.read_record()
    assert record is not None, 'No referee record'

    out = record['generation']
    return out

# ################################################################################################################################

def _update_pods() -> 'float':
    """ Changes an annotation of the pod template, which replaces both pods one after the other, waits until the update
    completes and returns the time it began.
    """
    patch = {
        'spec': {
            'template': {
                'metadata': {
                    'annotations': {
                        ModuleCtx.Restart_Annotation: str(time.time()),
                    },
                },
            },
        },
    }

    out = time.time()
    _ = kubectl('patch', 'statefulset', EnvCtx.StatefulSet_Name, '-n', ClusterCtx.Namespace, '-p', json.dumps(patch))

    wait_for_rollout('statefulset', EnvCtx.StatefulSet_Name)

    return out

# ################################################################################################################################

def _get_failure_runs(records:'record_list', after:'float') -> 'request_run_list':
    """ Returns each run of consecutive requests sent after a moment that the Service did not answer.
    """
    out:'request_run_list' = []
    current:'record_list' = []

    for record in records:
        if record.sent < after:
            continue

        if record.outcome == TrafficCtx.Outcome_OK:
            if current:
                out.append(current)
                current = []
        else:
            current.append(record)

    if current:
        out.append(current)

    return out

# ################################################################################################################################

def _describe_runs(runs:'request_run_list') -> 'strlist':
    out:'strlist' = []

    for run in runs:
        first = run[0]
        last = run[-1]
        duration = last.ended - first.sent
        out.append(f'{first.sent:.3f}+{duration:.3f}s ({len(run)} requests, {first.outcome}, {last.outcome})')

    return out

# ################################################################################################################################

def _check_releases(lines:'followed_line_list', after:'float', limit:'float') -> 'None':
    """ Checks that each takeover after a moment took over a released record, no later than the limit after the release.
    """
    release_at = 0.0

    for line in lines:
        if line.moment < after:
            continue

        if ModuleCtx.Release_Line.search(line.text):
            release_at = line.moment
            continue

        if ModuleCtx.Takeover_Line.search(line.text):
            assert ModuleCtx.Released_By_Any in line.text, f'Takeover without a release in {line.pod_name} -> {line.text}'
            assert release_at, f'Takeover in {line.pod_name} before any release -> {line.text}'

            delay = line.moment - release_at
            assert delay <= limit, f'Takeover in {line.pod_name} {delay:.3f}s after the release, above {limit:.3f}s'

# ################################################################################################################################

def _get_readiness_violations(samples:'sample_list') -> 'strlist':
    """ Returns each sample of a pod that is not terminating and is Ready while its node is down, fenced
    or does not answer.
    """
    out:'strlist' = []

    for sample in samples:
        if sample.is_terminating:
            continue

        if not sample.is_ready:
            continue

        if sample.role is None:
            out.append(f'{sample.moment:.3f} {sample.pod_name} {sample.uid} Ready without an answer')

        elif sample.role in ModuleCtx.Not_Ready_Roles:
            out.append(f'{sample.moment:.3f} {sample.pod_name} {sample.uid} Ready in {sample.role}')

    return out

# ################################################################################################################################

def _update_under_workload(env:'KubeEnvironment', workload:'Workload', handovers:'int') -> 'None':
    """ Replaces both pods while the workload runs and checks each handover of the update and the workload afterwards.
    """
    generation_before = _read_generation(env)

    client = FailoverClient(env.session.control_plane_ip, EnvCtx.Service_Node_Port)
    follower = PodLogFollower(os.path.join(env.logs_dir, SamplerCtx.Followed_Dir))
    sampler = PodSampler(env, follower)

    client.start()
    sampler.start()

    try:
        # The client is served before the update ..
        _ = wait_for_ok(client, 0.0, ModuleCtx.Served_Timeout)

        # .. the update replaces both pods ..
        started = _update_pods()
        _ = env.wait_for_pair(ChecksCtx.Recovery_Timeout)

        # .. and the client is served afterwards.
        served_after = time.time()
        _ = wait_for_ok(client, served_after, ModuleCtx.Served_Timeout)
        time.sleep(ModuleCtx.Served_Seconds)

    finally:
        sampler.stop()
        client.stop()
        follower.stop()

    # The generation rises once for each handover ..
    generation_after = _read_generation(env)
    assert generation_after - generation_before == handovers, \
        f'Generation {generation_before} -> {generation_after}, expected {handovers} handovers'

    # .. each takeover follows a release ..
    release_limit = env.timers.heartbeat + ModuleCtx.Release_Margin
    lines = follower.read_lines()
    _check_releases(lines, started, release_limit)

    # .. no pod is Ready in a role in which it cannot serve or take over ..
    samples = sampler.get_samples()
    violations = _get_readiness_violations(samples)
    assert not violations, f'Ready without a role -> {violations}'

    # .. the client fails at most once in each handover and for no longer than the handover may take ..
    records = client.get_records()
    runs = _get_failure_runs(records, started)
    described = _describe_runs(runs)
    handover_limit = _get_handover_limit(env)

    assert len(runs) <= handovers, f'More failure runs than the {handovers} handovers -> {described}'

    for run in runs:
        first = run[0]
        last = run[-1]
        duration = last.ended - first.sent
        assert duration <= handover_limit, f'Failure run above {handover_limit:.3f}s -> {described}'

        workload.fault_windows.append((first.sent, last.ended))

    # .. and nothing acknowledged is lost, while each replaced active pod may leave the claim it committed
    # before the run began without a run.
    unrun_claims = ChecksCtx.Unrun_Claims_After_Fault * handovers
    _ = finish(env, workload, started, unrun_claims)

    # The stages of each handover are recorded while a performance suite asks for them.
    if os.environ.get(PerfCtx.Env_Results_File, ''):
        _report_handovers(env, lines, started)

# ################################################################################################################################

def _handover_starts(lines:'followed_line_list', after:'float') -> 'floatlist':
    """ Returns the moment at which each pod that served began to stop its server after a moment. A pod whose label
    was never applied, such as one that starts, begins no handover.
    """
    out:'floatlist' = []

    # The UIDs of the pods whose own label is applied
    labeled:'strset' = set()

    for line in lines:

        # A pod that applies its own label serves from then on ..
        if ModuleCtx.Label_Applied_Line.search(line.text):
            labeled.add(line.uid)

        # .. the stop of the server of a pod that serves begins a handover ..
        elif ModuleCtx.Server_Stop_Line.search(line.text):
            if line.uid in labeled:
                labeled.remove(line.uid)

                if line.moment >= after:
                    out.append(line.moment)

        # .. and a pod whose label is removed for another reason serves no longer.
        elif ModuleCtx.Label_Removed_Line.search(line.text):
            labeled.discard(line.uid)

    return out

# ################################################################################################################################

def _stage_figures(lines:'followed_line_list', handover_start:'float', handover_end:'float') -> 'strfloatdict':
    """ Returns how long after the stop of the server each stage of a handover was reported.
    """
    moments:'stage_moment_list' = []

    for name, pattern in ModuleCtx.Stage_Patterns:
        for line in lines:
            if line.moment < handover_start:
                continue

            if line.moment >= handover_end:
                break

            if pattern.search(line.text):
                moments.append((name, line.moment))
                break

    out:'strfloatdict' = {}

    for name, moment in moments:
        out[name] = moment - handover_start

    return out

# ################################################################################################################################

def _report_handovers(env:'KubeEnvironment', lines:'followed_line_list', after:'float') -> 'None':
    """ Records the stages of each handover after a moment with the settings of the active server.
    """
    starts = _handover_starts(lines, after)
    assert starts, f'No handover after {after}'

    client = AdminClient(env.haproxy.base_url, env.session.base.invoke_password)
    measurement = start_measurement(client, env.database)

    # Each handover ends where the next one begins, and the last one at the end of the output.
    ends = starts[1:] + [math.inf]

    for handover_start, handover_end in zip(starts, ends, strict=True):
        stages = _stage_figures(lines, handover_start, handover_end)
        duration = stages[ModuleCtx.Stage_Patterns[-1][0]]

        figures = {
            'stages': stages,
            'duration': duration,
            'window_start': handover_start,
            'window_end': handover_start + duration,
        }

        _ = report_result(measurement, ModuleCtx.Result_Name, figures)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('active_ordinal', [0, 1])
def test_rolling_update(kube_pair:'KubeEnvironment', active_ordinal:'int') -> 'None':
    """ A rolling update replaces both pods under traffic with the active role on the given ordinal. Each handover
    follows a release, no pod is Ready in a role in which it cannot serve or take over, the client fails only
    for the duration of each handover, and nothing acknowledged is lost.
    """
    env = kube_pair
    handovers = ModuleCtx.Handovers[active_ordinal]

    _ = place_active(env, active_ordinal)

    workload = start_workload(env)

    # The checks of the workload stop its threads only when they complete, so a failed condition stops them here.
    try:
        _update_under_workload(env, workload, handovers)
    finally:
        workload.stop()

# ################################################################################################################################

def _find_line(entries:'log_entry_list', after:'float', pattern:'re.Pattern[str]') -> 'log_entry':
    """ Returns the first line after a moment that matches a pattern, with its time.
    """
    for entry in entries:
        moment, text = entry
        if moment >= after:
            if pattern.search(text):
                return entry

    raise Exception(f'No line matching `{pattern.pattern}` after {after}')

# ################################################################################################################################

def _read_pod_uid(pod_name:'str') -> 'str':
    """ Returns the UID of a pod, or an empty string while the pod does not exist.
    """
    result = kubectl('get', 'pod', pod_name, '-n', ClusterCtx.Namespace, '-o', 'jsonpath={.metadata.uid}', check=False)

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def _wait_for_replacement(node:'KubeNode', uid:'str', generation:'int') -> 'anydict':
    """ Waits until the pod that replaced a deleted one reports the active role at a generation above the given one.
    """
    deadline = time.monotonic() + ModuleCtx.Takeover_Timeout

    while time.monotonic() < deadline:

        current_uid = _read_pod_uid(node.pod_name)

        if current_uid not in ('', uid):
            report = node.read_role()

            if report is not None:
                if report['role'] == EnvCtx.Role_Active:
                    if report['generation'] > generation:
                        return report

        time.sleep(ChecksCtx.Poll_Interval)

    raise Exception(f'{node.pod_name} not active above generation {generation} after {ModuleCtx.Takeover_Timeout}s')

# ################################################################################################################################

def test_restart_alone(kube_pair:'KubeEnvironment') -> 'None':
    """ The node of the standby is unreachable while the active pod is replaced, and the pod that replaces it takes over
    the record that it released at its first heartbeat, without the takeover time.
    """
    env = kube_pair
    active, standby = get_pair(env)

    uid = get_pod_uid(active.pod_name)
    generation = _read_generation(env)

    client = FailoverClient(env.session.control_plane_ip, EnvCtx.Service_Node_Port)
    client.start()

    try:
        # The client is served before the restart ..
        _ = wait_for_ok(client, 0.0, ModuleCtx.Served_Timeout)

        # .. the standby becomes unreachable and the active pod is replaced ..
        _ = isolate_node(standby.host_node)
        deleted_at = delete_pod(active.pod_name)

        # .. the pod that replaces it takes over ..
        _ = _wait_for_replacement(active, uid, generation)

        # .. and the client is served again.
        _ = wait_for_ok(client, deleted_at, ModuleCtx.Served_Timeout)

    finally:
        client.stop()
        heal_node(standby.host_node)

    # The new pod starts as the standby and takes over the record released by its own name at its first heartbeat.
    entries = read_pod_log(active.pod_name)
    standby_at = find_moment(entries, deleted_at, ModuleCtx.Standby_Line, 'the start as the standby')
    takeover_at, takeover_text = _find_line(entries, deleted_at, ModuleCtx.Takeover_Line)

    released_by = ModuleCtx.Released_By.format(active.pod_name)
    assert released_by in takeover_text, f'Takeover without the own release -> {takeover_text}'

    delay = takeover_at - standby_at
    limit = env.timers.heartbeat + ModuleCtx.Release_Margin
    assert delay <= limit, f'Takeover {delay:.3f}s after the start, above {limit:.3f}s'

    # The pair forms again once the standby is reachable.
    _ = env.wait_for_pair(ChecksCtx.Recovery_Timeout)

# ################################################################################################################################
# ################################################################################################################################
