from typing import Any

import os
from datetime import datetime
from http.client import NO_CONTENT, NOT_FOUND, OK
from logging import getLogger
from urllib.parse import quote
import requests
from requests.exceptions import RequestException
from zato.common.pubsub.util_cli import close_queue_consumers, get_queue_consumers
from zato.common.api import PubSub
from zato.common.pubsub.common import BrokerConfig
from zato.common.util.api import as_bool, utcnow, wait_for_predicate
from zato.common.odb.model import PubSubPermission
from zato.common.pubsub.matcher import PatternMatcher
from zato.common.odb.model import SecurityBase

class ModuleCtx:
    Max_Length: Any

def get_broker_config() -> BrokerConfig: ...

def validate_topic_name(topic_name: str) -> None: ...

def validate_pattern(pattern: str) -> None: ...

def _contains_reserved_name(pattern: str) -> bool: ...

def _is_ascii_only(text: str) -> bool: ...

def get_permissions_for_sec_base(session: Any, sec_base_id: int, cluster_id: int) -> list: ...

def evaluate_pattern_match(session: Any, sec_base_name: str, sec_base_id: int, cluster_id: int, topic_name: str) -> str: ...

def create_subscription_bindings(broker_client: Any, cid: str, sub_key: str, exchange_name: str, topic_name: str) -> None: ...

def cleanup_broker_impl(broker_config: BrokerConfig, management_port: int) -> dict: ...

class ConsumerManager:
    broker_config: Any
    cid: Any
    host: Any
    management_port: Any
    auth: Any
    ignore_prefixes: Any
    request_timeout: Any
    def __init__(self: Any, cid: str, broker_config: BrokerConfig) -> None: ...
    def _close_consumers(self: Any, queue_name: str) -> None: ...
    def close_consumers(self: Any, queue_name: str) -> None: ...

def get_security_definition(session: Any, cluster_id: Any, username: Any = ..., sec_name: Any = ...) -> None: ...

def set_time_since(message: dict, pub_time_iso: str, recv_time_iso: str, current_time: datetime) -> None: ...
