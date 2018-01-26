# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################

class WebSphereMQ(WorkerImpl):
    """ WebSphere MQ-related functionality for worker objects.
    """

# ################################################################################################################################

    def on_broker_msg_DEFINITION_WMQ_CREATE(self, msg):
        self.server.invoke_wmq_connector(msg)

    # Everything is delegated to connectors
    on_broker_msg_DEFINITION_WMQ_EDIT = on_broker_msg_DEFINITION_WMQ_CREATE
    on_broker_msg_DEFINITION_WMQ_DELETE = on_broker_msg_DEFINITION_WMQ_CREATE

# ################################################################################################################################
