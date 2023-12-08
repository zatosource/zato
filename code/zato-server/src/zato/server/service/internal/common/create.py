# -*- coding: utf-8 -*-

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.api import CommonObject, PUBSUB
from zato.common.exception import BadRequest
from zato.common.odb.model import PubSubTopic
from zato.common.typing_ import anylist, intlistnone, intnone, strlistnone, strnone
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict

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
class CreateObjectsRequest(Model):
    object_type: str
    id: intnone
    id_list: intlistnone
    name: strnone
    name_list: strlistnone
    pattern: strnone

@dataclass(init=False)
class CreateObjectsResponse(Model):
    objects: anylist

# ################################################################################################################################
# ################################################################################################################################

class CreateObjects(Service):

    name = 'zato.common.create-objects'
    input = CreateObjectsRequest
    output = CreateObjectsResponse

# ################################################################################################################################

    def _get_basic_pubsub_topic(self) -> 'strdict':

        request = {
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

        return request

# ################################################################################################################################

    def _extract_response_items(self, response:'strdict') -> 'strdict':

        # Our response to produce
        out:'strdict' = {}

        return out

# ################################################################################################################################

    def handle(self):

        # Zato
        from zato.server.service.internal.pubsub.topic import Create as CreateTopic

        # Local variables
        input:'CreateObjectsRequest' = self.request.input

        # Our response to produce:
        out = CreateObjectsResponse()
        out.objects = []

        # Maps object types to services that create them

        # Maps incoming string names of objects to services that actually delete them
        service_map = {
            CommonObject.PubSub_Topic: CreateTopic,
        }

        # Maps incoming string names of objects to functions that prepare basic create requests
        request_func_map = {
            CommonObject.PubSub_Topic: self._get_basic_pubsub_topic,
        }

        # Get the service that will create the object
        service = service_map[input.object_type]

        # Make sure this is provided
        input.name_list = input.name_list or []

        # Log what we are about to do
        self.logger.info('Creating topics -> len=%s', len(input.name_list))

        # .. go through each name we are given on input ..
        for name in input.name_list:

            # .. get a request with basic details ..
            request_func = request_func_map[input.object_type]
            request = request_func()

            # .. add the name from input ..
            request['name'] = name

            # .. create an object now ..
            try:
                response = self.invoke(service.get_name(), request)
                response = self._extract_response_items(response)
                out.objects.append(response)
            except BadRequest as e:

                # .. ignore objects that already exist ..
                self.logger.info('Ignoring -> %s', e)

            else:
                # .. finally, store information in logs that we are done.
                self.logger.info('Object created -> %s -> %s', name, response)

        # Produce the response for our caller
        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################
