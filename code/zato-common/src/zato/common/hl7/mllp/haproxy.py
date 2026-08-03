# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# Zato
from zato.common.defaults import http_plain_server_port

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

__all__ = ('resolve_internal_port',)

# ################################################################################################################################
# ################################################################################################################################

# Where the MLLP listener sits on loopback. The load balancer's mllp_backend points at this same
# port, which is why it is a fixed number rather than anything discovered at run time.
Internal_Port_Base = 31312

# If this environment variable is set, the internal MLLP server binds to exactly this port.
# The load balancer reads the same variable, so the two never disagree.
Env_Port_Name = 'Zato_HL7_MLLP_Port'

# ################################################################################################################################

def resolve_internal_port(server_port:'int'=http_plain_server_port) -> 'int':
    """ Returns the internal port the MLLP listener of a server on the given port binds to.
    """

    # An explicitly configured port always wins - this is what tests use to know the port upfront
    env_port = os.environ.get(Env_Port_Name)

    if env_port:
        out = int(env_port)
        logger.info('Using internal MLLP port %d from %s', out, Env_Port_Name)
        return out

    # Every server sits as far above the MLLP base as it does above the first server's own port,
    # so two servers never collide and neither has to probe for a free port.
    out = Internal_Port_Base + server_port - http_plain_server_port

    logger.info('Resolved internal MLLP port %d for server port %d', out, server_port)

    return out

# ################################################################################################################################
# ################################################################################################################################
