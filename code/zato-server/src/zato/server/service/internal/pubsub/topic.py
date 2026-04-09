# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.pubsub.matcher import PatternMatcher
from zato.common.pubsub.util import validate_topic_name
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub topics available.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_pubsub_topic_get_list_request'
        response_elem = 'zato_pubsub_topic_get_list_response'
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active'
        output_optional = 'description', 'publisher_count', 'subscriber_count'

    def handle(self):
        items = self.server.config_store.get_list('pubsub_topic')
        self.response.payload[:] = items

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topic_create_request'
        response_elem = 'zato_pubsub_topic_create_response'
        input_required = 'name', 'is_active'
        input_optional = 'cluster_id', 'description'
        output_required = 'id', 'name'

    def handle(self):
        input = self.request.input

        validate_topic_name(input.name)

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'description': input.get('description') or '',
        }

        self.server.config_store.set('pubsub_topic', input.name, data)

        self.response.payload.id = input.name
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a pub/sub topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topic_edit_request'
        response_elem = 'zato_pubsub_topic_edit_response'
        input_required = 'name', 'is_active'
        input_optional = 'id', 'cluster_id', 'description'
        output_required = 'id', 'name'

    def handle(self):
        input = self.request.input

        validate_topic_name(input.name)

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'description': input.get('description') or '',
        }

        self.server.config_store.set('pubsub_topic', input.name, data)

        self.response.payload.id = input.get('id') or input.name
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub topic.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topic_delete_request'
        response_elem = 'zato_pubsub_topic_delete_response'
        input_required = 'id',

    def handle(self):
        input_id = self.request.input.id

        for item in self.server.config_store.get_list('pubsub_topic'):
            if item.get('id') == input_id or item.get('name') == input_id:
                self.server.config_store.delete('pubsub_topic', item['name'])
                return

        raise Exception('Pub/sub topic with id `{}` not found'.format(input_id))

# ################################################################################################################################
# ################################################################################################################################

class GetMatches(AdminService):
    """ Returns a list of pub/sub topics matching a given pattern.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_pubsub_topic_get_matches_request'
        response_elem = 'zato_pubsub_topic_get_matches_response'
        input_required = 'cluster_id', 'pattern'
        output_optional = 'id', 'name', 'description'

    def handle(self):

        input_pattern = self.request.input.pattern

        if input_pattern.startswith('pub=') or input_pattern.startswith('sub='):
            topic_pattern = input_pattern.split('=', 1)[1]
        else:
            topic_pattern = input_pattern

        topics = self.server.config_store.get_list('pubsub_topic')

        matcher = PatternMatcher()
        client_id = 'temp_client'
        permissions = [{
            'pattern': topic_pattern,
            'access_type': 'subscriber'
        }]
        matcher.add_client(client_id, permissions)

        matching_topics = []
        for topic in topics:
            if not topic.get('is_active'):
                continue
            result = matcher.evaluate(client_id, topic['name'], 'subscribe')
            if result.is_ok:
                matching_topics.append({
                    'id': topic.get('id', ''),
                    'name': topic['name'],
                    'description': topic.get('description', '')
                })

        self.response.payload = matching_topics

# ################################################################################################################################
# ################################################################################################################################
