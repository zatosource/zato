# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The session and the pair of the Kubernetes suites. A session creates the cluster, loads the images, creates
# the quickstart environment that both pods begin from and starts Consul. Each test replaces the pair with
# a new StatefulSet whose pods begin from that environment, under a referee key with no record.

# stdlib
import json
import logging
import os
import shutil
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

# Zato
from ha_authority import Authority
from ha_env import create_quickstart_environment, start_receivers, HASession
from kube_cluster import apply_manifest, create_cluster, delete_cluster, get_kind_gateway, get_node_ip, get_pod_node, \
    get_zato_node_names, get_zone_volume_dir, KubeProxy, kubectl, load_image, ModuleCtx as ClusterCtx, prepare_runtime_dir, \
    save_pod_logs, wait_for_rollout
from kube_endpoints import EndpointWatcher
from nodes import ModuleCtx as NodesCtx, Node, Timers
from topology import Consul, ModuleCtx as TopologyCtx
from zato.common.test.pubsub_database import PubSubDatabase, PubSubDBMode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul_kubernetes.env')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The pods of the pair
    Pod_Names = ['zato-ha-0', 'zato-ha-1']
    StatefulSet_Name = 'zato-ha'
    Pod_Selector = 'app=zato-ha'

    # The node ports through which the test process reaches the Service, each pod and Consul
    Service_Node_Port = 30170
    Pod_Node_Ports = {
        'zato-ha-0': (30180, 30181),
        'zato-ha-1': (30190, 30191),
    }
    Consul_Node_Port = 30501

    # The manifests of Consul and of the pair
    Consul_Manifest = 'consul.yaml'
    Zato_Manifest = 'zato.yaml'

    # The Consul servers
    Consul_StatefulSet = 'consul'
    Consul_Replicas = 3

    # The label of the environment that the quickstart creates once per session
    Quickstart_Label = 'kube'

    # How long both pods may take to form a pair, in seconds
    Pair_Ready_Timeout = 600

    # How long the pods of a replaced pair may take to end, in seconds
    Delete_Timeout = 300

    # How often the roles are read while a test waits for the pair, in seconds
    Poll_Interval = 0.5

    # The role of a standby in sync
    Role_Standby_In_Sync = 'StandbyInSync'

    # The database file of pub/sub
    PubSub_DB_File = 'pubsub.db'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class KubeNode(Node):
    """ One pod of the pair, reached through its node ports on the control plane node, with its local volume
    on the host under the zone of the worker node it runs on.
    """
    pod_name: 'str' = ''
    control_plane_ip: 'str' = ''
    server_node_port: 'int' = 0
    role_node_port: 'int' = 0
    host_node: 'str' = ''

    @property
    def node_name(self) -> 'str':
        return self.pod_name

    @property
    def zone(self) -> 'str':
        out = ClusterCtx.Zones[self.host_node]
        return out

    @property
    def directory(self) -> 'str':
        zone_dir = get_zone_volume_dir(self.run_dir, self.zone)

        out = os.path.join(zone_dir, self.pod_name)
        return out

    @property
    def run_log_path(self) -> 'str':
        out = os.path.join(self.run_dir, 'run-logs', f'{self.pod_name}.jsonl')
        return out

    @property
    def scheduler_log_path(self) -> 'str':
        out = os.path.join(self.run_dir, 'logs', f'{self.pod_name}-scheduler.log')
        return out

    @property
    def server_url(self) -> 'str':
        out = f'http://{self.control_plane_ip}:{self.server_node_port}'
        return out

    @property
    def role_url(self) -> 'str':
        out = f'http://{self.control_plane_ip}:{self.role_node_port}/zato/ha/role'
        return out

    def locate(self) -> 'None':
        """ Reads the worker node that the pod is scheduled on.
        """
        host_node = get_pod_node(self.pod_name)
        assert host_node, f'Pod {self.pod_name} is not scheduled'

        self.host_node = host_node

# ################################################################################################################################

class KubeConsul(Consul):
    """ The Consul servers of the cluster, reached through their node port on the control plane node.
    """

    def __init__(self, authority:'Authority', run_dir:'str', address:'str') -> 'None':
        super().__init__(authority, run_dir)
        self.address = address

    def delete_record(self) -> 'None':
        _ = self.request('DELETE', f'/v1/kv/{TopologyCtx.Consul_Key}')

# ################################################################################################################################

@dataclass(init=False)
class ServiceEndpoint:
    """ The Service of the pair, through which the workload reaches the active pod.
    """
    base_url: 'str'

# ################################################################################################################################

@dataclass(init=False)
class KubeSession:
    """ What one session creates once for every test.
    """
    base: 'HASession'
    authority: 'Authority'
    consul: 'KubeConsul'
    proxy: 'KubeProxy'
    control_plane_ip: 'str'
    data_mount: 'str'
    placeholders: 'strstrdict'

# ################################################################################################################################

@dataclass
class KubeEnvironment:
    """ The pair of one test, with what the shared workload and checks expect of an environment.
    """
    session: 'KubeSession'
    consul: 'KubeConsul'
    haproxy: 'ServiceEndpoint'
    database: 'PubSubDatabase'
    watcher: 'EndpointWatcher'
    timers: 'Timers'
    publisher_password: 'str'
    puller_password: 'str'
    receivers: 'anydict'
    publisher_username: 'str' = 'test.pubsub.publisher'
    puller_username: 'str' = 'test.pubsub.puller'
    logs_dir: 'str' = ''
    node_list: 'list[KubeNode]' = field(default_factory=list)

    @property
    def servers(self) -> 'list[KubeNode]':
        out = self.node_list
        return out

    def get_node(self, node_name:'str') -> 'KubeNode':
        for node in self.node_list:
            if node.node_name == node_name:
                return node

        raise Exception(f'No node named {node_name}')

    def get_active(self) -> 'KubeNode | None':
        for node in self.node_list:
            if node.is_active():
                return node

        return None

    def get_other(self, node:'Node') -> 'KubeNode':
        for other in self.node_list:
            if other.node_name != node.node_name:
                return other

        raise Exception(f'No node other than {node.node_name}')

    def point_database_at(self, node:'KubeNode') -> 'None':
        node.locate()
        self.database.env['Zato_PubSub_DB_Path'] = node.db_path(ModuleCtx.PubSub_DB_File)

    def wait_for_pair(self, timeout:'float') -> 'KubeNode':
        """ Waits until one pod is active with its server up and the other is its standby in sync,
        and returns the active one.
        """
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            active = self.get_active()

            if active is not None:
                standby = self.get_other(active)
                report = standby.read_role()

                if report is not None:
                    if report['role'] == ModuleCtx.Role_Standby_In_Sync:
                        remaining = deadline - time.monotonic()
                        _ = active.wait_until_server_up(remaining)

                        for node in self.node_list:
                            node.locate()

                        self.point_database_at(active)
                        return active

            time.sleep(ModuleCtx.Poll_Interval)

        reports:'anydict' = {}
        for node in self.node_list:
            reports[node.node_name] = node.read_role()

        raise Exception(f'Pair not formed after {timeout}s, reports -> {reports}')

    def save_logs(self) -> 'None':
        os.makedirs(self.logs_dir, exist_ok=True)

        for node in self.node_list:
            save_pod_logs(node.pod_name, self.logs_dir)

# ################################################################################################################################
# ################################################################################################################################

def _create_secret(name:'str', files:'strstrdict', literals:'strstrdict') -> 'None':
    """ Creates a Secret in the namespace of the suites from files and literal values, replacing an earlier one.
    """
    args:'strlist' = ['create', 'secret', 'generic', name, '-n', ClusterCtx.Namespace, '--dry-run=client', '-o', 'yaml']

    for key, path in files.items():
        args.append(f'--from-file={key}={path}')

    for key, value in literals.items():
        args.append(f'--from-literal={key}={value}')

    manifest = kubectl(*args).stdout
    _ = kubectl('apply', '-f', '-', input_text=manifest)

# ################################################################################################################################

def _write_consul_config(run_dir:'str', management_token:'str') -> 'str':
    """ Writes the configuration of the Consul servers and returns its path.
    """
    namespace = ClusterCtx.Namespace
    retry_join:'strlist' = []

    for index in range(ModuleCtx.Consul_Replicas):
        retry_join.append(f'consul-{index}.consul.{namespace}.svc.cluster.local')

    config = {
        'server': True,
        'bootstrap_expect': ModuleCtx.Consul_Replicas,
        'datacenter': 'dc1',
        'data_dir': '/consul/data',
        'client_addr': '0.0.0.0',
        'retry_join': retry_join,
        'performance': {
            'raft_multiplier': 1,
        },
        'ports': {
            'http': -1,
            'https': TopologyCtx.Consul_HTTPS_Port,
        },
        'tls': {
            'defaults': {
                'ca_file': '/consul/certs/ca.pem',
                'cert_file': '/consul/certs/consul.pem',
                'key_file': '/consul/certs/consul.key',
                'verify_incoming': False,
                'verify_outgoing': True,
            },
            'internal_rpc': {
                'verify_server_hostname': True,
            },
        },
        'acl': {
            'enabled': True,
            'default_policy': 'deny',
            'enable_token_persistence': True,
            'tokens': {
                'initial_management': management_token,
            },
        },
    }

    out = os.path.join(run_dir, 'consul.json')

    with open(out, 'w') as config_file:
        json.dump(config, config_file, indent=2)

    return out

# ################################################################################################################################

def _start_consul(run_dir:'str', authority:'Authority', control_plane_ip:'str') -> 'KubeConsul':
    """ Starts the three Consul servers and creates the token of the nodes.
    """
    namespace = ClusterCtx.Namespace

    dns_names = [
        'server.dc1.consul',
        'localhost',
        f'consul-api.{namespace}.svc',
        f'consul-api.{namespace}.svc.cluster.local',
        f'*.consul.{namespace}.svc.cluster.local',
    ]

    issued = authority.issue('consul', dns_names, ['127.0.0.1', control_plane_ip])

    address = f'https://{control_plane_ip}:{ModuleCtx.Consul_Node_Port}'
    out = KubeConsul(authority, run_dir, address)

    config_path = _write_consul_config(run_dir, out.management_token)

    _create_secret('consul-config', {'consul.json': config_path}, {})
    _create_secret('consul-tls', {
        'ca.pem': authority.cert_path,
        'consul.pem': issued.cert_path,
        'consul.key': issued.key_path,
    }, {})

    placeholders = {
        'namespace': namespace,
        'consul_image': TopologyCtx.Consul_Image,
        'consul_node_port': str(ModuleCtx.Consul_Node_Port),
    }

    apply_manifest(ModuleCtx.Consul_Manifest, placeholders)
    wait_for_rollout('statefulset', ModuleCtx.Consul_StatefulSet)

    out.wait_until_ready()
    out.create_node_token()

    _create_secret('zato-ha-consul', {}, {'token': out.node_token})

    return out

# ################################################################################################################################

def _create_pod_certificates(authority:'Authority') -> 'None':
    """ Issues the certificate of each pod under its name, which the peer verifies, into the Secret of the pair.
    """
    files = {'ca.pem': authority.cert_path}

    for pod_name in ModuleCtx.Pod_Names:
        issued = authority.issue(pod_name, [pod_name], [])
        files[f'{pod_name}.pem'] = issued.cert_path
        files[f'{pod_name}.key'] = issued.key_path

    _create_secret('zato-ha-tls', files, {})

# ################################################################################################################################

def _create_host_directories(run_dir:'str') -> 'None':
    """ Creates the directories that the pods write to, owned by the user the pods run as.
    """
    for zone in ClusterCtx.Zones.values():
        zone_dir = get_zone_volume_dir(run_dir, zone)

        for pod_name in ModuleCtx.Pod_Names:
            os.makedirs(os.path.join(zone_dir, pod_name))

    os.makedirs(os.path.join(run_dir, 'logs'))
    os.makedirs(os.path.join(run_dir, 'run-logs'))

# ################################################################################################################################

def create_kube_session() -> 'KubeSession':
    """ Creates the cluster, the receivers, the quickstart environment of the pods and the Consul servers.
    """
    run_dir = prepare_runtime_dir()
    _create_host_directories(run_dir)

    create_cluster(run_dir, NodesCtx.Repository_Dir)

    load_image(NodesCtx.Zato_Image, get_zato_node_names())
    load_image(TopologyCtx.Consul_Image, list(ClusterCtx.Zones))

    base = HASession()
    base.run_dir = run_dir
    base.template_dir = os.path.join(run_dir, 'k8s-template')

    # The receivers listen on the address of the host on the network of kind ..
    rendered_yaml, invoke_password = start_receivers(base, get_kind_gateway())

    # .. the environment is created at the path that each pod mounts its local volume at, and kept as the template
    # that each pod copies to its volume when it first starts ..
    data_mount = os.path.join(run_dir, 'k8s-data')
    home_dir = os.path.join(data_mount, 'home')

    server_directory = create_quickstart_environment(ModuleCtx.Quickstart_Label, data_mount, home_dir, rendered_yaml,
        invoke_password)
    base.server_directories[ModuleCtx.Quickstart_Label] = server_directory

    os.rename(data_mount, base.template_dir)

    # .. and Consul with the certificates of both sides starts.
    authority = Authority(os.path.join(run_dir, 'authority'))
    control_plane_ip = get_node_ip(ClusterCtx.Control_Plane)

    consul = _start_consul(run_dir, authority, control_plane_ip)
    _create_pod_certificates(authority)

    proxy = KubeProxy()
    proxy.start()

    out = KubeSession()
    out.base = base
    out.authority = authority
    out.consul = consul
    out.proxy = proxy
    out.control_plane_ip = control_plane_ip
    out.data_mount = data_mount
    out.placeholders = {
        'namespace': ClusterCtx.Namespace,
        'zato_image': NodesCtx.Zato_Image,
        'uid': str(os.getuid()),
        'gid': str(os.getgid()),
        'repository_dir': NodesCtx.Repository_Dir,
        'run_dir': run_dir,
        'volume_dir': ClusterCtx.Volume_Dir,
        'data_mount': data_mount,
        'template_dir': base.template_dir,
        'start_script': NodesCtx.Start_Script,
        'consul_key': TopologyCtx.Consul_Key,
        'replication_port': str(NodesCtx.Replication_Port),
        'role_port': str(NodesCtx.Role_Port),
        'server_port': str(NodesCtx.Server_Port),
        'redis_port': str(NodesCtx.Redis_Port),
        'scheduler_http_port': str(NodesCtx.Scheduler_HTTP_Port),
        'pull_lease_seconds': NodesCtx.Pull_Lease_Seconds,
        'node_binary': NodesCtx.Node_Binary,
        'server_launcher': NodesCtx.Server_Launcher,
        'scheduler_binary': NodesCtx.Scheduler_Binary,
        'zato_binary': NodesCtx.Zato_Binary,
        'logs_dir': os.path.join(run_dir, 'logs'),
        'run_logs_dir': os.path.join(run_dir, 'run-logs'),
        'server_directory': server_directory,
        'service_node_port': str(ModuleCtx.Service_Node_Port),
    }

    for pod_name, (server_node_port, role_node_port) in ModuleCtx.Pod_Node_Ports.items():
        key = pod_name.replace('zato-ha-', 'pod_')
        out.placeholders[f'{key}_server_node_port'] = str(server_node_port)
        out.placeholders[f'{key}_role_node_port'] = str(role_node_port)

    return out

# ################################################################################################################################

def remove_kube_session(session:'KubeSession') -> 'None':
    session.proxy.stop()

    for receiver in session.base.receivers.values():
        receiver.stop()

    delete_cluster()

# ################################################################################################################################

def _remove_pair(session:'KubeSession') -> 'None':
    """ Deletes the StatefulSet of an earlier test, waits until its pods end and clears what they left.
    """
    _ = kubectl('delete', 'statefulset', ModuleCtx.StatefulSet_Name, '-n', ClusterCtx.Namespace, '--ignore-not-found',
        '--wait=true')

    # The pods end after their StatefulSet, each within its grace period.
    deadline = time.monotonic() + ModuleCtx.Delete_Timeout

    while kubectl('get', 'pods', '-l', ModuleCtx.Pod_Selector, '-n', ClusterCtx.Namespace, '-o', 'name').stdout.strip():
        assert time.monotonic() < deadline, f'Pods of {ModuleCtx.StatefulSet_Name} not deleted'
        time.sleep(ModuleCtx.Poll_Interval)

    run_dir = session.base.run_dir

    for zone in ClusterCtx.Zones.values():
        zone_dir = get_zone_volume_dir(run_dir, zone)

        for pod_name in ModuleCtx.Pod_Names:
            pod_dir = os.path.join(zone_dir, pod_name)
            shutil.rmtree(pod_dir)
            os.makedirs(pod_dir)

    for directory_name in ('logs', 'run-logs'):
        directory = os.path.join(run_dir, directory_name)
        shutil.rmtree(directory)
        os.makedirs(directory)

    session.consul.delete_record()

# ################################################################################################################################

def build_kube_environment(session:'KubeSession', test_name:'str', timers:'Timers') -> 'KubeEnvironment':
    """ Replaces the pair of an earlier test with a new one with the given timers, without waiting for it.
    """
    _remove_pair(session)

    placeholders = dict(session.placeholders)
    placeholders['heartbeat_time'] = str(timers.heartbeat)
    placeholders['mark_out_time'] = str(timers.mark_out)
    placeholders['takeover_time'] = str(timers.takeover)

    apply_manifest(ModuleCtx.Zato_Manifest, placeholders)

    haproxy = ServiceEndpoint()
    haproxy.base_url = f'http://{session.control_plane_ip}:{ModuleCtx.Service_Node_Port}'

    node_list:'list[KubeNode]' = []

    for index, pod_name in enumerate(ModuleCtx.Pod_Names):
        server_node_port, role_node_port = ModuleCtx.Pod_Node_Ports[pod_name]

        node = KubeNode(short_name=str(index), run_dir=session.base.run_dir)
        node.pod_name = pod_name
        node.control_plane_ip = session.control_plane_ip
        node.server_node_port = server_node_port
        node.role_node_port = role_node_port

        node_list.append(node)

    watcher = EndpointWatcher(session.proxy)
    watcher.start()

    out = KubeEnvironment(
        session=session,
        consul=session.consul,
        haproxy=haproxy,
        database=PubSubDatabase(PubSubDBMode.SQLite),
        watcher=watcher,
        timers=timers,
        publisher_password=session.base.publisher_password,
        puller_password=session.base.puller_password,
        receivers=session.base.receivers,
        logs_dir=os.path.join(session.base.run_dir, 'test-logs', test_name),
        node_list=node_list,
    )

    return out

# ################################################################################################################################

@contextmanager
def ready_kube_pair(session:'KubeSession', test_name:'str', timers:'Timers') -> 'any_':
    """ A pair that is ready, whose Service never lists more than one pod while the test runs.
    """
    for receiver in session.base.receivers.values():
        receiver.clear_output()

    env = build_kube_environment(session, test_name, timers)

    try:
        _ = env.wait_for_pair(ModuleCtx.Pair_Ready_Timeout)
        yield env

    finally:
        env.watcher.stop()
        env.save_logs()

    assert not env.watcher.multiple, f'The Service listed more than one pod -> {env.watcher.multiple}'

# ################################################################################################################################
# ################################################################################################################################
