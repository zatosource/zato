from typing import Any, TYPE_CHECKING

import os
from logging import getLogger
from base64 import b64decode
from zato.common.py23_.past.builtins import unicode
from six import PY2
from zato.common.api import AUTH_RESULT
from zato.common.crypto.api import is_string_equal
from zato.common.util.api import as_bool
from zato.server.connection.http_soap import Forbidden
from zato.common.ext.future.moves.urllib.parse import quote_plus
from lxml import etree
from yaml import dump
from yaml import CDumper as Dumper
from yaml import Dumper


def parse_basic_auth(auth: Any, prefix: Any = ...) -> None: ...

class AuthResult:
    __nonzero__: Any
    status: Any
    code: Any
    description: Any
    _auth_info: Any
    def __init__(self: Any, status: Any = ..., code: Any = ..., description: Any = ...) -> None: ...
    @property
    def auth_info(self: Any) -> None: ...
    def auth_info(self: Any, value: Any) -> None: ...
    def __repr__(self: Any) -> None: ...
    def __bool__(self: Any) -> None: ...

class SecurityException(Exception):
    description: Any
    def __init__(self: Any, description: Any) -> None: ...

def on_wsse_pwd(wsse: Any, url_config: Any, data: Any, needs_auth_info: Any = ...) -> None: ...

def extract_basic_auth(cid: str, auth: str) -> str: ...

def check_basic_auth(cid: Any, auth: Any, expected_username: Any, expected_password: Any, _needs_details: Any = ...) -> None: ...

def on_basic_auth(cid: Any, env: Any, url_config: Any, needs_auth_info: Any = ...) -> None: ...

def enrich_with_sec_data(data_dict: Any, sec_def: Any, sec_def_type: Any) -> None: ...
