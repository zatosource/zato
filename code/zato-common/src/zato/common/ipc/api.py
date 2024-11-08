# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import IPC
from zato.common.ipc.client import IPCClient
from zato.common.ipc.server import IPCServer
from zato.common.util.api import fs_safe_name, load_ipc_pid_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ipc.client import IPCResponse
    from zato.common.typing_ import callable_
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class IPCAPI:
    """ API through which IPC is performed.
    """
    pid: 'int'
    parallel_server: 'ParallelServer'
    username: 'str'
    password: 'str'
    on_message_callback: 'callable_'

    def __init__(self, parallel_server:'ParallelServer') -> 'None':
        self.parallel_server = parallel_server
        self.username = IPC.Credentials.Username
        self.password = ''

# ################################################################################################################################

    def set_password(self, password:'str') -> 'None':
        self.password = password

# ################################################################################################################################

    def start_server(
        self,
        pid,           # type: str
        base_dir,      # type: str
        *,
        bind_host='',  # type: str
        bind_port=-1,  # type: int
        username='',   # type: str
        password='',   # type: str
        callback_func, # type: callable_
    ) -> 'None':

        username = username or self.username
        password = password or self.password

        server_type_suffix = f':{pid}'

        IPCServer.start_from_repo_location(
            base_dir=base_dir,
            bind_host=bind_host,
            bind_port=bind_port,
            username=username,
            password=password,
            callback_func=callback_func,
            server_type_suffix=server_type_suffix
        )

# ################################################################################################################################

    def invoke_by_pid(
        self,
        use_tls,      # type: bool
        service,      # type: str
        request,      # type: str
        cluster_name, # type: str
        server_name,  # type: str
        target_pid,   # type: int
        timeout=90    # type: int
    ) -> 'IPCResponse':
        """ Invokes a service in a specific process synchronously through IPC.
        """

        # This is constant
        ipc_host = '127.0.0.1'

        # Get the port that we can find the PID listening on
        ipc_port = load_ipc_pid_port(cluster_name, server_name, target_pid)

        # Log what we are about to do
        log_msg = f'Invoking {service} on {cluster_name}:{server_name}:{target_pid}-tcp:{ipc_port}'
        logger.debug(log_msg)

        # Use this URL path to be able to easily find requests in logs
        url_path = f'{cluster_name}:{server_name}:{target_pid}-tcp:{ipc_port}-service:{service}'
        url_path = fs_safe_name(url_path)

        client = IPCClient(use_tls, ipc_host, ipc_port, IPC.Credentials.Username, self.password)
        response = client.invoke(
            service,
            request,
            url_path,
            cluster_name=cluster_name,
            server_name=server_name,
            server_pid=target_pid,
            timeout=timeout,
            source_server_name=self.parallel_server.name,
            source_server_pid=self.parallel_server.pid,
        )
        return response

# ################################################################################################################################
# ################################################################################################################################
