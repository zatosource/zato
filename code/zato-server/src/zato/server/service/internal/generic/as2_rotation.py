# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The scheduled completion of AS2 certificate rotations - a sweep over the live outgoing AS2 connections
# that promotes each due next certificate through the edit service of generic connections.

# stdlib
from datetime import datetime, timezone

# Zato
from zato.common.api import AS2
from zato.common.as2.rotation import complete_rotation, needs_rotation_completion
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

# The entries of a live connection's config dict that must not travel to the edit service -
# the live wrapper objects plus the values the config manager adds at runtime,
# with the secret left out so the edit keeps the one already stored.
_rotation_runtime_only_keys = ('conn', 'parent', 'secret', 'queue_build_cap', 'auth_url')

# ################################################################################################################################
# ################################################################################################################################

class CompleteAS2Rotation(AdminService):
    """ Completes the scheduled certificate rotation of every outgoing AS2 connection
    whose next-certificate activation date plus the grace window has passed -
    the next certificate becomes the current one and the next-certificate fields are cleared.
    """
    name = AS2.Default.Rotation_Service

    def handle(self) -> 'None':

        # One reference moment for the whole sweep
        now = datetime.now(timezone.utc)

        # Take a snapshot of the current connections because completing a rotation modifies the container ..
        conn_dicts = list(self.server.config_manager.outconn_as2.values())

        for conn_dict in conn_dicts:

            # .. skip the connections with no rotation to complete ..
            if not needs_rotation_completion(conn_dict, now):
                continue

            # .. copy the config without its runtime-only entries ..
            request = {}
            for key, value in conn_dict.items():
                if key in _rotation_runtime_only_keys:
                    continue
                request[key] = value

            # .. promote the next certificate to the current one ..
            complete_rotation(request)

            # .. and persist the change through the edit service, which keeps the ext-db id mapping,
            # .. secret re-encryption and the cluster-wide propagation correct.
            _ = self.invoke('zato.generic.connection.edit', request)

            self.logger.info('Completed AS2 certificate rotation for connection `%s`', request['name'])

# ################################################################################################################################
# ################################################################################################################################
