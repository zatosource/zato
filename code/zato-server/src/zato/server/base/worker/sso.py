# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import RATE_LIMIT
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.worker import WorkerStore

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Rate_Limit_Type = RATE_LIMIT.OBJECT_TYPE.SSO_USER

# ################################################################################################################################
# ################################################################################################################################

class SSO(WorkerImpl):
    """ Callbacks for messages related to SSO.
    """
    def on_broker_msg_SSO_USER_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.server._create_sso_user_rate_limiting(msg.user_id, msg.is_rate_limit_active, msg.rate_limit_def)

# ################################################################################################################################

    def on_broker_msg_SSO_USER_EDIT(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if self.server.rate_limiting.has_config(ModuleCtx.Rate_Limit_Type, msg.user_id):
            self.server.rate_limiting.edit(ModuleCtx.Rate_Limit_Type, msg.user_id, {
                'id': msg.user_id,
                'type_': ModuleCtx.Rate_Limit_Type,
                'name': msg.user_id,
                'is_active': msg.is_rate_limit_active,
                'parent_type': None,
                'parent_name': None,
            }, msg.rate_limit_def, True)

# ################################################################################################################################

    def on_broker_msg_SSO_LINK_AUTH_CREATE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.server.sso_api.user.on_broker_msg_SSO_LINK_AUTH_CREATE('zato.{}'.format(msg.auth_type), msg.auth_id, msg.user_id)

# ################################################################################################################################

    def on_broker_msg_SSO_LINK_AUTH_DELETE(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        self.server.sso_api.user.on_broker_msg_SSO_LINK_AUTH_DELETE(msg.auth_type, msg.auth_id)

# ################################################################################################################################
