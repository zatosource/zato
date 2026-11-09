# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class PubSubReplaced(Exception):
    """ Raised by every transaction of a server that is no longer the active one, either because another server
    raised the generation of the pub/sub database or because the node of this server is no longer active.
    """

# ################################################################################################################################
# ################################################################################################################################
