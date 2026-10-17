# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc

# gevent
from gevent.lock import RLock

# Zato
from zato.common.typing_ import cast_
from zato.server.openapi_console.diff import report_breaking_changes
from zato.server.openapi_console.rule_engine import merge_rule_engine_spec
from zato.server.openapi_console.caller import resolve_session
from zato.server.openapi_console.spec import build_full_spec, filter_spec, get_spec_inputs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylistnone, tuple_
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SpecCache:
    """ Keeps the full OpenAPI document in memory so that per-request work is filtering only.
    The document is rebuilt on hot-deployment, on channel configuration events and on configuration reloads,
    and each rebuild reports breaking changes against the previous document. Each read also compares
    the channels and services the document was built out of with the current ones, and rebuilds it
    when they differ, e.g. after a service or a security definition with channels of its own was deleted.
    """
    def __init__(self) -> 'None':
        self.lock = RLock()
        self.spec:'anydictnone' = None
        self.channel_map:'anydict' = {}
        self.inputs:'anylistnone' = None

# ################################################################################################################################

    def rebuild(self, server:'ParallelServer') -> 'None':
        """ Rebuilds the cached document, comparing it with the previous one to report breaking changes.
        """
        inputs = get_spec_inputs(server)
        spec, channel_map = build_full_spec(server)

        with self.lock:
            previous = self.spec
            self.spec = spec
            self.channel_map = channel_map
            self.inputs = inputs

        # The very first build has nothing to compare against
        if previous is not None:
            report_breaking_changes(previous, spec)

# ################################################################################################################################

    def get(self, server:'ParallelServer') -> 'tuple_[anydict, anydict]':
        """ Returns the cached document and its channel map, building them first if no build has run yet
        or if what the document is built out of has changed since.
        """
        with self.lock:
            inputs = get_spec_inputs(server)

            if inputs != self.inputs:
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
    caller = resolve_session(server, fields['session_token'])

    if caller is None:
        return None

    # .. the channel part of the document comes from the cache, since it is derived from
    # scanning deployed services, which is expensive ..
    spec, channel_map = spec_cache.get(server)

    # .. while the rule engine part is built fresh from its database on every request -
    # a spec fetch is a cold path, so the document is always exactly what the database holds ..
    spec, channel_map = merge_rule_engine_spec(server, spec, channel_map)

    # .. admin callers receive the complete document ..
    if caller.is_admin:
        return spec

    # .. and other callers only what their credentials can invoke.
    out = filter_spec(server, spec, channel_map, caller.security_ids)

    return out

# ################################################################################################################################

def rebuild_spec_cache(server:'ParallelServer') -> 'None':
    """ Rebuilds the cached document after a configuration or deployment change.
    A failure to rebuild never breaks the deployment or the configuration event that triggered it.
    """
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
