# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from typing import Dict, List, Optional

    # Define type aliases
    Any = Any
    Optional = Optional

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Message:
    """ Represents a single PubSub message captured by the test server.
    """
    message_id: str
    publication_time: datetime
    publisher_name: str
    topic_name: str
    queue_name: str
    priority: int
    expiration: int
    content: Any
    received_time: datetime = field(default_factory=datetime.utcnow)
    sequence_number: int = 0

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class TestCollector:
    """ Manages collection of messages and test state.
    """
    expected_count: int
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime = None
    received_count: int = 0
    duplicate_count: int = 0
    malformed_count: int = 0
    messages: list = field(default_factory=list)
    message_ids: set = field(default_factory=set)
    topics_count: dict = field(default_factory=dict)  # Count by topic_name
    subscriptions_count: dict = field(default_factory=dict)  # Count by sub_key/queue_name
    publisher_count: dict = field(default_factory=dict)  # Count by publisher

    def add_message(self, message:'Message') -> 'bool':
        """ Add a message to the collector.
        Returns True if the message was added, False if it was a duplicate.
        """
        if message.message_id in self.message_ids:
            self.duplicate_count += 1
            return False

        self.message_ids.add(message.message_id)
        message.sequence_number = self.received_count + 1
        self.messages.append(message)
        self.received_count += 1

        # Track message by topic
        topic_name = message.topic_name
        if topic_name not in self.topics_count:
            self.topics_count[topic_name] = 0
        self.topics_count[topic_name] += 1

        # Track message by queue/subscription
        queue_name = message.queue_name
        if queue_name not in self.subscriptions_count:
            self.subscriptions_count[queue_name] = 0
        self.subscriptions_count[queue_name] += 1

        # Track message by publisher
        publisher_name = message.publisher_name
        if publisher_name not in self.publisher_count:
            self.publisher_count[publisher_name] = 0
        self.publisher_count[publisher_name] += 1

        return True

    def increment_malformed(self) -> 'None':
        """ Increment the count of malformed messages.
        """
        self.malformed_count += 1

    def is_complete(self) -> 'bool':
        """ Check if the test has collected the expected number of messages.
        """
        return self.received_count >= self.expected_count

    def complete_test(self) -> 'None':
        """ Mark the test as complete by setting the end time.
        """
        if not self.end_time:
            self.end_time = datetime.utcnow()

    def get_duration_seconds(self) -> 'float':
        """ Get the test duration in seconds.
        """
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds()

    def get_message_rate(self) -> 'float':
        """ Calculate the message rate (messages per second).
        """
        duration = self.get_duration_seconds()
        if duration > 0:
            return self.received_count / duration
        return 0

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class QueueStats:
    """ Statistics for a specific message queue.
    """
    queue_name: str
    message_count: int = 0
    success_count: int = 0
    error_count: int = 0
    min_processing_time: float = float('inf')
    max_processing_time: float = 0
    total_processing_time: float = 0

    def add_message_time(self, processing_time:'float', success:'bool'=True) -> 'None':
        """ Add a message processing time and update statistics.
        """
        self.message_count += 1

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

        self.min_processing_time = min(self.min_processing_time, processing_time)
        self.max_processing_time = max(self.max_processing_time, processing_time)
        self.total_processing_time += processing_time

    def get_avg_processing_time(self) -> 'float':
        """ Calculate the average message processing time.
        """
        if self.message_count > 0:
            return self.total_processing_time / self.message_count
        return 0

    def get_success_rate(self) -> 'float':
        """ Calculate the success rate as a percentage.
        """
        if self.message_count > 0:
            return (self.success_count / self.message_count) * 100
        return 0

# ################################################################################################################################
# ################################################################################################################################
