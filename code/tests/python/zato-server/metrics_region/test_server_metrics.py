# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from multiprocessing import get_context

# prometheus_client
from prometheus_client import generate_latest, REGISTRY
from prometheus_client.parser import text_string_to_metric_families

# Zato
from zato.server import metrics
from zato.server.metrics_region import bind_metrics
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from zato.common.typing_ import anytuple, callable_, dict_, tuple_

    anytuple = anytuple
    callable_ = callable_
    Path = Path

    sampledict = dict_[tuple_[str, tuple_[tuple_[str, str], ...]], float]

# ################################################################################################################################
# ################################################################################################################################

_context = get_context('fork')

# How long the test waits for a process, in seconds
_join_timeout = 60.0

_slot_count = 3
_collecting_slot = 0
_recording_slots = (1, 2)

_channel_name = 'api.orders'
_service_name = 'orders.get'

# The expiry time of a certificate, as a Unix timestamp
_certificate_expiry = 1900000000.0

# ################################################################################################################################
# ################################################################################################################################

def _new_region() -> 'SharedRegion':
    out = SharedRegion({
        'slot_count': _slot_count,
        'wake_capacity': 0,
        'cell_capacity': 0,
        'queue_count': 0,
        'metric_count': 0,
        'series_capacity': 256,
        'series_key_bytes': 256 * 256 * _slot_count,
        'dedup_capacity': 0,
        'breaker_capacity': 0,
        'lock_capacity': 0,
        'start_id': 1,
    })

    return out

# ################################################################################################################################

def _run_in_child(target:'callable_', args:'anytuple') -> 'None':
    process = _context.Process(target=target, args=args)
    process.start()
    process.join(_join_timeout)

    assert process.exitcode == 0

# ################################################################################################################################

def _serve_request(region:'SharedRegion', slot:'int') -> 'None':
    """ Records one REST request in the way that the HTTP server of a worker records it, with the labels given by name.
    """
    bind_metrics(region, slot)

    metrics.zato_server_requests_in_flight.inc()

    metrics.zato_rest_channel_requests_total.labels(
        channel_name=_channel_name,
        status_code=metrics.get_status_code_class('200'),
        error_source='none',
    ).inc()

    metrics.zato_rest_channel_request_duration_seconds.labels(channel_name=_channel_name).observe(0.25)
    metrics.zato_service_invocations_total.labels(service_name=_service_name, outcome='ok').inc()
    metrics.zato_server_config_reloads_total.labels(result='success').inc()

    _ = metrics.zato_server_config_last_reload_timestamp_seconds.set(float(slot))
    _ = metrics.zato_tls_certificate_expiry_timestamp_seconds.labels('server', 'http').set(_certificate_expiry)

    # The request in progress completes, and one more begins that the scrape finds in progress
    metrics.zato_server_requests_in_flight.dec()
    metrics.zato_server_requests_in_flight.inc()

# ################################################################################################################################

def _scrape(region:'SharedRegion', text_path:'Path') -> 'None':
    """ Scrapes the registry of the server in the way that the metrics endpoint does.
    """
    bind_metrics(region, _collecting_slot)

    metrics.set_server_info('server1')
    metrics.refresh_uptime()

    _ = text_path.write_bytes(generate_latest(REGISTRY))

# ################################################################################################################################

def _get_samples(text:'str') -> 'sampledict':
    out:'sampledict' = {}

    for family in text_string_to_metric_families(text):
        for sample in family.samples:
            labels = tuple(sorted(sample.labels.items()))
            out[sample.name, labels] = sample.value

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_registry_of_the_server_returns_the_metrics_of_every_worker(tmp_path:'Path') -> 'None':
    region = _new_region()

    for slot in _recording_slots:
        _run_in_child(_serve_request, (region, slot))

    text_path = tmp_path / 'scrape.txt'
    _run_in_child(_scrape, (region, text_path))

    samples = _get_samples(text_path.read_text())
    worker_count = len(_recording_slots)

    # The counters and the requests in progress add up across the workers ..
    request_labels = (('channel_name', _channel_name), ('error_source', 'none'), ('status_code', '2xx'))
    assert samples['zato_rest_channel_requests_total', request_labels] == worker_count

    service_labels = (('outcome', 'ok'), ('service_name', _service_name))
    assert samples['zato_service_invocations_total', service_labels] == worker_count

    assert samples['zato_server_config_reloads_total', (('result', 'success'),)] == worker_count
    assert samples['zato_server_requests_in_flight', ()] == worker_count

    # .. each histogram counts the requests of every worker in its buckets ..
    duration_labels = (('channel_name', _channel_name),)
    assert samples['zato_rest_channel_request_duration_seconds_count', duration_labels] == worker_count
    assert samples['zato_rest_channel_request_duration_seconds_sum', duration_labels] == 0.25 * worker_count

    # .. the gauges of a moment are the latest values of any worker ..
    assert samples['zato_server_config_last_reload_timestamp_seconds', ()] == max(_recording_slots)

    expiry_labels = (('cert_name', 'server'), ('listener', 'http'))
    assert samples['zato_tls_certificate_expiry_timestamp_seconds', expiry_labels] == _certificate_expiry

    # .. and the process that scrapes adds its uptime and the information of the server.
    assert samples['zato_server_uptime_seconds', ()] > 0
    assert samples['zato_server_info', (('server_name', 'server1'), ('version', '4.1'))] == 1

# ################################################################################################################################
# ################################################################################################################################
