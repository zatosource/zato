# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from unittest import main, TestCase

# Zato
from zato.broker.client import BrokerClient
from zato.common.broker_message import SCHEDULER
from zato.common.test.config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

# Reusable test configuration
scheduler_config = {
    'scheduler_host': TestConfig.scheduler_host,
    'scheduler_port': TestConfig.scheduler_port,
    'scheduler_use_tls': False,
}

# ################################################################################################################################
# ################################################################################################################################

class InvokeSchedulerClientTestCase(TestCase):

    def test_client_invoke_server_to_scheduler_message_valid(self):

        if not (username := os.environ.get('Zato_Scheduler_API_Client_For_Server_Username')):
            return

        if not (password := os.environ.get('Zato_Scheduler_API_Client_For_Server_Password')):
            return

        # If we are here, it means that we have the credentials
        scheduler_config['scheduler_api_username'] = username
        scheduler_config['scheduler_api_password'] = password

        # Client that invokes the scheduler from servers
        client = BrokerClient(scheduler_config=scheduler_config)

        # Build a valid test message
        msg = {
            'action': SCHEDULER.EXECUTE.value,
            'name': 'zato.outgoing.sql.auto-ping'
        }

        response = client.invoke_sync(msg)

        cid = response['cid'] # type: str

        self.assertTrue(cid.startswith('zsch'))
        self.assertGreaterEqual(len(cid), 20)
        self.assertEqual(response['status'], 'ok')

# ################################################################################################################################

    def xtest_client_invoke_server_to_scheduler_invalid_request(self):

        if not (username := os.environ.get('Zato_Scheduler_API_Client_For_Server_Username')):
            return

        if not (password := os.environ.get('Zato_Scheduler_API_Client_For_Server_Password')):
            return

        # If we are here, it means that we have the credentials
        scheduler_config['scheduler_api_username'] = username
        scheduler_config['scheduler_api_password'] = password

        # Client that invokes the scheduler from servers
        client = BrokerClient(scheduler_config=scheduler_config)

        # Build an invalid test message
        msg = {
            'action': SCHEDULER.EXECUTE.value,
            'invalid-key':'invalid-value'
        }

        # This will check whether the scheduler replies with the expected metadata
        response = client.invoke_sync(msg)

        cid = response['cid'] # type: str

        self.assertTrue(cid.startswith('zsch'))
        self.assertGreaterEqual(len(cid), 20)
        self.assertEqual(response['status'], 'error')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
