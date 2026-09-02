# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
from time import sleep, time
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

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

    # Name of the container so stale ones can be removed
    Kafka_Container = 'zato-kafka-test'

    # How long to wait for the broker to accept connections
    Ready_Timeout = 300

    # How long to sleep between readiness checks
    Ready_Sleep = 2

    # Where the Kafka CLI tools live inside the container
    Kafka_Bin_Dir = '/opt/kafka/bin'

# ################################################################################################################################
# ################################################################################################################################

class KafkaServer(NamedTuple):
    container_name: str
    address: str

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

def _wait_until_ready(container_name:'str', port:'int') -> 'None':
    """ Retries listing topics inside the container until the broker responds or the timeout is reached.
    """
    deadline = time() + ModuleCtx.Ready_Timeout
    last_output = ''

    command = [
        'docker', 'exec', container_name,
        f'{ModuleCtx.Kafka_Bin_Dir}/kafka-topics.sh',
        '--bootstrap-server', f'localhost:{port}',
        '--list',
    ]

    while time() < deadline:
        result = subprocess.run(command, capture_output=True, check=False)
        if result.returncode == 0:
            return

        last_output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
        sleep(ModuleCtx.Ready_Sleep)

    raise Exception(f'Kafka broker in `{container_name}` did not become ready, last output: {last_output}')

# ################################################################################################################################

def create_topic(container_name:'str', topic:'str') -> 'None':
    """ Creates a topic inside the container - consumers subscribed to a topic that does not exist yet
    would only discover it on their next metadata refresh, which is minutes away by default.
    """
    command = [
        'docker', 'exec', container_name,
        f'{ModuleCtx.Kafka_Bin_Dir}/kafka-topics.sh',
        '--bootstrap-server', f'localhost:{ModuleCtx.Kafka_Port}',
        '--create',
        '--topic', topic,
    ]

    result = subprocess.run(command, capture_output=True, check=False)

    if result.returncode != 0:
        stdout = result.stdout.decode('utf-8')
        stderr = result.stderr.decode('utf-8')
        raise Exception(f'Could not create topic `{topic}` in `{container_name}`, stdout: `{stdout}`, stderr: `{stderr}`')

# ################################################################################################################################

def start_kafka() -> 'KafkaServer':
    """ Starts a single-node KRaft Kafka container that clients on the host reach through localhost.
    """
    container_name = ModuleCtx.Kafka_Container
    port = ModuleCtx.Kafka_Port
    controller_port = ModuleCtx.Controller_Port

    # Starting a container is silent and can take a while, e.g. when the image needs to be pulled first,
    # which is why each phase reports itself.
    print(f'Starting Kafka container {container_name} on port {port}', flush=True)

    _remove_stale_container(container_name)

    # The broker listens on the same port inside and outside the container,
    # which keeps the advertised listener valid for host clients and in-container tools alike.
    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', container_name,
        '-e', 'KAFKA_NODE_ID=1',
        '-e', 'KAFKA_PROCESS_ROLES=broker,controller',
        '-e', f'KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:{port},CONTROLLER://0.0.0.0:{controller_port}',
        '-e', f'KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:{port}',
        '-e', 'KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER',
        '-e', f'KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:{controller_port}',
        '-e', 'KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT',
        '-e', 'KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1',
        '-e', 'KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS=0',
        '-e', 'KAFKA_AUTO_CREATE_TOPICS_ENABLE=true',
        '-p', f'{port}:{port}',
        ModuleCtx.Kafka_Image,
    ]

    # Start the container, surfacing docker's own error message if the command fails -
    # a bare CalledProcessError hides both stdout and stderr.
    result = subprocess.run(command, capture_output=True, check=False)

    if result.returncode != 0:
        stdout = result.stdout.decode('utf-8')
        stderr = result.stderr.decode('utf-8')
        raise Exception(f'Could not start `{container_name}`, stdout: `{stdout}`, stderr: `{stderr}`')

    # Wait until the broker responds to a metadata request
    print(f'Waiting for Kafka container {container_name} to accept connections', flush=True)
    _wait_until_ready(container_name, port)
    print(f'Kafka container {container_name} is ready', flush=True)

    out = KafkaServer(container_name=container_name, address=f'localhost:{port}')
    return out

# ################################################################################################################################
# ################################################################################################################################
