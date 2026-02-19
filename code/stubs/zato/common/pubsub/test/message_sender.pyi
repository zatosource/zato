from typing import Any

from datetime import datetime
from dataclasses import dataclass
from logging import getLogger
from time import sleep
import random
import uuid
from traceback import format_exc
from urllib.parse import urljoin
from bunch import bunchify
from yaml import safe_load as yaml_load
import requests
from zato.common.api import PubSub
from zato.common.util.api import get_absolute_path
from zato.common.typing_ import any_, strdict

class ClientConfig:
    server_url: str
    request_timeout: int
    retry_count: int

class MessagingConfig:
    users_yaml_path: str
    messages_per_topic_per_user: int
    max_concurrent_publishers: int
    max_send_rate: int
    send_interval: float

class ContentConfig:
    template_path: str
    min_size: int
    max_size: int
    complexity: str

class SenderConfig:
    client: ClientConfig
    messaging: MessagingConfig
    content: ContentConfig

def load_config(config_file: str) -> SenderConfig: ...

class UsersYAMLParser:
    data: strdict
    def __init__(self: Any, users_yaml_path: str) -> None: ...
    def _load_yaml(self: Any) -> None: ...
    def get_users(self: Any) -> list[str]: ...
    def get_topics(self: Any) -> list[str]: ...
    def get_user_credentials(self: Any, username: str) -> str: ...

class MessageSender:
    def __init__(self: Any, config_path: str) -> None: ...
    def _generate_message_content(self: Any, publisher: str, topic: str, message_index: int) -> strdict: ...
    def send_message(self: Any, publisher: str, topic: str, content: any_) -> bool: ...
    def _record_failure(self: Any, publisher: str, topic: str, error: str) -> None: ...
    def _publisher_worker(self: Any, publisher: str, topic: str, message_count: int) -> None: ...
    def start(self: Any) -> strdict: ...
