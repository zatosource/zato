# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.server.base.worker import WorkerStore

# ################################################################################################################################
# ################################################################################################################################

class WebSphereMQ(WorkerImpl):
    """ IBM MQ-related functionality for worker objects.
    """
    def _on_broker_msg_invoke_wmq_connector(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        if self.server.is_first_worker:
            self.server.connector_ibm_mq.invoke_wmq_connector(msg)

    # Everything is delegated to connectors ..
    on_broker_msg_DEFINITION_WMQ_CREATE = _on_broker_msg_invoke_wmq_connector
    on_broker_msg_DEFINITION_WMQ_EDIT = _on_broker_msg_invoke_wmq_connector
    on_broker_msg_DEFINITION_WMQ_DELETE = _on_broker_msg_invoke_wmq_connector
    on_broker_msg_DEFINITION_WMQ_CHANGE_PASSWORD = _on_broker_msg_invoke_wmq_connector

    # .. including outconns ..
    on_broker_msg_OUTGOING_WMQ_CREATE = _on_broker_msg_invoke_wmq_connector
    on_broker_msg_OUTGOING_WMQ_EDIT = _on_broker_msg_invoke_wmq_connector
    on_broker_msg_OUTGOING_WMQ_DELETE = _on_broker_msg_invoke_wmq_connector

    # .. and channels ..
    on_broker_msg_CHANNEL_WMQ_CREATE = _on_broker_msg_invoke_wmq_connector
    on_broker_msg_CHANNEL_WMQ_EDIT = _on_broker_msg_invoke_wmq_connector
    on_broker_msg_CHANNEL_WMQ_DELETE = _on_broker_msg_invoke_wmq_connector

# ################################################################################################################################
# ################################################################################################################################
