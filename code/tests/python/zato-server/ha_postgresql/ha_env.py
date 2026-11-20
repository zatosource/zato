# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The environment of the active-standby suites. One session creates the network, the kind cluster of the referee,
# the receivers of push deliveries and the quickstart environments of both nodes, and every test receives a referee
# without leases, both nodes started from a copy of those environments and HAProxy in front of them. The suite
# that builds the pair provides its Zato database.

# stdlib
import errno
import logging
import os
import shutil
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import partial

# Zato
from nodes import is_named_by_record, ModuleCtx as NodesCtx, Node, NodeHook, Timers
from load_balancer import HAProxy
from pair import ModuleCtx as PairCtx, render_job_file
from topology import Backend, create_network, Lease, ModuleCtx as TopologyCtx, prepare_runtime_dir, Referee, remove_network, \
    save_container_logs
from zato.common.crypto.api import CryptoManager
from zato.common.test.conftest_base_pubsub import patch_server_conf, render_template, run_quickstart_and_enmasse, \
    SessionState
from zato.common.test.receiver import WebhookReceiver
from zato.common.test.reservation import PortInUse, start_on_reserved_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.test.reservation import PortReservation
    from zato.common.typing_ import any_, anydict, strstrdict
    PubSubDatabase = PubSubDatabase

# ################################################################################################################################
# ################################################################################################################################

reservation_list = list['PortReservation']

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.env')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The scheduler suite, whose service of the jobs both nodes deploy
    Scheduler_Failover_Dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scheduler_failover'))

    # The enmasse file of the pub/sub push suite, whose topics, subscriptions and outgoing connections both nodes import
    Template_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pubsub_push', '_enmasse_template.yaml')

    # The address of the receivers in that file, which the containers reach on the gateway of the network instead
    Template_Receiver_Host = 'http://127.0.0.1:'

    # The purpose under which each receiver reserves its port
    Receiver_Port_Purpose = 'ha-postgresql-receiver'

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

    # How long both nodes may take to form a pair after they start, in seconds
    Pair_Ready_Timeout = 180

    # How often the roles of the nodes are read while the fixture waits for the pair, in seconds
    Poll_Interval = 0.5

    # The role of the standby of a pair that is ready
    Role_Standby = 'Standby'

    # The variable through which zato start receives the directory that the server deploys from each time it starts -
    # the services of its code directory first and then the enmasse files of its enmasse directory.
    Env_Deploy_From = 'Zato_Deploy_From'

    # The directory that both nodes deploy from, its directories and the enmasse file with the scheduler jobs
    Deploy_Dir_Name     = 'deploy'
    Deploy_Code_Dir     = 'code'
    Deploy_Enmasse_Dir  = 'enmasse'
    Jobs_File_Name      = 'jobs.yaml'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class HASession:
    """ What one session creates once for every test - the referee, the receivers, the credentials
    and the quickstart environments.
    """
    run_dir: 'str'
    lease: 'Lease'
    template_dir: 'str'
    publisher_password: 'str'
    puller_password: 'str'
    invoke_password: 'str'
    receivers: 'anydict'
    receiver_ports: 'reservation_list'
    server_directories: 'strstrdict'
    deploy_dir: 'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HAEnvironment:
    """ The pair of one test, with its referee, its load balancer and what the shared workload of the pub/sub suites
    expects of an environment.
    """
    run_dir: 'str'
    referee: 'Referee'
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
    backends: 'list[Backend]' = field(default_factory=list)

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

    def wait_for_pair(self, timeout:'float') -> 'Node':
        """ Waits until one node is active with its server up, the referee record names it at the generation it reports,
        and the other node is its standby, and returns the active node.
        """
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            active = self.get_active()

            if active is not None:
                standby = self.get_other(active)
                report = standby.read_role()

                if report is not None:
                    if report['role'] == ModuleCtx.Role_Standby and is_named_by_record(active, self.referee.read_record()):
                        remaining = deadline - time.monotonic()
                        _ = active.wait_until_server_up(remaining)
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
    """ Creates a quickstart environment in a directory, with the given home directory and the objects of pub/sub,
    and returns its server directory.
    """
    os.makedirs(os.path.join(home_dir, 'env', 'qs-1'), exist_ok=True)

    extra_env = {'HOME': home_dir}
    state = SessionState(f'zato.test.ha_postgresql.{label}', f'server-logs-ha-{label}.txt')

    out = run_quickstart_and_enmasse(
        state=state,
        logger=logger,
        zato_bin=NodesCtx.Zato_Binary,
        invoke_password=invoke_password,
        rendered_yaml=rendered_yaml,
        quickstart_prefix='quickstart-',
        extra_env=extra_env,
        quickstart_parent_dir=directory,
        log_to_files=False,
    )

    patch_server_conf(out, NodesCtx.Server_Port, True)

    return out

# ################################################################################################################################
# ################################################################################################################################

def create_deploy_dir(run_dir:'str', job_yaml:'str') -> 'str':
    """ Creates the directory that both nodes deploy from each time their servers start - the service of the jobs
    in its code directory and the jobs in its enmasse directory, which the server imports once the service is deployed.
    """
    out = os.path.join(run_dir, ModuleCtx.Deploy_Dir_Name)

    code_dir = os.path.join(out, ModuleCtx.Deploy_Code_Dir)
    enmasse_dir = os.path.join(out, ModuleCtx.Deploy_Enmasse_Dir)

    os.makedirs(code_dir)
    os.makedirs(enmasse_dir)

    service_path = os.path.join(ModuleCtx.Scheduler_Failover_Dir, PairCtx.Service_File_Name)
    _ = shutil.copy2(service_path, code_dir)

    jobs_path = os.path.join(enmasse_dir, ModuleCtx.Jobs_File_Name)

    with open(jobs_path, 'w') as jobs_file:
        _ = jobs_file.write(job_yaml)

    return out

# ################################################################################################################################

def _start_receiver(port:'int', *, output_directory:'str', host:'str') -> 'WebhookReceiver':
    """ Starts a receiver on a reserved port, reporting a port that a process without a reservation took as PortInUse.
    """
    receiver = WebhookReceiver(port, output_directory, host=host)

    try:
        receiver.start()
    except OSError as error:
        if error.errno == errno.EADDRINUSE:
            raise PortInUse(f'Receiver could not bind port {port}') from error
        raise

    return receiver

# ################################################################################################################################

def stop_receivers(session:'HASession') -> 'None':
    """ Stops the receivers of a session and releases the reservations of their ports.
    """
    for receiver in session.receivers.values():
        receiver.stop()

    for reservation in session.receiver_ports:
        reservation.release()

# ################################################################################################################################

def start_receivers(session:'HASession', host:'str') -> 'tuple[str, str]':
    """ Creates the credentials of a session, starts its receivers on the given address and creates the directory
    that the nodes deploy the scheduler jobs from, returning the enmasse file with the objects of pub/sub
    and the password of the service that the jobs invoke.
    """
    session.publisher_password = 'test.pub.' + CryptoManager.generate_hex_string()
    session.puller_password = 'test.pull.' + CryptoManager.generate_hex_string()
    session.receivers = {}
    session.receiver_ports = []
    session.server_directories = {}

    placeholders:'strstrdict' = {}
    placeholders['publisher_password'] = session.publisher_password
    placeholders['puller_password'] = session.puller_password

    # The receivers listen on reserved ports of an address of the host that the nodes reach ..
    for topic_name in ModuleCtx.Topic_Names:
        key = _topic_to_key(topic_name)

        output_directory = os.path.join(session.run_dir, 'receivers', key)
        os.makedirs(output_directory, exist_ok=True)

        started = start_on_reserved_port(ModuleCtx.Receiver_Port_Purpose,
            partial(_start_receiver, output_directory=output_directory, host=host))

        session.receivers[topic_name] = started.result
        session.receiver_ports.append(started.reservation)

        placeholders[f'sub_{key}_password'] = 'test.sub.' + CryptoManager.generate_hex_string()
        placeholders[f'port_{key}'] = str(started.reservation.port)

    pubsub_yaml = render_template(ModuleCtx.Template_Path, placeholders)
    pubsub_yaml = pubsub_yaml.replace(ModuleCtx.Template_Receiver_Host, f'http://{host}:')

    # .. both nodes import the objects of pub/sub with their environments, and the scheduler jobs as their servers start.
    job_yaml, _ = render_job_file(placeholders)
    session.deploy_dir = create_deploy_dir(session.run_dir, job_yaml)

    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

    out = (pubsub_yaml, invoke_password)
    return out

# ################################################################################################################################

def create_session() -> 'HASession':
    """ Creates the network, the referee, the receivers and the quickstart environments of both nodes,
    which every test copies.
    """
    run_dir = prepare_runtime_dir()
    create_network()

    session = HASession()
    session.run_dir = run_dir
    session.template_dir = os.path.join(run_dir, 'templates')

    # The API server of the referee serves every test of the session, each of which begins without leases ..
    node_names:'list[str]' = []

    for short_name in ModuleCtx.Node_Names:
        node = Node(short_name=short_name, run_dir=run_dir)
        node_names.append(node.node_name)

    session.lease = Lease(run_dir)
    session.lease.create_cluster(node_names)

    # .. the receivers listen on the gateway of the network, which is the address of the host on it ..
    rendered_yaml, invoke_password = start_receivers(session, TopologyCtx.Gateway)
    session.invoke_password = invoke_password

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
    stop_receivers(session)

    session.lease.delete_cluster()
    remove_network()

# ################################################################################################################################

def _restore_node_directory(session:'HASession', node:'Node') -> 'None':
    """ Replaces the directory of a node with the copy that the session created, at the same path.
    """
    shutil.rmtree(node.directory, ignore_errors=True)

    template_path = os.path.join(session.template_dir, os.path.basename(node.directory))
    _ = shutil.copytree(template_path, node.directory, symlinks=True)

# ################################################################################################################################

def new_nodes(session:'HASession') -> 'list[Node]':
    """ Returns both nodes, each with its directory restored from the copy that the session created.
    """
    out:'list[Node]' = []

    for short_name in ModuleCtx.Node_Names:
        node = Node(short_name=short_name, run_dir=session.run_dir)
        _restore_node_directory(session, node)

        node.server_directory = session.server_directories[short_name]
        out.append(node)

    return out

# ################################################################################################################################

def start_pair(
    session:'HASession',
    test_name:'str',
    timers:'Timers',
    hooks:'list[NodeHook]',
    referee:'Referee',
    database:'PubSubDatabase',
    node_list:'list[Node]',
    backends:'list[Backend]',
) -> 'HAEnvironment':
    """ Starts both prepared nodes with HAProxy in front of them, without waiting for the pair.
    Each hook prepares each node before its container starts, and the backends are the containers of the test
    that the environment removes with the nodes.
    """
    nodes:'dict[str, Node]' = {}
    node_ips:'list[str]' = []

    for node in node_list:
        node.env[ModuleCtx.Env_Deploy_From] = session.deploy_dir

        for hook in hooks:
            hook.before_start(node)

        nodes[node.short_name] = node
        node_ips.append(node.ip)

    haproxy = HAProxy(session.run_dir, node_ips, NodesCtx.Server_Port, NodesCtx.Role_Port)

    out = HAEnvironment(
        run_dir=session.run_dir,
        referee=referee,
        haproxy=haproxy,
        nodes=nodes,
        database=database,
        publisher_password=session.publisher_password,
        puller_password=session.puller_password,
        receivers=session.receivers,
        timers=timers,
        logs_dir=os.path.join(session.run_dir, 'logs', test_name),
        node_list=node_list,
        hooks=hooks,
        backends=backends,
    )

    # Both nodes start together, with HAProxy in front of them.
    for node in node_list:
        node.start()

    haproxy.start()

    return out

# ################################################################################################################################

def remove_environment(env:'HAEnvironment') -> 'None':
    """ Saves the logs of every container of a test and removes the containers.
    """
    env.save_logs()

    for backend in env.backends:
        for container_name in backend.container_names:
            save_container_logs(container_name, env.logs_dir)

    save_container_logs(TopologyCtx.HAProxy_Container, env.logs_dir)

    for node in env.node_list:
        node.remove()

        for hook in env.hooks:
            hook.after_remove(node)

    env.haproxy.remove()
    env.referee.remove()

    for backend in env.backends:
        backend.remove()

# ################################################################################################################################

def clear_receivers(session:'HASession') -> 'None':
    for receiver in session.receivers.values():
        receiver.clear_output()

# ################################################################################################################################

@contextmanager
def until_removed(env:'HAEnvironment') -> 'any_':
    """ Yields an environment once its pair is ready - one node active with its server up and the other
    its standby, and removes it when the test completes.
    """
    try:
        _ = env.wait_for_pair(ModuleCtx.Pair_Ready_Timeout)
        yield env
    finally:
        remove_environment(env)

# ################################################################################################################################
# ################################################################################################################################
