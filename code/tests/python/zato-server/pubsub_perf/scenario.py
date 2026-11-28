# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from typing import NamedTuple

# Zato
from pubsub_perf.clients import get_receipt_key, PublisherGroup, PushSubscriberGroup, ReceiptReader, SubscriberGroup
from pubsub_perf.config import PerfConfig
from pubsub_perf.figures import get_rate_figures, Latencies
from zato.common.test.perf_report import report_result
from zato.common.test.pubsub_database import ModuleCtx as DatabaseCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from pubsub_perf.clients import futurelist, PushCheck, strfloatdictlist
    from pubsub_perf.config import Scenario
    from pubsub_perf.progress import Progress
    from zato.common.test.perf_report import Measurement
    from zato.common.typing_ import stranydict, strfloatdict, strintdict

    futurelist = futurelist
    PushCheck = PushCheck
    strfloatdictlist = strfloatdictlist

# ################################################################################################################################
# ################################################################################################################################

# The names under which the progress of a scenario is logged
_published_name = 'published'
_pulled_name = 'pulled'
_pushed_name = 'pushed'

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
    """ How many deliveries to pull subscribers no subscriber processed, how many were processed more than once,
    and how many receipts belong to no published message.
    """
    expected_count: 'int'
    lost_count: 'int'
    duplicate_count: 'int'
    unexpected_count: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _get_kind_figures(
    subscriber_count:'int',
    published_count:'int',
    first_receipts:'strfloatdictlist',
    sent_times:'strfloatdict',
    start:'float',
    latencies:'Latencies',
    ) -> 'stranydict':
    """ Returns the figures of the subscribers of one kind - their deliveries per second, until the last first receipt
    of a key, and the time from the publication of each message to its first receipt by each subscriber, which
    are also added to the latencies of both kinds.
    """
    kind_latencies = Latencies()
    last_receipt = start

    for receipts in first_receipts:
        for key, received_at in receipts.items():

            latency = received_at - sent_times[key]

            kind_latencies.add(latency)
            latencies.add(latency)

            last_receipt = max(last_receipt, received_at)

    delivered_count = published_count * subscriber_count
    seconds = last_receipt - start

    out:'stranydict' = {
        'subscribers': subscriber_count,
        'deliveries': get_rate_figures(delivered_count, seconds),
        'publication_to_delivery': kind_latencies.get_figures(),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class ScenarioRun:
    """ The publishers and the subscribers of one scenario, publishing to its topic under keys unique to the run,
    the reader of the receipts that the pull subscribers commit with their acknowledgements, and the pushes
    to the push subscribers that the receiver recorded.
    """

    def __init__(self, scenario:'Scenario', prefix:'str') -> 'None':
        self.scenario = scenario
        self.prefix = prefix

        publisher_credentials = PerfConfig.publishers[:scenario.publisher_count]
        pull_credentials = PerfConfig.subscribers[:scenario.pull_count]
        push_credentials = PerfConfig.push_subscribers[:scenario.push_count]

        self.publishers = PublisherGroup(publisher_credentials, scenario.topic_name, prefix)
        self.subscribers = SubscriberGroup(pull_credentials)
        self.push_subscribers = PushSubscriberGroup(push_credentials, PerfConfig.push_receiver, prefix)
        self.receipt_reader = ReceiptReader(PerfConfig.receipt_reader, prefix)

        self.thread_count = scenario.publisher_count + scenario.pull_count + 1

# ################################################################################################################################

    def count_published(self) -> 'int':
        out = self.publishers.count_published()
        return out

# ################################################################################################################################

    def count_pulled(self) -> 'int':
        """ Returns how many deliveries the pull subscribers processed, by the distinct receipts that they committed.
        """
        receipt_keys = self.receipt_reader.get_receipt_keys()

        out = len(set(receipt_keys))
        return out

# ################################################################################################################################

    def count_pushed(self) -> 'int':
        """ Returns how many distinct keys the push subscribers received, added over the subscribers.
        """
        out = self.push_subscribers.count_delivered()
        return out

# ################################################################################################################################

    def add_progress(self, progress:'Progress') -> 'None':
        progress.add_count(_published_name, self.count_published)
        progress.add_count(_pulled_name, self.count_pulled)
        progress.add_count(_pushed_name, self.count_pushed)

# ################################################################################################################################

    def submit_subscribers(self, executor:'ThreadPoolExecutor', stop:'Event') -> 'futurelist':
        """ Starts every pull subscriber and the reader of their receipts, each of which runs until the test stops it.
        The push subscribers receive their messages through the receiver of the session.
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
        """ Whether each pull subscriber processed and each push subscriber received every published message.
        """
        published = self.publishers.count_published()

        # The pull subscribers are settled first ..
        if self.count_pulled() < published * self.scenario.pull_count:
            out = False

        # .. and then the push subscribers.
        else:
            out = self.count_pushed() >= published * self.scenario.push_count

        return out

# ################################################################################################################################

    def check(self) -> 'DeliveryCheck':
        """ Compares the receipts that the pull subscribers committed with one receipt per message and subscriber.
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

    def check_pushes(self) -> 'PushCheck':
        """ Compares the keys that each push subscriber received with the keys that the publishers published.
        """
        keys = self.publishers.get_keys()

        out = self.push_subscribers.check(keys)
        return out

# ################################################################################################################################

    def get_figures(self, timing:'Timing', worker_kills:'int', push_check:'PushCheck') -> 'stranydict':
        """ Returns the business figures of a run in which each pull subscriber processed and each push subscriber
        received each message. The deliveries and the latencies of both kinds are added together,
        and each kind has figures of its own as well.
        """
        published_count = self.publishers.count_published()
        subscriber_count = self.scenario.pull_count + self.scenario.push_count
        delivered_count = published_count * subscriber_count

        published_seconds = timing.published_at - timing.start
        settled_seconds = timing.settled_at - timing.start

        sent_times = self.publishers.get_sent_times()
        publish_latencies = self.publishers.get_publish_latencies()

        # The latencies of both kinds are collected while the figures of each kind are computed.
        latencies = Latencies()

        pull_receipts = self.subscribers.get_first_receipts()
        push_receipts = self.push_subscribers.get_first_receipts()

        pull_figures = _get_kind_figures(
            self.scenario.pull_count, published_count, pull_receipts, sent_times, timing.start, latencies)

        push_figures = _get_kind_figures(
            self.scenario.push_count, published_count, push_receipts, sent_times, timing.start, latencies)

        push_figures['repeated'] = push_check.repeated_count
        push_figures['retried'] = self.push_subscribers.count_retried()

        # The timing is monotonic and the window is in seconds since the epoch, which the recorders of the host use.
        epoch_offset = time.time() - time.monotonic()

        out:'stranydict' = {
            'window_start': timing.start + epoch_offset,
            'window_end': timing.settled_at + epoch_offset,
            'publishers': self.scenario.publisher_count,
            'subscribers': subscriber_count,
            'worker_kills': worker_kills,
            'publications': get_rate_figures(published_count, published_seconds),
            'deliveries': get_rate_figures(delivered_count, settled_seconds),
            'publication': publish_latencies.get_figures(),
            'publication_to_delivery': latencies.get_figures(),
            'pull': pull_figures,
            'push': push_figures,
        }

        # The round-trip time that the network of the database container was given, if any
        if DatabaseCtx.Env_Round_Trip_Ms in os.environ:
            out['database_round_trip_ms'] = float(os.environ[DatabaseCtx.Env_Round_Trip_Ms])

        return out

# ################################################################################################################################
# ################################################################################################################################

def verify_and_report(measurement:'Measurement', name:'str', run:'ScenarioRun', timing:'Timing', worker_kills:'int') -> 'None':
    """ Verifies that a finished run delivered each message exactly once to each pull subscriber and at least once
    to each push subscriber, exactly once without worker kills, and then records its figures.
    """
    check = run.check()

    assert check.lost_count == 0, f'{check.lost_count} of {check.expected_count} pull deliveries lost'
    assert check.duplicate_count == 0, f'{check.duplicate_count} pull deliveries processed more than once'
    assert check.unexpected_count == 0, f'{check.unexpected_count} receipts of messages never published'

    push_check = run.check_pushes()

    assert push_check.lost_count == 0, f'{push_check.lost_count} of {push_check.expected_count} push deliveries lost'
    assert push_check.unexpected_count == 0, f'{push_check.unexpected_count} pushes of messages never published'
    assert push_check.mismatch_count == 0, f'{push_check.mismatch_count} pushes with a message ID other than their key'

    # A push that the receiver confirmed and whose acknowledgement did not commit before a worker kill
    # is pushed again, so repeated pushes are a figure of a run with kills and a failure of any other.
    if not worker_kills:
        assert push_check.repeated_count == 0, f'{push_check.repeated_count} pushes repeated'

    figures = run.get_figures(timing, worker_kills, push_check)
    _ = report_result(measurement, name, figures)

# ################################################################################################################################
# ################################################################################################################################
