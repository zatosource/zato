# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Item 15.6 - the faults of the connections of one link through Toxiproxy - latency, a limit of the bandwidth,
# slicing of the segments, resets and cuts after a number of bytes, with a black hole as the total loss of each.

# stdlib
from time import monotonic

# Zato
from faults import Fault, Total_Loss
from toxiproxy import Both_Streams, Stream_Downstream

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from toxiproxy import Toxiproxy

    strintdict = dict[str, int]

# ################################################################################################################################
# ################################################################################################################################

# The kinds of stream faults.
Stream_Latency   = 'latency'
Stream_Bandwidth = 'bandwidth'
Stream_Slicer    = 'slicer'
Stream_Reset     = 'reset'
Stream_Cut       = 'cut'

Stream_Kinds = [Stream_Latency, Stream_Bandwidth, Stream_Slicer, Stream_Reset, Stream_Cut]

# How long one step of the latency is at each percentage of the severity, in milliseconds.
_latency_ms_per_level = 10

# The largest average size of a slice, in bytes, which the severity reduces.
_max_slice_bytes = 100

# After how many bytes a cut ends a connection, which is in the middle of a large result set or COPY stream.
_cut_bytes = 65536

# The smallest bandwidth that a link is limited to, in kilobytes per second.
_min_rate_kbps = 1

_bytes_per_kilobyte = 1024

# ################################################################################################################################
# ################################################################################################################################

def _remaining(level:'int') -> 'float':
    """ The share of a resource that is left at a severity level.
    """
    out = (Total_Loss - level) / Total_Loss
    return out

# ################################################################################################################################
# ################################################################################################################################

class StreamFault(Fault):
    """ One kind of toxic on one proxy - in both directions, apart from resets and cuts, which apply to what the client
    receives, at a toxicity of the severity, so that they end that share of the connections.
    """

    def __init__(self, toxiproxy:'Toxiproxy', proxy:'str', kind:'str') -> 'None':
        self.toxiproxy = toxiproxy
        self.proxy = proxy
        self.kind = kind
        self.name = f'stream-{kind}'

        self.baseline_kbps = 0.0
        self._baseline_started = 0.0
        self._baseline_bytes = 0

# ################################################################################################################################

    def start_baseline(self) -> 'None':
        self._baseline_started = monotonic()
        self._baseline_bytes = self.toxiproxy.read_received_bytes(self.proxy)

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        elapsed = monotonic() - self._baseline_started
        received = self.toxiproxy.read_received_bytes(self.proxy) - self._baseline_bytes
        received_kb = received / _bytes_per_kilobyte

        self.baseline_kbps = received_kb / elapsed

# ################################################################################################################################

    def _add_to_both(self, toxic_type:'str', attributes:'strintdict') -> 'None':
        for stream in Both_Streams:
            self.toxiproxy.add_toxic(self.proxy, toxic_type, attributes, stream)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        toxicity = level / Total_Loss

        # A total loss holds every byte without closing a connection ..
        if level == Total_Loss:
            self._add_to_both('timeout', {'timeout': 0})

        # .. the latency grows with the level ..
        elif self.kind == Stream_Latency:
            latency = level * _latency_ms_per_level
            self._add_to_both('latency', {'latency': latency, 'jitter': level})

        # .. the bandwidth is the share of the baseline that is left ..
        elif self.kind == Stream_Bandwidth:
            rate = int(self.baseline_kbps * _remaining(level))
            rate = max(rate, _min_rate_kbps)
            self._add_to_both('bandwidth', {'rate': rate})

        # .. the slices grow smaller ..
        elif self.kind == Stream_Slicer:
            average_size = int(_max_slice_bytes * _remaining(level))
            average_size = max(average_size, 1)
            size_variation = average_size // 2
            self._add_to_both('slicer', {'average_size': average_size, 'size_variation': size_variation, 'delay': level})

        # .. resets and cuts end that share of the connections ..
        elif self.kind == Stream_Reset:
            self.toxiproxy.add_toxic(self.proxy, 'reset_peer', {'timeout': 0}, Stream_Downstream, toxicity)

        elif self.kind == Stream_Cut:
            self.toxiproxy.add_toxic(self.proxy, 'limit_data', {'bytes': _cut_bytes}, Stream_Downstream, toxicity)

        # .. and anything else is not a kind of stream fault.
        else:
            raise Exception(f'Unknown stream fault `{self.kind}`')

# ################################################################################################################################

    def remove(self) -> 'None':
        self.toxiproxy.remove_toxics(self.proxy)

# ################################################################################################################################
# ################################################################################################################################
