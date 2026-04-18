# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.pubsub.matcher import PatternMatcher
from zato.common.pubsub.util import validate_topic_name
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of pub/sub topics available.
    """
    input = 'cluster_id',
    output = 'id', 'name', 'is_active', '-description', '-publisher_count', '-subscriber_count'

    def handle(self):
        items = self.server.config_manager.get_list('pubsub_topic')
        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new pub/sub topic.
    """
    input = 'name', 'is_active', '-cluster_id', '-description'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input

        validate_topic_name(input.name)

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'description': input.get('description') or '',
        }

        self.server.config_manager.set('pubsub_topic', input.name, data)

        self.response.payload.id = input.name
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates a pub/sub topic.
    """
    input = 'name', 'is_active', '-id', '-cluster_id', '-description', '-old_name'
    output = 'id', 'name'

    def handle(self):
        input = self.request.input

        validate_topic_name(input.name)

        topic_id = input.get('id')
        existing = None

        if topic_id:
            for item in self.server.config_manager.get_list('pubsub_topic'):
                if item['id'] == topic_id:
                    existing = item
                    break

        if not existing:
            raise Exception('Pub/sub topic not found (id:`{}`, name:`{}`)'.format(topic_id, input.name))

        old_name = existing['name']

        existing['name'] = input.name
        existing['is_active'] = input.is_active
        existing['description'] = input.get('description') or ''

        if old_name != input.name:
            self.server.config_manager.delete('pubsub_topic', old_name)

        self.server.config_manager.set('pubsub_topic', input.name, existing)

        item = self.server.config_manager.get('pubsub_topic', input.name)
        self.response.payload.id = item['id']
        self.response.payload.name = item['name']

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a pub/sub topic.
    """
    input = 'id',

    def handle(self):
        input_id = self.request.input.id

        for item in self.server.config_manager.get_list('pubsub_topic'):
            if item.get('id') == input_id or item.get('name') == input_id:
                self.server.config_manager.delete('pubsub_topic', item['name'])
                return

        raise Exception('Pub/sub topic with id `{}` not found'.format(input_id))

# ################################################################################################################################
# ################################################################################################################################

class GetMatches(AdminService):
    """ Returns a list of pub/sub topics matching a given pattern.
    """
    input = 'cluster_id', 'pattern'
    output = '-id', '-name', '-description'

    def handle(self):

        input_pattern = self.request.input.pattern

        if input_pattern.startswith('pub=') or input_pattern.startswith('sub='):
            topic_pattern = input_pattern.split('=', 1)[1]
        else:
            topic_pattern = input_pattern

        topics = self.server.config_manager.get_list('pubsub_topic')

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
