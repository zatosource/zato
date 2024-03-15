# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# atlassian-python-api
from atlassian import Jira as AtlassianJiraClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strlist, strset

# ################################################################################################################################
# ################################################################################################################################

class JiraClient(AtlassianJiraClient):

    zato_api_version: 'str'
    zato_address: 'str'
    zato_username: 'str'
    zato_token: 'str'
    zato_is_cloud: 'bool'

    def __init__(
        self,
        *,
        zato_api_version, # type: str
        zato_address, # type: str
        zato_username, # type: str
        zato_token, # type: str
        zato_is_cloud, # type: bool
    ) -> 'None':

        # We need to make sure that the API version is a string
        # because this is what the underlying Jira API requires.
        self.zato_api_version = str(zato_api_version)

        self.zato_address = zato_address
        self.zato_username = zato_username
        self.zato_token = zato_token
        self.zato_is_cloud = zato_is_cloud

        super().__init__(
            url = self.zato_address,
            username = self.zato_username,
            password = self.zato_token,
            api_version = self.zato_api_version,
            cloud = self.zato_is_cloud,
        )

# ################################################################################################################################

    @staticmethod
    def from_config(config:'stranydict') -> 'JiraClient':
        return JiraClient(
            zato_api_version = config['api_version'],
            zato_address = config['address'],
            zato_username = config['username'],
            zato_token = config['secret'],
            zato_is_cloud = config['is_cloud'],
        )

# ################################################################################################################################

    def append_to_field(
        self,
        *,
        key, # type: str
        field_id, # type: str
        value, # type: str
    ) -> 'strlist':

        # Get the current values ..
        value_list:'strlist | strset' = self.issue_field_value(key, field_id)

        # .. make sure it is always a list ..
        value_list = value_list or []

        # .. remove any potential duplicates ..
        value_list = set(value_list)

        # .. actually add the new value ..
        value_list.add(value)

        # .. ensure the list of values is always sorted to make it easier
        # .. to browse it in Jira ..
        value_list = sorted(value_list)

        # .. update the ticket with a new list ..
        _:'any_' = self.update_issue_field(key, {
            field_id: value_list
        })

        return value_list

# ################################################################################################################################

    def append_and_transition_if_field_complete(
        self,
        *,
        key, # type: str
        field_id, # type: str
        value, # type: str
        transition_to, # type: str
        complete_list # type: strlist
    ) -> 'None':

        # This will modify the ticket and return the current value of the field's list ..
        current_list = self.append_to_field(
            key=key,
            field_id=field_id,
            value=value
        )

        # .. now, compare it to what the complete list looks like, ..
        # .. note that the lists need to be sorted to make sure they are the same.
        if sorted(current_list) == sorted(complete_list):

            # .. if we are here, it means that we must have append the final item
            # .. in the list above, in which case we can make the transition.
            _:'any_' = self.set_issue_status(key, transition_to)

# ################################################################################################################################
# ################################################################################################################################
