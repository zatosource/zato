# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import unittest
from time import monotonic, sleep

# Zato
from zato.common.test.client import AdminClient
from zato.common.test.config_multi_cpu_pubsub import PubSubConfig
from zato.common.test.conftest_base_multi_cpu import MultiCPUTestConfig, new_connection, post_json

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.multi_cpu_pubsub.payload_edit')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Publish_Path = '/test/multi-cpu/publish'
    Update_Service = 'zato.pubsub.subscription.update-message'

    Version_Original = 'original'
    Version_Edited   = 'edited'

    # How long the test waits for every subscriber to reject the original payload, and for the edited delivery, in seconds
    Reject_Deadline  = 60.0
    Delivery_Timeout = 120.0

    Poll_Interval = 0.25

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadEditAcrossWorkers(unittest.TestCase):
    """ A payload edited through one worker is the payload that every worker delivers afterwards, including the workers
    that read the original payload into their caches.
    """

    def test_edited_payload_is_delivered_by_every_owner(self) -> 'None':

        admin = AdminClient(MultiCPUTestConfig.base_url, MultiCPUTestConfig.invoke_password)

        # .. every subscriber rejects its deliveries, so the workers that own the keys read the original payload ..
        for receiver in PubSubConfig.receivers:
            receiver.behavior.set_reject_503()

        try:
            connection = new_connection()
            published = post_json(connection, ModuleCtx.Publish_Path, {
                'topic_name': PubSubConfig.Push_Topic,
                'data': {'seq': 0, 'version': ModuleCtx.Version_Original},
            })
            connection.close()

            # .. wait until each owner attempted the original payload at least once ..
            deadline = monotonic() + ModuleCtx.Reject_Deadline

            for index, receiver in enumerate(PubSubConfig.receivers):
                while receiver.behavior.reject_count == 0:
                    if monotonic() > deadline:
                        self.fail(f'Subscriber {index} received no attempt within {ModuleCtx.Reject_Deadline}s')
                    sleep(ModuleCtx.Poll_Interval)

            # .. edit the payload through whichever worker serves the admin request ..
            edited = {'seq': 0, 'version': ModuleCtx.Version_Edited}

            _ = admin.invoke(ModuleCtx.Update_Service, {
                'msg_id': published['msg_id'],
                'topic_name': PubSubConfig.Push_Topic,
                'data': json.dumps(edited),
            })
            logger.info('Edited %s, published through slot %s', published['msg_id'], published['slot'])

        finally:
            for receiver in PubSubConfig.receivers:
                receiver.behavior.set_accept()

        # .. and every subscriber receives the edited payload.
        for index, receiver in enumerate(PubSubConfig.receivers):
            messages = receiver.wait_for_delivery(1, ModuleCtx.Delivery_Timeout)
            data:'any_' = messages[0]['data']

            if isinstance(data, str):
                data = json.loads(data)

            self.assertEqual(data['version'], ModuleCtx.Version_Edited, f'Subscriber {index}')

# ################################################################################################################################
# ################################################################################################################################
