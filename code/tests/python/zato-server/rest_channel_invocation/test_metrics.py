# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Prometheus metrics of channels and services, read from the metrics channel of the server.

# stdlib
import time
from http.client import OK
from threading import Thread

# Prometheus
from prometheus_client.parser import text_string_to_metric_families

# Zato
from channel_client import basic_auth_header
from channel_definitions import Channels, Paths, Services
from channel_environment import Metrics_Username

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_suite import Suite
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

_metrics_path = '/metrics'

# How long the sleeping request lasts, and how long after it starts the gauge is read, in seconds
_sleep_seconds = 2
_gauge_read_delay = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _read_samples(suite:'Suite') -> 'strdict':
    """ Returns every sample of the metrics, keyed by the name of the sample and its sorted labels.
    """
    authorization = basic_auth_header(Metrics_Username, suite.environment.metrics_password)
    response = suite.client.get(_metrics_path, {'Authorization': authorization})

    assert response.status == OK, response.body

    out:'strdict' = {}

    for family in text_string_to_metric_families(response.text):
        for sample in family.samples:
            label_items = sorted(sample.labels.items())
            key = sample.name + repr(label_items)
            out[key] = sample.value

    return out

# ################################################################################################################################

def _key(name:'str', **labels:'str') -> 'str':
    label_items = sorted(labels.items())
    out = name + repr(label_items)
    return out

# ################################################################################################################################

def _value(samples:'strdict', key:'str') -> 'float':
    if key in samples:
        out = samples[key]
    else:
        out = 0.0
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_channel_and_service_metrics(suite:'Suite') -> 'None':

    request_counter = _key('zato_rest_channel_requests_total', channel_name=Channels.Echo, status_code='2xx', error_source='none')
    duration_count = _key('zato_rest_channel_request_duration_seconds_count', channel_name=Channels.Echo)
    service_counter = _key('zato_service_invocations_total', service_name=Services.Echo, outcome='ok')
    service_duration_count = _key('zato_service_duration_seconds_count', service_name=Services.Echo)

    before = _read_samples(suite)

    for _ in range(3):
        assert suite.client.get(Paths.Echo).status == OK

    after = _read_samples(suite)

    assert _value(after, request_counter) - _value(before, request_counter) == 3
    assert _value(after, duration_count) - _value(before, duration_count) == 3
    assert _value(after, service_counter) - _value(before, service_counter) == 3
    assert _value(after, service_duration_count) - _value(before, service_duration_count) == 3

# ################################################################################################################################

def test_error_metrics(suite:'Suite') -> 'None':
    channel_name = 'test.channel.error.exception'
    service_name = 'test.channel.error.exception'

    request_counter = _key('zato_rest_channel_requests_total', channel_name=channel_name, status_code='5xx', error_source='gateway')
    # The dispatcher converts the exception of the service into a response, which is why the invocation is counted as ok.
    service_counter = _key('zato_service_invocations_total', service_name=service_name, outcome='ok')

    before = _read_samples(suite)
    _ = suite.client.get(Paths.Error_Exception)
    after = _read_samples(suite)

    assert _value(after, request_counter) - _value(before, request_counter) == 1
    assert _value(after, service_counter) - _value(before, service_counter) == 1

# ################################################################################################################################

def test_requests_in_flight(suite:'Suite') -> 'None':
    gauge = _key('zato_server_requests_in_flight')

    idle = _value(_read_samples(suite), gauge)

    thread = Thread(target=suite.client.get, args=(f'{Paths.Sleep}?seconds={_sleep_seconds}',))
    thread.start()

    try:
        time.sleep(_gauge_read_delay)
        busy = _value(_read_samples(suite), gauge)
    finally:
        thread.join()

    after = _value(_read_samples(suite), gauge)

    assert busy >= idle + 1
    assert after == idle

# ################################################################################################################################
# ################################################################################################################################
