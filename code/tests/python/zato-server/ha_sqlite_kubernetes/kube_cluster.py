# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The kind cluster of the Kubernetes suites - one control plane node and three worker nodes, one per zone, each a Docker
# container with the repository and the run directory mounted at their own paths - and the commands that act on it.

# stdlib
import json
import logging
import os
import re
import shutil
import subprocess
import time
from string import Template
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen

# Zato
from topology import docker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul_kubernetes.cluster')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Where every run keeps its data, removed at the beginning and at the end of each run
    Runtime_Dir = '/tmp/zato-ha-kube-test'

    # The cluster, its kubectl context and the namespace of the suites
    Cluster_Name = 'zato-ha'
    Context = 'kind-zato-ha'
    Namespace = 'zato-ha'

    # The worker nodes with their zones, as kind names them
    Control_Plane = 'zato-ha-control-plane'
    Zones = {
        'zato-ha-worker':  'zone-a',
        'zato-ha-worker2': 'zone-b',
        'zato-ha-worker3': 'zone-c',
    }

    # The zones of the Zato pods, whose worker nodes receive the Zato image
    Zato_Zones = ['zone-a', 'zone-b']

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
    out = run(['kubectl', '--context', ModuleCtx.Context, *args], input_text, check)
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
    """ Removes what an earlier run left in the runtime directory, including its cluster, and creates the directory again.
    """
    delete_cluster()

    shutil.rmtree(ModuleCtx.Runtime_Dir, ignore_errors=True)
    os.makedirs(ModuleCtx.Runtime_Dir)

    out = ModuleCtx.Runtime_Dir
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
        'cluster_name': ModuleCtx.Cluster_Name,
        'repository_dir': repository_dir,
        'run_dir': run_dir,
        'volume_dir': ModuleCtx.Volume_Dir,
    }

    for zone in ModuleCtx.Zones.values():
        key = zone.replace('-', '_')
        placeholders[f'volume_{key}'] = get_zone_volume_dir(run_dir, zone)

    config = render_manifest(ModuleCtx.Cluster_Manifest, placeholders)
    config_path = os.path.join(run_dir, ModuleCtx.Cluster_Manifest)

    with open(config_path, 'w') as config_file:
        _ = config_file.write(config)

    # A cluster that an interrupted run left behind is deleted before the new one is created.
    delete_cluster()

    _ = run(['kind', 'create', 'cluster', '--name', ModuleCtx.Cluster_Name, '--config', config_path,
        '--wait', ModuleCtx.Create_Timeout])

    _ = kubectl('create', 'namespace', ModuleCtx.Namespace)

    logger.info('Cluster %s created', ModuleCtx.Cluster_Name)

# ################################################################################################################################

def delete_cluster() -> 'None':
    _ = run(['kind', 'delete', 'cluster', '--name', ModuleCtx.Cluster_Name], check=False)

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

        _ = run(['kind', 'load', 'image-archive', archive_path, '--name', ModuleCtx.Cluster_Name,
            '--nodes', ','.join(node_names)])

# ################################################################################################################################

def get_zato_node_names() -> 'strlist':
    """ Returns the worker nodes of the zones that the Zato pods run in.
    """
    out:'strlist' = []

    for node_name, zone in ModuleCtx.Zones.items():
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

def get_kind_gateway() -> 'str':
    """ Returns the address of the host on the network of kind, which the pods reach it at.
    """
    network = json.loads(docker('network', 'inspect', 'kind').stdout)[0]

    for config in network['IPAM']['Config']:
        gateway = config['Gateway']

        # The network has an IPv6 subnet as well, which the receivers do not listen on.
        if ':' not in gateway:
            return gateway

    raise Exception('No IPv4 gateway on the network of kind')

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
            ['kubectl', '--context', ModuleCtx.Context, 'proxy', f'--address={ModuleCtx.Proxy_Host}', '--port=0'],
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
