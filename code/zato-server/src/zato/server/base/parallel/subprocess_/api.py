# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class StartConfig:
    __slots__ = 'has_ibm_mq', 'has_sftp', 'has_stats'

    def __init__(self, has_ibm_mq=False, has_sftp=False, has_stats=False):
        self.has_ibm_mq = has_ibm_mq
        self.has_sftp   = has_sftp
        self.has_stats  = has_stats

# ################################################################################################################################
# ################################################################################################################################

class CurrentState:
    """ Represents current runtime state of subprocess-based connectors.
    """
    __slots__ = 'is_ibm_mq_running', 'is_sftp_running', 'is_stats_running'

    def __init__(self):
        self.is_ibm_mq_running = False
        self.is_sftp_running   = False
        self.is_stats_running  = False

# ################################################################################################################################
# ################################################################################################################################
