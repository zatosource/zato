# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The session and the pair of the Kubernetes suites. A session creates the cluster, loads the images and creates
# the quickstart environment that both pods begin from. The referee record is in a Lease of the namespace of the pair.
# Each test replaces the pair with a new StatefulSet whose pods begin from that environment, with no Lease of the pair.

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
    save_pod_logs
from kube_endpoints import EndpointWatcher
from nodes import ModuleCtx as NodesCtx, Node, Timers
from topology import ModuleCtx as TopologyCtx, Referee
from zato.common.test.pubsub_database import PubSubDatabase, PubSubDBMode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite_kubernetes.env')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The pods of the pair
    Pod_Names = ['zato-ha-0', 'zato-ha-1']
    StatefulSet_Name = 'zato-ha'
    Pod_Selector = 'app=zato-ha'

    # The node ports through which the test process reaches the Service and each pod
    Service_Node_Port = 30170
    Pod_Node_Ports = {
        'zato-ha-0': (30180, 30181),
        'zato-ha-1': (30190, 30191),
    }

    # The manifest of the pair
    Zato_Manifest = 'zato.yaml'

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

    # The optional Secret with the pub/sub database settings of the pods, and the CA file that the pods mount
    PubSub_DB_Secret = 'zato-ha-pubsub-db'
    Pod_CA_File = '/zato-ha-tls/ca.pem'

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

class KubeLease(Referee):
    """ The referee record in the Lease of the pair, which the pods write through the API server of the cluster.
    """

    def __init__(self, control_plane_ip:'str') -> 'None':
        self.ip = control_plane_ip

    def _get(self, *args:'str') -> 'any_':
        result = kubectl('get', 'leases', *args, '-n', ClusterCtx.Namespace, '-o', 'json')
        out = json.loads(result.stdout)
        return out

    def read_record(self) -> 'anydict | None':
        """ Returns the referee record with its version, or None if the pair has not written one yet.
        """
        leases = self._get('--field-selector', f'metadata.name={TopologyCtx.Lease_Name}')

        if not leases['items']:
            return None

        metadata = leases['items'][0]['metadata']
        value = metadata['annotations'][TopologyCtx.Record_Annotation]

        out = json.loads(value)
        out['version'] = metadata['resourceVersion']

        return out

    def read_address_names(self) -> 'strlist':
        """ Returns the names of the leases in which the pods published their addresses, in order.
        """
        leases = self._get('-l', f'{TopologyCtx.Lease_Label}={TopologyCtx.Lease_Name}')

        out:'strlist' = []

        for item in leases['items']:
            out.append(item['metadata']['name'])

        out.sort()
        return out

    def clear(self) -> 'None':
        _ = kubectl('delete', 'leases', '--all', '-n', ClusterCtx.Namespace, '--wait=true')

    def recreate_without_data(self) -> 'None':
        self.clear()

# ################################################################################################################################

class KubeBackend:
    """ A service of the cluster that the pair depends on besides the API server, with the pods whose logs
    each test keeps.
    """
    pod_names: 'strlist'

    def clear(self) -> 'None':
        """ Removes what the pair of an earlier test left in the service.
        """
        raise NotImplementedError()

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
    referee: 'Referee'
    backends: 'list[KubeBackend]'
    database: 'PubSubDatabase'
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
    referee: 'Referee'
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

        for backend in self.session.backends:
            for pod_name in backend.pod_names:
                save_pod_logs(pod_name, self.logs_dir)

# ################################################################################################################################
# ################################################################################################################################

def create_secret(name:'str', files:'strstrdict', literals:'strstrdict') -> 'None':
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

def _create_pod_certificates(authority:'Authority') -> 'None':
    """ Issues the certificate of each pod under its name, which the peer verifies, into the Secret of the pair.
    """
    files = {'ca.pem': authority.cert_path}

    for pod_name in ModuleCtx.Pod_Names:
        issued = authority.issue(pod_name, [pod_name], [])
        files[f'{pod_name}.pem'] = issued.cert_path
        files[f'{pod_name}.key'] = issued.key_path

    create_secret('zato-ha-tls', files, {})

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

def create_cluster_session() -> 'KubeSession':
    """ Creates the cluster, the receivers, the quickstart environment of the pods, their certificates and the referee,
    without the database of pub/sub, which the caller adds.
    """
    run_dir = prepare_runtime_dir()
    _create_host_directories(run_dir)

    create_cluster(run_dir, NodesCtx.Repository_Dir)

    load_image(NodesCtx.Zato_Image, get_zato_node_names())

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

    # .. and the certificates of the pods are issued.
    authority = Authority(os.path.join(run_dir, 'authority'))
    control_plane_ip = get_node_ip(ClusterCtx.Control_Plane)

    _create_pod_certificates(authority)

    proxy = KubeProxy()
    proxy.start()

    out = KubeSession()
    out.base = base
    out.authority = authority
    out.referee = KubeLease(control_plane_ip)
    out.backends = []
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
        'pubsub_db_secret': ModuleCtx.PubSub_DB_Secret,
        'lease_name': TopologyCtx.Lease_Name,
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

def create_kube_session() -> 'KubeSession':
    """ Creates the cluster, the receivers, the quickstart environment of the pods and the referee.
    """
    out = create_cluster_session()
    out.database = PubSubDatabase(PubSubDBMode.SQLite)

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

    session.referee.clear()

    for backend in session.backends:
        backend.clear()

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
        referee=session.referee,
        haproxy=haproxy,
        database=session.database,
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
