from typing import Any

import os
import random
from copy import deepcopy
from zato.cli import common_odb_opts, ZatoCommand
from zato.common.const import ServiceConst
from zato.common.util.api import utcnow
from traceback import format_exc
from sqlalchemy.exc import IntegrityError
from zato.common.api import IDEDeploy
from zato.common.odb.model import Cluster, HTTPBasicAuth, Service
from zato.common.odb.post_process import ODBPostProcess
from uuid import uuid4
from cryptography.fernet import Fernet
from zato.common.const import SECRETS
from zato.common.api import SIMPLE_IO
from zato.common.odb.model import HTTPSOAP, Service
from zato.common.api import DATA_FORMAT
from zato.common.odb.model import HTTPBasicAuth, HTTPSOAP
from zato.common.api import MISC, SIMPLE_IO
from zato.common.odb.model import HTTPSOAP
from zato.common.api import CACHE
from zato.common.odb.model import CacheBuiltin
from zato.common.api import DATA_FORMAT, Groups, SEC_DEF_TYPE
from zato.server.groups.base import GroupsManager
from json import dumps
from zato.common.util.channel import create_openapi_channel, openapi_service_name

def get_random_integer() -> None: ...

class Create(ZatoCommand):
    opts: Any
    def execute(self: Any, args: Any, show_output: Any = ...) -> None: ...
    def generate_password(self: Any) -> None: ...
    def add_ping_service(self: Any, session: Any, cluster: Any) -> None: ...
    def add_metrics_channel(self: Any, session: Any, cluster: Any, service: Any) -> None: ...
    def add_admin_invoke(self: Any, session: Any, cluster: Any, service: Any, security: Any) -> None: ...
    def add_ide_publisher_channel(self: Any, session: Any, cluster: Any, service: Any, security: Any) -> None: ...
    def add_default_caches(self: Any, session: Any, cluster: Any) -> None: ...
    def add_rule_engine_configuration(self: Any, session: Any, cluster: Any, ping_service: Any) -> None: ...
    def add_streaming_channels(self: Any, session: Any, cluster: Any, service: Any, security: Any) -> None: ...
    def add_django_channel(self: Any, session: Any, cluster: Any, service: Any) -> None: ...
