# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
from functools import partial
from tempfile import mkdtemp
from typing import NamedTuple
from uuid import uuid4

# Zato
from live_containers.ready import wait_until
from live_kafka.tls import generate_kafka_tls

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_kafka.tls import KafkaTLS
    from zato.common.typing_ import any_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Docker image the broker runs from
    Kafka_Image = 'apache/kafka:latest'

    # Host port the broker listens on - the same port is used inside the container
    # so the advertised listener works for both host clients and in-container tools
    Kafka_Port = 29092

    # In-container port of the KRaft controller listener
    Controller_Port = 29093

    # Host port of the TLS listener, used inside the container too
    SSL_Port = 29094

    # Name of the container so stale ones can be removed
    Kafka_Container = 'zato-kafka-test'

    # Where the Kafka CLI tools live inside the container
    Kafka_Bin_Dir = '/opt/kafka/bin'

    # The image reads a complete server.properties from this directory, so the certificates
    # are written next to it and the same mount serves both.
    Config_Dir = '/mnt/shared/config'

    # The directory the certificates of a run are written to on the host, so a stale run's can be told apart
    Config_Prefix = 'zato-kafka-'

    # How many partitions a topic has unless a test says otherwise
    Default_Partitions = 1

# ################################################################################################################################
# ################################################################################################################################

class KafkaServer(NamedTuple):
    container_name: str
    address: str
    ssl_address: str
    tls: 'KafkaTLS'

# ################################################################################################################################
# ################################################################################################################################

def _remove_stale_container(name:'str') -> 'None':
    """ Removes a container left over from a previous, possibly interrupted, run.
    """
    _ = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, check=False)

# ################################################################################################################################

def stop_container(name:'str') -> 'None':
    """ Stops a container - it removes itself because it was started with --rm.
    """
    _ = subprocess.run(['docker', 'stop', name], capture_output=True, check=False)

# ################################################################################################################################

def _list_topics(container_name:'str', port:'int') -> 'bool':
    """ One attempt at listing topics inside the container - the broker's output is the error when it fails.
    """
    command = [
        'docker', 'exec', container_name,
        f'{ModuleCtx.Kafka_Bin_Dir}/kafka-topics.sh',
        '--bootstrap-server', f'localhost:{port}',
        '--list',
    ]

    result = subprocess.run(command, capture_output=True, check=False)

    if result.returncode != 0:
        output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
        raise Exception(output.strip())

    return True

# ################################################################################################################################

def wait_until_ready(container_name:'str', port:'int'=ModuleCtx.Kafka_Port) -> 'None':
    """ Retries listing topics inside the container until the broker responds.
    """
    check = partial(_list_topics, container_name, port)
    wait_until(check, f'the Kafka broker in `{container_name}`')

# ################################################################################################################################

def run_kafka_tool(container_name:'str', tool:'str', arguments:'strlist', port:'int'=ModuleCtx.Kafka_Port) -> 'str':
    """ Runs one of the Kafka CLI tools inside a container and returns what it printed.
    """
    command = [
        'docker', 'exec', container_name,
        f'{ModuleCtx.Kafka_Bin_Dir}/{tool}',
        '--bootstrap-server', f'localhost:{port}',
    ]
    command.extend(arguments)

    result = subprocess.run(command, capture_output=True, check=False)

    stdout = result.stdout.decode('utf-8')
    stderr = result.stderr.decode('utf-8')

    if result.returncode != 0:
        raise Exception(f'Could not run `{tool} {arguments}` in `{container_name}`, stdout: `{stdout}`, stderr: `{stderr}`')

    out = stdout
    return out

# ################################################################################################################################

def create_topic(
    container_name:'str',
    topic:'str',
    partitions:'int'=ModuleCtx.Default_Partitions,
    port:'int'=ModuleCtx.Kafka_Port,
    replication_factor:'int'=1,
    config:'strdict | None'=None,
    ) -> 'None':
    """ Creates a topic inside the container - consumers subscribed to a topic that does not exist yet
    would only discover it on their next metadata refresh, which is minutes away by default.
    """
    arguments = [
        '--create',
        '--topic', topic,
        '--partitions', str(partitions),
        '--replication-factor', str(replication_factor),
    ]

    for key, value in (config or {}).items():
        arguments.extend(['--config', f'{key}={value}'])

    _ = run_kafka_tool(container_name, 'kafka-topics.sh', arguments, port)

# ################################################################################################################################

def tls_properties(tls:'KafkaTLS') -> 'strdict':
    """ The broker properties that make a TLS listener read its PEM certificates and require a client certificate.
    """
    config_dir = ModuleCtx.Config_Dir
    broker_pem_name = os.path.basename(tls.broker_pem)
    ca_cert_name = os.path.basename(tls.ca_cert)

    out = {
        'ssl.keystore.type': 'PEM',
        'ssl.keystore.location': f'{config_dir}/{broker_pem_name}',
        'ssl.truststore.type': 'PEM',
        'ssl.truststore.location': f'{config_dir}/{ca_cert_name}',
        'ssl.client.auth': 'required',
    }

    return out

# ################################################################################################################################

def write_server_properties(directory:'str', properties:'strdict') -> 'None':
    """ Writes the broker's configuration file where the container's mount will find it.
    """
    lines = [f'{key}={value}' for key, value in properties.items()]
    path = os.path.join(directory, 'server.properties')

    with open(path, 'w') as f:
        _ = f.write('\n'.join(lines) + '\n')

    os.chmod(path, 0o644)

# ################################################################################################################################

def run_container(container_name:'str', command:'strlist') -> 'None':
    """ Starts a container, surfacing docker's own error message if the command fails -
    a bare CalledProcessError hides both stdout and stderr.
    """
    result = subprocess.run(command, capture_output=True, check=False)

    if result.returncode != 0:
        stdout = result.stdout.decode('utf-8')
        stderr = result.stderr.decode('utf-8')
        raise Exception(f'Could not start `{container_name}`, stdout: `{stdout}`, stderr: `{stderr}`')

# ################################################################################################################################

def new_config_directory() -> 'str':
    """ A directory the container's user can read - the certificates and server.properties of one broker go there.
    """
    out = mkdtemp(prefix=ModuleCtx.Config_Prefix)
    os.chmod(out, 0o755)
    return out

# ################################################################################################################################

def start_kafka() -> 'KafkaServer':
    """ Starts a single-node KRaft Kafka container that clients on the host reach through localhost,
    over a plaintext listener and over a TLS one.
    """
    container_name = ModuleCtx.Kafka_Container
    port = ModuleCtx.Kafka_Port
    ssl_port = ModuleCtx.SSL_Port
    controller_port = ModuleCtx.Controller_Port

    # Starting a container is silent and can take a while, e.g. when the image needs to be pulled first,
    # which is why each phase reports itself.
    print(f'Starting Kafka container {container_name} on ports {port} and {ssl_port}', flush=True)

    _remove_stale_container(container_name)

    config_dir = new_config_directory()
    tls = generate_kafka_tls(config_dir)

    # The broker listens on the same ports inside and outside the container,
    # which keeps the advertised listeners valid for host clients and in-container tools alike.
    properties = {
        'node.id': '1',
        'process.roles': 'broker,controller',
        'listeners': f'PLAINTEXT://0.0.0.0:{port},SSL://0.0.0.0:{ssl_port},CONTROLLER://0.0.0.0:{controller_port}',
        'advertised.listeners': f'PLAINTEXT://localhost:{port},SSL://localhost:{ssl_port}',
        'controller.listener.names': 'CONTROLLER',
        'inter.broker.listener.name': 'PLAINTEXT',
        'controller.quorum.voters': f'1@localhost:{controller_port}',
        'listener.security.protocol.map': 'PLAINTEXT:PLAINTEXT,SSL:SSL,CONTROLLER:PLAINTEXT',
        'offsets.topic.replication.factor': '1',
        'transaction.state.log.replication.factor': '1',
        'transaction.state.log.min.isr': '1',
        'share.coordinator.state.topic.replication.factor': '1',
        'share.coordinator.state.topic.min.isr': '1',
        'group.initial.rebalance.delay.ms': '0',
        'auto.create.topics.enable': 'true',
        'log.dirs': '/tmp/kraft-combined-logs',
    }
    properties.update(tls_properties(tls))
    write_server_properties(config_dir, properties)

    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', container_name,
        '-v', f'{config_dir}:{ModuleCtx.Config_Dir}:ro',
        '-p', f'{port}:{port}',
        '-p', f'{ssl_port}:{ssl_port}',
        ModuleCtx.Kafka_Image,
    ]

    run_container(container_name, command)

    # Wait until the broker responds to a metadata request
    print(f'Waiting for Kafka container {container_name} to accept connections', flush=True)
    wait_until_ready(container_name, port)
    print(f'Kafka container {container_name} is ready', flush=True)

    out = KafkaServer(
        container_name=container_name,
        address=f'localhost:{port}',
        ssl_address=f'localhost:{ssl_port}',
        tls=tls,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

class ClusterCtx:

    # The Docker network the instances find each other on - each is reachable by its container name
    Network = 'zato-kafka-cluster'

    # Container names are this followed by the instance's number, starting from 1
    Container_Prefix = 'zato-kafka-cluster-'

    # Every instance has its own host port for plaintext and for TLS, the number is the instance's index
    Plaintext_Port_Base = 29100
    SSL_Port_Base = 29200

    # In-container ports of the listeners that only other instances use
    Internal_Port = 29090
    Controller_Port = 29093

    # Where the shared certificates are mounted in every instance
    Certificates_Dir = '/mnt/shared/certs'

    # The cluster id every instance must agree on
    Cluster_Id = 'ZatoKafkaClusterTest0001'

    # How long one metadata request from the host may take
    Metadata_Timeout = 5.0

    # How long a follower may lag before the leader drops it from the in-sync set
    Replica_Lag_Max_Ms = 120_000

# ################################################################################################################################
# ################################################################################################################################

class KafkaInstance(NamedTuple):
    index: int
    node_id: int
    container_name: str
    address: str
    ssl_address: str

# ################################################################################################################################
# ################################################################################################################################

class KafkaCluster:
    """ N Kafka containers on one Docker network, each a combined broker and controller. Instances can be stopped,
    started, paused and resumed one at a time, each call returning once the cluster's own metadata agrees.
    """

    def __init__(self, instances:'list[KafkaInstance]', tls:'KafkaTLS') -> 'None':
        self.instances = instances
        self.tls = tls
        self.bootstrap = ','.join(instance.address for instance in instances)
        self.ssl_bootstrap = ','.join(instance.ssl_address for instance in instances)

        # What each instance is doing right now, so a teardown knows which ones to unpause first
        self._is_paused:'dict[int, bool]' = {instance.index: False for instance in instances}
        self._is_running:'dict[int, bool]' = {instance.index: True for instance in instances}

# ################################################################################################################################

    def __getitem__(self, index:'int') -> 'KafkaInstance':
        return self.instances[index]

# ################################################################################################################################

    def running_instances(self) -> 'list[KafkaInstance]':
        """ The instances that are up and not paused - the ones a request from the host can reach.
        """
        out = [elem for elem in self.instances if self._is_running[elem.index] and not self._is_paused[elem.index]]
        return out

# ################################################################################################################################

    def _running_bootstrap(self) -> 'str':
        """ A bootstrap string of the reachable instances only, so a metadata request never waits on a paused one.
        """
        running = self.running_instances()

        if not running:
            raise Exception('No Kafka instance is running')

        out = ','.join(elem.address for elem in running)
        return out

# ################################################################################################################################

    def metadata(self, topic:'str | None'=None) -> 'any_':
        """ The cluster's view of itself as the reachable instances report it.
        """
        from confluent_kafka.admin import AdminClient

        config = {
            'bootstrap.servers': self._running_bootstrap(),
            'socket.timeout.ms': int(ClusterCtx.Metadata_Timeout * 1000),
        }
        admin = AdminClient(config)
        out = admin.list_topics(topic=topic, timeout=ClusterCtx.Metadata_Timeout)

        return out

# ################################################################################################################################

    def live_node_ids(self) -> 'set[int]':
        """ The node ids the cluster currently lists as its members - a fenced or stopped instance is not among them.
        """
        out = set(self.metadata().brokers)
        return out

# ################################################################################################################################

    def leader_of(self, topic:'str', partition:'int') -> 'int':
        """ The index of the instance leading a partition, -1 when the partition has no leader right now.
        """
        metadata = self.metadata(topic)
        leader_node_id = metadata.topics[topic].partitions[partition].leader

        for instance in self.instances:
            if instance.node_id == leader_node_id:
                return instance.index

        return -1

# ################################################################################################################################

    def coordinator_of(self, group_id:'str') -> 'int':
        """ The index of the instance coordinating a consumer group - the one whose going away makes the group rebalance.
        """
        from confluent_kafka.admin import AdminClient

        config = {
            'bootstrap.servers': self._running_bootstrap(),
            'socket.timeout.ms': int(ClusterCtx.Metadata_Timeout * 1000),
        }
        admin = AdminClient(config)
        futures = admin.describe_consumer_groups([group_id], request_timeout=ClusterCtx.Metadata_Timeout)
        description = futures[group_id].result()
        node_id = description.coordinator.id

        for instance in self.instances:
            if instance.node_id == node_id:
                return instance.index

        raise Exception(f'No instance has node id {node_id}, the coordinator of `{group_id}`')

# ################################################################################################################################

    def end_offset(self, topic:'str', partition:'int'=0) -> 'int':
        """ The offset the next message appended to a partition will take, as the reachable instances report it.
        """
        from confluent_kafka import Consumer, TopicPartition

        config = {
            'bootstrap.servers': self._running_bootstrap(),
            'group.id': f'zato-test-offsets-{uuid4().hex}',
            'socket.timeout.ms': int(ClusterCtx.Metadata_Timeout * 1000),
        }
        consumer = Consumer(config)

        try:
            _, out = consumer.get_watermark_offsets(TopicPartition(topic, partition), timeout=ClusterCtx.Metadata_Timeout)
        finally:
            consumer.close()

        return out

# ################################################################################################################################

    def wait_until_leader_moves(self, topic:'str', partition:'int', away_from:'int') -> 'int':
        """ Waits until a partition has a leader other than the given instance and returns the new leader's index.
        """
        def _check() -> 'bool':
            leader = self.leader_of(topic, partition)
            return leader not in (-1, away_from)

        wait_until(_check, f'a new leader of {topic}/{partition}')
        out = self.leader_of(topic, partition)

        return out

# ################################################################################################################################

    def _wait_until_member(self, index:'int', is_member:'bool') -> 'None':
        """ Waits until the cluster's metadata does or does not list an instance.
        """
        node_id = self.instances[index].node_id
        what = 'join' if is_member else 'leave'

        # With nothing left running there is nobody to ask, and a cluster that is down lists no one
        if not self.running_instances():
            return

        def _check() -> 'bool':
            return (node_id in self.live_node_ids()) is is_member

        wait_until(_check, f'Kafka instance {index} to {what} the cluster')

# ################################################################################################################################

    def wait_until_all_in_sync(self, topic:'str') -> 'None':
        """ Waits until every partition of a topic has all its replicas in sync, so a stopped and restarted instance
        has caught up before a test goes on.
        """
        def _check() -> 'bool':
            metadata = self.metadata(topic)
            for partition in metadata.topics[topic].partitions.values():
                if set(partition.isrs) != set(partition.replicas):
                    return False
            return True

        wait_until(_check, f'all replicas of {topic} to be in sync')

# ################################################################################################################################

    def stop_instance(self, index:'int') -> 'None':
        """ Stops an instance - the container keeps its data so start_instance brings the same instance back.
        """
        instance = self.instances[index]
        print(f'Stopping Kafka instance {index} ({instance.container_name})', flush=True)

        if self._is_paused[index]:
            _ = subprocess.run(['docker', 'unpause', instance.container_name], capture_output=True, check=False)
            self._is_paused[index] = False

        _ = subprocess.run(['docker', 'stop', instance.container_name], capture_output=True, check=False)
        self._is_running[index] = False

        self._wait_until_member(index, False)

# ################################################################################################################################

    def kill_instance(self, index:'int', *, needs_wait:'bool'=True) -> 'None':
        """ Kills an instance outright, paused or not - what it had in its socket buffers but had not read yet is gone
        with it, which a graceful stop would let it finish first. The data on disk stays, so start_instance brings
        the same instance back. A test that has every other instance paused asks not to wait, since nothing can
        answer about the membership until it resumes them.
        """
        instance = self.instances[index]
        print(f'Killing Kafka instance {index} ({instance.container_name})', flush=True)

        _ = subprocess.run(['docker', 'kill', '--signal', 'KILL', instance.container_name], capture_output=True, check=False)
        self._is_paused[index] = False
        self._is_running[index] = False

        if needs_wait:
            self._wait_until_member(index, False)

# ################################################################################################################################

    def start_instance(self, index:'int', *, needs_wait:'bool'=True) -> 'None':
        """ Starts a stopped instance again and waits until the cluster lists it - unless told not to, which is for
        starting several at once when the ones that are up are too few to answer about anything.
        """
        instance = self.instances[index]
        print(f'Starting Kafka instance {index} ({instance.container_name})', flush=True)

        result = subprocess.run(['docker', 'start', instance.container_name], capture_output=True, check=False)

        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8')
            raise Exception(f'Could not start `{instance.container_name}`, stderr: `{stderr}`')

        self._is_running[index] = True

        if needs_wait:
            self._wait_until_member(index, True)

# ################################################################################################################################

    def pause_instance(self, index:'int') -> 'None':
        """ Freezes an instance - its ports stay open but nothing answers, which is what a hung instance looks like.
        Returns once the rest of the cluster has fenced it.
        """
        instance = self.instances[index]
        print(f'Pausing Kafka instance {index} ({instance.container_name})', flush=True)

        _ = subprocess.run(['docker', 'pause', instance.container_name], capture_output=True, check=False)
        self._is_paused[index] = True

        self._wait_until_member(index, False)

# ################################################################################################################################

    def pause_instance_now(self, index:'int') -> 'None':
        """ Freezes an instance without waiting for the cluster to notice - for tests that need the pause
        to land between a confirmation and the replication that would have followed it.
        """
        instance = self.instances[index]
        _ = subprocess.run(['docker', 'pause', instance.container_name], capture_output=True, check=False)
        self._is_paused[index] = True

# ################################################################################################################################

    def resume_instance(self, index:'int', *, needs_wait:'bool'=True) -> 'None':
        """ Thaws a paused instance and waits until the cluster lists it again.
        """
        instance = self.instances[index]
        print(f'Resuming Kafka instance {index} ({instance.container_name})', flush=True)

        _ = subprocess.run(['docker', 'unpause', instance.container_name], capture_output=True, check=False)
        self._is_paused[index] = False

        if needs_wait:
            self._wait_until_member(index, True)

# ################################################################################################################################

    def restore_all(self) -> 'None':
        """ Brings every instance back to running and unpaused, whatever state a test left it in.
        """
        # Every paused or stopped one is brought back before any is waited for - the first one back cannot answer on its own
        paused = [instance.index for instance in self.instances if self._is_paused[instance.index]]
        stopped = [instance.index for instance in self.instances if not self._is_running[instance.index]]

        for index in paused:
            self.resume_instance(index, needs_wait=False)

        for index in stopped:
            self.start_instance(index, needs_wait=False)

        for index in paused + stopped:
            self._wait_until_member(index, True)

# ################################################################################################################################

    def create_topic(
        self,
        topic:'str',
        partitions:'int'=ModuleCtx.Default_Partitions,
        replication_factor:'int | None'=None,
        config:'strdict | None'=None,
        ) -> 'None':
        """ Creates a topic through a reachable instance, replicated to every instance unless told otherwise.
        """
        instance = self.running_instances()[0]
        port = int(instance.address.rsplit(':', 1)[1])
        replication_factor = replication_factor or len(self.instances)

        create_topic(instance.container_name, topic, partitions, port, replication_factor, config)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Removes every container and the network - the containers were not started with --rm
        because a stopped one has to be startable again.
        """
        for instance in self.instances:
            _ = subprocess.run(['docker', 'rm', '-f', instance.container_name], capture_output=True, check=False)

        _ = subprocess.run(['docker', 'network', 'rm', ClusterCtx.Network], capture_output=True, check=False)

# ################################################################################################################################
# ################################################################################################################################

def _cluster_instance(index:'int') -> 'KafkaInstance':
    """ The names and host addresses of one instance - node ids start from 1 as Kafka's own examples do.
    """
    node_id = index + 1
    plaintext_port = ClusterCtx.Plaintext_Port_Base + node_id
    ssl_port = ClusterCtx.SSL_Port_Base + node_id

    out = KafkaInstance(
        index=index,
        node_id=node_id,
        container_name=f'{ClusterCtx.Container_Prefix}{node_id}',
        address=f'localhost:{plaintext_port}',
        ssl_address=f'localhost:{ssl_port}',
    )

    return out

# ################################################################################################################################

def _cluster_properties(instance:'KafkaInstance', instances:'list[KafkaInstance]', tls:'KafkaTLS') -> 'strdict':
    """ The configuration of one cluster instance - clients from the host use the per-instance localhost ports,
    the instances talk to each other by container name on the internal and controller listeners.
    """
    instance_count = len(instances)
    plaintext_port = instance.address.rsplit(':', 1)[1]
    ssl_port = instance.ssl_address.rsplit(':', 1)[1]
    internal_port = ClusterCtx.Internal_Port
    controller_port = ClusterCtx.Controller_Port

    voters = ','.join(f'{elem.node_id}@{elem.container_name}:{controller_port}' for elem in instances)

    out = {
        'node.id': str(instance.node_id),
        'process.roles': 'broker,controller',
        'listeners': (
            f'PLAINTEXT://0.0.0.0:{plaintext_port},SSL://0.0.0.0:{ssl_port},'
            f'INTERNAL://0.0.0.0:{internal_port},CONTROLLER://0.0.0.0:{controller_port}'
        ),
        'advertised.listeners': (
            f'PLAINTEXT://localhost:{plaintext_port},SSL://localhost:{ssl_port},'
            f'INTERNAL://{instance.container_name}:{internal_port}'
        ),
        'controller.listener.names': 'CONTROLLER',
        'inter.broker.listener.name': 'INTERNAL',
        'controller.quorum.voters': voters,
        'listener.security.protocol.map': 'PLAINTEXT:PLAINTEXT,SSL:SSL,INTERNAL:PLAINTEXT,CONTROLLER:PLAINTEXT',
        'default.replication.factor': str(instance_count),
        'offsets.topic.replication.factor': str(instance_count),
        'transaction.state.log.replication.factor': str(instance_count),
        'transaction.state.log.min.isr': str(instance_count - 1),
        'share.coordinator.state.topic.replication.factor': str(instance_count),
        'share.coordinator.state.topic.min.isr': str(instance_count - 1),
        'min.insync.replicas': str(instance_count - 1),
        # A paused follower stays in sync for this long, so a test that pauses one for a while sees the leader
        # wait for it rather than shrink the in-sync set under it - a stopped instance leaves the set at once regardless
        'replica.lag.time.max.ms': str(ClusterCtx.Replica_Lag_Max_Ms),
        'group.initial.rebalance.delay.ms': '0',
        'auto.create.topics.enable': 'true',
        'log.dirs': '/tmp/kraft-combined-logs',
    }

    # The certificates are shared by all the instances and mounted apart from each one's own configuration
    for key, value in tls_properties(tls).items():
        out[key] = value.replace(ModuleCtx.Config_Dir, ClusterCtx.Certificates_Dir)

    return out

# ################################################################################################################################

def _wait_until_cluster_ready(cluster:'KafkaCluster') -> 'None':
    """ Waits until every instance is a member - a quorum that has not formed yet answers nothing at all.
    """
    expected = {instance.node_id for instance in cluster.instances}

    def _check() -> 'bool':
        return cluster.live_node_ids() == expected

    wait_until(_check, f'all {len(expected)} Kafka instances to join the cluster')

# ################################################################################################################################

def start_kafka_cluster(instance_count:'int'=3) -> 'KafkaCluster':
    """ Starts N KRaft Kafka containers on one Docker network with a quorum of all N controllers.
    Topics are replicated to every instance and need N minus 1 of them in sync for a write with all confirmations.
    """
    instances = [_cluster_instance(index) for index in range(instance_count)]

    print(f'Starting a Kafka cluster of {instance_count} instances', flush=True)

    # Whatever a previous run left behind goes first
    for instance in instances:
        _remove_stale_container(instance.container_name)

    _ = subprocess.run(['docker', 'network', 'rm', ClusterCtx.Network], capture_output=True, check=False)

    result = subprocess.run(['docker', 'network', 'create', ClusterCtx.Network], capture_output=True, check=False)

    if result.returncode != 0:
        stderr = result.stderr.decode('utf-8')
        raise Exception(f'Could not create network `{ClusterCtx.Network}`, stderr: `{stderr}`')

    # One set of certificates for all of them - the server certificate is for localhost, which every instance is to the host
    certificates_dir = new_config_directory()
    tls = generate_kafka_tls(certificates_dir)

    for instance in instances:

        config_dir = new_config_directory()
        write_server_properties(config_dir, _cluster_properties(instance, instances, tls))

        plaintext_port = instance.address.rsplit(':', 1)[1]
        ssl_port = instance.ssl_address.rsplit(':', 1)[1]

        command:'strlist' = [
            'docker', 'run', '-d',
            '--name', instance.container_name,
            '--network', ClusterCtx.Network,
            '-e', f'CLUSTER_ID={ClusterCtx.Cluster_Id}',
            '-v', f'{config_dir}:{ModuleCtx.Config_Dir}:ro',
            '-v', f'{certificates_dir}:{ClusterCtx.Certificates_Dir}:ro',
            '-p', f'{plaintext_port}:{plaintext_port}',
            '-p', f'{ssl_port}:{ssl_port}',
            ModuleCtx.Kafka_Image,
        ]

        run_container(instance.container_name, command)

    cluster = KafkaCluster(instances, tls)

    print('Waiting for the Kafka cluster to form', flush=True)
    _wait_until_cluster_ready(cluster)
    print(f'Kafka cluster is ready at {cluster.bootstrap}', flush=True)

    return cluster

# ################################################################################################################################
# ################################################################################################################################
