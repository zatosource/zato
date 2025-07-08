# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web.forms.pubsub.subscription import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import PubSubSubscription

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'pubsub-subscription'
    template = 'zato/pubsub/subscription.html'
    service_name = 'zato.pubsub.subscription.get-list'
    output_class = PubSubSubscription
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'sub_key', 'is_active', 'created'
        output_optional = 'topic_name', 'sec_name',
        output_repeated = True

    def handle(self):
        create_form = CreateForm(req=self.req)
        edit_form = EditForm(prefix='edit', req=self.req)
        return {
            'create_form': create_form,
            'edit_form': edit_form,
        }

# ################################################################################################################################
# ################################################################################################################################

class Create(CreateEdit):
    method_allowed = 'POST'
    url_name = 'pubsub-subscription-create'
    service_name = 'zato.pubsub.subscription.create'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'cluster_id', 'topic_id', 'sec_base_id'
        input_optional = 'is_active',
        output_required = 'id', 'sub_key'

    def success_message(self, item):
        return 'Successfully created the pub/sub subscription'

# ################################################################################################################################
# ################################################################################################################################

class Edit(CreateEdit):
    method_allowed = 'POST'
    url_name = 'pubsub-subscription-edit'
    service_name = 'zato.pubsub.subscription.edit'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'id', 'cluster_id', 'topic_id', 'sec_base_id'
        input_optional = 'is_active',
        output_required = 'id', 'sub_key'

    def success_message(self, item):
        return 'Successfully updated the pub/sub subscription'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'pubsub-subscription-delete'
    error_message = 'Could not delete the pub/sub subscription'
    service_name = 'zato.pubsub.subscription.delete'

# ################################################################################################################################
# ################################################################################################################################
