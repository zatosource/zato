from typing import Any

from datetime import datetime
from logging import getLogger, INFO
from traceback import format_exc
from pytz import UTC
from tzlocal import get_localzone
from zato.common.api import NO_REMOTE_ADDRESS
from zato.common.util.api import make_cid_public, new_cid_server
from zato.common.util.time_ import utcnow
from prometheus_client import Counter, Histogram
from zato.common.typing_ import any_, callable_, list_, stranydict
from zato.server.base.parallel import ParallelServer
from prometheus_client import REGISTRY

class HTTPHandler:
    def on_wsgi_request(self: ParallelServer, wsgi_environ: Any, start_response: Any, _new_cid: Any = ..., _local_zone: Any = ..., _utcnow: Any = ..., _INFO: Any = ..., _UTC: Any = ..., _Access_Log_Date_Time_Format: Any = ..., _no_remote_address: Any = ..., _cid_components_no: Any = ..., **kwargs: any_) -> list_[bytes]: ...
