from typing import Any

from zato.common.api import CONNECTION, DATA_FORMAT, URL_TYPE
from zato.common.odb.model import HTTPSOAP
from zato.common.odb.model import Cluster, HTTPSOAP, Service

def create_openapi_channel(session: Any, cluster: Any, service: Any) -> None: ...

def ensure_openapi_channel_exists(session: Any, cluster_id: Any) -> None: ...

def ensure_django_channel_exists(session: Any, cluster_id: Any) -> None: ...
