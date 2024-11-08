# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.aux_server.base import AuxServer, AuxServerConfig
from zato.common.crypto.api import ServerCryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class IPCServerConfig(AuxServerConfig):
    ipc_port: 'int'

# ################################################################################################################################
# ################################################################################################################################

class IPCServer(AuxServer):
    callback_func: 'callable_'
    needs_logging_setup = False
    cid_prefix = 'zipc'
    server_type = 'IPCServer'
    conf_file_name = 'server.conf'
    config_class = AuxServerConfig
    crypto_manager_class = ServerCryptoManager

    def on_ipc_msg_SERVER_IPC_INVOKE(self, msg:'Bunch') -> 'str':
        return self.config.callback_func(msg)

# ################################################################################################################################

    def get_action_func_impl(self, action_name:'str') -> 'callable_':
        func_name = 'on_ipc_msg_{}'.format(action_name)
        func = getattr(self, func_name)
        return func

# ################################################################################################################################
# ################################################################################################################################

def main():

    # stdlib
    import logging
    import os

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    def my_callback(msg:'Bunch') -> 'str':
        return 'Hello'

    bind_host = '127.0.0.1'
    bind_port = 17050
    base_dir = os.environ['Zato_Test_Server_Root_Dir']
    username = 'test.username'
    password = 'test.password'
    server_type_suffix = ':test'

    IPCServer.start_from_repo_location(
        base_dir=base_dir,
        bind_host=bind_host,
        bind_port=bind_port,
        username=username,
        password=password,
        callback_func=my_callback,
        server_type_suffix=server_type_suffix
    )

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
