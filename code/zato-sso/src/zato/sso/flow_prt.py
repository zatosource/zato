# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.odb.model import SSOFlowPRT as FlowPRTModel
from zato.sso import Default

# ################################################################################################################################

if 0:

    # stdlib
    from typing import Callable

# ################################################################################################################################
# ################################################################################################################################

FlowPRTModelTable = FlowPRTModel.__table__
FlowPRTModelInsert = FlowPRTModelTable.insert

# ################################################################################################################################
# ################################################################################################################################

class FlowPRTAPI(object):
    """ Message flow around password-reset tokens (PRT).
    """
    def __init__(self, sso_conf):
        # type: (dict) -> None
        self.sso_conf = sso_conf
        self.odb_session_func = None
        self.is_sqlite = None

        # PRT runtime configuration
        prt_config = sso_conf.get('prt', {})

        # For how long PRTs are valid (in seconds)
        valid_for = prt_config.get('valid_for')
        valid_for = valid_for or Default.prt_valid_for
        self.valid_for = int(valid_for)

        # For how long the one-off session to change the password will last (in minutes)
        duration = prt_config.get('password_change_session_duration')
        duration = duration or Default.prt_password_change_session_duration
        self.password_change_session_duration = int(duration)

# ################################################################################################################################

    def create_token(self):
        pass

# ################################################################################################################################

    def post_configure(self, func, is_sqlite):
        # type: (Callable, bool) -> None
        self.odb_session_func = func
        self.is_sqlite = is_sqlite

# ################################################################################################################################
# ################################################################################################################################
