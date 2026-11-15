# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.rate_limiting.common import Microseconds_Per_Second
from zato.common.rate_limiting.fixed_window import compute_window_end_us, FixedWindowCheckResult
from zato.common.rate_limiting.token_bucket import CheckResult

# Rust
from zato_ipc_core.zato_ipc_core import RateLimitKey, SharedRegionFull

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rate_limiting.fixed_window import FixedWindowConfig
    from zato.common.rate_limiting.token_bucket import TokenBucketConfig
    from zato_ipc_core.zato_ipc_core import SharedRegion

    FixedWindowConfig = FixedWindowConfig
    SharedRegion = SharedRegion
    TokenBucketConfig = TokenBucketConfig

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a request refused because the table is at capacity waits before it is retried, in microseconds
    Table_Full_Retry_After_us = Microseconds_Per_Second

# ################################################################################################################################
# ################################################################################################################################

class _RegionRegistry:
    """ The counters of one kind in the rate limiting table of the shared region, which every worker reads and updates.
    """

    def __init__(self, region:'SharedRegion', slot:'int', table_full_metric:'int') -> 'None':

        # The worker adds to table_full_metric in its own row each time the table has no cell for a new key
        self.region = region
        self.slot = slot
        self.table_full_metric = table_full_metric

# ################################################################################################################################

    def _on_table_full(self, key:'str') -> 'None':
        logger.error('The rate limiting table of the shared region is at capacity, refusing a request for key `%s`', key)
        self.region.metric_add(self.slot, self.table_full_metric, 1)

# ################################################################################################################################

    def remove(self, key:'str') -> 'None':
        """ Resets the counters of a key in every worker.
        """
        self.region.cell_reset(key)

# ################################################################################################################################

    def remove_by_prefix(self, prefix:'str') -> 'None':
        """ Resets in every worker the counters of the keys whose group is the prefix, which is how a rule's counters are cleared.
        """
        self.region.cell_reset_group(prefix)

# ################################################################################################################################

    def clear(self) -> 'None':
        """ Resets every counter of the table in every worker.
        """
        self.region.cell_reset_all()

# ################################################################################################################################
# ################################################################################################################################

class RegionTokenBucketRegistry(_RegionRegistry):
    """ The token buckets of every worker, each bucket in one cell of the shared region.
    """

    def check_in_group(self, key:'str', group:'str', config:'TokenBucketConfig', now_us:'int') -> 'CheckResult':
        """ Takes one token from the bucket of a key, whose group is the prefix that a clear of its rule's counters uses.
        """
        out = CheckResult()
        region_key = RateLimitKey(key, group)

        try:
            result = self.region.token_bucket_check(region_key, config.rate, config.burst_allowed, now_us)
        except SharedRegionFull:
            self._on_table_full(key)
            out.is_allowed       = False
            out.tokens_remaining = 0
            out.retry_after_us   = ModuleCtx.Table_Full_Retry_After_us
        else:
            out.is_allowed       = result.is_allowed
            out.tokens_remaining = result.remaining
            out.retry_after_us   = result.retry_after_us

        return out

# ################################################################################################################################
# ################################################################################################################################

class RegionFixedWindowRegistry(_RegionRegistry):
    """ The fixed window counters of every worker, each counter in one cell of the shared region.
    """

    def check_in_group(self, key:'str', group:'str', config:'FixedWindowConfig', now_us:'int') -> 'FixedWindowCheckResult':
        """ Counts one request in the window of a key, whose group is the prefix that a clear of its rule's counters uses.
        """
        out = FixedWindowCheckResult()
        region_key = RateLimitKey(key, group)

        # The window that starts at this clock reading replaces a stored window that has ended
        window_end_us = compute_window_end_us(config.unit(), now_us)

        try:
            result = self.region.fixed_window_check(region_key, config.limit, window_end_us, now_us)
        except SharedRegionFull:
            self._on_table_full(key)
            out.is_allowed     = False
            out.remaining      = 0
            out.retry_after_us = ModuleCtx.Table_Full_Retry_After_us
        else:
            out.is_allowed     = result.is_allowed
            out.remaining      = result.remaining
            out.retry_after_us = result.retry_after_us

        return out

# ################################################################################################################################
# ################################################################################################################################
