# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# HAProxy in front of an active-standby pair, which routes to the node whose role endpoint answers 200.

# stdlib
import os

# Zato
from topology import docker, ModuleCtx as TopologyCtx, remove_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

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
        self.base_url = f'http://{TopologyCtx.HAProxy_IP}:{TopologyCtx.HAProxy_Port}'

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
            f'    bind :{TopologyCtx.HAProxy_Port}',
            '    default_backend zato_servers',
            '',
            'backend zato_servers',
            '    option httpchk GET /zato/ha/role',
            '    http-check expect status 200',
            f'    default-server inter {TopologyCtx.HAProxy_Check_Interval_Ms}ms fall 1 rise 1',
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
        remove_container(TopologyCtx.HAProxy_Container)
        config_path = self._write_config()

        _ = docker(
            'run', '-d',
            '--name', TopologyCtx.HAProxy_Container,
            '--network', TopologyCtx.Network_Name,
            '--ip', TopologyCtx.HAProxy_IP,
            '-v', f'{config_path}:/usr/local/etc/haproxy/haproxy.cfg:ro',
            TopologyCtx.HAProxy_Image,
        )

# ################################################################################################################################

    def restart(self) -> 'None':
        _ = docker('restart', '-t', '1', TopologyCtx.HAProxy_Container)

# ################################################################################################################################

    def remove(self) -> 'None':
        remove_container(TopologyCtx.HAProxy_Container)

# ################################################################################################################################
# ################################################################################################################################
