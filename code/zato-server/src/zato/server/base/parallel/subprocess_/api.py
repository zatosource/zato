# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################
# ################################################################################################################################

class StartConfig:
    __slots__ = 'has_ibm_mq', 'has_sftp'

    def __init__(self, has_ibm_mq=False, has_sftp=False):
        self.has_ibm_mq = has_ibm_mq
        self.has_sftp   = has_sftp

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
