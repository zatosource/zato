# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.forms.gateway.rule_engine import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import GENERIC, Groups, Sec_Def_Type_Name
from zato.common.rule_engine.invocation import unmatched_ruleset_patterns

# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, anytuple, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The hidden inputs the security badge picker injects into the form.
_security_input_prefix = 'rule_engine_security_'

# The auto-created security group of each object is named after it.
_group_name_prefix = 'rule-engine-api.'

# The request attribute the published ruleset catalog is cached under,
# so one index page fetches it once no matter how many objects it lists.
_published_cache_attr = '_zato_rule_engine_published_rulesets'

# ################################################################################################################################
# ################################################################################################################################

def _get_published_rulesets(req:'any_') -> 'strlist':
    """ Returns the names of every published ruleset, cached per request.
    """
    if hasattr(req, _published_cache_attr):
        return getattr(req, _published_cache_attr)

    response = req.zato.client.invoke('zato.rule-engine.api.get-ruleset-list', {})

    # A server without a reachable rule engine database answers with an error -
    # the screen still works, it just cannot flag any grants.
    if response.ok:
        out = response.data['rulesets']
    else:
        out = []

    setattr(req, _published_cache_attr, out)
    return out

# ################################################################################################################################

def build_ruleset_grants(req:'any_', grants:'strlist') -> 'anylist':
    """ Joins each grant entry with whether it matches at least one published ruleset -
    a grant that matches nothing is either a typo or a ruleset that is not published yet.
    """
    # The checker needs the catalog in Python's own string order.
    published = sorted(_get_published_rulesets(req))
    unmatched = set(unmatched_ruleset_patterns(grants, published))

    out = []
    for grant in grants:
        is_matched = grant not in unmatched
        out.append({'name': grant, 'is_matched': is_matched})

    return out

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'rule-engine-api'
    template = 'zato/rule-engine/api.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active'
    output_optional = 'url_path', 'rulesets', 'security_groups'
    output_repeated = True

    def get_initial_input(self) -> 'strdict':

        # The type is constant for this page so it is not expected in the URL,
        # it is always added to the service request here instead.
        return {'type_': GENERIC.CONNECTION.TYPE.GATEWAY_RULE_ENGINE}

    def on_before_append_item(self, item:'any_') -> 'any_':

        # Resolve the security member count from the auto-created group ..
        security_groups = getattr(item, 'security_groups', None) or []
        if security_groups:
            group_id = security_groups[0]
            member_response = self.req.zato.client.invoke('zato.groups.get-member-list', {
                'group_type': Groups.Type.API_Clients,
                'group_id': group_id,
            })
            item.security_member_count = len(member_response.data) if member_response.ok and member_response.data else 0
        else:
            item.security_member_count = 0

        # .. an object created before any grants were given carries none ..
        grants = getattr(item, 'rulesets', None) or []
        item.rulesets = grants

        # .. and each grant knows whether anything published matches it.
        item.ruleset_grants = build_ruleset_grants(self.req, grants)

        return item

    def handle(self) -> 'strdict':
        out = {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name',
    input_optional = 'is_active', 'url_path', 'rulesets'
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict:'strdict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.GATEWAY_RULE_ENGINE
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

    def pre_process_input_dict(self, input_dict:'strdict') -> 'None':

        # The grants arrive as one comma-separated string and are stored as a list ..
        grants = []
        if value := input_dict['rulesets']:
            for grant in value.split(','):
                grant = grant.strip()
                if grant:
                    grants.append(grant)
        input_dict['rulesets'] = grants

        # .. collect security definitions from the security badge picker ..
        member_id_list = []
        for key in self.req.POST:
            if key.startswith(_security_input_prefix):
                member_id_list.append(self.req.POST[key])

        # .. the group name is derived from the object name ..
        object_name = input_dict['name']
        group_name = _group_name_prefix + object_name

        # .. auto-create or update the security group with the picked members ..
        existing_groups = self.req.zato.client.invoke('zato.groups.get-list', {
            'group_type': Groups.Type.API_Clients,
        })

        group_id = None
        for group in existing_groups.data:
            if group['name'] == group_name:
                group_id = group['id']
                break

        if group_id:
            # .. update the existing group with the new member list ..
            self.req.zato.client.invoke('zato.groups.edit', {
                'id': group_id,
                'group_type': Groups.Type.API_Clients,
                'name': group_name,
                'member_id_list': member_id_list,
            })
        else:
            # .. or create a new group if one does not exist yet ..
            response = self.req.zato.client.invoke('zato.groups.create', {
                'group_type': Groups.Type.API_Clients,
                'name': group_name,
                'member_id_list': member_id_list,
            })
            group_id = response.data['id']

        # .. store the group ID so the hook can assign it to the REST channel.
        input_dict['security_groups'] = [group_id]

    def post_process_return_data(self, return_data:'strdict') -> 'strdict':

        # Count the security definitions that were submitted ..
        security_count = 0
        for key in self.req.POST:
            if key.startswith(_security_input_prefix):
                security_count += 1
        return_data['security_count'] = security_count

        # .. and flag the submitted grants for the JS data table row,
        # the same way the index page flags them - the field's name carries
        # the edit form's prefix when it is the edit form that was submitted.
        value = self.req.POST[self.form_prefix + 'rulesets']

        grants = []
        for grant in value.split(','):
            grant = grant.strip()
            if grant:
                grants.append(grant)

        return_data['ruleset_grants'] = build_ruleset_grants(self.req, grants)
        return_data['rulesets'] = ', '.join(grants)

        out = return_data
        return out

    def success_message(self, item:'any_') -> 'str':
        return 'Successfully {} Rule engine API object `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'rule-engine-api-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'rule-engine-api-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'rule-engine-api-delete'
    error_message = 'Could not delete the Rule engine API object'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_security_list(req:'any_') -> 'HttpResponse':
    """ Returns the list of available security definitions (API key, Basic Auth)
    for the security badge picker, with is_member flags set from the object's
    auto-created security group.
    """

    # The object ID is provided when editing an existing object ..
    object_id = req.GET.get('object_id')

    # .. get all available security definitions of the supported types ..
    response = req.zato.client.invoke('zato.security.get-list', {
        'sec_type': ['apikey', 'basic_auth'],
        'paginate': False,
    })

    # .. extract the items, skipping built-in and internal entries ..
    items = []
    for item in response.data:
        name = item['name']
        if name in {'ide_publisher', 'pubapi'} or 'zato.' in name:
            continue

        sec_type = item['sec_type']
        sec_type_name = Sec_Def_Type_Name[sec_type]
        items.append({
            'id': item['id'],
            'name': name,
            'sec_type': sec_type,
            'sec_type_name': sec_type_name,
            'is_member': False,
        })

    # .. sort by type then name ..
    def _by_type_and_name(elem:'strdict') -> 'anytuple':
        out = (elem['sec_type'], elem['name'])
        return out

    items.sort(key=_by_type_and_name)

    # .. if editing, figure out which definitions are already assigned ..
    if object_id:

        # .. look up the object's security_groups field ..
        object_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': req.zato.cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.GATEWAY_RULE_ENGINE,
            'paginate': False,
        })

        if object_response.ok and object_response.data:
            for object_item in object_response.data:
                if str(object_item['id']) != str(object_id):
                    continue

                security_groups = object_item.get('security_groups', [])
                if security_groups:
                    group_id = security_groups[0]
                    member_response = req.zato.client.invoke('zato.groups.get-member-list', {
                        'group_type': Groups.Type.API_Clients,
                        'group_id': group_id,
                    })

                    if member_response.ok and member_response.data:
                        member_security_ids = set()
                        for member in member_response.data:
                            member_security_ids.add(member['security_id'])

                        for item in items:
                            if item['id'] in member_security_ids:
                                item['is_member'] = True
                break

    # .. and return the JSON response.
    body = dumps(items).encode('utf-8')

    out = HttpResponse(body, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################
