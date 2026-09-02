# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import subprocess
from time import sleep, time
from typing import NamedTuple

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from mq_certificates import CertificatePaths
    from zato.common.typing_ import optional, strlist

    CertificatePaths = CertificatePaths
    certificatepathsnone = optional[CertificatePaths]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Docker image the queue manager runs from
    MQ_Image = 'icr.io/ibm-messaging/mq:latest'

    # Host ports the containers listen on
    MQ_Port     = 21414
    MQ_SSL_Port = 21415

    # Names of the containers so stale ones can be removed
    MQ_Container     = 'zato-ibm-mq-test'
    MQ_SSL_Container = 'zato-ibm-mq-test-ssl'

    # Queue manager details, matching the image's developer defaults
    Queue_Manager      = 'QM1'
    MQ_Channel_Name    = 'DEV.APP.SVRCONN'
    Request_Queue      = 'DEV.QUEUE.1'
    Reply_Queue        = 'DEV.QUEUE.2'
    Keep_Headers_Queue = 'DEV.QUEUE.3'

    # Credentials the developer defaults grant access to
    Username = 'app'
    Password = 'test-ibm-mq-password'

    # Cipher the developer defaults set on the SVRCONN channel when TLS is enabled
    Cipher_Spec = 'ANY_TLS12_OR_HIGHER'

    # How long to wait for the queue manager to accept connections
    Ready_Timeout = 300

    # How long to sleep between readiness checks
    Ready_Sleep = 2

    # How long to wait for a host port to be released by whatever container still holds it
    Port_Free_Timeout = 120

    # How long to sleep between checks of whether a host port can be bound
    Port_Free_Sleep = 1

    # How many times starting the container is attempted while its host port is still busy
    Start_Attempts = 5

    # What docker says when the host port is not free yet
    Port_In_Use_Marker = 'address already in use'

    # Hard resource limits for the container so a test run can never overwhelm the host -
    # queue manager startup is CPU-hungry and spawns hundreds of processes if left unbounded
    CPU_Limit    = '2'
    Memory_Limit = '2g'
    PID_Limit    = '2048'

# ################################################################################################################################
# ################################################################################################################################

class MQServer(NamedTuple):
    container_name: str
    address: str

# ################################################################################################################################
# ################################################################################################################################

def _remove_stale_container(name:'str') -> 'None':
    """ Removes a container left over from a previous, possibly interrupted, run.
    """
    _ = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, check=False)

# ################################################################################################################################

def _remove_containers_using_port(port:'int') -> 'None':
    """ Removes any container publishing the host port, whatever its name is - a container
    from an interrupted run keeps the port bound and docker run would refuse to start ours.
    """
    result = subprocess.run(
        ['docker', 'ps', '-a', '--filter', f'publish={port}', '--format', '{{.Names}}'],
        capture_output=True,
        check=False,
    )

    names = result.stdout.decode('utf-8').split()

    for name in names:
        _ = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, check=False)

# ################################################################################################################################

def _wait_until_port_is_free(port:'int') -> 'None':
    """ Waits until the host port can be bound - docker releases a published port asynchronously
    after a container goes away, so a start following a stop can otherwise race with it.
    """
    deadline = time() + ModuleCtx.Port_Free_Timeout

    while time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:

            # Without this a port left in TIME_WAIT would look busy even though docker could publish it
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                test_socket.bind(('0.0.0.0', port))
            except OSError:
                sleep(ModuleCtx.Port_Free_Sleep)
            else:
                return

    raise Exception(f'Host port {port} was still in use after {ModuleCtx.Port_Free_Timeout}s')

# ################################################################################################################################

def stop_container(name:'str') -> 'None':
    """ Stops a container - it removes itself because it was started with --rm.
    """
    _ = subprocess.run(['docker', 'stop', name], capture_output=True, check=False)

# ################################################################################################################################

def _wait_until_ready(container_name:'str') -> 'None':
    """ Retries the in-container readiness check until the queue manager is up or the timeout is reached.
    """
    deadline = time() + ModuleCtx.Ready_Timeout
    last_output = ''

    while time() < deadline:
        result = subprocess.run(
            ['docker', 'exec', container_name, 'chkmqready'],
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            return

        last_output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
        sleep(ModuleCtx.Ready_Sleep)

    raise Exception(f'Queue manager in `{container_name}` did not become ready, last output: {last_output}')

# ################################################################################################################################

def start_ibm_mq(*, needs_ssl:'bool', certificates:'certificatepathsnone' = None) -> 'MQServer':
    """ Starts an IBM MQ container, optionally one whose developer channels require TLS.
    Certificates are always given when needs_ssl is True and they are dereferenced only then.
    """
    ssl_certificates:'CertificatePaths' = cast_('CertificatePaths', certificates)

    if needs_ssl:
        container_name = ModuleCtx.MQ_SSL_Container
        port = ModuleCtx.MQ_SSL_Port
    else:
        container_name = ModuleCtx.MQ_Container
        port = ModuleCtx.MQ_Port

    _remove_stale_container(container_name)
    _remove_containers_using_port(port)

    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', container_name,
        '--cpus', ModuleCtx.CPU_Limit,
        '--memory', ModuleCtx.Memory_Limit,
        '--pids-limit', ModuleCtx.PID_Limit,
        '-e', 'LICENSE=accept',
        '-e', 'MQ_QMGR_NAME=' + ModuleCtx.Queue_Manager,
        '-e', 'MQ_APP_PASSWORD=' + ModuleCtx.Password,

        # The web console is a Java server the tests never talk to and it is by far
        # the most expensive part of the container, so it stays off.
        '-e', 'MQ_ENABLE_EMBEDDED_WEB_SERVER=false',

        '-p', f'{port}:1414',
    ]

    # The TLS-required variant mounts the server certificate and key where the image
    # picks them up, setting the developer channels' cipher spec to ANY_TLS12_OR_HIGHER.
    if needs_ssl:
        command.extend(['-v', f'{ssl_certificates.server_keys_directory}:/etc/mqm/pki/keys/default:ro'])

    command.append(ModuleCtx.MQ_Image)

    # Start the container, surfacing docker's own error message if the command fails -
    # a bare CalledProcessError hides both stdout and stderr.
    is_started = False
    last_stdout = ''
    last_stderr = ''

    for _ in range(ModuleCtx.Start_Attempts):

        # The port a previous container published may still be going away, so it is confirmed free first
        _wait_until_port_is_free(port)

        result = subprocess.run(command, capture_output=True, check=False)

        if result.returncode == 0:
            is_started = True
            break

        last_stdout = result.stdout.decode('utf-8')
        last_stderr = result.stderr.decode('utf-8')

        # Docker creates the container before it sets its networking up, so a failed attempt leaves one behind
        _remove_stale_container(container_name)

        # Anything other than a port that is still busy is a real error and retrying would not help
        if ModuleCtx.Port_In_Use_Marker not in last_stderr:
            break

        sleep(ModuleCtx.Port_Free_Sleep)

    if not is_started:
        raise Exception(f'Could not start `{container_name}`, stdout: `{last_stdout}`, stderr: `{last_stderr}`')

    # Wait until the queue manager reports it is ready to accept connections
    _wait_until_ready(container_name)

    out = MQServer(container_name=container_name, address=f'localhost:{port}')
    return out

# ################################################################################################################################
# ################################################################################################################################
