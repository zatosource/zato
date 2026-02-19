from typing import Any

from dataclasses import dataclass
from logging import getLogger
from yaml import safe_load as yaml_load
from zato.common.api import PubSub
from zato.common.pubsub.test.users_yaml import calculate_expected_messages

class ServerConfig:
    host: str
    port: int

class CollectionConfig:
    users_yaml_path: str
    messages_per_topic_per_user: int
    log_interval: int
    timeout_seconds: int
    expected_message_count: int

class ReportConfig:
    url_path: str

class AppConfig:
    server: ServerConfig
    collection: CollectionConfig
    report: ReportConfig
    def __post_init__(self: Any) -> None: ...

def load_config(config_file: str) -> AppConfig: ...
