# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The two nodes of an active-standby pair, each in a container of the published Zato image, which is used as it is.
# The current tree, the node binary, the start script, the certificates and the home directory of each node
# are mounted into its container, and the node starts the Zato server of the container whenever it is active.

# stdlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from http.client import OK
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Zato
from topology import docker, ModuleCtx as TopologyCtx, remove_container, save_container_logs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from certificates import Authority
    from topology import Consul
    from zato.common.typing_ import anydict, strlist, strstrdict

    # Dummy assignments to satisfy type checkers
    Authority = Authority
    Consul = Consul

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.nodes')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The published image that every node runs
    Zato_Image = 'zatosource/zato-4.1:latest'

    # The repository with the current tree, mounted at its own path
    Repository_Dir = os.environ['ZATO_TEST_BASE_DIR']

    # The node binary and the zato command of the current tree
    Node_Binary = os.path.join(Repository_Dir, 'code', 'bin', '_zato_ha_node')
    Zato_Binary = os.path.join(Repository_Dir, 'code', 'bin', 'zato')

    # The script that the container runs in place of the entrypoint of the image
    Start_Script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ha-start.sh')

    # The ports of each node, the same on both, as each node has an address of its own
    Server_Port      = 17010
    Replication_Port = 35200
    Role_Port        = 35201

    # The addresses of the nodes, by their short names
    Node_IPs = {
        'a': '10.231.77.21',
        'b': '10.231.77.22',
    }

    # How long a request to the role endpoint or to the server may take, in seconds
    Request_Timeout = 2

    # How often the role of a node is read while a test waits for it, in seconds
    Poll_Interval = 0.2

    # How long a container may take to stop gracefully, in seconds
    Stop_Timeout = 20

    # The roles in which a node serves requests
    Active_Roles = ('ActiveSolo', 'ActiveReplicated')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Timers:
    """ The timers of both nodes, in seconds.
    """
    heartbeat: 'float' = 0.5
    mark_out:  'float' = 3.0
    takeover:  'float' = 6.0

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Node:
    """ One node of the pair and the container it runs in.
    """
    short_name: 'str'
    run_dir: 'str'
    env: 'strstrdict' = field(default_factory=dict)

    # The variables that a fault adds to the environment of the next start, e.g. a preloaded library
    fault_env: 'strstrdict' = field(default_factory=dict)

    # The host directories that a fault mounts into the container at the next start, at the same path
    fault_mounts: 'strlist' = field(default_factory=list)

    # The server directory, which the quickstart environment of the node creates
    server_directory: 'str' = ''

# ################################################################################################################################

    @property
    def node_name(self) -> 'str':
        out = f'zato-ha-{self.short_name}'
        return out

    @property
    def container_name(self) -> 'str':
        out = f'zato-ha-test-{self.short_name}'
        return out

    @property
    def ip(self) -> 'str':
        out = ModuleCtx.Node_IPs[self.short_name]
        return out

    @property
    def directory(self) -> 'str':
        out = os.path.join(self.run_dir, f'node-{self.short_name}')
        return out

    @property
    def home_dir(self) -> 'str':
        out = os.path.join(self.directory, 'home')
        return out

    @property
    def data_dir(self) -> 'str':
        out = os.path.join(self.home_dir, 'env', 'qs-1')
        return out

    @property
    def cert_dir(self) -> 'str':
        out = os.path.join(self.directory, 'certs')
        return out

    @property
    def server_url(self) -> 'str':
        out = f'http://{self.ip}:{ModuleCtx.Server_Port}'
        return out

    @property
    def role_url(self) -> 'str':
        out = f'http://{self.ip}:{ModuleCtx.Role_Port}/zato/ha/role'
        return out

    def db_path(self, file_name:'str') -> 'str':
        out = os.path.join(self.data_dir, file_name)
        return out

# ################################################################################################################################

    def prepare(self, authority:'Authority', consul:'Consul', timers:'Timers') -> 'None':
        """ Creates the directories and the certificate of the node and fills in its environment.
        """
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.cert_dir, exist_ok=True)

        issued = authority.issue(self.node_name, [self.node_name], [self.ip])

        self.env.update({
            'HOME': self.home_dir,
            'Zato_HA_Mode': 'active-standby',
            'Zato_HA_Referee_Type': 'consul',
            'Zato_HA_Consul_Address': consul.address,
            'Zato_HA_Consul_Token': consul.node_token,
            'Zato_HA_Consul_CA_File': authority.cert_path,
            'Zato_HA_Consul_Key': TopologyCtx.Consul_Key,
            'Zato_HA_Node_Name': self.node_name,
            'Zato_HA_Advertised_Address': self.ip,
            'Zato_HA_Replication_Port': str(ModuleCtx.Replication_Port),
            'Zato_HA_Role_Port': str(ModuleCtx.Role_Port),
            'Zato_HA_Data_Dir': self.data_dir,
            'Zato_HA_TLS_CA_File': authority.cert_path,
            'Zato_HA_TLS_Cert_File': issued.cert_path,
            'Zato_HA_TLS_Key_File': issued.key_path,
            'Zato_HA_Heartbeat_Time': str(timers.heartbeat),
            'Zato_HA_Mark_Out_Time': str(timers.mark_out),
            'Zato_HA_Takeover_Time': str(timers.takeover),
            'Zato_HA_Log_Level': 'info',
            'Zato_Config_Bind_Port': str(ModuleCtx.Server_Port),
            'Zato_Test_HA_Node_Binary': ModuleCtx.Node_Binary,
            'Zato_Test_Zato_Binary': ModuleCtx.Zato_Binary,
        })

# ################################################################################################################################

    def _run_command(self) -> 'strlist':
        """ Builds the docker run command of the node.
        """
        out:'strlist' = [
            'run', '-d',
            '--name', self.container_name,
            '--hostname', self.node_name,
            '--network', TopologyCtx.Network_Name,
            '--ip', self.ip,
            '--user', f'{os.getuid()}:{os.getgid()}',
            '-v', f'{ModuleCtx.Repository_Dir}:{ModuleCtx.Repository_Dir}',
            '-v', f'{self.run_dir}:{self.run_dir}',
            '-v', f'{ModuleCtx.Start_Script}:/ha-start.sh:ro',
        ]

        for path in self.fault_mounts:
            out.extend(['-v', f'{path}:{path}'])

        environment = dict(self.env)
        environment['Zato_Test_Server_Directory'] = self.server_directory
        environment.update(self.fault_env)

        for name, value in environment.items():
            out.extend(['-e', f'{name}={value}'])

        out.extend(['--entrypoint', '/bin/bash', ModuleCtx.Zato_Image, '/ha-start.sh'])

        return out

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the node in a new container, with the data that its home directory holds.
        """
        remove_container(self.container_name)
        command = self._run_command()
        _ = docker(*command)

        logger.info('Node %s started at %s', self.node_name, self.ip)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the node gracefully, which stops its Zato server first.
        """
        _ = docker('stop', '-t', str(ModuleCtx.Stop_Timeout), self.container_name, check=False)

# ################################################################################################################################

    def kill(self) -> 'None':
        _ = docker('kill', '--signal', 'KILL', self.container_name, check=False)

# ################################################################################################################################

    def pause(self) -> 'None':
        _ = docker('pause', self.container_name)

# ################################################################################################################################

    def unpause(self) -> 'None':
        _ = docker('unpause', self.container_name)

# ################################################################################################################################

    def resume(self) -> 'None':
        """ Starts the stopped container of the node again.
        """
        _ = docker('start', self.container_name)

# ################################################################################################################################

    def remove(self) -> 'None':
        remove_container(self.container_name)

# ################################################################################################################################

    def save_logs(self, directory:'str') -> 'None':
        save_container_logs(self.container_name, directory)

# ################################################################################################################################

    def is_running(self) -> 'bool':
        result = docker('inspect', '--format', '{{.State.Running}}', self.container_name, check=False)

        out = result.stdout.strip() == 'true'
        return out

# ################################################################################################################################

    def read_role(self) -> 'anydict | None':
        """ Returns the role report of the node, or None if its role endpoint does not answer.
        """
        request = Request(self.role_url, method='GET')

        try:
            with urlopen(request, timeout=ModuleCtx.Request_Timeout) as response:
                body = response.read()

        # The node that does not serve requests answers 503 with the same report ..
        except HTTPError as e:
            body = e.read()

        # .. and a node that is down does not answer at all.
        except (URLError, OSError):
            return None

        out = json.loads(body)
        return out

# ################################################################################################################################

    def is_active(self) -> 'bool':
        report = self.read_role()

        if report is None:
            out = False
        elif report['isolated']:
            out = False
        else:
            out = report['role'] in ModuleCtx.Active_Roles

        return out

# ################################################################################################################################

    def wait_for_role(self, roles:'strlist', timeout:'float') -> 'anydict':
        """ Waits until the node reports one of the given roles and returns its report.
        """
        deadline = time.monotonic() + timeout
        report = None

        while time.monotonic() < deadline:
            report = self.read_role()

            if report is not None:
                if report['role'] in roles:
                    return report

            time.sleep(ModuleCtx.Poll_Interval)

        raise Exception(f'Node {self.node_name} not in any of {roles} after {timeout}s, last report -> {report}')

# ################################################################################################################################

    def is_server_up(self) -> 'bool':
        """ Returns whether the Zato server of the node answers its ping endpoint.
        """
        request = Request(f'{self.server_url}/zato/ping', method='GET')

        try:
            with urlopen(request, timeout=ModuleCtx.Request_Timeout) as response:
                out = response.status == OK
        except (OSError, URLError):
            out = False

        return out

# ################################################################################################################################

    def wait_until_server_up(self, timeout:'float') -> 'float':
        """ Waits until the Zato server of the node answers and returns how long it took, in seconds.
        """
        start = time.monotonic()
        deadline = start + timeout

        while not self.is_server_up():
            if time.monotonic() > deadline:
                logs = docker('logs', '--tail', '80', self.container_name, check=False)
                raise Exception(f'Server of {self.node_name} not up after {timeout}s:\n{logs.stdout}{logs.stderr}')
            time.sleep(ModuleCtx.Poll_Interval)

        out = time.monotonic() - start
        return out

# ################################################################################################################################

    def read_generation_file(self) -> 'int':
        """ Returns the highest generation the node has persisted, or 0 if it has persisted none.
        """
        path = self.db_path('ha-generation')

        if not os.path.exists(path):
            return 0

        with open(path) as generation_file:
            value = generation_file.read()

        out = int(value.strip())
        return out

# ################################################################################################################################
# ################################################################################################################################
