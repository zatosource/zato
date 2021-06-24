# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import math
from datetime import timedelta
from operator import itemgetter

# Humanize
from humanize import precisedelta

# numpy
import numpy as np

# Zato
from zato.common.api import StatsKey

# ################################################################################################################################
# ################################################################################################################################

float_stats = ('item_max', 'item_min', 'item_mean', 'item_total_time')

# ################################################################################################################################
# ################################################################################################################################

def tmean(data, limit_from=None, limit_to=None):
    """ Trimmed mean - includes only elements up to the input limit, if it is given at all.
    """
    data = data if isinstance(data, list) else [data]

    if limit_from or limit_to:
        _data = []
        for elem in data:
            if limit_from:
                if elem < limit_from:
                    continue
            if limit_to:
                if elem > limit_to:
                    continue
            _data.append(elem)
        data = _data[:]

    count = len(data)
    total = sum(data)

    return total / count if count else 0

# ################################################################################################################################
# ################################################################################################################################

#
# Taken from https://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/
#
# Original code by Wai Yip Tung, licensed under the Python Foundation License
#
def percentile(data, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter data - a list of values
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of data.

    @return - the percentile of the values
    """
    if not data:
        return 0

    data.sort()
    k = (len(data)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(data[int(k)])
    d0 = key(data[int(f)]) * (c-k)
    d1 = key(data[int(c)]) * (k-f)

    return d0 + d1

# ################################################################################################################################
# ################################################################################################################################

def collect_current_usage(data):
    # type: (list) -> dict

    # For later use
    usage = 0

    last_duration = None
    last_timestamp = ''

    usage_min  = None
    usage_max  = None
    usage_mean = None

    # Make sure we always have a list to iterate over (rather than None)
    data = data or []

    for elem in data:

        if elem is None:
            continue

        usage += elem[StatsKey.PerKeyValue]

        if elem[StatsKey.PerKeyLastTimestamp] > last_timestamp:
            last_timestamp = elem[StatsKey.PerKeyLastTimestamp]
            last_duration = elem[StatsKey.PerKeyLastDuration]

        if usage_min:
            usage_min = min([usage_min, elem[StatsKey.PerKeyMin]])
        else:
            usage_min = elem[StatsKey.PerKeyMin]

        if usage_max:
            usage_max  = max([usage_max, elem[StatsKey.PerKeyMax]])
        else:
            usage_max = elem[StatsKey.PerKeyMax]

        if usage_mean:
            usage_mean = np.mean([usage_mean, elem[StatsKey.PerKeyMean]])
        else:
            usage_mean = elem[StatsKey.PerKeyMean]

        usage_mean = round(usage_mean, 3)

    return {
        StatsKey.PerKeyValue: usage,
        StatsKey.PerKeyLastDuration:  last_duration,
        StatsKey.PerKeyLastTimestamp: last_timestamp,
        StatsKey.PerKeyMin: usage_min,
        StatsKey.PerKeyMax: usage_max,
        StatsKey.PerKeyMean: usage_mean,
    }

# ################################################################################################################################
# ################################################################################################################################

def should_include_in_table_stats(service_name):
    # type: (str) -> bool
    if service_name.startswith('pub.zato'):
        return False
    elif service_name.startswith('zato'):
        return False
    else:
        return True

# ################################################################################################################################
# ################################################################################################################################

def combine_table_data(data, round_digits=2):
    # type: (list, int) -> dict

    # Response to return
    out = []

    # How many objects we have seen, e.g. how many individual services
    total_object_id = 0

    # Total usage across all events
    total_usage = 0

    # Total time spent in all the events (in ms)
    total_time = 0

    # Total mean time across all objects
    total_mean = 0

    # First pass, filter out objects with known unneeded names
    # and collect total usage of each object and of objects as a whole.
    for pid_response in data: # type: dict
        if pid_response:
            for object_name, stats in pid_response.items(): # type: (str, dict)
                if should_include_in_table_stats(object_name):

                    # Update per object counters

                    # Total usage needs to be an integer
                    stats['item_total_usage'] = int(stats['item_total_usage'])

                    # These are always floats that we need to round up
                    for name in float_stats:
                        stats[name] = round(stats[name], round_digits)

                    # Add to totals
                    total_usage += stats['item_total_usage']
                    total_mean  += stats['item_mean']
                    total_time  += stats['item_total_time']
                    total_object_id += 1

                    # Finally, add the results so that they can be used in further steps
                    item = dict(stats)
                    item['name'] = object_name

                    out.append(item)

    # We know how many events we have so we can now compute the mean across all of them
    if total_object_id:
        total_mean = total_mean / total_object_id

    # In this pass, we can attach additional per-object statistics
    for item in out: # type: dict

        item_usage_share = item['item_total_usage'] / total_usage * 100
        item_usage_share = round(item_usage_share, round_digits)

        item_time_share = item['item_total_time'] / total_time * 100
        item_time_share = round(item_time_share, round_digits)

        item['item_usage_share'] = item_usage_share
        item['item_time_share'] = item_time_share
        item['item_total_usage_human'] = item['item_total_usage'] # Currently, this is the same

        total_time_delta_min_unit = 'milliseconds' if item['item_total_time'] < 1 else 'seconds'
        total_time_delta = timedelta(milliseconds=item['item_total_time'])
        total_time_delta = precisedelta(total_time_delta, minimum_unit=total_time_delta_min_unit)

        item['item_total_time_human'] = total_time_delta

    # Sort by the most interesting attribute
    out.sort(key=itemgetter('item_time_share'), reverse=True)

    return out

# ################################################################################################################################
# ################################################################################################################################
