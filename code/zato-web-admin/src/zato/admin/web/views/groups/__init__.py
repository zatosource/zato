# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.pubsub.endpoint import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import Groups
from zato.common.model.groups import GroupObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strdict, strnone

# ################################################################################################################################
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
        input_required = ('group_type',)
        output_required = ('type', 'id', 'name')
        output_repeated = True

    def get_initial_input(self) -> 'strdict':
        return {
            'cluster_id': self.cluster_id,
            'group_type': self.input.group_type
        }

    def handle_return_data(self, return_data:'strdict') -> 'strdict':
        return_data['group_type'] = Groups.Type.API_Credentials
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
        input_optional = 'id',
        output_required = 'id', 'name'

    def success_message(self, item:'any_') -> 'str':
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

def get_member_list(req:'any_', group_type:'str', group_id:'int') -> 'anylist':

    # Obtain an initial list of members for this group ..
    response = req.zato.client.invoke('dev.groups.get-member-list', {
        'group_type': group_type,
        'group_id': group_id,
    })

    # .. extract the business data ..
    out = response.data

    # .. and return it to our caller.
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_security_list(req:'any_', sec_type:'strnone'=None) -> 'anylist':

    # Obtain an initial list of members for this group ..
    response = req.zato.client.invoke('zato.security.get-list', {
        'sec_type': sec_type,
    })

    # .. extract the business data ..
    out = response.data

    print()
    print(111, out)
    print()

    # .. and return it to our caller.
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def view(req:'any_', group_type:'str', group_id:'int') -> 'HttpResponse':

    '''
    try:
    except Exception:
        return HttpResponseServerError(format_exc())
    else:
        return HttpResponse(dumps(response.data), content_type='application/javascript')
    '''

    # Local variables
    template_name = 'zato/groups/members.html'

    # Obtain an initial list of members for this group
    member_list = get_member_list(req, group_type, group_id)

    # Obtain an initial list of security definitions
    security_list = get_security_list(req)

    # .. build the return data for the template ..
    return_data = {
        'cluster_id': req.zato.cluster_id,
        'member_list': member_list,
        'security_list': security_list,
    }

    # .. and return everything to our caller.
    return TemplateResponse(req, template_name, return_data)

# ################################################################################################################################
