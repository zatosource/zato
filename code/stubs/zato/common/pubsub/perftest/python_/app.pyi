from typing import Any

import logging
import random
from logging import getLogger
from colorama import Fore, Style, init as colorama_init
from zato.common.pubsub.perftest.python_.producer import Producer
from zato.common.pubsub.perftest.python_.consumer import Consumer
from zato.common.pubsub.perftest.python_.progress_tracker import ProgressTracker
from zato.common.typing_ import any_, intnone
import argparse
import os

class ConsumerManager:
    def _start_consumer(self: Any, consumer_id: int, pull_interval: float, max_messages: int, progress_tracker: ProgressTracker, cpu_num: intnone = ..., use_new_requests: bool = ...) -> any_: ...
    def run(self: Any, consumer_spec: str, pull_interval: float = ..., max_messages: int = ..., cpu_num: intnone = ..., use_new_requests: bool = ...) -> None: ...

class ProducerManager:
    def _start_producer(self: Any, reqs_per_producer: int, producer_id: int, reqs_per_second: float, topic_spec: str, progress_tracker: ProgressTracker, burst_multiplier: int = ..., burst_duration: int = ..., burst_interval: int = ..., cpu_num: intnone = ..., use_new_requests: bool = ...) -> any_: ...
    def run(self: Any, num_producers: int, reqs_per_producer: int = ..., reqs_per_second: float = ..., topic_spec: str = ..., burst_multiplier: int = ..., burst_duration: int = ..., burst_interval: int = ..., cpu_num: intnone = ..., use_new_requests: bool = ...) -> None: ...

def _parse_consumer_range(consumer_spec: str) -> tuple[int, int]: ...

def _parse_topic_range(topic_spec: str) -> tuple[int, int]: ...
