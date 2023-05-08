# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import captureWarnings, getLogger
from traceback import format_exc

# Zato
from zato.broker.client import BrokerClient
from zato.common.api import SCHEDULER
from zato.common.aux_server.base import AuxServer, AuxServerConfig
from zato.common.crypto.api import SchedulerCryptoManager
from zato.common.typing_ import cast_
from zato.common.util.api import get_config, set_up_logging, store_pidfile
from zato.scheduler.api import SchedulerAPI
from zato.scheduler.util import set_up_zato_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, type_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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

    @classmethod
    def start(class_:'type_[AuxServer]'):

        if 'ZATO_SCHEDULER_BASE_DIR' in os.environ:
            os.chdir(os.environ['ZATO_SCHEDULER_BASE_DIR'])

        # Always attempt to store the PID file first
        store_pidfile(os.path.abspath('.'))

        # Capture warnings to log files
        captureWarnings(True)

        # Where we keep our configuration
        repo_location = os.path.join('.', 'config', 'repo')

        # Logging configuration
        set_up_logging(repo_location)

        # The main configuration object
        config = SchedulerServerConfig.from_repo_location(
            'Scheduler',
            repo_location,
            SchedulerServer.conf_file_name,
            SchedulerServer.crypto_manager_class,
        )
        config = cast_('SchedulerServerConfig', config)

        logger = getLogger(__name__)
        logger.info('{} starting (http{}://{}:{})'.format(
            config.server_type,
            's' if config.main.crypto.use_tls else '',
            config.main.bind.host,
            config.main.bind.port)
        )

        # Reusable
        startup_jobs_config_file = 'startup_jobs.conf'

        # Fix up configuration so it uses the format that internal utilities expect
        startup_jobs_config = get_config(repo_location, startup_jobs_config_file, needs_user_config=False)
        for name, job_config in startup_jobs_config.items():

            # Ignore jobs that have been removed
            if name in SCHEDULER.JobsToIgnore:
                logger.info('Ignoring job `%s (%s)`', name, startup_jobs_config_file)
                continue

            job_config['name'] = name
            config.startup_jobs.append(job_config)

        # Run the scheduler server now
        try:
            SchedulerServer(config).serve_forever()
        except Exception:
            logger.warning(format_exc())

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
