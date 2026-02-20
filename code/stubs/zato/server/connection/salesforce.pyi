from typing import Any

from json import dumps
from requests import get as request_get, post as requests_post
from zato.common.typing_ import any_, anydict, dictnone, stranydict, strnone

class ModuleCtx:
    PathLogin: Any
    PathBase: Any
    MethodGet: Any
    MethodPost: Any

class SalesforceClient:
    api_version: str
    address: str
    username: str
    password: str
    consumer_key: str
    consumer_secret: str
    access_token: str
    http_bearer: str
    api_version: Any
    address: Any
    username: Any
    password: Any
    consumer_key: Any
    consumer_secret: Any
    def __init__(self: Any) -> None: ...
    @staticmethod
    def from_config(config: stranydict) -> SalesforceClient: ...
    def _invoke_http(self: Any) -> anydict: ...
    def ensure_access_token_is_assigned(self: Any) -> None: ...
    def _send_request(self: Any) -> any_: ...
    def get(self: Any, path: Any) -> any_: ...
    def post(self: Any, path: Any, data: Any = ...) -> any_: ...
    def ping(self: Any) -> None: ...
