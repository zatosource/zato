# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The containers around an active-standby pair - one Docker bridge network with a fixed address per container,
# one kind cluster whose API server is the referee, attached to that network at a fixed address, and HAProxy,
# which routes to the node whose role endpoint answers 200.

# stdlib
import base64
import json
import logging
import os
import shutil
import ssl
import subprocess
import time
from http.client import NOT_FOUND
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.topology')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Where every run keeps its data, removed at the beginning and at the end of each run
    Runtime_Dir = '/tmp/zato-ha-test'

    # The network of the run and the addresses on it
    Network_Name   = 'zato-ha-test'
    Subnet         = '10.231.77.0/24'
    Gateway        = '10.231.77.1'
    API_Server_IP  = '10.231.77.10'
    HAProxy_IP     = '10.231.77.11'

    # The pinned image of the load balancer
    HAProxy_Image = 'haproxy:3.2.4'

    # The image with iptables and tc that joins the network namespace of a container
    Net_Image      = 'zato-pubsub-test-net:1'
    Net_Dockerfile = 'FROM alpine:latest\nRUN apk add --no-cache iptables iproute2-tc iproute2-minimal\n'

    # The name of the container of the load balancer
    HAProxy_Container = 'zato-ha-test-haproxy'

    # The kind cluster of the referee, the container of its control-plane node and the port of its API server
    Cluster_Name            = 'zato-ha-test'
    Control_Plane_Container = 'zato-ha-test-control-plane'
    API_Server_Port         = 6443

    # The namespace of the leases and of the pods of the nodes, and the name of the lease of the record
    Namespace  = 'zato-ha'
    Lease_Name = 'zato-ha'

    # The service account of the nodes and the one that the test process uses
    Node_Service_Account  = 'zato-ha'
    Admin_Service_Account = 'zato-ha-test-admin'

    # The directory of the service account credentials in a pod
    Service_Account_Mount = '/var/run/secrets/kubernetes.io/serviceaccount'

    # The image of the pods of the nodes, which never leave the Pending phase, and the label that no node has
    Pod_Image          = 'registry.k8s.io/pause:3.10'
    Pod_Placement_Key  = 'zato.io/test-placement'
    Pod_Placement_None = 'none'

    # The annotation of the lease that holds the referee record
    Record_Annotation = 'zato.io/ha-record'

    # The API paths of the leases
    Leases_Path = f'/apis/coordination.k8s.io/v1/namespaces/{Namespace}/leases'

    # How long the cluster may take to serve requests for leases, in seconds
    API_Server_Ready_Timeout = 180

    # How many consecutive answers establish that the API server serves leases
    API_Server_Ready_Answers = 5

    # How long one request to the API server may take, in seconds
    API_Server_Request_Timeout = 5

    # How often the API server is asked whether it is ready, in seconds
    Poll_Interval = 0.5

    # The port that HAProxy exposes to the test process
    HAProxy_Port = 11223

    # How often HAProxy checks the role endpoint of each node, in milliseconds
    HAProxy_Check_Interval_Ms = 1000

# ################################################################################################################################
# ################################################################################################################################

def docker(*args:'str', check:'bool'=True) -> 'subprocess.CompletedProcess[str]':
    """ Runs one docker command and returns its result.
    """
    command = ['docker', *args]

    out = subprocess.run(command, capture_output=True, text=True, check=False)

    if check:
        if out.returncode != 0:
            raise Exception(f'Command {command} failed with {out.returncode}: {out.stderr.strip()}')

    return out

# ################################################################################################################################

def remove_container(name:'str') -> 'None':
    _ = docker('rm', '-f', name, check=False)

# ################################################################################################################################

def save_container_logs(name:'str', directory:'str') -> 'None':
    """ Copies the output of a container into a file, so that it outlives the container.
    """
    result = docker('logs', name, check=False)
    path = os.path.join(directory, f'{name}.log')

    with open(path, 'a') as log_file:
        _ = log_file.write(result.stdout)
        _ = log_file.write(result.stderr)

# ################################################################################################################################

def ensure_image(name:'str', dockerfile:'str') -> 'None':
    """ Builds a tool image from its Dockerfile unless it exists already.
    """
    result = docker('image', 'inspect', name, check=False)

    if result.returncode != 0:
        _ = subprocess.run(['docker', 'build', '-t', name, '-'], input=dockerfile.encode('utf8'), capture_output=True,
            check=True)

# ################################################################################################################################

def ensure_net_image() -> 'None':
    """ Builds the image with iptables and tc unless it exists already.
    """
    ensure_image(ModuleCtx.Net_Image, ModuleCtx.Net_Dockerfile)

# ################################################################################################################################

def run_in_network_namespace(container_name:'str', script:'str') -> 'str':
    """ Runs a shell script with iptables and tc in the network namespace of a container.
    """
    ensure_net_image()

    result = docker('run', '--rm', '--net', f'container:{container_name}', '--cap-add', 'NET_ADMIN',
        ModuleCtx.Net_Image, 'sh', '-c', script)

    out = result.stdout
    return out

# ################################################################################################################################
# ################################################################################################################################

def prepare_runtime_dir() -> 'str':
    """ Removes what an earlier run left in the runtime directory and creates it again.
    """
    shutil.rmtree(ModuleCtx.Runtime_Dir, ignore_errors=True)
    os.makedirs(ModuleCtx.Runtime_Dir)

    out = ModuleCtx.Runtime_Dir
    return out

# ################################################################################################################################

def create_network() -> 'None':
    """ Creates the bridge network of the run, removing one that an earlier run left behind.
    """
    remove_network()
    _ = docker('network', 'create', '--driver', 'bridge', '--subnet', ModuleCtx.Subnet, '--gateway', ModuleCtx.Gateway,
        ModuleCtx.Network_Name)

# ################################################################################################################################

def remove_network() -> 'None':
    """ Removes the bridge network of the run together with each container that an interrupted run left attached to it.
    """
    result = docker('network', 'inspect', '--format', '{{range .Containers}}{{.Name}} {{end}}', ModuleCtx.Network_Name,
        check=False)

    for name in result.stdout.split():
        remove_container(name)

    _ = docker('network', 'rm', ModuleCtx.Network_Name, check=False)

# ################################################################################################################################
# ################################################################################################################################

class Referee:
    """ The referee of a pair as the suites act on it - the address that a partition cuts a node off from,
    the containers whose output the logs of a test keep, and its record.
    """
    ip: 'str'
    container_names: 'strlist'

    def read_record(self) -> 'anydict | None':
        raise NotImplementedError()

    def stop(self) -> 'None':
        raise NotImplementedError()

    def resume(self) -> 'None':
        raise NotImplementedError()

    def remove(self) -> 'None':
        raise NotImplementedError()

    def recreate_without_data(self) -> 'None':
        raise NotImplementedError()

    def clear(self) -> 'None':
        """ Removes what the pair of an earlier test left in the referee, which a referee that outlives one test needs.
        """
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

def kubectl(*args:'str', input_text:'str'='') -> 'subprocess.CompletedProcess[str]':
    """ Runs one kubectl command against the cluster of the referee and returns its result.
    """
    command = ['kubectl', '--context', f'kind-{ModuleCtx.Cluster_Name}', *args]

    out = subprocess.run(command, input=input_text, capture_output=True, text=True, check=False)

    if out.returncode != 0:
        raise Exception(f'Command {command} failed with {out.returncode}: {out.stderr.strip()}')

    return out

# ################################################################################################################################

def _kind_config() -> 'str':
    """ Returns the configuration of the cluster, whose API server certificate names its address on the network of the run.
    """
    lines = [
        'kind: Cluster',
        'apiVersion: kind.x-k8s.io/v1alpha4',
        'kubeadmConfigPatches:',
        '- |',
        '  kind: ClusterConfiguration',
        '  apiServer:',
        '    certSANs:',
        f'    - "{ModuleCtx.API_Server_IP}"',
    ]

    out = '\n'.join(lines) + '\n'
    return out

# ################################################################################################################################

def _token_secret(service_account:'str') -> 'anydict':
    """ Returns a secret that the token controller fills in with a token of the service account that does not expire.
    """
    out = {
        'apiVersion': 'v1',
        'kind': 'Secret',
        'type': 'kubernetes.io/service-account-token',
        'metadata': {
            'name': f'{service_account}-token',
            'namespace': ModuleCtx.Namespace,
            'annotations': {'kubernetes.io/service-account.name': service_account},
        },
    }

    return out

# ################################################################################################################################

def _pending_pod(node_name:'str') -> 'anydict':
    """ Returns the pod of a node, which no cluster node may run, so that its labels are the only part of it in use.
    """
    out = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {'name': node_name, 'namespace': ModuleCtx.Namespace},
        'spec': {
            'automountServiceAccountToken': False,
            'nodeSelector': {ModuleCtx.Pod_Placement_Key: ModuleCtx.Pod_Placement_None},
            'containers': [{'name': 'node', 'image': ModuleCtx.Pod_Image}],
        },
    }

    return out

# ################################################################################################################################

def _manifest(node_names:'strlist') -> 'str':
    """ Returns the namespace, the permissions of the nodes and of the test process, their tokens and the pods
    of the nodes, as one list that kubectl applies.
    """
    namespace = ModuleCtx.Namespace
    node_account = ModuleCtx.Node_Service_Account
    admin_account = ModuleCtx.Admin_Service_Account

    items:'anylist' = [
        {'apiVersion': 'v1', 'kind': 'Namespace', 'metadata': {'name': namespace}},
        {'apiVersion': 'v1', 'kind': 'ServiceAccount', 'metadata': {'name': node_account, 'namespace': namespace}},
        {
            'apiVersion': 'rbac.authorization.k8s.io/v1',
            'kind': 'Role',
            'metadata': {'name': node_account, 'namespace': namespace},
            'rules': [
                {'apiGroups': ['coordination.k8s.io'], 'resources': ['leases'], 'verbs': ['get', 'list', 'create', 'patch']},
                {'apiGroups': [''], 'resources': ['pods'], 'verbs': ['get', 'patch']},
            ],
        },
        {
            'apiVersion': 'rbac.authorization.k8s.io/v1',
            'kind': 'RoleBinding',
            'metadata': {'name': node_account, 'namespace': namespace},
            'roleRef': {'apiGroup': 'rbac.authorization.k8s.io', 'kind': 'Role', 'name': node_account},
            'subjects': [{'kind': 'ServiceAccount', 'name': node_account, 'namespace': namespace}],
        },
        _token_secret(node_account),
        {'apiVersion': 'v1', 'kind': 'ServiceAccount', 'metadata': {'name': admin_account, 'namespace': namespace}},
        {
            'apiVersion': 'rbac.authorization.k8s.io/v1',
            'kind': 'ClusterRoleBinding',
            'metadata': {'name': admin_account},
            'roleRef': {'apiGroup': 'rbac.authorization.k8s.io', 'kind': 'ClusterRole', 'name': 'cluster-admin'},
            'subjects': [{'kind': 'ServiceAccount', 'name': admin_account, 'namespace': namespace}],
        },
        _token_secret(admin_account),
    ]

    for node_name in node_names:
        pod = _pending_pod(node_name)
        items.append(pod)

    manifest = {'apiVersion': 'v1', 'kind': 'List', 'items': items}

    out = json.dumps(manifest)
    return out

# ################################################################################################################################
# ################################################################################################################################

class Lease(Referee):
    """ The referee record in a lease of a kind cluster of one control-plane node, whose container is attached
    to the network of the run, so that the faults of the suites cut the nodes off from the API server.
    """

    def __init__(self, run_dir:'str') -> 'None':
        self.ip = ModuleCtx.API_Server_IP
        self.container_names = []
        self.directory = os.path.join(run_dir, 'kubernetes')
        self.service_account_dir = os.path.join(self.directory, 'serviceaccount')
        self.address = f'https://{ModuleCtx.API_Server_IP}:{ModuleCtx.API_Server_Port}'
        self.admin_token = ''
        self.ssl_context = ssl.create_default_context()

# ################################################################################################################################

    def create_cluster(self, node_names:'strlist') -> 'None':
        """ Creates the cluster, removing one that an earlier run left behind, attaches it to the network of the run
        and creates the namespace, the permissions and the pods of the nodes.
        """
        self.delete_cluster()
        os.makedirs(self.service_account_dir, exist_ok=True)

        config_path = os.path.join(self.directory, 'kind-cluster.yaml')
        config = _kind_config()

        with open(config_path, 'w') as config_file:
            _ = config_file.write(config)

        # The cluster is created on the network of kind and attached to the network of the run afterwards ..
        _ = subprocess.run(['kind', 'create', 'cluster', '--name', ModuleCtx.Cluster_Name, '--config', config_path],
            capture_output=True, check=True)

        _ = docker('network', 'connect', '--ip', ModuleCtx.API_Server_IP, ModuleCtx.Network_Name,
            ModuleCtx.Control_Plane_Container)

        # .. the nodes and the test process verify the API server against the CA of the cluster ..
        ca_data = kubectl('config', 'view', '--raw', '--minify', '--flatten',
            '-o', 'jsonpath={.clusters[0].cluster.certificate-authority-data}').stdout
        ca_pem = base64.b64decode(ca_data)
        ca_path = os.path.join(self.service_account_dir, 'ca.crt')

        with open(ca_path, 'wb') as ca_file:
            _ = ca_file.write(ca_pem)

        self.ssl_context = ssl.create_default_context(cafile=ca_path)

        # .. the objects are applied again until the service account controller has created what the pods need ..
        self._apply(_manifest(node_names))

        # .. and each process authenticates with a token of its own service account.
        node_token = self._read_token(ModuleCtx.Node_Service_Account)
        self.admin_token = self._read_token(ModuleCtx.Admin_Service_Account)

        for name, value in (('token', node_token), ('namespace', ModuleCtx.Namespace)):
            path = os.path.join(self.service_account_dir, name)
            with open(path, 'w') as credential_file:
                _ = credential_file.write(value)

        self.wait_until_ready()
        logger.info('API server ready at %s', self.address)

# ################################################################################################################################

    def _apply(self, manifest:'str') -> 'None':
        """ Applies the manifest, again after each refusal, until the cluster accepts every object of it.
        """
        deadline = time.monotonic() + ModuleCtx.API_Server_Ready_Timeout

        while True:
            try:
                _ = kubectl('apply', '-f', '-', input_text=manifest)
                break
            except Exception:
                if time.monotonic() > deadline:
                    raise
                time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def _read_token(self, service_account:'str') -> 'str':
        """ Waits until the token controller fills in the token of the service account and returns it.
        """
        deadline = time.monotonic() + ModuleCtx.API_Server_Ready_Timeout

        while True:
            token = kubectl('--namespace', ModuleCtx.Namespace, 'get', 'secret', f'{service_account}-token',
                '-o', 'jsonpath={.data.token}').stdout

            if token:
                break

            if time.monotonic() > deadline:
                raise Exception(f'No token of {service_account} after {ModuleCtx.API_Server_Ready_Timeout}s')

            time.sleep(ModuleCtx.Poll_Interval)

        out = base64.b64decode(token).decode('utf8')
        return out

# ################################################################################################################################

    def delete_cluster(self) -> 'None':
        _ = subprocess.run(['kind', 'delete', 'cluster', '--name', ModuleCtx.Cluster_Name], capture_output=True, check=False)

# ################################################################################################################################

    def node_env(self) -> 'strstrdict':
        """ Returns the variables through which a node in a container reaches the API server, as a node in a pod does.
        """
        out = {
            'KUBERNETES_SERVICE_HOST': ModuleCtx.API_Server_IP,
            'KUBERNETES_SERVICE_PORT': str(ModuleCtx.API_Server_Port),
            'Zato_HA_Lease_Name': ModuleCtx.Lease_Name,
        }

        return out

# ################################################################################################################################

    def request(self, method:'str', path:'str') -> 'any_':
        """ Sends one request with the token of the test process and returns the decoded answer.
        """
        url = f'{self.address}{path}'
        request = Request(url, method=method)
        request.add_header('Authorization', f'Bearer {self.admin_token}')

        with urlopen(request, timeout=ModuleCtx.API_Server_Request_Timeout, context=self.ssl_context) as response:
            answer = response.read()

        out = json.loads(answer)
        return out

# ################################################################################################################################

    def wait_until_ready(self) -> 'None':
        """ Waits for consecutive answers to a list of leases, since the API server answers before every controller runs.
        """
        deadline = time.monotonic() + ModuleCtx.API_Server_Ready_Timeout
        answers = 0

        while answers < ModuleCtx.API_Server_Ready_Answers:
            try:
                _ = self.request('GET', ModuleCtx.Leases_Path)
                answers += 1
            except (HTTPError, URLError, OSError) as e:
                answers = 0
                if time.monotonic() > deadline:
                    raise Exception(f'API server not ready after {ModuleCtx.API_Server_Ready_Timeout}s -> {e}') from e

            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Freezes the control-plane node, which stops the API server and etcd from answering.
        """
        _ = docker('pause', ModuleCtx.Control_Plane_Container)

# ################################################################################################################################

    def resume(self) -> 'None':
        _ = docker('unpause', ModuleCtx.Control_Plane_Container)
        self.wait_until_ready()

# ################################################################################################################################

    def recreate_without_data(self) -> 'None':
        """ Deletes every lease of the pair while the pair runs, as an API server restored without its data.
        """
        _ = self.request('DELETE', ModuleCtx.Leases_Path)

# ################################################################################################################################

    def remove(self) -> 'None':
        self.clear()

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Unfreezes a control-plane node that a failed test left frozen and deletes the leases of the pair.
        """
        result = docker('inspect', '--format', '{{.State.Paused}}', ModuleCtx.Control_Plane_Container)

        if result.stdout.strip() == 'true':
            self.resume()

        _ = self.request('DELETE', ModuleCtx.Leases_Path)

# ################################################################################################################################

    def read_record(self) -> 'anydict | None':
        """ Returns the referee record with its version, or None if the pair has not written one yet.
        """
        try:
            lease = self.request('GET', f'{ModuleCtx.Leases_Path}/{ModuleCtx.Lease_Name}')
        except HTTPError as e:
            if e.code == NOT_FOUND:
                return None
            raise

        metadata = lease['metadata']
        value = metadata['annotations'][ModuleCtx.Record_Annotation]

        out = json.loads(value)
        out['version'] = metadata['resourceVersion']

        return out

# ################################################################################################################################
# ################################################################################################################################

class HAProxy:
    """ HAProxy in front of the HTTP port of both nodes, routing to the node whose role endpoint answers 200.
    """

    def __init__(self, run_dir:'str', backends:'strlist', server_port:'int', role_port:'int') -> 'None':
        self.directory = os.path.join(run_dir, 'haproxy')
        self.backends = backends
        self.server_port = server_port
        self.role_port = role_port
        self.base_url = f'http://{ModuleCtx.HAProxy_IP}:{ModuleCtx.HAProxy_Port}'

# ################################################################################################################################

    def _write_config(self) -> 'str':
        os.makedirs(self.directory, exist_ok=True)

        lines = [
            'global',
            '    log stdout format raw local0',
            '',
            'defaults',
            '    mode http',
            '    log global',
            '    option httplog',
            '    timeout connect 2s',
            '    timeout client 60s',
            '    timeout server 60s',
            '',
            'frontend zato',
            f'    bind :{ModuleCtx.HAProxy_Port}',
            '    default_backend zato_servers',
            '',
            'backend zato_servers',
            '    option httpchk GET /zato/ha/role',
            '    http-check expect status 200',
            f'    default-server inter {ModuleCtx.HAProxy_Check_Interval_Ms}ms fall 1 rise 1',
        ]

        for index, backend in enumerate(self.backends):
            lines.append(f'    server node{index} {backend}:{self.server_port} check port {self.role_port}')

        config = '\n'.join(lines) + '\n'
        out = os.path.join(self.directory, 'haproxy.cfg')

        with open(out, 'w') as config_file:
            _ = config_file.write(config)

        return out

# ################################################################################################################################

    def start(self) -> 'None':
        remove_container(ModuleCtx.HAProxy_Container)
        config_path = self._write_config()

        _ = docker(
            'run', '-d',
            '--name', ModuleCtx.HAProxy_Container,
            '--network', ModuleCtx.Network_Name,
            '--ip', ModuleCtx.HAProxy_IP,
            '-v', f'{config_path}:/usr/local/etc/haproxy/haproxy.cfg:ro',
            ModuleCtx.HAProxy_Image,
        )

# ################################################################################################################################

    def restart(self) -> 'None':
        _ = docker('restart', '-t', '1', ModuleCtx.HAProxy_Container)

# ################################################################################################################################

    def remove(self) -> 'None':
        remove_container(ModuleCtx.HAProxy_Container)

# ################################################################################################################################
# ################################################################################################################################
