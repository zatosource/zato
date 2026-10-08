# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a message from Azure Service Bus is settled - by the service through self.request.amqp,
# or by the channel's acknowledgment mode when the service leaves it alone.

# Zato
from zato.common.api import AMQP
from zato.server.connection.amqp_ import _AzureMessageWrapper

# Test support
from amqp_stub import new_channel_config, new_connector, AzureProducerRecorder, AzureReceiverRecorder, Channel_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The message as the Azure SDK hands it over and its body as text
_azure_message = object()
_body = '{"flight_no":"LH123", "status":"delayed"}'

# ################################################################################################################################
# ################################################################################################################################

class ServiceStub:
    """ Stands in for the service a channel invokes - what it does with the message is configurable.
    """

    def __init__(self, action:'str'='') -> 'None':
        self.action = action
        self.invoked = 0

    def __call__(self, service_name:'str', body:'any_', **kwargs:'any_') -> 'None':
        self.invoked += 1

        msg = kwargs['zato_ctx']['zato.channel_item']['amqp_msg']

        if self.action == 'ack':
            msg.ack()
        elif self.action == 'reject':
            msg.reject()
        elif self.action == 'raise':
            raise Exception('Flight display system unavailable')

# ################################################################################################################################
# ################################################################################################################################

def _deliver(service:'ServiceStub', ack_mode:'str'=AMQP.ACK_MODE.ACK.id) -> 'AzureReceiverRecorder':
    """ Delivers one message to the service through the connector and returns what the receiver recorded.
    """
    connector = new_connector(service, AzureProducerRecorder(), is_azure=True)
    channel_config = new_channel_config(ack_mode)

    out = AzureReceiverRecorder()
    msg = _AzureMessageWrapper(_azure_message, out)

    try:
        connector.on_amqp_message(_body, msg, Channel_Name, channel_config)
    except Exception:
        if service.action != 'raise':
            raise

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_message_the_service_leaves_alone_is_completed_under_ack_mode() -> 'None':
    service = ServiceStub()

    receiver = _deliver(service)

    assert service.invoked == 1
    assert receiver.completed == [_azure_message]
    assert receiver.abandoned == []

# ################################################################################################################################

def test_a_message_the_service_leaves_alone_is_abandoned_under_reject_mode() -> 'None':
    receiver = _deliver(ServiceStub(), AMQP.ACK_MODE.REJECT.id)

    assert receiver.completed == []
    assert receiver.abandoned == [_azure_message]

# ################################################################################################################################

def test_a_message_the_service_acknowledged_is_completed_once() -> 'None':
    receiver = _deliver(ServiceStub('ack'))

    assert receiver.completed == [_azure_message]
    assert receiver.abandoned == []

# ################################################################################################################################

def test_a_message_the_service_rejected_is_abandoned_once() -> 'None':
    receiver = _deliver(ServiceStub('reject'))

    assert receiver.completed == []
    assert receiver.abandoned == [_azure_message]

# ################################################################################################################################

def test_a_message_whose_service_raised_is_abandoned_for_redelivery() -> 'None':
    receiver = _deliver(ServiceStub('raise'))

    assert receiver.completed == []
    assert receiver.abandoned == [_azure_message]

# ################################################################################################################################

def test_the_wrapper_reports_its_state() -> 'None':
    receiver = AzureReceiverRecorder()

    msg = _AzureMessageWrapper(_azure_message, receiver)
    assert msg._state == 'RECEIVED'

    msg.ack()
    assert msg._state == 'ACK'

    msg = _AzureMessageWrapper(_azure_message, receiver)
    msg.reject()
    assert msg._state == 'REJECTED'

    msg = _AzureMessageWrapper(_azure_message, receiver)
    msg.requeue()
    assert msg._state == 'REQUEUED'

# ################################################################################################################################
# ################################################################################################################################
