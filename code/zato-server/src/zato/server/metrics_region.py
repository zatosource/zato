# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from bisect import bisect_left
from dataclasses import dataclass
from logging import getLogger

# prometheus_client
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily, HistogramMetricFamily
from prometheus_client.registry import Collector
from prometheus_client.utils import floatToGoString

# Zato
from zato_ipc_core.zato_ipc_core import SharedRegion, SharedRegionFull

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from prometheus_client.metrics_core import Metric
    from zato.common.typing_ import any_, dict_, list_, strlist, tuple_

    any_ = any_
    Generator = Generator
    Metric = Metric
    strlist = strlist

    strtuple         = tuple_[str, ...]
    floattuple       = tuple_[float, ...]
    intlist          = list_[int]
    metricgen        = Generator[Metric, None, None]
    metriclist       = list_[Metric]
    seriesrecord     = tuple_[strlist, int, int]
    seriesrecordlist = list_[seriesrecord]
    strrecordsdict   = dict_[str, seriesrecordlist]
    strmetricdict    = dict_[str, 'RegionMetric']
    childdict        = dict_[strtuple, any_]
    strintdict       = dict_[str, int]
    countsdict       = dict_[strtuple, strintdict]
    sumsdict         = dict_[strtuple, float]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The kinds of series in the region, one series per counter or gauge and label set,
    # and one per bucket and one for the sum of a histogram and label set
    Kind_Counter          = 1
    Kind_Gauge            = 2
    Kind_Histogram_Bucket = 3
    Kind_Histogram_Sum    = 4

    # Separates the metric name, the label values and the bucket of a histogram in the key of a series
    Key_Separator = '\x00'

    # How the values of a gauge in the rows of the slots form its value on scrape
    Aggregate_Sum = 'sum'
    Aggregate_Max = 'max'

    # The upper bound of the last bucket of every histogram
    Bucket_Infinity = '+Inf'

    # The region of a process that no arbiter bound to the region of its server, which has one slot
    Local_Slot             = 0
    Local_Slot_Count       = 1
    Local_Series_Capacity  = 16384
    Local_Series_Key_Bytes = 16384 * 256
    Local_Start_ID         = 1

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MetricsBinding:
    """ The region that the metrics of this process record into and the slot whose row they write.
    """
    region: SharedRegion
    slot: int

# ################################################################################################################################
# ################################################################################################################################

class MetricsState:
    """ The binding of this process and every metric created in it.
    """
    def __init__(self) -> 'None':
        self.binding:'MetricsBinding | None' = None
        self.metrics:'strmetricdict' = {}

_state = MetricsState()

# ################################################################################################################################
# ################################################################################################################################

def _new_local_region() -> 'SharedRegion':
    """ Returns a region of one slot for a process that runs without an arbiter.
    """
    out = SharedRegion({
        'slot_count': ModuleCtx.Local_Slot_Count,
        'wake_capacity': 0,
        'cell_capacity': 0,
        'queue_count': 0,
        'metric_count': 0,
        'series_capacity': ModuleCtx.Local_Series_Capacity,
        'series_key_bytes': ModuleCtx.Local_Series_Key_Bytes,
        'dedup_capacity': 0,
        'breaker_capacity': 0,
        'lock_capacity': 0,
        'start_id': ModuleCtx.Local_Start_ID,
    })

    return out

# ################################################################################################################################

def _new_binding(region:'SharedRegion', slot:'int') -> 'MetricsBinding':
    out = MetricsBinding()
    out.region = region
    out.slot = slot

    return out

# ################################################################################################################################

def get_binding() -> 'MetricsBinding':
    """ Returns the binding of this process, binding a process that no arbiter bound to a region of its own.
    """
    if _state.binding is None:
        region = _new_local_region()
        _state.binding = _new_binding(region, ModuleCtx.Local_Slot)

    return _state.binding

# ################################################################################################################################

def bind_metrics(region:'SharedRegion', slot:'int') -> 'None':
    """ Makes the metrics of this process record into the row of a slot of the region of its server.
    """

    # The gauges of the row are reset, because a terminated predecessor in the slot left its own values in them ..
    for _key, kind, index in region.series_list():
        if kind == ModuleCtx.Kind_Gauge:
            region.series_set_float(slot, index, 0.0)

    # .. the binding replaces any earlier one ..
    _state.binding = _new_binding(region, slot)

    # .. and every label set registers its series anew, in the region of the binding.
    for metric in _state.metrics.values():
        metric.clear_children()

# ################################################################################################################################

def _series_key(name:'str', label_values:'strtuple') -> 'str':
    out = ModuleCtx.Key_Separator.join((name, *label_values))
    return out

# ################################################################################################################################
# ################################################################################################################################

class DiscardedChild:
    """ The label set of a metric whose series did not fit in the series table, which records nothing.
    """
    def inc(self, amount:'float'=1) -> 'None':
        pass

    def dec(self, amount:'float'=1) -> 'None':
        pass

    def set(self, value:'float') -> 'None':
        pass

    def observe(self, value:'float') -> 'None':
        pass

_discarded_child = DiscardedChild()

# ################################################################################################################################
# ################################################################################################################################

class CounterChild:
    """ One label set of a counter.
    """
    def __init__(self, binding:'MetricsBinding', index:'int') -> 'None':
        self.region = binding.region
        self.slot = binding.slot
        self.index = index

# ################################################################################################################################

    def inc(self, amount:'int'=1) -> 'None':
        self.region.series_add(self.slot, self.index, amount)

# ################################################################################################################################
# ################################################################################################################################

class GaugeChild:
    """ One label set of a gauge.
    """
    def __init__(self, binding:'MetricsBinding', index:'int') -> 'None':
        self.region = binding.region
        self.slot = binding.slot
        self.index = index

# ################################################################################################################################

    def inc(self, amount:'float'=1.0) -> 'None':
        self.region.series_add_float(self.slot, self.index, amount)

# ################################################################################################################################

    def dec(self, amount:'float'=1.0) -> 'None':
        self.region.series_add_float(self.slot, self.index, -amount)

# ################################################################################################################################

    def set(self, value:'float') -> 'None':
        self.region.series_set_float(self.slot, self.index, value)

# ################################################################################################################################
# ################################################################################################################################

class HistogramChild:
    """ One label set of a histogram.
    """
    def __init__(
        self,
        binding:'MetricsBinding',
        upper_bounds:'floattuple',
        bucket_indexes:'intlist',
        sum_index:'int',
        ) -> 'None':
        self.region = binding.region
        self.slot = binding.slot
        self.upper_bounds = upper_bounds
        self.bucket_indexes = bucket_indexes
        self.sum_index = sum_index

# ################################################################################################################################

    def observe(self, value:'float') -> 'None':

        # A value falls into the first bucket whose upper bound is not below it, or into the last, unbounded one ..
        position = bisect_left(self.upper_bounds, value)
        bucket_index = self.bucket_indexes[position]

        # .. and both the bucket and the sum record it.
        self.region.series_add(self.slot, bucket_index, 1)
        self.region.series_add_float(self.slot, self.sum_index, value)

# ################################################################################################################################
# ################################################################################################################################

class RegionMetric:
    """ A metric whose label sets are series of the region, which a scrape sums across the slots.
    """
    def __init__(self, name:'str', documentation:'str', labelnames:'strtuple') -> 'None':
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames
        self.children:'childdict' = {}

# ################################################################################################################################

    def clear_children(self) -> 'None':
        self.children.clear()

# ################################################################################################################################

    def labels(self, *label_values:'str', **named_label_values:'str') -> 'any_':
        """ Returns the child of a label set, given by position or by name, registering its series the first time.
        """
        if named_label_values:
            label_values = tuple(named_label_values[name] for name in self.labelnames)

        out = self.children.get(label_values)

        if out is None:
            out = self._new_child_or_discarded(label_values)
            self.children[label_values] = out

        return out

# ################################################################################################################################

    def _new_child_or_discarded(self, label_values:'strtuple') -> 'any_':
        binding = get_binding()

        try:
            out = self.new_child(binding, label_values)

        # A full series table is logged once per label set, whose child then records nothing.
        except SharedRegionFull:
            logger.error('Metric `%s` with labels %s is not recorded, the series table is full', self.name, label_values)
            out = _discarded_child

        return out

# ################################################################################################################################

    def new_child(self, binding:'MetricsBinding', label_values:'strtuple') -> 'any_':
        raise Exception('Must be implemented in subclasses')

# ################################################################################################################################

    def collect_family(self, region:'SharedRegion', records:'seriesrecordlist') -> 'Metric':
        raise Exception('Must be implemented in subclasses')

# ################################################################################################################################
# ################################################################################################################################

class RegionCounter(RegionMetric):
    """ A counter, summed across the slots.
    """
    def new_child(self, binding:'MetricsBinding', label_values:'strtuple') -> 'CounterChild':
        key = _series_key(self.name, label_values)
        index = binding.region.series_register(ModuleCtx.Kind_Counter, key)

        out = CounterChild(binding, index)
        return out

# ################################################################################################################################

    def collect_family(self, region:'SharedRegion', records:'seriesrecordlist') -> 'Metric':
        out = CounterMetricFamily(self.name, self.documentation, labels=self.labelnames)

        for label_values, _kind, index in records:
            value = region.series_sum(index)
            out.add_metric(label_values, value)

        return out

# ################################################################################################################################
# ################################################################################################################################

class RegionGauge(RegionMetric):
    """ A gauge, whose value is the sum or the largest of its values in the rows of the slots.
    """
    def __init__(self, name:'str', documentation:'str', labelnames:'strtuple', aggregate:'str') -> 'None':
        super().__init__(name, documentation, labelnames)
        self.aggregate = aggregate

# ################################################################################################################################

    def inc(self, amount:'float'=1.0) -> 'None':
        self.labels().inc(amount)

# ################################################################################################################################

    def dec(self, amount:'float'=1.0) -> 'None':
        self.labels().dec(amount)

# ################################################################################################################################

    def set(self, value:'float') -> 'None':
        self.labels().set(value)

# ################################################################################################################################

    def new_child(self, binding:'MetricsBinding', label_values:'strtuple') -> 'GaugeChild':
        key = _series_key(self.name, label_values)
        index = binding.region.series_register(ModuleCtx.Kind_Gauge, key)

        out = GaugeChild(binding, index)
        return out

# ################################################################################################################################

    def collect_family(self, region:'SharedRegion', records:'seriesrecordlist') -> 'Metric':
        out = GaugeMetricFamily(self.name, self.documentation, labels=self.labelnames)

        for label_values, _kind, index in records:

            # A gauge that counts work in progress is the sum of the slots ..
            if self.aggregate == ModuleCtx.Aggregate_Sum:
                value = region.series_sum_float(index)

            # .. and a gauge of a time or a moment is the largest value of any slot.
            elif self.aggregate == ModuleCtx.Aggregate_Max:
                value = region.series_max_float(index)

            # .. anything else is not a recognized aggregation.
            else:
                raise Exception(f'Unknown aggregation `{self.aggregate}` of gauge `{self.name}`')

            out.add_metric(label_values, value)

        return out

# ################################################################################################################################
# ################################################################################################################################

class RegionHistogram(RegionMetric):
    """ A histogram, whose buckets and sum are summed across the slots.
    """
    def __init__(self, name:'str', documentation:'str', labelnames:'strtuple', buckets:'floattuple') -> 'None':
        super().__init__(name, documentation, labelnames)
        self.upper_bounds = buckets

        # The names of the buckets as the exposition format writes them, the unbounded one last
        self.bucket_names:'strlist' = []

        for bound in buckets:
            self.bucket_names.append(floatToGoString(bound))

        self.bucket_names.append(ModuleCtx.Bucket_Infinity)

# ################################################################################################################################

    def new_child(self, binding:'MetricsBinding', label_values:'strtuple') -> 'HistogramChild':
        bucket_indexes:'intlist' = []

        # The buckets are registered before the sum, so a scrape that finds the sum of a label set finds its buckets ..
        for bucket_name in self.bucket_names:
            key = _series_key(self.name, (*label_values, bucket_name))
            index = binding.region.series_register(ModuleCtx.Kind_Histogram_Bucket, key)
            bucket_indexes.append(index)

        # .. once their entries are published.
        key = _series_key(self.name, label_values)
        sum_index = binding.region.series_register(ModuleCtx.Kind_Histogram_Sum, key)

        out = HistogramChild(binding, self.upper_bounds, bucket_indexes, sum_index)
        return out

# ################################################################################################################################

    def collect_family(self, region:'SharedRegion', records:'seriesrecordlist') -> 'Metric':
        counts:'countsdict' = {}
        sums:'sumsdict' = {}

        # The count of each bucket and the sum are read for each label set ..
        for label_values, kind, index in records:

            if kind == ModuleCtx.Kind_Histogram_Bucket:
                labels = tuple(label_values[:-1])
                bucket_name = label_values[-1]

                if labels not in counts:
                    counts[labels] = {}

                counts[labels][bucket_name] = region.series_sum(index)

            else:
                labels = tuple(label_values)
                sums[labels] = region.series_sum_float(index)

        out = HistogramMetricFamily(self.name, self.documentation, labels=self.labelnames)

        # .. and the buckets become cumulative, in the order of their upper bounds.
        for labels, sum_value in sums.items():
            buckets:'any_' = []
            cumulative = 0

            for bucket_name in self.bucket_names:

                # A bucket that a scrape listed before its entry was published has recorded nothing yet
                if labels in counts and bucket_name in counts[labels]:
                    cumulative += counts[labels][bucket_name]

                buckets.append((bucket_name, cumulative))

            out.add_metric(list(labels), buckets, sum_value)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _register_metric(metric:'any_') -> 'any_':
    """ Returns the metric of the same name created earlier in this process, or registers the new one.
    """
    if metric.name in _state.metrics:
        out = _state.metrics[metric.name]
    else:
        _state.metrics[metric.name] = metric
        out = metric

    return out

# ################################################################################################################################

def get_counter(name:'str', documentation:'str', labelnames:'strtuple') -> 'RegionCounter':
    metric = RegionCounter(name, documentation, labelnames)
    out = _register_metric(metric)
    return out

# ################################################################################################################################

def get_gauge(name:'str', documentation:'str', labelnames:'strtuple', aggregate:'str') -> 'RegionGauge':
    metric = RegionGauge(name, documentation, labelnames, aggregate)
    out = _register_metric(metric)
    return out

# ################################################################################################################################

def get_histogram(name:'str', documentation:'str', labelnames:'strtuple', buckets:'floattuple') -> 'RegionHistogram':
    metric = RegionHistogram(name, documentation, labelnames, buckets)
    out = _register_metric(metric)
    return out

# ################################################################################################################################
# ################################################################################################################################

class RegionCollector(Collector):
    """ Produces every metric of the region on scrape, with the values of every slot combined.
    """
    def describe(self) -> 'metriclist':

        # A registry that describes a collector by collecting it would bind this process before its arbiter does
        return []

# ################################################################################################################################

    def collect(self) -> 'metricgen':
        region = get_binding().region
        records_by_name:'strrecordsdict' = {}

        # The series of every metric are grouped by its name ..
        for key, kind, index in region.series_list():
            name, *label_values = key.split(ModuleCtx.Key_Separator)

            if name not in records_by_name:
                records_by_name[name] = []

            records_by_name[name].append((label_values, kind, index))

        # .. and each metric produces its family, with no samples if no worker recorded it yet.
        for metric in _state.metrics.values():

            if metric.name in records_by_name:
                records = records_by_name[metric.name]
            else:
                records = []

            yield metric.collect_family(region, records)

# ################################################################################################################################
# ################################################################################################################################
