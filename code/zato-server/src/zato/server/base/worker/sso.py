# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Zato
from zato.common import RATE_LIMIT
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

class SSO(WorkerImpl):
    """ Callbacks for messages related to SSO.
    """

# ################################################################################################################################

    def on_broker_msg_SSO_USER_CREATE(self, msg):
        self.server.rate_limiting.create({
            'id': msg.user_id,
            'type_': RATE_LIMIT.OBJECT_TYPE.SSO_USER,
            'name': msg.username,
            'is_active': msg.is_rate_limit_active,
            'parent_type': None,
            'parent_name': None,
        }, msg.rate_limit_def, True)

# ################################################################################################################################

    def on_broker_msg_SSO_USER_EDIT(self, msg):
        logger.warn('WWW %s', msg)

# ################################################################################################################################

    def on_broker_msg_SSO_LINK_AUTH_CREATE(self, msg):
        self.server.sso_api.user.on_broker_msg_SSO_LINK_AUTH_CREATE('zato.{}'.format(msg.auth_type), msg.auth_id, msg.user_id)

# ################################################################################################################################

    def on_broker_msg_SSO_LINK_AUTH_DELETE(self, msg):
        self.server.sso_api.user.on_broker_msg_SSO_LINK_AUTH_DELETE('zato.{}'.format(msg.auth_type), msg.auth_id, msg.user_id)

# ################################################################################################################################
