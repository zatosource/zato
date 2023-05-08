# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.broker.client import BrokerClient
from zato.common.aux_server.base import AuxServer, AuxServerConfig
from zato.common.crypto.api import SchedulerCryptoManager
from zato.scheduler.api import SchedulerAPI
from zato.scheduler.util import set_up_zato_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SchedulerServerConfig(AuxServerConfig):

    def __init__(self) -> 'None':
        super().__init__()

        self.startup_jobs = []
        self.on_job_executed_cb = None
        self.job_log_level = 'debug'
        self._add_startup_jobs = True
        self._add_scheduler_jobs = True

# ################################################################################################################################
# ################################################################################################################################

class SchedulerServer(AuxServer):
    """ Main class spawning scheduler-related tasks and listening for HTTP API requests.
    """
    cid_prefix = 'zsch'
    conf_file_name = 'scheduler.conf'
    crypto_manager_class = SchedulerCryptoManager

    def __init__(self, config:'SchedulerServerConfig') -> 'None':

        super().__init__(config)

        # Configures a client to Zato servers
        self.zato_client = set_up_zato_client(config.main)

        # SchedulerAPI
        self.scheduler_api = SchedulerAPI(self.config)
        self.scheduler_api.broker_client = BrokerClient(zato_client=self.zato_client, server_rpc=None, scheduler_config=None)

# ################################################################################################################################

    def action_func_impl(self, action_name:'str') -> 'callable_':

        func_name = 'on_broker_msg_{}'.format(action_name)
        func = getattr(self.scheduler_api, func_name)

        return func

# ################################################################################################################################

    def serve_forever(self) -> 'None':
        self.scheduler_api.serve_forever()
        super().serve_forever()

# ################################################################################################################################
# ################################################################################################################################
