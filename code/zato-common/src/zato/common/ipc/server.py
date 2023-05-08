# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import captureWarnings, getLogger

# Zato
from zato.broker.client import BrokerClient
from zato.common.aux_server.base import AuxServer, AuxServerConfig
from zato.common.crypto.api import SchedulerCryptoManager
from zato.common.typing_ import cast_
from zato.common.util.api import get_config, set_up_logging
from zato.scheduler.api import SchedulerAPI
from zato.scheduler.util import set_up_zato_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
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
    pass

# ################################################################################################################################
# ################################################################################################################################

def main():

    ipc_port = 27050

    # Capture warnings to log files
    captureWarnings(True)

    # Where we keep our configuration
    repo_location = os.path.join('.', 'config', 'repo')

    # Logging configuration
    set_up_logging(repo_location)

    # The main configuration object
    config = IPCServerConfig.from_repo_location(
        f'IPCServer:{ipc_port}',
        repo_location,
        IPCServerConfig.conf_file_name,
        IPCServerConfig.crypto_manager_class,
    )
    config = cast_('IPCServerConfig', config)

    logger = getLogger(__name__)
    logger.info('{} starting (http{}://{}:{})'.format(
        config.server_type,
        's' if config.main.crypto.use_tls else '',
        config.main.bind.host,
        config.main.bind.port)
    )

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
