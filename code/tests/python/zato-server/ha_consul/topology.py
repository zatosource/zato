# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The containers around an active-standby pair - one Docker bridge network with a fixed address per container,
# one Consul server with ACLs and TLS that serves as the referee, and HAProxy, which routes to the node
# whose role endpoint answers 200.

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
from uuid import uuid4

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_authority import Authority
    from zato.common.typing_ import any_, anydict, strlist

    # Dummy assignments to satisfy type checkers
    Authority = Authority

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.topology')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Where every run keeps its data, removed at the beginning and at the end of each run
    Runtime_Dir = '/tmp/zato-ha-test'

    # Where Consul keeps its data, in memory, so that the syncs of its log do not delay the syncs of the nodes,
    # as a referee on hosts of its own does not
    Consul_Data_Dir = '/dev/shm/zato-ha-test-consul'

    # The network of the run and the addresses on it
    Network_Name = 'zato-ha-test'
    Subnet       = '10.231.77.0/24'
    Gateway      = '10.231.77.1'
    Consul_IP    = '10.231.77.10'
    HAProxy_IP   = '10.231.77.11'

    # The pinned images of the referee and the load balancer
    Consul_Image  = 'hashicorp/consul:1.21.4'
    HAProxy_Image = 'haproxy:3.2.4'

    # The image with iptables and tc that joins the network namespace of a container
    Net_Image      = 'zato-pubsub-test-net:1'
    Net_Dockerfile = 'FROM alpine:latest\nRUN apk add --no-cache iptables iproute2-tc iproute2-minimal\n'

    # The names of the containers
    Consul_Container  = 'zato-ha-test-consul'
    HAProxy_Container = 'zato-ha-test-haproxy'

    # The HTTPS port of Consul and the key prefix that the nodes may write to
    Consul_HTTPS_Port = 8501
    Consul_Key        = 'zato/ha/test'

    # The port that HAProxy exposes to the test process
    HAProxy_Port = 11223

    # How long Consul may take to elect itself the leader, in seconds
    Consul_Ready_Timeout = 60

    # How long one request to Consul may take, in seconds
    Consul_Request_Timeout = 5

    # How often Consul is asked whether it is ready, in seconds
    Poll_Interval = 0.5

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
    shutil.rmtree(ModuleCtx.Consul_Data_Dir, ignore_errors=True)
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
    _ = docker('network', 'rm', ModuleCtx.Network_Name, check=False)

# ################################################################################################################################
# ################################################################################################################################

def _new_uuid() -> 'str':
    """ Returns a random UUID, which Consul expects of the secret of a token.
    """
    out = str(uuid4())
    return out

# ################################################################################################################################
# ################################################################################################################################

def _decode_value(value:'str') -> 'str':
    """ Decodes a value of the Consul key-value store, which Consul returns in Base64.
    """
    decoded = base64.b64decode(value)

    out = decoded.decode('utf8')
    return out

# ################################################################################################################################
# ################################################################################################################################

class Consul:
    """ One Consul server with ACLs and TLS, whose management token the test process uses and whose node token
    may only read and write the key prefix of the pair.
    """

    def __init__(self, authority:'Authority', run_dir:'str') -> 'None':
        self.authority = authority
        self.directory = os.path.join(run_dir, 'consul')
        self.config_dir = os.path.join(self.directory, 'config')
        self.data_dir = ModuleCtx.Consul_Data_Dir
        self.cert_dir = os.path.join(self.directory, 'certs')

        self.management_token = _new_uuid()
        self.node_token = _new_uuid()

        self.address = f'https://{ModuleCtx.Consul_IP}:{ModuleCtx.Consul_HTTPS_Port}'
        self.ssl_context = ssl.create_default_context(cafile=authority.cert_path)

# ################################################################################################################################

    def _write_config(self) -> 'None':
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.cert_dir, exist_ok=True)

        issued = self.authority.issue('consul', ['server.dc1.consul', 'localhost'], [ModuleCtx.Consul_IP, '127.0.0.1'])

        authority_path = os.path.join(self.cert_dir, 'ca.pem')
        cert_path = os.path.join(self.cert_dir, 'consul.pem')
        key_path = os.path.join(self.cert_dir, 'consul.key')

        _ = shutil.copyfile(self.authority.cert_path, authority_path)
        _ = shutil.copyfile(issued.cert_path, cert_path)
        _ = shutil.copyfile(issued.key_path, key_path)

        config = {
            'server': True,
            'bootstrap_expect': 1,
            'datacenter': 'dc1',
            'node_name': 'consul',
            'data_dir': '/consul/data',
            'client_addr': '0.0.0.0',
            'bind_addr': ModuleCtx.Consul_IP,
            'ports': {
                'http': -1,
                'https': ModuleCtx.Consul_HTTPS_Port,
            },
            'tls': {
                'defaults': {
                    'ca_file': '/consul/certs/ca.pem',
                    'cert_file': '/consul/certs/consul.pem',
                    'key_file': '/consul/certs/consul.key',
                    'verify_incoming': False,
                    'verify_outgoing': True,
                },
            },
            'acl': {
                'enabled': True,
                'default_policy': 'deny',
                'enable_token_persistence': True,
                'tokens': {
                    'initial_management': self.management_token,
                },
            },
        }

        config_path = os.path.join(self.config_dir, 'consul.json')

        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=2)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts Consul with its configuration and data from earlier starts, if any.
        """
        remove_container(ModuleCtx.Consul_Container)

        if not os.path.exists(self.config_dir):
            self._write_config()

        os.makedirs(self.data_dir, exist_ok=True)

        _ = docker(
            'run', '-d',
            '--name', ModuleCtx.Consul_Container,
            '--hostname', 'consul',
            '--network', ModuleCtx.Network_Name,
            '--ip', ModuleCtx.Consul_IP,
            '--user', f'{os.getuid()}:{os.getgid()}',

            # The entrypoint script of the image changes the owner of the data directory, which requires root
            '--entrypoint', 'consul',
            '-v', f'{self.config_dir}:/consul/config:ro',
            '-v', f'{self.data_dir}:/consul/data',
            '-v', f'{self.cert_dir}:/consul/certs:ro',
            ModuleCtx.Consul_Image,
            'agent', '-config-dir=/consul/config',
        )

        self.wait_until_ready()

# ################################################################################################################################

    def stop(self) -> 'None':
        _ = docker('stop', '-t', '10', ModuleCtx.Consul_Container, check=False)

# ################################################################################################################################

    def resume(self) -> 'None':
        """ Starts the stopped container of Consul again, with the data it had.
        """
        _ = docker('start', ModuleCtx.Consul_Container)
        self.wait_until_ready()

# ################################################################################################################################

    def recreate_without_data(self) -> 'None':
        """ Replaces Consul with one that has the same configuration and no data, as a referee that lost its data.
        """
        remove_container(ModuleCtx.Consul_Container)
        shutil.rmtree(self.data_dir, ignore_errors=True)
        self.start()
        self.create_node_token()

# ################################################################################################################################

    def remove(self) -> 'None':
        remove_container(ModuleCtx.Consul_Container)

# ################################################################################################################################

    def request(self, method:'str', path:'str', body:'any_'=None) -> 'any_':
        """ Sends one request with the management token and returns the decoded answer, or None if there is none.
        """
        url = f'{self.address}{path}'

        if body is None:
            data = None
        else:
            data = json.dumps(body).encode('utf8')

        request = Request(url, data=data, method=method)
        request.add_header('X-Consul-Token', self.management_token)

        with urlopen(request, timeout=ModuleCtx.Consul_Request_Timeout, context=self.ssl_context) as response:
            answer = response.read()

        if answer:
            out = json.loads(answer)
        else:
            out = None

        return out

# ################################################################################################################################

    def wait_until_ready(self) -> 'None':
        """ Waits until Consul has a leader and accepts the management token.
        """
        deadline = time.monotonic() + ModuleCtx.Consul_Ready_Timeout

        while True:
            try:
                leader = self.request('GET', '/v1/status/leader')
                if leader:
                    _ = self.request('GET', '/v1/acl/token/self')
                    break
            except (HTTPError, URLError, OSError) as e:
                if time.monotonic() > deadline:
                    raise Exception(f'Consul not ready after {ModuleCtx.Consul_Ready_Timeout}s -> {e}') from e

            time.sleep(ModuleCtx.Poll_Interval)

        logger.info('Consul ready at %s', self.address)

# ################################################################################################################################

    def create_node_token(self) -> 'None':
        """ Creates the policy that allows the key prefix of the pair only and the token of the nodes with it.
        """
        policy_name = 'zato-ha-test'
        rules = f'key_prefix "{ModuleCtx.Consul_Key}" {{ policy = "write" }}'

        policy = {
            'Name': policy_name,
            'Rules': rules,
        }

        token = {
            'SecretID': self.node_token,
            'Description': 'Zato active-standby nodes',
            'Policies': [{'Name': policy_name}],
        }

        _ = self.request('PUT', '/v1/acl/policy', policy)
        _ = self.request('PUT', '/v1/acl/token', token)

# ################################################################################################################################

    def read_record(self) -> 'anydict | None':
        """ Returns the referee record with its version, or None if the pair has not written one yet.
        """
        try:
            entries = self.request('GET', f'/v1/kv/{ModuleCtx.Consul_Key}')
        except HTTPError as e:
            if e.code == NOT_FOUND:
                return None
            raise

        entry = entries[0]
        value = _decode_value(entry['Value'])

        out = json.loads(value)
        out['version'] = entry['ModifyIndex']

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
