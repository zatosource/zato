# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from typing import NamedTuple

# Zato
from pubsub_perf.clients import get_receipt_key, PublisherGroup, ReceiptReader, SubscriberGroup
from pubsub_perf.config import PerfConfig
from pubsub_perf.figures import get_rate_figures
from zato.common.test.perf_report import report_result
from zato.common.test.pubsub_database import ModuleCtx as DatabaseCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from pubsub_perf.clients import futurelist
    from pubsub_perf.config import Scenario
    from pubsub_perf.progress import Progress
    from zato.common.test.perf_report import Measurement
    from zato.common.typing_ import stranydict, strintdict

    futurelist = futurelist

# ################################################################################################################################
# ################################################################################################################################

# The names under which the progress of a scenario is logged
_published_name = 'published'
_delivered_name = 'delivered'

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
    """ The publishers and the subscribers of one scenario, publishing to its topic under keys unique to the run,
    and the reader of the receipts that the subscribers commit with their acknowledgements.
    """

    def __init__(self, scenario:'Scenario', prefix:'str') -> 'None':
        self.scenario = scenario
        self.prefix = prefix

        publisher_credentials = PerfConfig.publishers[:scenario.publisher_count]
        subscriber_credentials = PerfConfig.subscribers[:scenario.subscriber_count]

        self.publishers = PublisherGroup(publisher_credentials, scenario.topic_name, prefix)
        self.subscribers = SubscriberGroup(subscriber_credentials)
        self.receipt_reader = ReceiptReader(PerfConfig.receipt_reader, prefix)

        self.thread_count = scenario.publisher_count + scenario.subscriber_count + 1

# ################################################################################################################################

    def count_published(self) -> 'int':
        out = self.publishers.count_published()
        return out

# ################################################################################################################################

    def count_delivered(self) -> 'int':
        """ Returns how many deliveries the subscribers processed, by the distinct receipts that they committed.
        """
        receipt_keys = self.receipt_reader.get_receipt_keys()

        out = len(set(receipt_keys))
        return out

# ################################################################################################################################

    def add_progress(self, progress:'Progress') -> 'None':
        progress.add_count(_published_name, self.count_published)
        progress.add_count(_delivered_name, self.count_delivered)

# ################################################################################################################################

    def submit_subscribers(self, executor:'ThreadPoolExecutor', stop:'Event') -> 'futurelist':
        """ Starts every subscriber and the reader of their receipts, each of which runs until the test stops it.
        """
        out = self.subscribers.submit(executor, stop)

        reader_future = executor.submit(self.receipt_reader.run, stop)
        out.append(reader_future)

        return out

# ################################################################################################################################

    def submit_publishers(self, executor:'ThreadPoolExecutor', deadline:'float') -> 'futurelist':
        out = self.publishers.submit(executor, deadline)
        return out

# ################################################################################################################################

    def is_settled(self) -> 'bool':
        """ Whether each subscriber processed every published message.
        """
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

        found_keys = self.receipt_reader.get_receipt_keys()
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

    def get_figures(self, timing:'Timing', worker_kills:'int') -> 'stranydict':
        """ Returns the business figures of a run in which each subscriber processed each message exactly once.
        """
        published_count = self.publishers.count_published()
        delivered_count = published_count * self.scenario.subscriber_count

        published_seconds = timing.published_at - timing.start
        settled_seconds = timing.settled_at - timing.start

        sent_times = self.publishers.get_sent_times()
        latencies = self.subscribers.get_latencies(sent_times)

        out:'stranydict' = {
            'publishers': self.scenario.publisher_count,
            'subscribers': self.scenario.subscriber_count,
            'worker_kills': worker_kills,
            'publications': get_rate_figures(published_count, published_seconds),
            'deliveries': get_rate_figures(delivered_count, settled_seconds),
            'publication_to_delivery': latencies.get_figures(),
        }

        # The round-trip time that the network of the database container was given, if any
        if DatabaseCtx.Env_Round_Trip_Ms in os.environ:
            out['database_round_trip_ms'] = float(os.environ[DatabaseCtx.Env_Round_Trip_Ms])

        return out

# ################################################################################################################################
# ################################################################################################################################

def verify_and_report(measurement:'Measurement', name:'str', run:'ScenarioRun', timing:'Timing', worker_kills:'int') -> 'None':
    """ Verifies that a finished run delivered each message exactly once and then records its figures.
    """
    check = run.check()

    assert check.lost_count == 0, f'{check.lost_count} of {check.expected_count} deliveries lost'
    assert check.duplicate_count == 0, f'{check.duplicate_count} deliveries processed more than once'
    assert check.unexpected_count == 0, f'{check.unexpected_count} receipts of messages never published'

    figures = run.get_figures(timing, worker_kills)
    _ = report_result(measurement, name, figures)

# ################################################################################################################################
# ################################################################################################################################
