# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger

# Zato
from zato.server.pattern.model import ParallelCtx

# ################################################################################################################################

if 0:
    from zato.server.service import Service

    Service = Service

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ParallelBase:
    """ A base class for most parallel integration patterns. An instance of this class is created for each service instance.
    """
    def __init__(self, source):
        # type: (Service) -> None
        self.source = source
        self.cid = source.cid

# ################################################################################################################################

    def _invoke(self, ctx):
        # type: (ParallelCtx)
        pass

# ################################################################################################################################

    def invoke(self, targets, on_final, on_target=None, cid=None, _utcnow=datetime.utcnow):
        """ Invokes targets collecting their responses, can be both as a whole or individual ones,
        and executes callback(s).
        """
        # type: (list, list, list, str) -> None

        # Establish what our CID is ..
        cid = cid or self.cid

        # .. create an execution context ..
        ctx = ParallelCtx()
        ctx.cid = cid
        ctx.req_ts_utc = _utcnow()
        ctx.source_name = self.source.name
        ctx.target_list = targets
        ctx.on_final_list = [on_final] if isinstance(on_final, str) else on_final
        ctx.on_target_list = [on_target] if isinstance(on_target, str) else on_target

        # .. invoke our implementation in background ..
        self._invoke(ctx)

        # .. and return the CID to the caller.
        return cid

# ################################################################################################################################
# ################################################################################################################################
