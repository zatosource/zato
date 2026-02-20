from typing import Any, TYPE_CHECKING

import http.client as http_client
import json
import logging
import os
from unittest import TestCase
from yaml import load as yaml_load
import requests
from requests.auth import HTTPBasicAuth
from zato.common.api import PubSub
from zato.common.pubsub.util import cleanup_broker_impl, get_broker_config
from yaml import CLoader as Loader
from zato.common.typing_ import any_
from yaml import Loader

_public_port = PubSub.REST_Server.Public_Port

class PubSubRESTServerBaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls: Any) -> None: ...
    def setUp(self: Any) -> None: ...
    def tearDown(self: Any) -> None: ...
    @classmethod
    def _setup_http_patching(cls: Any) -> None: ...
    def _call_diagnostics(self: Any) -> any_: ...
