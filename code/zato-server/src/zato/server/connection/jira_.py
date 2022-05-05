# -*- coding: utf-8 -*-

# atlassian-python-api
from atlassian import Jira as AtlassianJiraClient


# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

class JiraClient:

    api_version: 'str'
    address: 'str'
    username: 'str'
    api_token: 'str'
    is_cloud: 'bool'
    conn: 'AtlassianJiraClient'

    def __init__(
        self,
        *,
        api_version, # type: str
        address, # type: str
        username, # type: str
        api_token, # type: str
        is_cloud, # type: bool
    ) -> 'None':

        self.api_version = api_version
        self.address = address
        self.username = username
        self.api_token = api_token
        self.is_cloud = is_cloud

        self.conn = AtlassianJiraClient(
            url = self.address,
            username = self.username,
            api_token = self.api_token,
            api_version = self.api_version,
            cloud = self.is_cloud,
        )

# ################################################################################################################################

    @staticmethod
    def from_config(config:'stranydict') -> 'JiraClient':
        return JiraClient(
            api_version = config['api_version'],
            address = config['address'],
            username = config['username'],
            api_token = config['api_token'],
            is_cloud = config['is_cloud'],
        )

# ################################################################################################################################
# ################################################################################################################################
