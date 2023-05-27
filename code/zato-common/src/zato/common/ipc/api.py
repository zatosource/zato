# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.ipc.server import IPCServer
from zato.common.util.api import load_ipc_pid_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class IPCAPI:
    """ API through which IPC is performed.
    """
    pid: 'int'
    server: 'IPCServer'
    username: 'str'
    password: 'str'
    on_message_callback: 'callable_'

    def __init__(self) -> 'None':
        self.username = 'ipc'
        self.password = ''

# ################################################################################################################################

    def set_password(self, password:'str') -> 'None':
        self.password = password

# ################################################################################################################################

    def start_server(
        self,
        pid,          # type: str
        base_dir,     # type: str
        *,
        bind_host='', # type: str
        bind_port=-1, # type: int
        username='',  # type: str
        password='',  # type: str
    ) -> 'None':

        def my_callback(msg:'Bunch') -> 'str':
            return 'Hello'

        server_type_suffix = f':{pid}'

        IPCServer.start(
            base_dir=base_dir,
            bind_host=bind_host,
            bind_port=bind_port,
            username=username,
            password=password,
            callback_func=my_callback,
            server_type_suffix=server_type_suffix
        )

# ################################################################################################################################

    def invoke_by_pid(
        self,
        service,      # type: str
        request,      # type: str
        cluster_name, # type: str
        server_name,  # type: str
        target_pid,   # type: int
        timeout=90    # type: int
    ) -> 'any_':
        """ Invokes a service in a specific process synchronously through IPC.
        """

        # Get the port that we can find the PID listening on
        ipc_port = load_ipc_pid_port(cluster_name, server_name, target_pid)

        # Log what we are about to do
        log_msg = f'Invoking {service} on {cluster_name}:{server_name}:{target_pid}-tcp:{ipc_port}'
        logger.info(log_msg)

        ipc_port
        ipc_port
        '''
        # Create a FIFO pipe to receive replies to come through
        fifo_path = os.path.join(tempfile.tempdir, 'zato-ipc-fifo-{}'.format(uuid4().hex))
        os.mkfifo(fifo_path, fifo_create_mode)

        logger.info('Invoking %s on %s (%s:%s) (%s) with %s',
            service, cluster_name, server_name, target_pid, fifo_path, payload)
            '''


# ################################################################################################################################
# ################################################################################################################################
