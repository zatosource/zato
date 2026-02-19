from typing import Any

from dataclasses import dataclass
from logging import getLogger
from bunch import bunchify
from kombu.connection import Connection as KombuAMQPConnection
from zato.common.api import AMQP, PubSub
from zato.common.pubsub.util import get_broker_config
from zato.server.connection.amqp_ import Consumer
from zato.common.typing_ import any_, callable_, strdict
import logging

class ConsumerConfig:
    cid: str
    name: str
    is_internal: bool
    queue_name: str
    prefetch_count: int
    consumer_tag_prefix: str
    on_msg_callback: callable_
    wait_for_conection: bool
    should_start: bool
    max_repeats: int

def start_consumer(consumer_config: ConsumerConfig) -> Consumer: ...

def start_internal_consumer(name: str, queue_name: str, consumer_tag_prefix: str, on_msg_callback: callable_) -> Consumer: ...

def start_public_consumer(cid: str, username: str, sub_key: str, on_msg_callback: callable_, should_start: bool = ...) -> Consumer: ...
