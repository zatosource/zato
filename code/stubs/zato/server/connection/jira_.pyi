from typing import Any

from atlassian import Jira as AtlassianJiraClient
from zato.common.typing_ import any_, stranydict, strlist, strset

class JiraClient(AtlassianJiraClient):
    zato_api_version: str
    zato_address: str
    zato_username: str
    zato_token: str
    zato_is_cloud: bool
    def __init__(self: Any) -> None: ...
    @staticmethod
    def from_config(config: stranydict) -> JiraClient: ...
    def append_to_field(self: Any) -> strlist: ...
    def append_and_transition_if_field_complete(self: Any) -> None: ...
