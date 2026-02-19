from typing import Any

from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

class Message:
    message_id: str
    publication_time: datetime
    publisher_name: str
    topic_name: str
    queue_name: str
    priority: int
    expiration: int
    content: Any
    received_time: datetime
    sequence_number: int

class TestCollector:
    expected_count: int
    start_time: datetime
    end_time: datetime
    received_count: int
    duplicate_count: int
    malformed_count: int
    messages: list
    message_ids: set
    topics_count: dict
    subscriptions_count: dict
    publisher_count: dict
    def add_message(self: Any, message: Message) -> bool: ...
    def increment_malformed(self: Any) -> None: ...
    def is_complete(self: Any) -> bool: ...
    def complete_test(self: Any) -> None: ...
    def get_duration_seconds(self: Any) -> float: ...
    def get_message_rate(self: Any) -> float: ...

class QueueStats:
    queue_name: str
    message_count: int
    success_count: int
    error_count: int
    min_processing_time: float
    max_processing_time: float
    total_processing_time: float
    def add_message_time(self: Any, processing_time: float, success: bool = ...) -> None: ...
    def get_avg_processing_time(self: Any) -> float: ...
    def get_success_rate(self: Any) -> float: ...
