# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps
from operator import attrgetter
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.groups import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, get_group_list as common_get_group_list,  \
    get_security_name_link, Index as _Index, method_allowed
from zato.common.api import Groups, SEC_DEF_TYPE_NAME
from zato.common.model.groups import GroupObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strdict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'groups'
    template = 'zato/groups/index.html'
    service_name = 'zato.groups.get-list'
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
        return_data['group_type'] = Groups.Type.API_Clients
        return_data['group_type_name_title'] = 'API Clients'
        return return_data

    def handle(self):

        # Get information about how many members are in each group ..
        response = self.req.zato.client.invoke('zato.groups.get-member-count', {
            'group_type': Groups.Type.API_Clients,
        })

        member_count = response.data

        return {
            'member_count': member_count,
            'create_form': CreateForm(self.req.POST),
            'edit_form': EditForm(self.req.POST, prefix='edit'),
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
    service_name = 'zato.groups.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'groups-edit'
    form_prefix = 'edit-'
    service_name = 'zato.groups.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'groups-delete'
    error_message = 'Could not delete groups'
    service_name = 'zato.groups.delete'

# ################################################################################################################################
# ################################################################################################################################

def _extract_items_from_response(req:'any_', response:'any_') -> 'anylist':

    # Type hints
    item:'any_'

    # Our response to produce
    out:'anylist' = []

    # .. preprocess all the items received ..
    for item in response.data:
        name = item['name']
        if name in {'pubsub', 'ide_publisher', 'pubapi'}:
            continue
        elif 'zato.' in name:
            continue
        else:
            sec_type = item['sec_type']
            sec_name = item['name']
            security_name = get_security_name_link(req, sec_type, sec_name, needs_type=False)
            sec_type_name = SEC_DEF_TYPE_NAME[sec_type] # type: ignore
            item['sec_type_name'] = sec_type_name
            item['security_name'] = security_name
            out.append(item)

    # .. sort it in a human-readable way ..
    out.sort(key=attrgetter('sec_type', 'name'))

    # .. and return it to our caller.
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_security_list(req:'any_', sec_type:'strnone | strlist'=None, query:'strnone'=None) -> 'anylist':

    # Handle optional parameters
    sec_type = sec_type or ['apikey', 'basic_auth']

    # Obtain an initial list of members for this group ..
    response = req.zato.client.invoke('zato.security.get-list', {
        'sec_type': sec_type,
        'query': query,
        'paginate': False,
    })

    # .. extract the business data ..
    out = _extract_items_from_response(req, response)

    # .. and return it to our caller.
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_member_list(req:'any_', group_type:'str', group_id:'int') -> 'anylist':

    # Obtain an initial list of members for this group ..
    response = req.zato.client.invoke('zato.groups.get-member-list', {
        'group_type': group_type,
        'group_id': group_id,
        'should_serialize': True,
    })

    # .. extract the business data ..
    out = _extract_items_from_response(req, response)

    # .. and return it to our caller.
    return out

# ################################################################################################################################
# ################################################################################################################################

def _filter_out_members_from_security_list(security_list:'anylist', member_list:'anylist') -> 'anylist':

    out:'anylist' = []

    for sec_item in security_list:
        for member in member_list:
            if sec_item.id == member.security_id:
                break
        else:
            out.append(sec_item)

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_security_list(req:'any_') -> 'HttpResponse':

    sec_type = req.GET.get('sec_type')
    query = req.GET.get('query')

    group_type = req.GET.get('group_type')
    group_id = req.GET.get('group_id')

    member_list = _get_member_list(req, group_type, group_id)
    security_list = _get_security_list(req, sec_type, query)
    security_list = _filter_out_members_from_security_list(security_list, member_list)

    data = dumps(security_list)
    return HttpResponse(data, content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_member_list(req:'any_') -> 'HttpResponse':

    group_type = req.GET.get('group_type')
    group_id = req.GET.get('group_id')

    member_list = _get_member_list(req, group_type, group_id)
    data = dumps(member_list)

    return HttpResponse(data, content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def manage_group_members(req:'any_', group_type:'str', group_id:'str | int') -> 'HttpResponse':

    # Local variables
    group_id = int(group_id)
    template_name = 'zato/groups/members.html'

    # Get a list of all groups that exist
    group_list = common_get_group_list(req, group_type)

    # Obtain an initial list of members for this group
    member_list = _get_member_list(req, group_type, group_id)

    # Obtain an initial list of security definitions
    security_list = _get_security_list(req)

    # Filter out security definitions with members that already exist in the current group
    security_list = _filter_out_members_from_security_list(security_list, member_list)

    # Build the return data for the template ..
    return_data = {
        'cluster_id': req.zato.cluster_id,
        'group_type': group_type,
        'group_id': group_id,
        'group_list': group_list,
        'member_list': member_list,
        'security_list': security_list,
    }

    # .. and return everything to our caller.
    return TemplateResponse(req, template_name, return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def members_action(req:'any_', action:'str', group_id:'str', member_id_list:'str') -> 'HttpResponse':

    # Local variables
    group_id = group_id.replace('group-', '')
    member_id_list = member_id_list.split(',') # type: ignore
    member_id_list = [elem.strip() for elem in member_id_list] # type: ignore

    # Invoke the remote service ..
    try:
        _ = req.zato.client.invoke('zato.groups.edit-member-list', {
            'group_action': action,
            'group_id': group_id,
            'member_id_list': member_id_list
        })
    except Exception:
        response = format_exc()
        response_class = HttpResponseBadRequest
    else:
        response = ''
        response_class = HttpResponse
    finally:
        return response_class(response, content_type='text/plain') # type: ignore

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_group_list(req:'any_', group_type:'str') -> 'HttpResponse':

    http_soap_channel_id = req.GET.get('http_soap_channel_id')
    group_list = common_get_group_list(req, group_type, http_soap_channel_id=http_soap_channel_id)
    data = dumps(group_list)
    return HttpResponse(data, content_type='application/javascript')

# ################################################################################################################################
# ################################################################################################################################
