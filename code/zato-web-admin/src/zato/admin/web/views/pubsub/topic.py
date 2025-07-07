# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web.forms.pubsub.topic import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import PubSubTopic

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-topic'
    template = 'zato/pubsub/topic.html'
    service_name = 'zato.pubsub.topic.get-list'
    output_class = PubSubTopic
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active'
        output_optional = 'description', 'publisher_count', 'subscriber_count',
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):

    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_active'
        input_optional = 'description',
        output_required = 'id', 'name'

    def success_message(self, item):
        return 'Successfully {} Pub/Sub topic `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'pubsub-topic-create'
    service_name = 'zato.pubsub.topic.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'pubsub-topic-edit'
    form_prefix = 'edit-'
    service_name = 'zato.pubsub.topic.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-topic-delete'
    error_message = 'Could not delete the Pub/Sub topic'
    service_name = 'zato.pubsub.topic.delete'

# ################################################################################################################################
# ################################################################################################################################

class GetMatches(_Index):
    method_allowed = 'POST'
    url_name = 'pubsub-topic-get-matches'
    service_name = 'zato.pubsub.topic.get-matches'

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'pattern'
        output_required = 'matches',
        output_repeated = True

    def handle(self):
        return self.req_resp_func(self.request, self.service_name, self.SimpleIO, method='POST')

# ################################################################################################################################
# ################################################################################################################################
