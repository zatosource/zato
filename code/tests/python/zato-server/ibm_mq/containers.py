# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
from time import sleep, time
from typing import NamedTuple

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from certificates import CertificatePaths
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

    _ = subprocess.run(command, check=True, capture_output=True)

    # Wait until the queue manager reports it is ready to accept connections
    _wait_until_ready(container_name)

    out = MQServer(container_name=container_name, address=f'localhost:{port}')
    return out

# ################################################################################################################################
# ################################################################################################################################
