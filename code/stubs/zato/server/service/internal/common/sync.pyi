from typing import Any, TYPE_CHECKING

from dataclasses import dataclass
from zato.common.broker_message import Common as BrokerMessageCommon
from zato.server.service import Model, Service


class SyncObjectsRequest(Model):
    security: bool

class SyncObjectsImpl(Service):
    name: Any
    input: Any
    def handle(self: Any) -> None: ...

class SyncObjects(Service):
    name: Any
    input: Any
    def handle(self: Any) -> None: ...
