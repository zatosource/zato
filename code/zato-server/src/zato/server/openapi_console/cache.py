# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import contextmanager
from traceback import format_exc

# gevent
from gevent.lock import RLock

# Zato
from zato.common.typing_ import cast_
from zato.server.openapi_console.diff import report_breaking_changes
from zato.server.openapi_console.spec import build_full_spec, filter_spec, resolve_caller

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, tuple_
    from zato.server.base.parallel import ParallelServer
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SpecCache:
    """ Keeps the full OpenAPI document in memory so that per-request work is filtering only.
    The document is rebuilt once per change - on hot-deployment and on channel configuration events -
    and each rebuild reports breaking changes against the previous document.
    """
    def __init__(self) -> 'None':
        self.lock = RLock()
        self.spec:'anydictnone' = None
        self.channel_map:'anydict' = {}

        # When True, rebuild_spec_cache is a no-op - a batch of configuration events
        # sets it so the document is rebuilt once at the end of the batch, never once per event.
        self.is_rebuild_suppressed = False

# ################################################################################################################################

    def rebuild(self, server:'ParallelServer') -> 'None':
        """ Rebuilds the cached document, comparing it with the previous one to report breaking changes.
        """
        spec, channel_map = build_full_spec(server)

        with self.lock:
            previous = self.spec
            self.spec = spec
            self.channel_map = channel_map

        # The very first build has nothing to compare against
        if previous is not None:
            report_breaking_changes(previous, spec)

# ################################################################################################################################

    def get(self, server:'ParallelServer') -> 'tuple_[anydict, anydict]':
        """ Returns the cached document and its channel map, building them first if no build has run yet.
        """
        with self.lock:
            if self.spec is None:
                self.rebuild(server)

            # A rebuild always leaves a document behind, hence the cast
            spec = cast_('anydict', self.spec)

            return spec, self.channel_map

# ################################################################################################################################
# ################################################################################################################################

# One cache per server process
spec_cache = SpecCache()

# ################################################################################################################################
# ################################################################################################################################

def get_spec(server:'ParallelServer', fields:'anydict') -> 'anydictnone':
    """ Returns the OpenAPI document filtered down to what the caller can access, or None if the caller
    could not be identified at all. Admin callers receive the complete cached document.
    """
    # Reject the request outright if the caller cannot be identified ..
    security_id, is_admin = resolve_caller(server, fields)

    if not security_id:
        if not is_admin:
            return None

    # .. the per-request work is filtering only, the full document comes from the cache ..
    spec, channel_map = spec_cache.get(server)

    # .. admin callers receive the complete document ..
    if is_admin:
        return spec

    # .. and other callers only what their identity can invoke - a non-admin caller
    # got past the check above only with a security definition, hence the cast.
    security_id = cast_('int', security_id)
    out = filter_spec(server, spec, channel_map, security_id, fields['username'], fields['password'])

    return out

# ################################################################################################################################

@contextmanager
def suppressed_rebuilds() -> 'any_':
    """ Turns off per-event rebuilds for the duration of a batch of configuration events -
    the caller rebuilds the document once after the batch instead.
    """
    spec_cache.is_rebuild_suppressed = True
    try:
        yield
    finally:
        spec_cache.is_rebuild_suppressed = False

# ################################################################################################################################

def rebuild_spec_cache(server:'ParallelServer') -> 'None':
    """ Rebuilds the cached document after a configuration or deployment change.
    A failure to rebuild never breaks the deployment or the configuration event that triggered it.
    """
    # A batch of events is in progress - it rebuilds the document once at its end
    if spec_cache.is_rebuild_suppressed:
        return

    # During server startup channels are not loaded yet - the cache is built lazily
    # on the first console request instead. The attribute itself appears only once
    # the server has begun reading its configuration in.
    if not hasattr(server, 'config_manager'):
        return

    if not server.config_manager.is_ready:
        return

    try:
        spec_cache.rebuild(server)
    except Exception:
        logger.warning('OpenAPI document could not be rebuilt: %s', format_exc())

# ################################################################################################################################
# ################################################################################################################################
