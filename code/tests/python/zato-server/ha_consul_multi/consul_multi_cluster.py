# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Three Consul servers with ACLs and TLS in place of the one server of the pair suite. Each node of the pair reaches
# the server on its own host through the single address of the node, and the third server holds the majority
# when either host is lost. The test process reaches whichever server answers.

# stdlib
import json
import logging
import os
import shutil
from urllib.error import HTTPError, URLError

# Zato
from topology import Consul, docker, ModuleCtx as TopologyCtx, remove_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_authority import Authority
    from zato.common.typing_ import any_, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul_multi.cluster')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The servers by name and their addresses on the network of the pair
    Server_IPs = {
        'consul-1': '10.231.77.31',
        'consul-2': '10.231.77.32',
        'consul-3': '10.231.77.33',
    }

    # The prefix of the containers of the servers
    Container_Prefix = 'zato-ha-test-'

    # Where the servers keep their data, in memory, as the server of the pair suite does
    Data_Dir = '/dev/shm/zato-ha-test-consul-multi'

    # The port of the Raft and RPC traffic between the servers, as /v1/status/leader reports it
    Server_Port = 8300

    # The status of an answer after which another server is asked, as a server without a leader answers it
    Status_Server_Error = 500

    # How long a server may take to stop gracefully, in seconds
    Stop_Timeout = 10

# ################################################################################################################################
# ################################################################################################################################

class ConsulServer:
    """ One Consul server of the cluster and its container.
    """

    def __init__(self, name:'str') -> 'None':
        self.name = name
        self.ip = ModuleCtx.Server_IPs[name]
        self.container_name = f'{ModuleCtx.Container_Prefix}{name}'
        self.data_dir = os.path.join(ModuleCtx.Data_Dir, name)
        self.address = f'https://{self.ip}:{TopologyCtx.Consul_HTTPS_Port}'

# ################################################################################################################################
# ################################################################################################################################

class ConsulCluster(Consul):
    """ The three Consul servers of a pair, with the management token and the node token of the one server
    of the pair suite.
    """

    def __init__(self, authority:'Authority', run_dir:'str') -> 'None':
        super().__init__(authority, run_dir)

        self.directory = os.path.join(run_dir, 'consul-multi')
        self.config_dir = os.path.join(self.directory, 'config')
        self.cert_dir = os.path.join(self.directory, 'certs')
        self.data_dir = ModuleCtx.Data_Dir

        self.servers:'list[ConsulServer]' = []
        self.container_names:'strlist' = []

        for name in ModuleCtx.Server_IPs:
            server = ConsulServer(name)
            self.servers.append(server)
            self.container_names.append(server.container_name)

        self.ip = self.servers[0].ip

        # The servers that a fault took away from the test process
        self.unavailable:'strset' = set()

# ################################################################################################################################

    def _write_config(self) -> 'None':
        """ Writes the certificate shared by the servers and the configuration of each server.
        """
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.cert_dir, exist_ok=True)

        ip_addresses = ['127.0.0.1']

        for server in self.servers:
            ip_addresses.append(server.ip)

        issued = self.authority.issue('consul', ['server.dc1.consul', 'localhost'], ip_addresses)

        _ = shutil.copyfile(self.authority.cert_path, os.path.join(self.cert_dir, 'ca.pem'))
        _ = shutil.copyfile(issued.cert_path, os.path.join(self.cert_dir, 'consul.pem'))
        _ = shutil.copyfile(issued.key_path, os.path.join(self.cert_dir, 'consul.key'))

        for server in self.servers:

            retry_join:'strlist' = []

            for other in self.servers:
                if other.name != server.name:
                    retry_join.append(other.ip)

            config = {
                'server': True,
                'bootstrap_expect': len(self.servers),
                'datacenter': 'dc1',
                'node_name': server.name,
                'data_dir': '/consul/data',
                'client_addr': '0.0.0.0',
                'bind_addr': server.ip,
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
                        'initial_management': self.management_token,
                    },
                },
            }

            server_config_dir = os.path.join(self.config_dir, server.name)
            os.makedirs(server_config_dir)

            with open(os.path.join(server_config_dir, 'consul.json'), 'w') as config_file:
                json.dump(config, config_file, indent=2)

# ################################################################################################################################

    def _start_server(self, server:'ConsulServer') -> 'None':
        os.makedirs(server.data_dir, exist_ok=True)

        _ = docker(
            'run', '-d',
            '--name', server.container_name,
            '--hostname', server.name,
            '--network', TopologyCtx.Network_Name,
            '--ip', server.ip,
            '--user', f'{os.getuid()}:{os.getgid()}',

            # The entrypoint script of the image changes the owner of the data directory, which requires root
            '--entrypoint', 'consul',
            '-v', f'{os.path.join(self.config_dir, server.name)}:/consul/config:ro',
            '-v', f'{server.data_dir}:/consul/data',
            '-v', f'{self.cert_dir}:/consul/certs:ro',
            TopologyCtx.Consul_Image,
            'agent', '-config-dir=/consul/config',
        )

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the three servers without data, waits until they elect a leader and creates the node token.
        """
        self.remove()

        shutil.rmtree(self.directory, ignore_errors=True)
        self._write_config()

        for server in self.servers:
            self._start_server(server)

        self.wait_until_ready()

# ################################################################################################################################

    def stop(self) -> 'None':
        for server in self.servers:
            _ = docker('stop', '-t', str(ModuleCtx.Stop_Timeout), server.container_name, check=False)
            self.unavailable.add(server.name)

# ################################################################################################################################

    def resume(self) -> 'None':
        """ Starts the stopped servers again, with the data they had.
        """
        for server in self.servers:
            _ = docker('start', server.container_name)
            self.unavailable.discard(server.name)

        self.wait_until_ready()

# ################################################################################################################################

    def remove(self) -> 'None':
        for server in self.servers:
            remove_container(server.container_name)

        shutil.rmtree(ModuleCtx.Data_Dir, ignore_errors=True)

# ################################################################################################################################

    def get_server(self, name:'str') -> 'ConsulServer':
        for server in self.servers:
            if server.name == name:
                return server

        raise Exception(f'No Consul server named {name}')

# ################################################################################################################################

    def get_leader(self) -> 'ConsulServer':
        """ Returns the server that the cluster reports as its leader.
        """
        leader = self.request('GET', '/v1/status/leader')
        assert leader, 'The Consul cluster has no leader'

        ip, _ = leader.rsplit(':', 1)

        for server in self.servers:
            if server.ip == ip:
                return server

        raise Exception(f'No Consul server at {leader}')

# ################################################################################################################################

    def request(self, method:'str', path:'str', body:'any_'=None) -> 'any_':
        """ Sends one request to the first server that answers it, skipping the servers that a fault took away
        and the servers without a leader.
        """
        last_error:'Exception | None' = None

        for server in self.servers:
            if server.name in self.unavailable:
                continue

            self.address = server.address

            try:
                out = super().request(method, path, body)
                return out

            except HTTPError as e:
                if e.code < ModuleCtx.Status_Server_Error:
                    raise
                last_error = e

            except (URLError, OSError) as e:
                last_error = e

        if last_error is None:
            raise Exception('No Consul server is available')

        raise last_error

# ################################################################################################################################
# ################################################################################################################################
