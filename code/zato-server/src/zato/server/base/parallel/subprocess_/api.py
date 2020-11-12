# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################
# ################################################################################################################################

class StartConfig:
    __slots__ = 'has_ibm_mq', 'has_sftp'

    def __init__(self):
        self.has_ibm_mq = False
        self.has_sftp   = False

# ################################################################################################################################
# ################################################################################################################################

class CurrentState:
    """ Represents current runtime state of subprocess-based connectors.
    """
    __slots__ = 'is_ibm_mq_running', 'is_sftp_running'

    def __init__(self):
        self.is_ibm_mq_running = False
        self.is_sftp_running   = False

# ################################################################################################################################
# ################################################################################################################################
