# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from traceback import format_exc

# Zato
from zato.server.service import AsIs, List
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################

class NotifyPubSubMessage(AdminService):
    def handle(self):
        # The request that we have on input needs to be sent to a pubsub_tool for each sub_key,
        # even if it is possibly the same pubsub_tool for more than one input sub_key.
        request = self.request.raw_request['request']

        for sub_key in request['sub_key_list']:
            pubsub_tool = self.pubsub.pubsub_tool_by_sub_key[sub_key]
            pubsub_tool.handle_new_messages(self.cid, request['has_gd'], [sub_key], request['non_gd_msg_list'])

# ################################################################################################################################
