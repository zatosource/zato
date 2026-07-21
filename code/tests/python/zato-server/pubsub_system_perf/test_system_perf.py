# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from concurrent.futures import ThreadPoolExecutor
from time import monotonic, sleep

# Shared perf floors and helpers
from perf import measure_median_seconds, Max_Operation_Seconds, Min_Delivery_Rate_Per_Second, Min_Publish_Rate_Per_Second

# Zato
from zato.common.test import pubsub_db
from zato.common.test.config_pubsub_system_perf import Expected_Deliveries, Facade_Publish_Every, Latency_Topic_Name, \
    Message_Count, Publisher_Thread_Count, Service_Count, Sub_Count, Topic_Count, Topic_Name_Template

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_system_perf')

# The per-request logging of the shared REST clients would drown the run
# at thousands of publishes, so only warnings get through.
logging.getLogger('zato.common.test.client').setLevel(logging.WARNING)

# The unacknowledged backlog must reach at least this depth before delivery
# starts - it is what makes the drain phase a real measurement of working off
# a deep queue rather than an idle-queue one.
_min_peak_backlog = 10_000

# How often the drain poll asks the server for the reception totals, in seconds.
_poll_interval = 0.5

# How many iterations each latency median is measured over.
_latency_iterations = 20

# The drain deadline allows twice the floor-implied time plus a fixed margin.
_drain_margin_seconds = 60

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_system_perf import TestConfig

    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_system_perf import TestConfig

    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _publish_share(thread_index:'int') -> 'None':
    """ One publisher thread's share of the total - round-robin over all the topics,
    with every n-th message going through the service facade instead of REST.
    """
    publisher = _get_publisher()
    admin = _get_admin()

    share = Message_Count // Publisher_Thread_Count

    for message_index in range(share):

        global_index = thread_index * share + message_index
        topic_name = Topic_Name_Template.format((global_index % Topic_Count) + 1)
        data = f'system-perf-{global_index}'

        # .. every n-th publish exercises self.pubsub.publish through the harness service ..
        if message_index % Facade_Publish_Every == 0:
            _ = admin.invoke('test.system.perf.publish', {'topic_name': topic_name, 'data': data})
        else:
            _ = publisher.publish(topic_name, data)

# ################################################################################################################################
# ################################################################################################################################

class TestSystemPerf:
    """ 10.2 - the system-level performance test through a running server:
    1,000 push queues over 200 topics delivering into 500 counting services,
    publishers going through both the REST API and self.pubsub.publish,
    with the standard floors asserted end to end.
    """

    def test_system_perf(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        # .. sanity - every subscription from the topology must exist ..
        sub_list = admin.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

        if isinstance(sub_list, list):
            items:'anylist' = sub_list
        else:
            items = sub_list['zato_pubsub_subscription_get_list_response']

        perf_subs = []
        for item in items:
            if item['sec_name'].startswith('test.system.perf.sub.'):
                perf_subs.append(item)

        assert len(perf_subs) == Sub_Count, f'Expected {Sub_Count} subscriptions, found {len(perf_subs)}'
        sample_sub_key = perf_subs[0]['sub_key']

        # .. reset the reception counters so the totals below are exact ..
        _ = admin.invoke('test.system.perf.clear-received')

        # .. stop delivery so the publish phase builds a deep unacknowledged backlog ..
        _ = admin.invoke('test.system.perf.stop-delivery')

        # .. the publish phase - concurrent threads pumping through REST and the facade ..
        publish_start = monotonic()

        with ThreadPoolExecutor(max_workers=Publisher_Thread_Count) as executor:
            futures = []
            for thread_index in range(Publisher_Thread_Count):
                futures.append(executor.submit(_publish_share, thread_index))
            for future in futures:
                future.result()

        publish_elapsed = monotonic() - publish_start
        publish_rate = Message_Count / publish_elapsed

        logger.info('Publish phase done: %d messages in %.1fs (%.0f/s)', Message_Count, publish_elapsed, publish_rate)

        # .. the backlog is now at its deepest - every publish multiplied by the fan-out ..
        backlog_depth = pubsub_db.count_all_deliveries()
        logger.info('Backlog depth before the drain: %d', backlog_depth)

        # .. with the deep backlog in place, measure the user-visible operations.
        # .. The latency topic has no subscribers so these publishes add no deliveries ..
        publish_median = measure_median_seconds(
            lambda: publisher.publish(Latency_Topic_Name, 'latency-probe'), _latency_iterations)

        topic_list_median = measure_median_seconds(
            lambda: admin.invoke('zato.pubsub.topic.get-list', {'cluster_id': 1}), _latency_iterations)

        browse_median = measure_median_seconds(
            lambda: admin.invoke('zato.pubsub.subscription.browse-queue', {
                'sub_key': sample_sub_key,
                'state': 'pending',
            }), _latency_iterations)

        logger.info('Latency medians under load: publish %.1f ms, topic list %.1f ms, browse %.1f ms',
            publish_median * 1000, topic_list_median * 1000, browse_median * 1000)

        # .. restart delivery - 1,000 greenlets begin working the backlog off ..
        drain_start = monotonic()
        _ = admin.invoke('test.system.perf.start-delivery')

        # .. poll the reception totals until every expected delivery arrived ..
        deadline = drain_start + (Expected_Deliveries / Min_Delivery_Rate_Per_Second) * 2 + _drain_margin_seconds

        total = 0
        last_logged = monotonic()

        while monotonic() < deadline:
            response = admin.invoke('test.system.perf.get-received')
            total = response['total']

            if total >= Expected_Deliveries:
                break

            now = monotonic()
            if now - last_logged >= 5:
                logger.info('Drain progress: %d/%d received', total, Expected_Deliveries)
                last_logged = now

            sleep(_poll_interval)

        drain_elapsed = monotonic() - drain_start

        # .. every message must have been delivered exactly once per subscriber ..
        assert total == Expected_Deliveries, \
            f'Expected {Expected_Deliveries} deliveries, got {total} after {drain_elapsed:.1f}s'

        # .. every service must have received something ..
        response = admin.invoke('test.system.perf.get-received')
        services_with_data = response['services_with_data']
        assert services_with_data == Service_Count, \
            f'Expected all {Service_Count} services to receive messages, got {services_with_data}'

        delivery_rate = Expected_Deliveries / drain_elapsed

        logger.info('System perf run done: publish %.0f/s, delivery %.0f/s over %.1fs, backlog depth %d',
            publish_rate, delivery_rate, drain_elapsed, backlog_depth)

        # .. the floors, end to end through the whole stack ..
        assert publish_rate >= Min_Publish_Rate_Per_Second, f'Publish rate too low: {publish_rate:.0f}/s'
        assert delivery_rate >= Min_Delivery_Rate_Per_Second, f'Delivery rate too low: {delivery_rate:.0f}/s'

        assert publish_median < Max_Operation_Seconds, f'Publish too slow under load: {publish_median * 1000:.1f} ms'
        assert topic_list_median < Max_Operation_Seconds, f'Topic list too slow under load: {topic_list_median * 1000:.1f} ms'
        assert browse_median < Max_Operation_Seconds, f'Queue browse too slow under load: {browse_median * 1000:.1f} ms'

        # .. and the drain must have started from a genuinely deep backlog.
        assert backlog_depth >= _min_peak_backlog, f'Backlog never got deep: depth was {backlog_depth}'

# ################################################################################################################################
# ################################################################################################################################
