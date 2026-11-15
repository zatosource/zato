# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from multiprocessing import get_context

# prometheus_client
from prometheus_client import CollectorRegistry, generate_latest, Histogram
from prometheus_client.parser import text_string_to_metric_families

# Zato
from zato.server.metrics_region import bind_metrics, DiscardedChild, get_counter, get_gauge, get_histogram, \
    ModuleCtx, RegionCollector
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.synchronize import Event
    from pathlib import Path
    from zato.common.typing_ import anytuple, callable_, dict_, list_, tuple_

    anytuple = anytuple
    callable_ = callable_
    Event = Event
    Path = Path

    floatlist  = list_[float]
    sampledict = dict_[tuple_[str, tuple_[tuple_[str, str], ...]], float]

# ################################################################################################################################
# ################################################################################################################################

_context = get_context('fork')

# How long the test waits for a process, in seconds
_join_timeout = 60.0

_slot_count = 4

# The slot whose process collects the metrics in each test
_collecting_slot = 0

# How many times each process records in the concurrency test
_concurrent_rounds = 1000

_counter = get_counter('zato_test_region_requests_total', 'Requests by channel', ('channel_name', 'status_code'))
_gauge_sum = get_gauge('zato_test_region_in_flight', 'Requests in progress', (), ModuleCtx.Aggregate_Sum)
_gauge_max = get_gauge('zato_test_region_reload_timestamp', 'Last reload', (), ModuleCtx.Aggregate_Max)

_buckets = (0.005, 0.01, 0.1, 1.0, 10.0)
_histogram_name = 'zato_test_region_duration_seconds'
_histogram = get_histogram(_histogram_name, 'Durations by channel', ('channel_name',), _buckets)

# The observations of each recording slot, which include values equal to an upper bound and values above every bound
_observations:'dict_[int, floatlist]' = {
    1: [0.001, 0.005, 0.05, 0.5, 20.0],
    2: [0.01, 0.01, 1.0, 9.99, 10.0, 11.0],
    3: [0.0, 0.1, 100.0],
}

# ################################################################################################################################
# ################################################################################################################################

def _new_region(series_capacity:'int') -> 'SharedRegion':
    out = SharedRegion({
        'slot_count': _slot_count,
        'wake_capacity': 0,
        'cell_capacity': 0,
        'queue_count': 0,
        'metric_count': 0,
        'series_capacity': series_capacity,
        'series_key_bytes': series_capacity * 256 * _slot_count,
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

def _collect(region:'SharedRegion', text_path:'Path') -> 'None':
    """ Binds to the collecting slot and writes what a scrape returns.
    """
    bind_metrics(region, _collecting_slot)

    registry = CollectorRegistry()
    registry.register(RegionCollector())

    _ = text_path.write_bytes(generate_latest(registry))

# ################################################################################################################################

def _get_samples(text:'str') -> 'sampledict':
    """ Returns the value of every sample of a scrape, by sample name and labels, without the creation times.
    """
    out:'sampledict' = {}

    for family in text_string_to_metric_families(text):
        for sample in family.samples:
            if not sample.name.endswith('_created'):
                labels = tuple(sorted(sample.labels.items()))
                out[sample.name, labels] = sample.value

    return out

# ################################################################################################################################

def _collected_samples(region:'SharedRegion', tmp_path:'Path') -> 'sampledict':
    text_path = tmp_path / 'scrape.txt'
    _run_in_child(_collect, (region, text_path))

    out = _get_samples(text_path.read_text())
    return out

# ################################################################################################################################
# ################################################################################################################################

def _record(region:'SharedRegion', slot:'int') -> 'None':
    """ Records the counter, both gauges and the observations of a slot.
    """
    bind_metrics(region, slot)

    for _ in range(slot * 100):
        _counter.labels('orders', '2xx').inc()

    _counter.labels(channel_name='invoices', status_code='5xx').inc()

    _gauge_sum.inc(3)
    _gauge_sum.dec()
    _gauge_max.set(slot * 1000.0)

    for value in _observations[slot]:
        _histogram.labels('orders').observe(value)

# ################################################################################################################################

def _expected_histogram_text() -> 'str':
    """ Returns what prometheus_client produces for every observation of every slot in one process.
    """
    registry = CollectorRegistry()
    histogram = Histogram(_histogram_name, 'Durations by channel', ('channel_name',), buckets=_buckets, registry=registry)

    for values in _observations.values():
        for value in values:
            histogram.labels('orders').observe(value)

    out = generate_latest(registry).decode('utf-8')
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_scrape_combines_the_rows_of_every_slot(tmp_path:'Path') -> 'None':
    region = _new_region(64)

    for slot in _observations:
        _run_in_child(_record, (region, slot))

    samples = _collected_samples(region, tmp_path)

    # The counters are the sums of the slots ..
    orders = (('channel_name', 'orders'), ('status_code', '2xx'))
    invoices = (('channel_name', 'invoices'), ('status_code', '5xx'))

    assert samples['zato_test_region_requests_total', orders] == 600
    assert samples['zato_test_region_requests_total', invoices] == len(_observations)

    # .. a gauge of work in progress is their sum, and a gauge of a moment is their largest value ..
    assert samples['zato_test_region_in_flight', ()] == 2 * len(_observations)
    assert samples['zato_test_region_reload_timestamp', ()] == 3000.0

    # .. and the histogram is the one that prometheus_client produces for every observation in one process.
    expected = _get_samples(_expected_histogram_text())

    for key, value in expected.items():
        assert samples[key] == value

    histogram_samples = {key for key in samples if key[0].startswith(_histogram_name)}
    assert histogram_samples == set(expected)

# ################################################################################################################################

def _record_and_exit(region:'SharedRegion', slot:'int') -> 'None':
    bind_metrics(region, slot)

    _counter.labels('orders', '2xx').inc(5)
    _gauge_sum.inc(7)

# ################################################################################################################################

def _start_without_recording(region:'SharedRegion', slot:'int') -> 'None':
    bind_metrics(region, slot)

# ################################################################################################################################

def test_a_replacement_worker_resets_the_gauges_of_its_slot_and_keeps_its_counters(tmp_path:'Path') -> 'None':
    region = _new_region(64)

    # A worker records and terminates, and its replacement starts in the same slot ..
    _run_in_child(_record_and_exit, (region, 1))
    _run_in_child(_start_without_recording, (region, 1))

    samples = _collected_samples(region, tmp_path)

    # .. which keeps the count of requests and drops the requests in progress of the terminated worker.
    assert samples['zato_test_region_requests_total', (('channel_name', 'orders'), ('status_code', '2xx'))] == 5
    assert samples['zato_test_region_in_flight', ()] == 0

# ################################################################################################################################

def _record_and_collect_unbound(text_path:'Path') -> 'None':
    """ Records and scrapes in a process that no arbiter bound.
    """
    _counter.labels('orders', '2xx').inc(2)

    registry = CollectorRegistry()
    registry.register(RegionCollector())

    _ = text_path.write_bytes(generate_latest(registry))

# ################################################################################################################################

def test_a_process_without_an_arbiter_records_into_a_region_of_its_own(tmp_path:'Path') -> 'None':
    text_path = tmp_path / 'scrape.txt'
    _run_in_child(_record_and_collect_unbound, (text_path,))

    samples = _get_samples(text_path.read_text())
    assert samples['zato_test_region_requests_total', (('channel_name', 'orders'), ('status_code', '2xx'))] == 2

# ################################################################################################################################

def _record_into_full_table(region:'SharedRegion') -> 'None':
    bind_metrics(region, 1)

    _counter.labels('first', '2xx').inc()
    _counter.labels('second', '2xx').inc()

    # The third label set finds no entry left, and its child records nothing without raising an exception
    third = _counter.labels('third', '2xx')
    third.inc()

    assert isinstance(third, DiscardedChild)

# ################################################################################################################################

def test_a_label_set_that_finds_the_series_table_full_is_discarded(tmp_path:'Path') -> 'None':
    region = _new_region(2)

    _run_in_child(_record_into_full_table, (region,))
    samples = _collected_samples(region, tmp_path)

    counter_samples = {key: value for key, value in samples.items() if key[0] == 'zato_test_region_requests_total'}

    assert counter_samples == {
        ('zato_test_region_requests_total', (('channel_name', 'first'), ('status_code', '2xx'))): 1,
        ('zato_test_region_requests_total', (('channel_name', 'second'), ('status_code', '2xx'))): 1,
    }

# ################################################################################################################################

def _record_before_and_after_binding(region:'SharedRegion') -> 'None':

    # A label set used before the arbiter binds the process is registered in its own region ..
    _counter.labels('orders', '2xx').inc(100)

    # .. and again in the region of the server, once bound.
    bind_metrics(region, 1)
    _counter.labels('orders', '2xx').inc()

# ################################################################################################################################

def test_a_label_set_used_before_binding_records_into_the_region_of_the_server_after_it(tmp_path:'Path') -> 'None':
    region = _new_region(64)

    _run_in_child(_record_before_and_after_binding, (region,))
    samples = _collected_samples(region, tmp_path)

    assert samples['zato_test_region_requests_total', (('channel_name', 'orders'), ('status_code', '2xx'))] == 1

# ################################################################################################################################

def _record_concurrently(region:'SharedRegion', slot:'int', start:'Event') -> 'None':
    bind_metrics(region, slot)

    # Every process registers the same label sets at the same moment
    _ = start.wait()

    for _ in range(_concurrent_rounds):
        _counter.labels('orders', '2xx').inc()
        _histogram.labels('orders').observe(0.5)

# ################################################################################################################################

def test_processes_that_register_the_same_label_sets_at_once_share_their_series(tmp_path:'Path') -> 'None':
    region = _new_region(64)
    start = _context.Event()

    processes = [
        _context.Process(target=_record_concurrently, args=(region, slot, start)) for slot in range(_slot_count)
    ]

    for process in processes:
        process.start()

    start.set()

    for process in processes:
        process.join(_join_timeout)
        assert process.exitcode == 0

    samples = _collected_samples(region, tmp_path)
    expected = _slot_count * _concurrent_rounds

    assert samples['zato_test_region_requests_total', (('channel_name', 'orders'), ('status_code', '2xx'))] == expected
    assert samples[_histogram_name + '_count', (('channel_name', 'orders'),)] == expected
    assert samples[_histogram_name + '_bucket', (('channel_name', 'orders'), ('le', '0.1'))] == 0
    assert samples[_histogram_name + '_bucket', (('channel_name', 'orders'), ('le', '1.0'))] == expected

# ################################################################################################################################
# ################################################################################################################################
