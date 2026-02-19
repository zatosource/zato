from typing import Any

from bunch import Bunch
from zato.server.base.parallel import ParallelServer
from zato.server.base.worker import WorkerStore
from zato.server.connection.http_soap.url_data import URLData

class WorkerImpl:
    server: ParallelServer
    url_data: URLData
    worker_idx: int
    def on_broker_msg_Common_Sync_Objects(self: WorkerStore, msg: Bunch) -> None: ...
