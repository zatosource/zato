# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Zato
from pubsub_exactly_once.harness import get_engine
from pubsub_perf.clients import get_receipt_key, PublisherGroup, SubscriberGroup
from pubsub_perf.config import PerfConfig, Receipts_Topic
from pubsub_perf.progress import count_messages
from zato.common.test.exactly_once.verify import count_topic_deliveries, read_correl_ids

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from pubsub_perf.clients import futurelist
    from pubsub_perf.config import Scenario
    from pubsub_perf.progress import PerfReport, Progress
    from zato.common.typing_ import strintdict

    futurelist = futurelist

# ################################################################################################################################
# ################################################################################################################################

# The names under which the progress of a scenario is logged
_published_name = 'published'
_delivered_name = 'delivered'
_waiting_name   = 'waiting'

# ################################################################################################################################
# ################################################################################################################################

class Timing(NamedTuple):
    """ When a run started, when its publishers stopped and when every subscriber received everything they published.
    """
    start: 'float'
    published_at: 'float'
    settled_at: 'float'

# ################################################################################################################################

class DeliveryCheck(NamedTuple):
    """ How many deliveries no subscriber processed, how many were processed more than once, and how many
    receipts belong to no published message.
    """
    expected_count: 'int'
    lost_count: 'int'
    duplicate_count: 'int'
    unexpected_count: 'int'

# ################################################################################################################################
# ################################################################################################################################

class ScenarioRun:
    """ The publishers and the subscribers of one scenario, publishing to its topic under keys unique to the run.
    """

    def __init__(self, scenario:'Scenario', prefix:'str') -> 'None':
        self.scenario = scenario
        self.prefix = prefix
        self.engine = get_engine()

        publisher_credentials = PerfConfig.publishers[:scenario.publisher_count]
        subscriber_credentials = PerfConfig.subscribers[:scenario.subscriber_count]

        self.publishers = PublisherGroup(publisher_credentials, scenario.topic_name, prefix)
        self.subscribers = SubscriberGroup(subscriber_credentials)

        self.thread_count = scenario.publisher_count + scenario.subscriber_count

# ################################################################################################################################

    def count_published(self) -> 'int':
        out = self.publishers.count_published()
        return out

# ################################################################################################################################

    def count_delivered(self) -> 'int':
        """ Returns how many deliveries the subscribers processed, by the receipts that they committed with them.
        """
        out = count_messages(self.engine, Receipts_Topic, self.prefix)
        return out

# ################################################################################################################################

    def count_waiting(self) -> 'int':
        """ Returns how many deliveries wait for their subscribers.
        """
        out = count_topic_deliveries(self.engine, self.scenario.topic_name)
        return out

# ################################################################################################################################

    def add_progress(self, progress:'Progress') -> 'None':
        progress.add_count(_published_name, self.count_published)
        progress.add_count(_delivered_name, self.count_delivered)
        progress.add_level(_waiting_name, self.count_waiting)

# ################################################################################################################################

    def submit_subscribers(self, executor:'ThreadPoolExecutor', stop:'Event') -> 'futurelist':
        out = self.subscribers.submit(executor, stop)
        return out

# ################################################################################################################################

    def submit_publishers(self, executor:'ThreadPoolExecutor', deadline:'float') -> 'futurelist':
        out = self.publishers.submit(executor, deadline)
        return out

# ################################################################################################################################

    def is_settled(self) -> 'bool':
        """ Whether each subscriber processed every published message and nothing waits in the queues.
        """
        if self.count_waiting():
            return False

        published = self.publishers.count_published()
        expected = published * self.scenario.subscriber_count

        out = self.count_delivered() >= expected
        return out

# ################################################################################################################################

    def check(self) -> 'DeliveryCheck':
        """ Compares the receipts that the subscribers committed with one receipt per message and subscriber.
        """
        keys = self.publishers.get_keys()
        names = self.subscribers.get_names()

        found_keys = read_correl_ids(self.engine, Receipts_Topic, self.prefix)
        counts:'strintdict' = {}

        for key in found_keys:
            if key in counts:
                counts[key] += 1
            else:
                counts[key] = 1

        expected_count = 0
        lost_count = 0
        duplicate_count = 0
        matched_count = 0

        for key in keys:
            for name in names:
                receipt_key = get_receipt_key(key, name)
                expected_count += 1

                if receipt_key not in counts:
                    lost_count += 1
                    continue

                found_count = counts[receipt_key]
                duplicate_count += found_count - 1
                matched_count += found_count

        unexpected_count = len(found_keys) - matched_count

        out = DeliveryCheck(expected_count, lost_count, duplicate_count, unexpected_count)
        return out

# ################################################################################################################################

    def report(self, report:'PerfReport', timing:'Timing', progress:'Progress', check:'DeliveryCheck') -> 'None':
        """ Adds the business figures of the run.
        """
        published_count = self.publishers.count_published()
        delivered_count = check.expected_count - check.lost_count

        published_seconds = timing.published_at - timing.start
        settled_seconds = timing.settled_at - timing.start

        sent_times = self.publishers.get_sent_times()
        latencies = self.subscribers.get_latencies(sent_times)

        waiting_peak = progress.peaks[_waiting_name]

        report.add_value('Publishers', f'{self.scenario.publisher_count}')
        subscriber_count = self.scenario.subscriber_count

        if subscriber_count == 1:
            subscribers = f'{subscriber_count}, with its own subscription'
        else:
            subscribers = f'{subscriber_count}, each with its own subscription'

        report.add_value('Subscribers', subscribers)
        report.add_rate('Publications', published_count, published_seconds, 'publications')
        report.add_rate('Deliveries', delivered_count, settled_seconds, 'deliveries')
        report.add_value('Lost deliveries', f'{check.lost_count}')
        report.add_value('Duplicate deliveries', f'{check.duplicate_count}')
        report.add_latencies(latencies)
        report.add_value('Peak deliveries waiting', f'{waiting_peak}')

# ################################################################################################################################

    def verify(self, check:'DeliveryCheck') -> 'None':
        """ Fails unless each subscriber processed each message exactly once and nothing remains in the queues.
        """
        assert check.lost_count == 0, f'{check.lost_count} of {check.expected_count} deliveries lost'
        assert check.duplicate_count == 0, f'{check.duplicate_count} deliveries processed more than once'
        assert check.unexpected_count == 0, f'{check.unexpected_count} receipts of messages never published'

        assert self.count_waiting() == 0

# ################################################################################################################################
# ################################################################################################################################

def report_and_verify(report:'PerfReport', run:'ScenarioRun', timing:'Timing', progress:'Progress') -> 'None':
    """ Logs the figures of a finished run and then verifies that it delivered each message exactly once.
    """
    check = run.check()

    run.report(report, timing, progress, check)
    report.log()

    run.verify(check)

# ################################################################################################################################
# ################################################################################################################################
