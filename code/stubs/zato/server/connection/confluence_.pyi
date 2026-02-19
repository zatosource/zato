from typing import Any

from atlassian import Confluence as AtlassianConfluenceClient
from zato.common.typing_ import stranydict

class ConfluenceClient(AtlassianConfluenceClient):
    zato_api_version: str
    zato_address: str
    zato_username: str
    zato_token: str
    zato_is_cloud: bool
    def __init__(self: Any) -> None: ...
    @staticmethod
    def from_config(config: stranydict) -> ConfluenceClient: ...
