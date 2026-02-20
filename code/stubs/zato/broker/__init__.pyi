from typing import Any

import logging
from zato.common.api import ZATO_NONE
from zato.common.broker_message import SERVICE
from zato.common.util.api import new_cid_broker_client
from zato.common.util.config import resolve_env_variables
from zato.broker.message_handler import handle_broker_msg
from kombu.transport.pyamqp import Message as KombuMessage
from zato.broker.client import BrokerClient
from zato.server.base.worker import WorkerStore

class BrokerMessageReceiver:
    broker_client: BrokerClient
    worker_store: WorkerStore
    broker_client_id: Any.format
    broker_callbacks: Any
    broker_messages: Any
    def __init__(self: Any) -> None: ...
    def on_broker_msg(self: Any, msg: strdict) -> None: ...
    def preprocess_msg(self: Any, msg: Any) -> None: ...
    def filter(self: Any, msg: Any) -> None: ...
