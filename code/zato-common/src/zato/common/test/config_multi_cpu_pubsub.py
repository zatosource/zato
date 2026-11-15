# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.receiver import WebhookReceiver
    from zato.common.typing_ import list_

    receiverlist = list_[WebhookReceiver]

# ################################################################################################################################
# ################################################################################################################################

class PubSubConfig:
    """ The subscribers of the suite and the receivers of their push deliveries.
    """

    # How many push subscribers the topic has, which gives every slot of up to eight workers keys of its own
    Subscriber_Count = 32

    Push_Topic = 'multi.cpu.push'
    Pull_Topic = 'multi.cpu.pull'
    Wake_Topic = 'multi.cpu.wake'
    Join_Topic = 'multi.cpu.join'

    Publisher_Name = 'test.multi-cpu.publisher'
    Puller_Name    = 'test.multi-cpu.puller'
    Waiter_Name    = 'test.multi-cpu.waiter'

    # The definition that may subscribe to the join topic and has no subscription until a test creates one
    Joiner_Name    = 'test.multi-cpu.joiner'

    receivers:'receiverlist' = []

# ################################################################################################################################
# ################################################################################################################################
