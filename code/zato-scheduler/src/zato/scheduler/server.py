# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import captureWarnings, getLogger

# Zato
from zato.broker.client import BrokerClient
from zato.common.api import SCHEDULER
from zato.common.aux_server.base import AuxServer, AuxServerConfig
from zato.common.crypto.api import SchedulerCryptoManager
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, get_config, store_pidfile
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

    # Our current status, e.g. active or paused
    current_status:'str' = SCHEDULER.Status.Active

    # Configuration via environment variables
    env_key_status   = SCHEDULER.Env.Status
    env_key_username = SCHEDULER.Env.Server_Username
    env_key_password = SCHEDULER.Env.Server_Password
    env_key_auth_required = SCHEDULER.Env.Server_Auth_Required

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
    needs_logging_setup = True
    cid_prefix = 'zsch'
    server_type = 'Scheduler'
    conf_file_name = 'scheduler.conf'
    config_class = SchedulerServerConfig
    crypto_manager_class = SchedulerCryptoManager

    def __init__(self, config:'AuxServerConfig') -> 'None':

        super().__init__(config)

        # Configures a client to Zato servers
        self.zato_client = set_up_zato_client(config.main)

        # Should the scheduler be started
        _should_run_scheduler = os.environ.get('Zato_Start_Scheduler') or True
        _should_run_scheduler = as_bool(_should_run_scheduler)
        self.should_run_scheduler = _should_run_scheduler

        # SchedulerAPI
        self.scheduler_api = SchedulerAPI(self.config) # type: ignore
        self.scheduler_api.broker_client = BrokerClient(zato_client=self.zato_client, server_rpc=None, scheduler_config=None)

# ################################################################################################################################

    def should_check_credentials(self) -> 'bool':

        api_clients = self.config.main.get('api_clients')
        api_clients = api_clients or self.config.main.get('api_users')
        api_clients = api_clients or {}

        auth_required = api_clients.get('auth_required')
        auth_required = auth_required or False

        return auth_required

# ################################################################################################################################

    @classmethod
    def before_config_hook(class_:'type_[AuxServer]') -> 'None':

        if 'ZATO_SCHEDULER_BASE_DIR' in os.environ:
            os.chdir(os.environ['ZATO_SCHEDULER_BASE_DIR'])

        # Always attempt to store the PID file first
        store_pidfile(os.path.abspath('.'))

        # Capture warnings to log files
        captureWarnings(True)

# ################################################################################################################################

    @classmethod
    def after_config_hook(
        class_, # type: type_[AuxServer]
        config, # type: AuxServerConfig
        repo_location, # type: str
    ) -> 'None':

        super().after_config_hook(config, repo_location)

        # Reusable
        startup_jobs_config_file = 'startup_jobs.conf'

        # Fix up configuration so it uses the format that internal utilities expect
        startup_jobs_config = get_config(repo_location, startup_jobs_config_file, needs_user_config=False)
        for name, job_config in startup_jobs_config.items(): # type: ignore

            # Ignore jobs that have been removed
            if name in SCHEDULER.JobsToIgnore:
                logger.info('Ignoring job `%s (%s)`', name, startup_jobs_config_file)
                continue

            job_config['name'] = name # type: ignore
            cast_('SchedulerServerConfig', config).startup_jobs.append(job_config)

# ################################################################################################################################

    def get_action_func_impl(self, action_name:'str') -> 'callable_':
        func_name = 'on_broker_msg_{}'.format(action_name)
        func = getattr(self.scheduler_api, func_name)
        return func

# ################################################################################################################################

    def serve_forever(self) -> 'None':
        if self.should_run_scheduler:
            self.scheduler_api.serve_forever()
        else:
            logger.info('Not starting the scheduler')
        super().serve_forever()

# ################################################################################################################################
# ################################################################################################################################
