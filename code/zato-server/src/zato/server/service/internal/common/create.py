# -*- coding: utf-8 -*-

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.api import PUBSUB
from zato.common.exception import BadRequest
from zato.common.odb.model import PubSubTopic
from zato.common.typing_ import dictlist, strlist
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

_ps_default = PUBSUB.DEFAULT

# ################################################################################################################################
# ################################################################################################################################

TopicTable = PubSubTopic.__table__
TopicInsert = TopicTable.insert

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CreateTopicRequest(Model):
    name_list: strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CreateTopicResponse(Model):
    topics_created: dictlist

# ################################################################################################################################
# ################################################################################################################################

class CreateTopics(Service):
    name = 'topics1.create-topics'

    class SimpleIO:
        input = CreateTopicRequest
        output = CreateTopicResponse

    def handle(self):

        # Local variables
        input:'CreateTopicRequest' = self.request.input

        # Log what we are about to do
        self.logger.info('Creating topics -> len=%s', len(input.name_list))

        # .. go through each name we are given on input ..
        for name in input.name_list:

            # .. fill out all the details ..
            request = {
                'name': name,
                'has_gd': True,
                'is_active': True,
                'is_api_sub_allowed': True,
                'cluster_id': 1,
                'task_sync_interval': _ps_default.TASK_SYNC_INTERVAL,
                'task_delivery_interval': _ps_default.TASK_DELIVERY_INTERVAL,
                'depth_check_freq': _ps_default.DEPTH_CHECK_FREQ,
                'max_depth_gd': _ps_default.TOPIC_MAX_DEPTH_GD,
                'max_depth_non_gd': _ps_default.TOPIC_MAX_DEPTH_NON_GD,
                'pub_buffer_size_gd': _ps_default.PUB_BUFFER_SIZE_GD,
            }

            # .. create a topic now ..
            try:
                _ = self.invoke('zato.pubsub.topic.create', request)
            except BadRequest as e:
                # .. ignore topics that already exist ..
                self.logger.info('Ignoring -> %s', e)

        # .. finally, store information in logs that we are done.
        self.logger.info('Topic created')

# ################################################################################################################################
# ################################################################################################################################
