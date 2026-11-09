# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment of the active-standby suites. One session creates the network, the receivers of push deliveries
# and the quickstart environments of both nodes, and every test receives a new Consul, both nodes started
# from a copy of those environments and HAProxy in front of them.

# stdlib
import logging
import os
import shutil
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

# Zato
from ha_authority import Authority
from nodes import ModuleCtx as NodesCtx, Node, NodeHook, Timers
from pair import add_service_row, import_jobs, ModuleCtx as PairCtx, render_job_file
from topology import Consul, create_network, HAProxy, ModuleCtx as TopologyCtx, prepare_runtime_dir, remove_network, \
    save_container_logs
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import find_free_port, patch_server_conf, render_template, \
    run_quickstart_and_enmasse, SessionState
from zato.common.test.pubsub_database import PubSubDatabase, PubSubDBMode
from zato.common.test.receiver import WebhookReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.env')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The scheduler suite, whose service of the jobs both nodes deploy
    Scheduler_Failover_Dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scheduler_failover'))

    # The enmasse file of the pub/sub push suite, whose topics, subscriptions and outgoing connections both nodes import
    Template_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pubsub_push', '_enmasse_template.yaml')

    # The address of the receivers in that file, which the containers reach on the gateway of the network instead
    Template_Receiver_Host = 'http://127.0.0.1:'

    # The topics of that file
    Topic_Names = [
        'iam.user.created',
        'iam.user.deleted',
        'iam.role.assigned',
        'iam.password.changed',
        'iam.login.failed',
        'customer.registered',
        'customer.updated',
        'customer.deactivated',
        'order.placed',
        'order.shipped',
    ]

    # The short names of the two nodes
    Node_Names = ('a', 'b')

    # The database files that the nodes replicate
    PubSub_DB_File = 'pubsub.db'

    # How long both nodes may take to form a pair after they start, in seconds
    Pair_Ready_Timeout = 180

    # How often the roles of the nodes are read while the fixture waits for the pair, in seconds
    Poll_Interval = 0.5

    # The roles of a pair that is ready
    Role_Standby_In_Sync = 'StandbyInSync'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class HASession:
    """ What one session creates once for every test - the receivers, the credentials and the quickstart environments.
    """
    run_dir: 'str'
    template_dir: 'str'
    publisher_password: 'str'
    puller_password: 'str'
    receivers: 'anydict'
    server_directories: 'strstrdict'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HAEnvironment:
    """ The pair of one test, with its referee, its load balancer and what the shared workload of the pub/sub suites
    expects of an environment.
    """
    run_dir: 'str'
    authority: 'Authority'
    consul: 'Consul'
    haproxy: 'HAProxy'
    nodes: 'dict[str, Node]'
    database: 'PubSubDatabase'
    publisher_password: 'str'
    puller_password: 'str'
    receivers: 'anydict'
    timers: 'Timers'
    publisher_username: 'str' = 'test.pubsub.publisher'
    puller_username: 'str' = 'test.pubsub.puller'
    logs_dir: 'str' = ''
    node_list: 'list[Node]' = field(default_factory=list)
    hooks: 'list[NodeHook]' = field(default_factory=list)

# ################################################################################################################################

    @property
    def servers(self) -> 'list[Node]':
        """ The nodes under the name that the run-log checks of the scheduler suite read.
        """
        out = self.node_list
        return out

# ################################################################################################################################

    def get_node(self, node_name:'str') -> 'Node':
        """ Returns the node of the given name, as the referee names it.
        """
        for node in self.node_list:
            if node.node_name == node_name:
                return node

        raise Exception(f'No node named {node_name}')

# ################################################################################################################################

    def get_active(self) -> 'Node | None':
        """ Returns the node that serves requests now, or None if neither does.
        """
        for node in self.node_list:
            if node.is_active():
                return node

        return None

# ################################################################################################################################

    def get_other(self, node:'Node') -> 'Node':
        for other in self.node_list:
            if other.short_name != node.short_name:
                return other

        raise Exception(f'No node other than {node.node_name}')

# ################################################################################################################################

    def point_database_at(self, node:'Node') -> 'None':
        """ Makes the checks of the shared workload read the pub/sub database of the given node.
        """
        self.database.env['Zato_PubSub_DB_Path'] = node.db_path(ModuleCtx.PubSub_DB_File)

# ################################################################################################################################

    def wait_for_pair(self, timeout:'float') -> 'Node':
        """ Waits until one node is active with its server up and the other is its standby in sync,
        and returns the active node.
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
                        self.point_database_at(active)
                        return active

            time.sleep(ModuleCtx.Poll_Interval)

        reports:'anydict' = {}
        for node in self.node_list:
            reports[node.node_name] = node.read_role()

        raise Exception(f'Pair not formed after {timeout}s, reports -> {reports}')

# ################################################################################################################################

    def save_logs(self) -> 'None':
        os.makedirs(self.logs_dir, exist_ok=True)

        for node in self.node_list:
            node.save_logs(self.logs_dir)

# ################################################################################################################################
# ################################################################################################################################

def _topic_to_key(topic_name:'str') -> 'str':
    out = topic_name.replace('.', '_')
    return out

# ################################################################################################################################

def create_quickstart_environment(
    label:'str',
    directory:'str',
    home_dir:'str',
    rendered_yaml:'str',
    invoke_password:'str',
) -> 'str':
    """ Creates a quickstart environment in a directory, with the given home directory, the objects of pub/sub,
    the scheduler jobs and the service that the jobs invoke, and returns its server directory.
    """
    os.makedirs(os.path.join(home_dir, 'env', 'qs-1'), exist_ok=True)

    extra_env = {'HOME': home_dir}
    state = SessionState(f'zato.test.ha_consul.{label}', f'server-logs-ha-{label}.txt')

    out = run_quickstart_and_enmasse(
        state=state,
        logger=logger,
        zato_bin=NodesCtx.Zato_Binary,
        invoke_password=invoke_password,
        rendered_yaml='',
        quickstart_prefix='quickstart-',
        extra_env=extra_env,
        quickstart_parent_dir=directory,
    )

    quickstart_directory = os.path.dirname(out)

    # The service of the jobs is deployed from the pickup directory as the server starts,
    # and its row exists before the jobs that invoke it are imported.
    pickup_dir = os.path.join(out, 'pickup', 'incoming', 'services')
    service_path = os.path.join(ModuleCtx.Scheduler_Failover_Dir, PairCtx.Service_File_Name)
    _ = shutil.copy(service_path, pickup_dir)

    add_service_row(quickstart_directory)
    import_jobs(quickstart_directory, out, rendered_yaml, extra_env)

    patch_server_conf(out, NodesCtx.Server_Port, True)

    return out

# ################################################################################################################################
# ################################################################################################################################

def start_receivers(session:'HASession', host:'str') -> 'tuple[str, str]':
    """ Creates the credentials of a session and starts its receivers on the given address, returning the enmasse file
    with the objects of pub/sub and the scheduler jobs, and the password of the service that the jobs invoke.
    """
    session.publisher_password = 'test.pub.' + CryptoManager.generate_hex_string()
    session.puller_password = 'test.pull.' + CryptoManager.generate_hex_string()
    session.receivers = {}
    session.server_directories = {}

    placeholders:'strstrdict' = {}
    placeholders['publisher_password'] = session.publisher_password
    placeholders['puller_password'] = session.puller_password

    # The receivers listen on an address of the host that the nodes reach ..
    for topic_name in ModuleCtx.Topic_Names:
        key = _topic_to_key(topic_name)
        port = find_free_port()

        placeholders[f'sub_{key}_password'] = 'test.sub.' + CryptoManager.generate_hex_string()
        placeholders[f'port_{key}'] = str(port)

        output_directory = os.path.join(session.run_dir, 'receivers', key)
        os.makedirs(output_directory, exist_ok=True)

        receiver = WebhookReceiver(port, output_directory, host=host)
        receiver.start()

        session.receivers[topic_name] = receiver

    pubsub_yaml = render_template(ModuleCtx.Template_Path, placeholders)
    pubsub_yaml = pubsub_yaml.replace(ModuleCtx.Template_Receiver_Host, f'http://{host}:')

    # .. and both nodes import one file with the objects of pub/sub and the scheduler jobs.
    job_yaml, _ = render_job_file(placeholders)
    rendered_yaml = pubsub_yaml + '\n' + job_yaml

    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

    out = (rendered_yaml, invoke_password)
    return out

# ################################################################################################################################

def create_session() -> 'HASession':
    """ Creates the network, the receivers and the quickstart environments of both nodes, which every test copies.
    """
    run_dir = prepare_runtime_dir()
    create_network()

    session = HASession()
    session.run_dir = run_dir
    session.template_dir = os.path.join(run_dir, 'templates')

    # The receivers listen on the gateway of the network, which is the address of the host on it ..
    rendered_yaml, invoke_password = start_receivers(session, TopologyCtx.Gateway)

    # .. and the environment of each node is kept as it was created, so that each test begins from it.
    for short_name in ModuleCtx.Node_Names:
        node = Node(short_name=short_name, run_dir=run_dir)

        server_directory = create_quickstart_environment(short_name, node.directory, node.home_dir, rendered_yaml,
            invoke_password)
        session.server_directories[short_name] = server_directory

        template_path = os.path.join(session.template_dir, os.path.basename(node.directory))
        _ = shutil.copytree(node.directory, template_path, symlinks=True)

    return session

# ################################################################################################################################

def remove_session(session:'HASession') -> 'None':
    for receiver in session.receivers.values():
        receiver.stop()

    remove_network()

# ################################################################################################################################

def _restore_node_directory(session:'HASession', node:'Node') -> 'None':
    """ Replaces the directory of a node with the copy that the session created, at the same path.
    """
    shutil.rmtree(node.directory, ignore_errors=True)

    template_path = os.path.join(session.template_dir, os.path.basename(node.directory))
    _ = shutil.copytree(template_path, node.directory, symlinks=True)

# ################################################################################################################################

def build_environment(session:'HASession', test_name:'str', timers:'Timers', hooks:'list[NodeHook]') -> 'HAEnvironment':
    """ Starts a new Consul, both nodes from the environments of the session and HAProxy, without waiting for the pair.
    Each hook prepares each node before its container starts.
    """
    run_dir = session.run_dir

    authority = Authority(os.path.join(run_dir, 'authority'))

    # Each test has a Consul with no data, configured with the tokens of this test ..
    consul = Consul(authority, run_dir)
    shutil.rmtree(consul.directory, ignore_errors=True)

    consul.start()
    consul.create_node_token()

    nodes:'dict[str, Node]' = {}
    node_list:'list[Node]' = []
    node_ips:'list[str]' = []

    for short_name in ModuleCtx.Node_Names:
        node = Node(short_name=short_name, run_dir=run_dir)
        _restore_node_directory(session, node)

        node.server_directory = session.server_directories[short_name]
        node.prepare(authority, consul, timers)

        for hook in hooks:
            hook.before_start(node)

        nodes[short_name] = node
        node_list.append(node)
        node_ips.append(node.ip)

    haproxy = HAProxy(run_dir, node_ips, NodesCtx.Server_Port, NodesCtx.Role_Port)

    database = PubSubDatabase(PubSubDBMode.SQLite)

    out = HAEnvironment(
        run_dir=run_dir,
        authority=authority,
        consul=consul,
        haproxy=haproxy,
        nodes=nodes,
        database=database,
        publisher_password=session.publisher_password,
        puller_password=session.puller_password,
        receivers=session.receivers,
        timers=timers,
        logs_dir=os.path.join(run_dir, 'logs', test_name),
        node_list=node_list,
        hooks=hooks,
    )

    out.point_database_at(node_list[0])

    # .. and both nodes start together, with HAProxy in front of them.
    for node in node_list:
        node.start()

    haproxy.start()

    return out

# ################################################################################################################################

def remove_environment(env:'HAEnvironment') -> 'None':
    """ Saves the logs of every container of a test and removes the containers.
    """
    env.save_logs()
    save_container_logs(TopologyCtx.Consul_Container, env.logs_dir)
    save_container_logs(TopologyCtx.HAProxy_Container, env.logs_dir)

    for node in env.node_list:
        node.remove()

        for hook in env.hooks:
            hook.after_remove(node)

    env.haproxy.remove()
    env.consul.remove()

# ################################################################################################################################

@contextmanager
def ready_pair(session:'HASession', test_name:'str', timers:'Timers', hooks:'list[NodeHook]') -> 'any_':
    """ A pair with the given timers and node hooks that is ready - one node active with its server up and the other
    its standby in sync, removed when the test completes.
    """
    for receiver in session.receivers.values():
        receiver.clear_output()

    env = build_environment(session, test_name, timers, hooks)

    try:
        _ = env.wait_for_pair(ModuleCtx.Pair_Ready_Timeout)
        yield env
    finally:
        remove_environment(env)

# ################################################################################################################################
# ################################################################################################################################
