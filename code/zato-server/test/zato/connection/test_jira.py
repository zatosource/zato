# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import loads
from unittest import main, TestCase

# Zato
from zato.common.util.api import as_bool
from zato.common.util.open_ import open_r
from zato.server.connection.jira_ import JiraClient

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Env_Key_API_Version = 'Zato_Test_Jira_API_Version'
    Env_Key_Address = 'Zato_Test_Jira_Address'
    Env_Key_Username = 'Zato_Test_Jira_Username'
    Env_Key_Token = 'Zato_Test_Jira_Token'
    Env_Key_Is_Cloud = 'Zato_Test_Jira_Is_Cloud'

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:
    zato_api_version: 'str'
    zato_address: 'str'
    zato_username: 'str'
    zato_token: 'str'
    zato_is_cloud: 'bool'

# ################################################################################################################################
# ################################################################################################################################

class JiraClientTestCase(TestCase):

    def get_client(self) -> 'JiraClient | None':

        if not (zato_api_version := os.environ.get('Zato_Test_Jira_API_Version')):
            return None

        config = TestConfig()
        config.zato_api_version = zato_api_version
        config.zato_address = os.environ['Zato_Test_Jira_Address']
        config.zato_username = os.environ['Zato_Test_Jira_Username']
        config.zato_token = os.environ['Zato_Test_Jira_Token']
        config.zato_is_cloud = as_bool(os.environ['Zato_Test_Jira_Is_Cloud'])

        client = JiraClient(
            zato_api_version=config.zato_api_version,
            zato_address=config.zato_address,
            zato_username=config.zato_username,
            zato_token=config.zato_token,
            zato_is_cloud=config.zato_is_cloud,
        )

        return client

# ################################################################################################################################

    def test_ping(self):

        if not (client := self.get_client()):
            return

        client.ping()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
