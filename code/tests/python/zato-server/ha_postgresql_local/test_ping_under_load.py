# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The latency of /zato/ping of a server that publishers and subscribers of pub/sub saturate, measured as an active-standby
# node measures it, with the interval and the timeout of the pings of the node. A ping that the load delays past the timeout
# counts towards the liveness timeout of the node, after which the node resigns, so no such ping is permitted.

# stdlib
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

# PyYAML
import yaml

# Zato
from local_server import create_local_server, is_answering, start_local_server, stop_local_server
from pubsub_perf.clients import Publisher, Subscriber
from pubsub_perf.config import Credentials, PerfConfig, Receipts_Topic
from pubsub_perf.payloads import build_documents
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient
from zato.common.test.ha_limits import HALimits
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from concurrent.futures import Future
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import anydict, anylist, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

credentialslist = list[Credentials]
floatlist       = list[float]
futurelist      = list['Future[None]']
publisherlist   = list[Publisher]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The topic of the load, and how many publishers and subscribers it has
    Topic_Name       = 'ha.liveness.load'
    Publisher_Count  = 16
    Subscriber_Count = 16

    # How long the load runs, in seconds
    Load_Duration = 60.0

    # How long the load runs before the first ping is counted, in seconds
    Warm_Up = 5.0

    # The prefix of the keys of the messages of each publisher, followed by its index and by the sequence of each message
    Key_Prefix = 'ha.liveness.'
    Key_Index_Width = 3
    Key_Sequence_Width = 7

    # How long a pulled message stays reserved for its subscriber, in seconds, as the default of the server
    Lease_Seconds = 30.0

    # The percentiles of the latency of the ping that the figures list
    Percentiles = (50, 90, 99)

    # The name under which the figures are recorded
    Result_Name = 'Ping latency under load'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PingRecord:
    """ The latencies of the answered pings and the moments of the unanswered ones, counted from the start of the load.
    """
    latencies: 'floatlist'
    unanswered_at: 'floatlist'

# ################################################################################################################################
# ################################################################################################################################

def _new_credentials(role:'str', count:'int') -> 'credentialslist':
    """ Returns the given number of API clients of one role, each with a password of its own.
    """
    out:'credentialslist' = []

    for index in range(count):
        username = f'test.ha.liveness.{role}.{index:02d}'
        password = f'{username}.{CryptoManager.generate_hex_string()}'

        credentials = Credentials(username, password)
        out.append(credentials)

    return out

# ################################################################################################################################

def _get_security(credentials:'Credentials') -> 'anydict':
    """ Returns the enmasse definition of the basic authentication of one API client.
    """
    out:'anydict' = {
        'name': credentials.username,
        'type': 'basic_auth',
        'username': credentials.username,
        'password': credentials.password,
    }

    return out

# ################################################################################################################################

def _build_definition(publishers:'credentialslist', subscribers:'credentialslist') -> 'str':
    """ Returns the enmasse YAML of the topic, of the topic of the receipts that the subscribers publish,
    of the API clients, of their permissions and of one pull subscription of each subscriber.
    """
    security:'anylist' = []
    permissions:'anylist' = []
    subscriptions:'anylist' = []

    for credentials in publishers:
        security.append(_get_security(credentials))
        permissions.append({
            'security': credentials.username,
            'pub': [ModuleCtx.Topic_Name],
        })

    for credentials in subscribers:
        security.append(_get_security(credentials))
        permissions.append({
            'security': credentials.username,
            'pub': [Receipts_Topic],
            'sub': [ModuleCtx.Topic_Name],
        })
        subscriptions.append({
            'security': credentials.username,
            'delivery_type': 'pull',
            'topic_list': [ModuleCtx.Topic_Name],
        })

    definition:'anydict' = {
        'security': security,
        'pubsub_topic': [{'name': ModuleCtx.Topic_Name}, {'name': Receipts_Topic}],
        'pubsub_permission': permissions,
        'pubsub_subscription': subscriptions,
    }

    out = yaml.safe_dump(definition, sort_keys=False)
    return out

# ################################################################################################################################

def _ping_until(ping_url:'str', started_at:'float', stop:'threading.Event', record:'PingRecord') -> 'None':
    """ Sends /zato/ping every Server_Ping_Interval with Server_Ping_Timeout, as the node does, and records each outcome.
    """
    while not stop.is_set():

        sent_at = time.monotonic()
        answered = is_answering(ping_url, HALimits.Server_Ping_Timeout)
        latency = time.monotonic() - sent_at

        if sent_at - started_at >= ModuleCtx.Warm_Up:
            if answered:
                record.latencies.append(latency)
            else:
                moment = sent_at - started_at
                record.unanswered_at.append(moment)
                logger.warning('Ping unanswered at %.3fs', moment)

        remaining = HALimits.Server_Ping_Interval - latency

        if remaining > 0:
            _ = stop.wait(remaining)

# ################################################################################################################################

def _get_percentile(values:'floatlist', percentile:'int') -> 'float':
    """ Returns the value below which the given percentage of the sorted values falls.
    """
    value_count = len(values)
    position = value_count * percentile // 100
    position = min(position, value_count - 1)

    out = values[position]
    return out

# ################################################################################################################################

def _get_figures(record:'PingRecord', published:'int', window_start:'float', window_end:'float') -> 'stranydict':
    """ Returns the percentiles and the maximum of the latency of the pings, the number of unanswered ones,
    the clients of the load, the messages they published and the window of the load in the time of the system.
    """
    latencies = sorted(record.latencies)
    duration = window_end - window_start

    out:'stranydict' = {
        'ping_count': len(latencies) + len(record.unanswered_at),
        'unanswered_count': len(record.unanswered_at),
        'ping_timeout': HALimits.Server_Ping_Timeout,
        'publishers': ModuleCtx.Publisher_Count,
        'subscribers': ModuleCtx.Subscriber_Count,
        'published_count': published,
        'published_per_second': published / duration,
        'window_start': window_start,
        'window_end': window_end,
    }

    for percentile in ModuleCtx.Percentiles:
        out[f'p{percentile}'] = _get_percentile(latencies, percentile)

    out['max'] = latencies[-1]

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_ping_under_load(pubsub_database:'PubSubDatabase') -> 'None':
    """ Under the load of publishers and subscribers, every ping of the node is answered within Server_Ping_Timeout.
    """
    publishers = _new_credentials('publisher', ModuleCtx.Publisher_Count)
    subscribers = _new_credentials('subscriber', ModuleCtx.Subscriber_Count)
    definition = _build_definition(publishers, subscribers)

    server = create_local_server(pubsub_database, definition)

    stop = threading.Event()
    record = PingRecord()
    record.latencies = []
    record.unanswered_at = []

    worker_count = ModuleCtx.Publisher_Count + ModuleCtx.Subscriber_Count
    executor = ThreadPoolExecutor(max_workers=worker_count)

    try:

        # The server answers ..
        _ = start_local_server(server)

        client = AdminClient(server.base_url, server.invoke_password)
        measurement = start_measurement(client, pubsub_database)

        # .. the clients of pub/sub reach it ..
        PerfConfig.base_url = server.base_url
        PerfConfig.lease_seconds = ModuleCtx.Lease_Seconds

        key_length = len(ModuleCtx.Key_Prefix) + ModuleCtx.Key_Index_Width + 1 + ModuleCtx.Key_Sequence_Width
        documents = build_documents(key_length)

        started_at = time.monotonic()
        window_start = time.time()
        deadline = started_at + ModuleCtx.Load_Duration

        # .. the subscribers and the publishers saturate it ..
        futures:'futurelist' = []

        for credentials in subscribers:
            subscriber = Subscriber(credentials)
            future = executor.submit(subscriber.run, stop)
            futures.append(future)

        publisher_objects:'publisherlist' = []

        for index, credentials in enumerate(publishers):
            key_prefix = f'{ModuleCtx.Key_Prefix}{index:0{ModuleCtx.Key_Index_Width}d}.'
            publisher = Publisher(credentials, ModuleCtx.Topic_Name, key_prefix, documents, index)
            publisher_objects.append(publisher)

            future = executor.submit(publisher.run, deadline)
            futures.append(future)

        # .. while the node pings it for the duration of the load ..
        ping_arguments = (server.ping_url, started_at, stop, record)
        ping_thread = threading.Thread(target=_ping_until, args=ping_arguments, daemon=True)
        ping_thread.start()

        remaining = deadline - time.monotonic()
        _ = stop.wait(remaining)
        stop.set()

        ping_thread.join()

        for future in futures:
            future.result()

        window_end = time.time()
        published = 0
        for publisher in publisher_objects:
            published += len(publisher.keys)

        # .. the figures are recorded ..
        figures = _get_figures(record, published, window_start, window_end)

        for name, value in figures.items():
            logger.info('Ping latency %s -> %s', name, value)

        _ = report_result(measurement, ModuleCtx.Result_Name, figures)

        # .. and every ping was answered within the timeout of the node.
        assert not record.unanswered_at, record.unanswered_at
        assert figures['max'] < HALimits.Server_Ping_Timeout, figures['max']

    finally:
        stop.set()
        executor.shutdown(wait=True, cancel_futures=True)
        stop_local_server(server)

# ################################################################################################################################
# ################################################################################################################################
