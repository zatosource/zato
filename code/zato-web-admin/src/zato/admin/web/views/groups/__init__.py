# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc

# Bunch
from bunch import Bunch

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms.pubsub.endpoint import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, slugify
from zato.common.json_internal import dumps
from zato.common.model.groups import GroupObject

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'groups'
    template = 'zato/groups/index.html'
    service_name = 'dev.groups.get-list'
    output_class = GroupObject
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'group_type'
        output_repeated = True

    def get_initial_input(self):
        return {'group_type': self.input.group_type} # type: ignore

    def handle_return_data(self, return_data):
        return_data['group_type_name_title'] = 'API Credentials'
        return return_data

    def handle(self):

        return {
            'create_form': CreateForm(self.req),
            'edit_form': EditForm(self.req, prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'group_type', 'name'
        output_required = 'id', 'name'

    def success_message(self, item):
        return 'Successfully {} group `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'groups-create'
    service_name = 'dev.groups.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'groups-edit'
    form_prefix = 'edit-'
    service_name = 'dev.groups.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'groups-delete'
    error_message = 'Could not delete groups'
    service_name = 'dev.groups.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def view(req, group_id, name_slug):

    try:
        response = req.zato.client.invoke('dev.groups.get-topic-sub-list', {
            'cluster_id': cluster_id,
            'endpoint_id': endpoint_id,
            'topic_filter_by': req.GET.get('topic_filter_by'),
        })
    except Exception:
        return HttpResponseServerError(format_exc())
    else:
        return HttpResponse(dumps(response.data.response.topic_sub_list), content_type='application/javascript')

# ################################################################################################################################
