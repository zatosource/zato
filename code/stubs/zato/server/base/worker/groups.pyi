from typing import Any

from zato.common.api import Groups
from zato.server.base.worker.common import WorkerImpl
from bunch import Bunch
from zato.common.typing_ import any_
from zato.server.base.worker import WorkerStore

class SecurityGroups(WorkerImpl):
    def _yield_security_groups_ctx_items(self: WorkerStore) -> any_: ...
    def on_broker_msg_Groups_Edit_Member_List(self: WorkerStore, msg: Any) -> None: ...
    def on_broker_msg_Groups_Delete(self: WorkerStore, msg: Any) -> None: ...
