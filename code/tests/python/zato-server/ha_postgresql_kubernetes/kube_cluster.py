# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The kind cluster of the Kubernetes suites - one control plane node and three worker nodes, one per zone, each a Docker
# container with the repository and the run directory mounted at their own paths - and the commands that act on it.

# stdlib
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from string import Template
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen

# Zato
from topology import docker
from zato.common.test.reservation import forget_name, is_name_live, is_reserved_name, reserve_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.reservation import NameReservation
    from zato.common.typing_ import any_, strlist, strlistdict, strset, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.cluster')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The prefix of the reserved name of each run, which names its cluster and its runtime directory
    Name_Prefix = 'zato-ha-kube'

    # The directory under which each run keeps its data in a directory of its reserved name
    Runtime_Base_Dir = '/tmp'

    # The prefix of the kubectl context that kind creates for a cluster, and the namespace of the suites
    Context_Prefix = 'kind-'
    Namespace = 'zato-ha'

    # The suffixes that kind appends to the name of a cluster to name its nodes, with the zone of each worker node
    Control_Plane_Suffix = '-control-plane'
    Worker_Zones = {
        '-worker':  'zone-a',
        '-worker2': 'zone-b',
        '-worker3': 'zone-c',
    }

    # The zones of the Zato pods, whose worker nodes receive the Zato image
    Zato_Zones = ['zone-a', 'zone-b']

    # The build directory of the runtime image of the Zato pods, the repository of its name and the length of its tag,
    # which is a prefix of the digest of its Dockerfile
    Pod_Image_Dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pod-image')
    Pod_Image_Repository = 'zato-test-kube-pod'
    Pod_Image_Tag_Length = 12

    # The path at which each worker node holds the local volumes of the Zato pods
    Volume_Dir = '/zato-ha-data'

    # The manifests of the suites
    Manifest_Dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifests')
    Cluster_Manifest = 'kind-cluster.yaml'

    # The marker of a placeholder that a manifest still contains after it was rendered
    Placeholder_Marker = '${'

    # How long the cluster may take to be created and its nodes to be ready, in seconds
    Create_Timeout = '300s'

    # How long kubectl waits for an object, in seconds
    Wait_Timeout = '300s'

    # The address that kubectl proxy listens on, and what it prints once it does
    Proxy_Host = '127.0.0.1'
    Proxy_Ready_Pattern = re.compile(r'Starting to serve on [\d.]+:(\d+)')

    # How long one request through kubectl proxy may take, in seconds
    Proxy_Request_Timeout = 5

    # How long kubectl proxy may take to start, and how often its output is read meanwhile, in seconds
    Proxy_Start_Timeout = 30
    Poll_Interval = 0.2

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class KubeCluster:
    """ The cluster of one run, whose names are derived from the name that the run reserves, so that runs
    in parallel processes use clusters of their own.
    """
    reservation: 'NameReservation'
    name: 'str'
    context: 'str'
    control_plane: 'str'
    zones: 'strstrdict'
    runtime_dir: 'str'

# The cluster of the run of this process, whose names reserve_cluster sets
cluster = KubeCluster()

# ################################################################################################################################
# ################################################################################################################################

def reserve_cluster() -> 'None':
    """ Reserves the name of the run and derives from it the names of its cluster, its nodes and its runtime directory.
    """
    reservation = reserve_name(ModuleCtx.Name_Prefix)
    name = reservation.name

    cluster.reservation = reservation
    cluster.name = name
    cluster.context = ModuleCtx.Context_Prefix + name
    cluster.control_plane = name + ModuleCtx.Control_Plane_Suffix
    cluster.runtime_dir = os.path.join(ModuleCtx.Runtime_Base_Dir, name)

    # kind names the worker nodes after the cluster, in the order in which its configuration lists them.
    cluster.zones = {}
    for suffix, zone in ModuleCtx.Worker_Zones.items():
        cluster.zones[name + suffix] = zone

    logger.info('Cluster name reserved -> %s', name)

# ################################################################################################################################

def _is_stale_name(name:'str') -> 'bool':
    """ Returns whether a name is one that a run reserved and whose process no longer runs.
    """
    if not is_reserved_name(name, ModuleCtx.Name_Prefix):
        return False

    out = not is_name_live(name)
    return out

# ################################################################################################################################

def remove_stale_clusters() -> 'None':
    """ Deletes the clusters and the runtime directories of earlier runs whose processes no longer run.
    A cluster or a directory of another name, or of a run in progress, is never touched.
    """
    # The clusters of earlier runs are found by their names ..
    result = run(['kind', 'get', 'clusters'])
    cluster_names = result.stdout.split()

    stale:'strset' = set()

    for name in cluster_names:
        if _is_stale_name(name):
            stale.add(name)

    # .. as are the runtime directories of runs whose clusters are already deleted ..
    for name in os.listdir(ModuleCtx.Runtime_Base_Dir):
        if _is_stale_name(name):
            stale.add(name)

    # .. and each is removed together with the reservation that its run left.
    for name in sorted(stale):
        if name in cluster_names:
            _ = run(['kind', 'delete', 'cluster', '--name', name])
            logger.info('Stale cluster deleted -> %s', name)

        shutil.rmtree(os.path.join(ModuleCtx.Runtime_Base_Dir, name), ignore_errors=True)
        forget_name(name)

# ################################################################################################################################
# ################################################################################################################################

def run(command:'strlist', input_text:'str'='', check:'bool'=True) -> 'subprocess.CompletedProcess[str]':
    """ Runs one command and returns its result.
    """
    out = subprocess.run(command, input=input_text, capture_output=True, text=True, check=False)

    if check:
        if out.returncode != 0:
            raise Exception(f'Command {command} failed with {out.returncode}: {out.stderr.strip()}')

    return out

# ################################################################################################################################

def kubectl(*args:'str', input_text:'str'='', check:'bool'=True) -> 'subprocess.CompletedProcess[str]':
    """ Runs one kubectl command against the cluster of the suites.
    """
    out = run(['kubectl', '--context', cluster.context, *args], input_text, check)
    return out

# ################################################################################################################################

def kubectl_json(*args:'str') -> 'any_':
    result = kubectl(*args, '-o', 'json')

    out = json.loads(result.stdout)
    return out

# ################################################################################################################################

def render_manifest(file_name:'str', placeholders:'strstrdict') -> 'str':
    """ Returns a manifest with its placeholders replaced. The variables of Kubernetes, such as $(POD_NAME),
    remain as they are.
    """
    path = os.path.join(ModuleCtx.Manifest_Dir, file_name)

    with open(path) as manifest_file:
        template = Template(manifest_file.read())

    out = template.safe_substitute(placeholders)

    if ModuleCtx.Placeholder_Marker in out:
        raise Exception(f'Placeholders not replaced in {file_name}')

    return out

# ################################################################################################################################

def apply_manifest(file_name:'str', placeholders:'strstrdict') -> 'None':
    manifest = render_manifest(file_name, placeholders)
    _ = kubectl('apply', '-f', '-', input_text=manifest)

# ################################################################################################################################

def delete_manifest(file_name:'str', placeholders:'strstrdict') -> 'None':
    """ Deletes the objects of a manifest and waits until they are gone.
    """
    manifest = render_manifest(file_name, placeholders)
    _ = kubectl('delete', '--ignore-not-found', '--wait=true', f'--timeout={ModuleCtx.Wait_Timeout}', '-f', '-',
        input_text=manifest)

# ################################################################################################################################
# ################################################################################################################################

def prepare_runtime_dir() -> 'str':
    """ Reserves the names of the run, removes the clusters and the directories of earlier runs that no longer run,
    and creates the runtime directory of the run.
    """
    reserve_cluster()
    remove_stale_clusters()

    os.makedirs(cluster.runtime_dir)

    out = cluster.runtime_dir
    return out

# ################################################################################################################################

def get_zone_volume_dir(run_dir:'str', zone:'str') -> 'str':
    """ Returns the host directory that the worker node of a zone holds the local volumes of the Zato pods in.
    """
    out = os.path.join(run_dir, 'workers', zone)
    return out

# ################################################################################################################################

def create_cluster(run_dir:'str', repository_dir:'str') -> 'None':
    """ Creates the cluster, with the repository, the run directory and the local volumes of each zone mounted
    into its worker nodes, and waits until every node is ready.
    """
    placeholders = {
        'cluster_name': cluster.name,
        'repository_dir': repository_dir,
        'run_dir': run_dir,
        'volume_dir': ModuleCtx.Volume_Dir,
    }

    for zone in cluster.zones.values():
        key = zone.replace('-', '_')
        placeholders[f'volume_{key}'] = get_zone_volume_dir(run_dir, zone)

    config = render_manifest(ModuleCtx.Cluster_Manifest, placeholders)
    config_path = os.path.join(run_dir, ModuleCtx.Cluster_Manifest)

    with open(config_path, 'w') as config_file:
        _ = config_file.write(config)

    _ = run(['kind', 'create', 'cluster', '--name', cluster.name, '--config', config_path,
        '--wait', ModuleCtx.Create_Timeout])

    _ = kubectl('create', 'namespace', ModuleCtx.Namespace)

    logger.info('Cluster %s created', cluster.name)

# ################################################################################################################################

def delete_cluster() -> 'None':
    """ Deletes the cluster of the run. Its runtime directory remains, with the logs of the run, until a later run
    finds the reservation of the name released.
    """
    _ = run(['kind', 'delete', 'cluster', '--name', cluster.name], check=False)

# ################################################################################################################################

def load_image(image:'str', node_names:'strlist') -> 'None':
    """ Loads an image of the host into the given nodes, pulling it first if the host does not have it.
    """
    result = docker('image', 'inspect', image, check=False)

    if result.returncode != 0:
        _ = docker('pull', image)

    # The containerd image store of the host holds the index of every platform of a pulled image but the content
    # of its own platform alone, which an import of all platforms in the nodes refuses, so only that platform is loaded.
    platform = docker('image', 'inspect', '-f', '{{.Os}}/{{.Architecture}}', image).stdout.strip()

    with TemporaryDirectory() as directory:
        archive_path = os.path.join(directory, 'image.tar')
        _ = docker('save', '--platform', platform, '-o', archive_path, image)

        _ = run(['kind', 'load', 'image-archive', archive_path, '--name', cluster.name,
            '--nodes', ','.join(node_names)])

# ################################################################################################################################

def load_images(images:'strlistdict') -> 'None':
    """ Loads each image into its nodes, all images at the same time.
    """
    with ThreadPoolExecutor(max_workers=len(images)) as executor:
        futures = [executor.submit(load_image, image, node_names) for image, node_names in images.items()]

        for future in futures:
            future.result()

# ################################################################################################################################

def build_pod_image() -> 'str':
    """ Builds the runtime image of the Zato pods unless the host has it already and returns its name, whose tag
    follows the content of its Dockerfile.
    """
    dockerfile_path = os.path.join(ModuleCtx.Pod_Image_Dir, 'Dockerfile')

    with open(dockerfile_path, 'rb') as dockerfile:
        digest = hashlib.sha256(dockerfile.read()).hexdigest()

    out = f'{ModuleCtx.Pod_Image_Repository}:{digest[:ModuleCtx.Pod_Image_Tag_Length]}'

    result = docker('image', 'inspect', out, check=False)

    if result.returncode != 0:
        _ = docker('build', '-t', out, ModuleCtx.Pod_Image_Dir)
        logger.info('Built the pod image %s', out)

    return out

# ################################################################################################################################

def get_zato_node_names() -> 'strlist':
    """ Returns the worker nodes of the zones that the Zato pods run in.
    """
    out:'strlist' = []

    for node_name, zone in cluster.zones.items():
        if zone in ModuleCtx.Zato_Zones:
            out.append(node_name)

    return out

# ################################################################################################################################

def get_node_ip(node_name:'str') -> 'str':
    """ Returns the address of a node on the network of kind.
    """
    result = docker('inspect', '-f', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', node_name)

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def _get_kind_ipv4_config() -> 'strstrdict':
    """ Returns the IPv4 subnet of the network of kind with its gateway.
    """
    network = json.loads(docker('network', 'inspect', 'kind').stdout)[0]

    for config in network['IPAM']['Config']:
        gateway = config['Gateway']

        # The network has an IPv6 subnet as well, which the services of the host do not listen on.
        if ':' not in gateway:
            return config

    raise Exception('No IPv4 gateway on the network of kind')

# ################################################################################################################################

def get_kind_gateway() -> 'str':
    """ Returns the address of the host on the network of kind, which the pods reach it at.
    """
    config = _get_kind_ipv4_config()

    out = config['Gateway']
    return out

# ################################################################################################################################

def get_kind_subnet() -> 'str':
    """ Returns the IPv4 subnet of the network of kind, from which the nodes and their pods reach the host.
    """
    config = _get_kind_ipv4_config()

    out = config['Subnet']
    return out

# ################################################################################################################################

def get_pod_node(pod_name:'str') -> 'str':
    """ Returns the node that a pod is scheduled on, or an empty string if it is not scheduled.
    """
    result = kubectl('get', 'pod', pod_name, '-n', ModuleCtx.Namespace, '-o', 'jsonpath={.spec.nodeName}', check=False)

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def get_pod_uid(pod_name:'str') -> 'str':
    result = kubectl('get', 'pod', pod_name, '-n', ModuleCtx.Namespace, '-o', 'jsonpath={.metadata.uid}')

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def get_node_pod_cidr(node_name:'str') -> 'str':
    result = kubectl('get', 'node', node_name, '-o', 'jsonpath={.spec.podCIDR}')

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def wait_for_rollout(kind:'str', name:'str') -> 'None':
    _ = kubectl('rollout', 'status', f'{kind}/{name}', '-n', ModuleCtx.Namespace, f'--timeout={ModuleCtx.Wait_Timeout}')

# ################################################################################################################################

def save_pod_logs(pod_name:'str', directory:'str') -> 'None':
    """ Copies the output of the current and the previous container of a pod into a file.
    """
    path = os.path.join(directory, f'{pod_name}.log')

    with open(path, 'a') as log_file:
        for options in (['--previous'], []):
            result = kubectl('logs', pod_name, '-n', ModuleCtx.Namespace, '--all-containers', *options, check=False)
            _ = log_file.write(result.stdout)
            _ = log_file.write(result.stderr)

# ################################################################################################################################
# ################################################################################################################################

class KubeProxy:
    """ kubectl proxy on a local port, through which the test process reads the API server without credentials.
    """

    def __init__(self) -> 'None':
        self.base_url = ''
        self._process:'subprocess.Popen[str] | None' = None

    def start(self) -> 'None':
        process = subprocess.Popen(
            ['kubectl', '--context', cluster.context, 'proxy', f'--address={ModuleCtx.Proxy_Host}', '--port=0'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        self._process = process

        assert process.stdout is not None
        deadline = time.monotonic() + ModuleCtx.Proxy_Start_Timeout

        while time.monotonic() < deadline:
            line = process.stdout.readline()
            match = ModuleCtx.Proxy_Ready_Pattern.search(line)

            if match:
                self.base_url = f'http://{ModuleCtx.Proxy_Host}:{match.group(1)}'
                return

            time.sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'kubectl proxy not started after {ModuleCtx.Proxy_Start_Timeout}s')

    def stop(self) -> 'None':
        if self._process is not None:
            self._process.terminate()
            _ = self._process.wait()

    def get(self, path:'str') -> 'any_':
        request = Request(f'{self.base_url}{path}', method='GET')

        with urlopen(request, timeout=ModuleCtx.Proxy_Request_Timeout) as response:
            out = json.loads(response.read())

        return out

# ################################################################################################################################
# ################################################################################################################################
