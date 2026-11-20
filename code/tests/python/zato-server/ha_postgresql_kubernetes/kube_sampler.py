# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The sampler of the pods of a pair and the follower of their output. Once per second, the sampler reads the role
# of each pod through its direct role node port, which answers in every status, and the Ready condition of each pod
# from the API server. The follower keeps the output of every container of the Zato pods that the sampler finds
# in a file of the run, so that the output of a pod that a rollout replaced remains readable.

# stdlib
import logging
import os
import subprocess
import threading
import time
from dataclasses import dataclass

# Zato
from kube_checks import read_pod_log
from kube_cluster import cluster, kubectl_json, ModuleCtx as ClusterCtx
from kube_env import ModuleCtx as EnvCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment
    from zato.common.typing_ import anydict, intnone, strnone

# ################################################################################################################################
# ################################################################################################################################

sample_list             = list['PodSample']
followed_line_list      = list['FollowedLine']
followed_container_dict = dict[str, '_FollowedContainer']

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.sampler')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often the pods are sampled, in seconds
    Sample_Interval = 1.0

    # How long the thread of the sampler may take to end once it is stopped, in seconds
    Stop_Timeout = 30.0

    # How long a follower process may take to end once it is terminated, in seconds
    Follower_Stop_Timeout = 5.0

    # The condition of a pod that its readiness probe sets, and its value while the probe succeeds
    Ready_Condition = 'Ready'
    Condition_True = 'True'

    # The subdirectory of the logs of a test that holds the output of each followed container
    Followed_Dir = 'followed'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PodSample:
    """ One pod at one moment - its role and generation, as its node reports them, and its Ready condition.
    The role is None if the node did not answer.
    """
    moment: 'float'
    pod_name: 'str'
    uid: 'str'
    role: 'strnone'
    generation: 'intnone'
    is_ready: 'bool'
    is_terminating: 'bool'

# ################################################################################################################################

@dataclass(init=False)
class FollowedLine:
    """ One line of the output of the Zato container of a pod, with the time at which the kubelet received it.
    """
    moment: 'float'
    pod_name: 'str'
    uid: 'str'
    text: 'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class _FollowedContainer:
    """ The output of the Zato container of one pod and the process of kubectl that writes it.
    """
    pod_name: 'str'
    uid: 'str'
    path: 'str'
    process: 'subprocess.Popen[bytes]'

# ################################################################################################################################
# ################################################################################################################################

class PodLogFollower:
    """ Follows the output of the Zato container of each pod that it is given, each into a file of its own.
    """

    def __init__(self, directory:'str') -> 'None':
        self.directory = directory
        self._containers:'followed_container_dict' = {}
        self._lock = threading.Lock()

        os.makedirs(self.directory, exist_ok=True)

# ################################################################################################################################

    def follow(self, pod_name:'str', uid:'str') -> 'None':
        """ Begins to follow the output of the Zato container of a pod, unless it is followed already.
        """
        with self._lock:
            if uid in self._containers:
                return

            path = os.path.join(self.directory, f'{pod_name}-{uid}.log')
            command = ['kubectl', '--context', cluster.context, 'logs', '--follow', '--timestamps', pod_name,
                '-n', ClusterCtx.Namespace, '-c', EnvCtx.Zato_Container]

            with open(path, 'wb') as log_file:
                process = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT)

            container = _FollowedContainer()
            container.pod_name = pod_name
            container.uid = uid
            container.path = path
            container.process = process

            self._containers[uid] = container

        logger.info('Following the output of %s, uid %s', pod_name, uid)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Ends every follower process, each of which has written the output of its container until then.
        """
        with self._lock:
            containers = list(self._containers.values())

        for container in containers:
            container.process.terminate()

        for container in containers:
            _ = container.process.wait(ModuleCtx.Follower_Stop_Timeout)

# ################################################################################################################################

    def read_lines(self) -> 'followed_line_list':
        """ Returns every line of every followed container, in the order of their times.
        """
        with self._lock:
            containers = list(self._containers.values())

        out:'followed_line_list' = []

        for container in containers:
            for moment, text in read_pod_log(container.pod_name, container.path):
                line = FollowedLine()
                line.moment = moment
                line.pod_name = container.pod_name
                line.uid = container.uid
                line.text = text
                out.append(line)

        out.sort(key=_get_moment)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_moment(line:'FollowedLine') -> 'float':
    return line.moment

# ################################################################################################################################

def _is_ready(pod:'anydict') -> 'bool':
    """ Returns whether the Ready condition of a pod holds.
    """
    status = pod['status']
    conditions = status.get('conditions', [])

    for condition in conditions:
        if condition['type'] == ModuleCtx.Ready_Condition:
            out = condition['status'] == ModuleCtx.Condition_True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def _is_container_running(pod:'anydict') -> 'bool':
    """ Returns whether the Zato container of a pod runs, which is when its output can be followed.
    """
    status = pod['status']
    container_statuses = status.get('containerStatuses', [])

    for container_status in container_statuses:
        if container_status['name'] == EnvCtx.Zato_Container:
            out = 'running' in container_status['state']
            break
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

class PodSampler:
    """ Samples the pods of a pair until it is stopped, and hands each pod whose Zato container runs to the follower.
    """

    def __init__(self, env:'KubeEnvironment', follower:'PodLogFollower') -> 'None':
        self.env = env
        self.follower = follower
        self.samples:'sample_list' = []
        self._lock = threading.Lock()
        self._stopped = threading.Event()
        self._thread = threading.Thread(target=self._run, name='pod-sampler', daemon=True)

    def start(self) -> 'None':
        self._thread.start()
        logger.info('Pod sampler started')

    def stop(self) -> 'None':
        self._stopped.set()
        self._thread.join(ModuleCtx.Stop_Timeout)
        assert not self._thread.is_alive(), 'Pod sampler did not stop'

    def get_samples(self) -> 'sample_list':
        with self._lock:
            out = list(self.samples)
        return out

# ################################################################################################################################

    def _sample_pod(self, pod:'anydict') -> 'PodSample':
        """ Samples one pod. The Ready condition is read before the role, so a pod that the sample shows as Ready
        had its node report a role in which it serves or takes over no later than the role of the sample was read.
        """
        metadata = pod['metadata']

        out = PodSample()
        out.pod_name = metadata['name']
        out.uid = metadata['uid']
        out.is_ready = _is_ready(pod)
        out.is_terminating = 'deletionTimestamp' in metadata

        node = self.env.get_node(out.pod_name)
        report = node.read_role()
        out.moment = time.time()

        if report is None:
            out.role = None
            out.generation = None
        else:
            out.role = report['role']
            out.generation = report['generation']

        return out

# ################################################################################################################################

    def _run(self) -> 'None':

        while not self._stopped.is_set():
            started = time.monotonic()

            # The pods are read once for each sample of all of them, and a read that fails leaves a gap in the samples ..
            try:
                pods = kubectl_json('get', 'pods', '-l', EnvCtx.Pod_Selector, '-n', ClusterCtx.Namespace)
            except Exception as e:
                logger.warning('Pods not read -> %s', e)
                pods = {'items': []}

            for pod in pods['items']:

                # .. each is sampled ..
                sample = self._sample_pod(pod)

                with self._lock:
                    self.samples.append(sample)

                # .. and its output is followed once its Zato container runs ..
                if _is_container_running(pod):
                    self.follower.follow(sample.pod_name, sample.uid)

            # .. until the next sample is due.
            elapsed = time.monotonic() - started
            remaining = ModuleCtx.Sample_Interval - elapsed

            if remaining > 0:
                _ = self._stopped.wait(remaining)

# ################################################################################################################################
# ################################################################################################################################
