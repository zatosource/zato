# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt
"""

# Must come first
from gevent.monkey import patch_all
_ = patch_all()

# stdlib
import logging
from logging import getLogger

# colorama
from colorama import Fore, Style, init as colorama_init

# gevent
from gevent import spawn

# Zato
from zato.common.pubsub.perftest.python_.producer import Producer
from zato.common.pubsub.perftest.python_.consumer import Consumer
from zato.common.pubsub.perftest.python_.progress_tracker import ProgressTracker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

log_level = logging.WARNING
log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=log_level, format=log_format)

colorama_init()

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class ConsumerManager:
    """ Creates new instances of Consumer class in greenlets.
    """

    def _start_consumer(self,
        consumer_id:'int',
        pull_interval:'float',
        max_topics:'int',
        progress_tracker:'ProgressTracker'
    ) -> 'any_':

        consumer = Consumer(progress_tracker, consumer_id, pull_interval, max_topics)
        greenlet = spawn(consumer.start)
        return greenlet

# ################################################################################################################################

    def run(self, num_consumers:'int', pull_interval:'float'=1.0, max_topics:'int'=3) -> 'None':
        """ Run the specified number of consumers.
        """
        if num_consumers == 1:
            noun = 'consumer'
        else:
            noun = 'consumers'

        progress_tracker = ProgressTracker(num_consumers, 0)

        print(f'{Fore.CYAN}Starting {num_consumers} {noun} with pull interval {pull_interval}s{Style.RESET_ALL}')
        print(f'{Fore.CYAN}Topics: {max_topics}{Style.RESET_ALL}')
        print()

        greenlets = []
        for consumer_id in range(1, num_consumers + 1):
            greenlet = self._start_consumer(consumer_id, pull_interval, max_topics, progress_tracker)
            greenlets.append(greenlet)

        # Wait for all greenlets to complete
        for greenlet in greenlets:
            greenlet.join()

# ################################################################################################################################
# ################################################################################################################################

class ProducerManager:
    """ Creates new instances of Producer class in greenlets.
    """

    def _start_producer(self,
        reqs_per_producer:'int',
        producer_id:'int',
        reqs_per_second:'float',
        max_topics:'int',
        progress_tracker:'ProgressTracker'
    ) -> 'any_':

        producer = Producer(progress_tracker, reqs_per_producer, producer_id, reqs_per_second, max_topics)
        greenlet = spawn(producer.start)
        return greenlet

# ################################################################################################################################

    def run(self, num_producers:'int', reqs_per_producer:'int'=1, reqs_per_second:'float'=1.0, max_topics:'int'=3) -> 'None':
        """ Run the specified number of producers and wait for completion.
        """
        if num_producers == 1:
            noun = 'producer'
        else:
            noun = 'producers'

        total_messages = num_producers * reqs_per_producer * max_topics
        progress_tracker = ProgressTracker(num_producers, total_messages)

        print(f'{Fore.CYAN}Starting {num_producers} {noun} with {total_messages:,} total messages{Style.RESET_ALL}')
        print(f'{Fore.CYAN}Rate: {reqs_per_second} req/s per producer, Topics: {max_topics}{Style.RESET_ALL}')
        print()

        greenlets = []
        for producer_id in range(1, num_producers + 1):
            greenlet = self._start_producer(reqs_per_producer, producer_id, reqs_per_second, max_topics, progress_tracker)
            greenlets.append(greenlet)

        # Wait for all greenlets to complete
        for greenlet in greenlets:
            greenlet.join()

        progress_tracker.finish()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import argparse

    parser = argparse.ArgumentParser(description='Producer/Consumer Manager')
    _ = parser.add_argument('--num-producers', type=int, help='Number of producers to start')
    _ = parser.add_argument('--num-consumers', type=int, help='Number of consumers to start')
    _ = parser.add_argument('--reqs-per-producer', type=int, default=1, help='Number of requests each producer should send')
    _ = parser.add_argument('--reqs-per-second', type=float, default=1.0, help='Number of requests per second each producer should make')
    _ = parser.add_argument('--pull-interval', type=float, default=1.0, help='Pull interval for consumers in seconds')
    _ = parser.add_argument('--max-topics', type=int, default=3, help='Number of topics to publish to')
    args = parser.parse_args()

    if args.num_producers:
        manager = ProducerManager()
        manager.run(args.num_producers, args.reqs_per_producer, args.reqs_per_second, args.max_topics)
    elif args.num_consumers:
        manager = ConsumerManager()
        manager.run(args.num_consumers, args.pull_interval, args.max_topics)
    else:
        parser.error('Must specify either --num-producers or --num-consumers')

# ################################################################################################################################
# ################################################################################################################################
