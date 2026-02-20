from typing import Any

import os
from copy import deepcopy
from zato.cli import common_odb_opts, common_scheduler_server_api_client_opts, common_scheduler_server_address_opts, ZatoCommand
from zato.common.typing_ import cast_
from zato.common.util.config import get_scheduler_api_client_for_server_password, get_scheduler_api_client_for_server_username
from zato.common.util.platform_ import is_windows
from zato.common.util.open_ import open_w
from bunch import Bunch
from zato.common.typing_ import any_
import random
import stat
from collections import OrderedDict
from contextlib import closing
from itertools import count
from uuid import uuid4
from cryptography.fernet import Fernet
from zato.cli import create_cluster, create_odb, create_scheduler, create_server, create_web_admin
from zato.common.crypto.api import CryptoManager
from zato.common.defaults import http_plain_server_port
from zato.common.odb.model import Cluster
from zato.common.util.api import get_engine, get_session

class CryptoMaterialLocation:
    ca_dir: Any
    component_pattern: Any
    ca_certs_path: os.path.join
    cert_path: Any
    pub_path: Any
    priv_path: Any
    def __init__(self: Any, ca_dir: str, component_pattern: str) -> None: ...
    def locate(self: Any) -> None: ...

class Create(ZatoCommand):
    needs_empty_dir: Any
    opts: any_
    def _bunch_from_args(self: Any, args: any_, admin_invoke_password: str, cluster_name: str = ...) -> Bunch: ...
    def allow_empty_secrets(self: Any) -> bool: ...
    def execute(self: Any, args: any_) -> None: ...
