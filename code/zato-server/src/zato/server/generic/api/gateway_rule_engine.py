# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class GatewayRuleEngineWrapper:
    """ Holds configuration for one Rule engine API object - the base URL path and the ruleset grants.
    All the heavy lifting happens in the invoke service, this wrapper only keeps the config current,
    so grant and path edits apply the moment the connection is edited, without a restart.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server

# ################################################################################################################################

    def build_wrapper(self) -> 'None':
        """ Nothing to build - the config dict this wrapper holds is the whole runtime state.
        """
        rulesets = self.config.get('rulesets') or []
        suffix = 'grant' if len(rulesets) == 1 else 'grants'
        logger.info('Rule engine API `%s` built with %d ruleset %s: %s', self.config.name, len(rulesets), suffix, rulesets)

# ################################################################################################################################

    def delete(self) -> 'None':
        """ Cleans up when the object is being removed.
        """
        logger.info('Rule engine API `%s` deleted', self.config.name)

# ################################################################################################################################
# ################################################################################################################################
