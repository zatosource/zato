from typing import Any

import argparse
import base64
from datetime import datetime, timezone
import json
import logging
import sys
from dataclasses import dataclass
import requests
from zato.common.typing_ import strdict, strlist, strnone
from logging import getLogger
from traceback import format_exc

class SetupResult:
    access_policy_id: str
    token: str
    encoded_credentials: str
    policy_response: strdict
    token_response: strdict
    error: strnone
    error_response: strdict | None

class AutoSetup:
    main_token: Any
    instance_id: Any
    region: Any
    base_url: Any
    def __init__(self: Any, main_token: str, instance_id: str, region: str | None = ...) -> None: ...
    def _extract_region_from_token(self: Any, token: str) -> str: ...
    def _make_request(self: Any, method: str, url: str, data: strdict | None = ...) -> strdict: ...
    def create_access_policy(self: Any, name: str, display_name: str, scopes: strlist) -> strdict: ...
    def create_token(self: Any, access_policy_id: str, name: str, display_name: str) -> strdict: ...
    def encode_credentials(self: Any, token: str) -> str: ...
    def test_connection(self: Any) -> strdict: ...
    def setup_complete(self: Any, policy_name: str, token_name: str) -> SetupResult: ...

class CLI:
    parser: self._create_parser
    def __init__(self: Any) -> None: ...
    def _create_parser(self: Any) -> argparse.ArgumentParser: ...
    def run(self: Any, args: strlist | None = ...) -> int: ...
