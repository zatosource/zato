# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The latencies of a suite judged second by second. A host that the suites share with other workloads stalls
# for a few seconds at a time, when another process flushes to the same drive or takes the processors, and each
# operation that begins in such a second is slow regardless of the server. The seconds of a measured interval
# in which an operation exceeded its limit, or in which the paced traffic began no operation at all, are stalled
# seconds. Up to a share of the seconds of a full interval are excluded as stalled, the slowest first, and the
# percentile is checked over the operations of the remaining seconds. A server that degrades for longer than
# the share, or that stays slow, still fails the check.

# stdlib
from dataclasses import dataclass
from math import floor, inf

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import floatlist

    latency_list = list[tuple[float, float]]
    int_set = set[int]

# ################################################################################################################################
# ################################################################################################################################

# The percentile of the latencies that each check uses.
Percentile = 0.99

# The share of the seconds of a measured interval that may be excluded as stalled.
Max_Stalled_Share = 0.2

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SteadyLatency:
    """ The percentile of the latencies of the seconds that were not stalled, and what was excluded as stalled.
    """
    percentile: 'float'
    sample_count: 'int'
    stalled_seconds: 'int'
    stalled_sample_count: 'int'
    slowest_stalled: 'float'

# ################################################################################################################################
# ################################################################################################################################

def get_percentile(values:'floatlist', percentile:'float'=Percentile) -> 'float':
    """ The value below which the given share of the values falls, or zero when there are no values.
    """
    if not values:
        return 0.0

    ordered = sorted(values)
    index = int(len(ordered) * percentile)
    index = min(index, len(ordered) - 1)

    out = ordered[index]
    return out

# ################################################################################################################################

def get_second(started:'float', start:'float') -> 'int':
    """ The second of a measured interval that began at start in which an operation that began at started began.
    """
    out = floor(started - start)
    return out

# ################################################################################################################################

def find_stalled_seconds(
    samples:'latency_list',
    start:'float',
    second_count:'int',
    limit:'float',
    counts_empty:'bool',
    max_stalled:'int',
    ) -> 'int_set':
    """ The seconds of a measured interval excluded as stalled. Each sample is the moment an operation began
    and the seconds it took. A second is stalled when an operation that began in it took longer than the limit,
    or, when counts_empty is set because the traffic is paced, when no operation began in one of the second_count
    full seconds of the interval. At most max_stalled seconds are excluded, the seconds without any operation first,
    then the slowest. The budget does not shrink with the interval, because a stall of the host lasts as long
    in the last, shorter interval of a run as in any other.
    """
    # The slowest operation that began in each second ..
    slowest:'dict[int, float]' = {}

    for started, seconds in samples:
        second = get_second(started, start)
        if second in slowest:
            slowest[second] = max(slowest[second], seconds)
        else:
            slowest[second] = seconds

    # .. the seconds of paced traffic in which no operation began are the most stalled ones ..
    candidates:'list[tuple[float, int]]' = []

    if counts_empty:
        for second in range(second_count):
            if second not in slowest:
                candidates.append((inf, second))

    # .. followed by the seconds with an operation above the limit, the slowest first ..
    for second, seconds in slowest.items():
        if seconds > limit:
            candidates.append((seconds, second))

    candidates.sort(reverse=True)

    # .. and as many of them as the share allows are excluded.
    out:'int_set' = set()

    for _, second in candidates[:max_stalled]:
        out.add(second)

    return out

# ################################################################################################################################

def get_steady_latency(
    samples:'latency_list',
    start:'float',
    stalled:'int_set',
    percentile:'float'=Percentile,
    ) -> 'SteadyLatency':
    """ The percentile of the latencies of the operations that began outside the stalled seconds.
    """
    kept:'floatlist' = []
    stalled_sample_count = 0
    slowest_stalled = 0.0

    for started, seconds in samples:
        if get_second(started, start) in stalled:
            stalled_sample_count += 1
            slowest_stalled = max(slowest_stalled, seconds)
        else:
            kept.append(seconds)

    out = SteadyLatency()
    out.percentile = get_percentile(kept, percentile)
    out.sample_count = len(kept)
    out.stalled_seconds = len(stalled)
    out.stalled_sample_count = stalled_sample_count
    out.slowest_stalled = slowest_stalled

    return out

# ################################################################################################################################

def get_run_latency(samples:'latency_list', limit:'float') -> 'SteadyLatency':
    """ The percentile of the latencies of a whole run, which spans the seconds from the first operation
    to the last one, with its stalled seconds excluded.
    """
    first = samples[0][0]
    last = first

    for started, _ in samples:
        first = min(first, started)
        last = max(last, started)

    second_count = get_second(last, first) + 1
    max_stalled = int(second_count * Max_Stalled_Share)
    stalled = find_stalled_seconds(samples, first, second_count, limit, False, max_stalled)

    out = get_steady_latency(samples, first, stalled)
    return out

# ################################################################################################################################

def get_latencies(samples:'latency_list') -> 'floatlist':
    """ The seconds that each operation took, without the moments they began.
    """
    out:'floatlist' = []

    for _, seconds in samples:
        out.append(seconds)

    return out

# ################################################################################################################################
# ################################################################################################################################
