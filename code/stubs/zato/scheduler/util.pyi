from typing import Any, TYPE_CHECKING

from zato.client import AnyServiceInvoker, ZatoClient
from zato.common.typing_ import anydict
from zato.common.util.api import get_client_from_server_conf
from zato.client import get_client_from_credentials


def _set_up_zato_client_by_server_path(server_path: str) -> AnyServiceInvoker: ...

def _set_up_zato_client_by_remote_details(server_use_tls: bool, server_host: str, server_port: int, server_username: str, server_password: str) -> ZatoClient: ...

def set_up_zato_client(config: anydict) -> AnyServiceInvoker: ...
