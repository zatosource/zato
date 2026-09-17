# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web import alerts_tab
from zato.admin.web.forms.gateway.mcp import CreateForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.admin.web.views.gateway.mcp.common import _alert_field_names, _alert_type, _choice_field_defaults, \
    _numeric_shaping_fields, _row_edit_prefix, _security_input_prefix, _service_input_prefix, _shaping_checkbox_fields, \
    _shaping_choice_fields, _shaping_display_defaults, _shaping_fields, _shaping_int_fields, _shaping_list_fields, \
    _skill_input_prefix, get_size_cap_label, numeric_from_bool, save_security_group
from zato.admin.web.views.gateway.mcp_tool_sources import Connection_Source_List
from zato.common.alerting.object_config import Field_Prefix
from zato.common.api import GENERIC, Groups
from zato.common.util.safeguards.common import SafeguardConfig
from zato.common.util.truncate.tokens import Default_Characters_Per_Token

# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, strlist
    any_ = any_
    strdict = strdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'gateway-mcp'
    template = 'zato/gateway/mcp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active'
    output_optional = ('url_path', 'services', 'security_groups') + _shaping_fields
    output_repeated = True

    def get_initial_input(self) -> 'strdict':

        # The type is constant for this page so it is not expected in the URL,
        # it is always added to the service request here instead.
        return {'type_': GENERIC.CONNECTION.TYPE.GATEWAY_MCP}

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

        # Response shaping fields absent from the item - because the gateway predates them
        # or because a falsy value was filtered out on the way - render as their defaults,
        # so the data table's hidden columns always carry definite values for the edit form.
        for name, default_value in _shaping_display_defaults.items():
            if not hasattr(item, name):
                setattr(item, name, default_value)

        # The numeric fields the opaque storage stored as booleans are numbers again
        # before the hidden columns are rendered.
        for name in _numeric_shaping_fields:
            value = getattr(item, name)
            value = numeric_from_bool(value)
            setattr(item, name, value)

        # What the size caps cell of this row says before it is clicked
        item.size_cap_label = get_size_cap_label(item.max_response_size, item.size_cap_mode)

        return item

    def handle(self) -> 'strdict':

        # Creating and editing happen in the wizard on its own page, so the list renders
        # no dialog - the row form is what the size caps popover edits a row through.
        out = {
            'show_search_form': True,
            'row_form': CreateForm(prefix=_row_edit_prefix, req=self.req),
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name',
    input_optional = ('is_active', 'url_path') + _shaping_fields + _alert_field_names
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict:'strdict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.GATEWAY_MCP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

# ################################################################################################################################

    def pre_process_item(self, name:'str', value:'any_') -> 'any_':
        """ The Alerts popup's fields arrive as text and are stored typed - booleans, integers, fractions and stripped text.
        """
        if name.startswith(Field_Prefix):
            out = alerts_tab.pre_process_alert_item(_alert_type, name, value)
        else:
            out = value

        return out

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict:'strdict') -> 'None':

        # A duration is stored as seconds and a size as bytes, which is what each count and unit join into
        alerts_tab.join_unit_fields(_alert_type, input_dict)

        # Checkboxes arrive as 'on' when ticked and are absent from POST otherwise, except that
        # names with a boolean prefix, e.g. is_audit_log_active, were already turned
        # into a bool by set_input upstream ..
        for name in _shaping_checkbox_fields:
            value = input_dict[name]
            input_dict[name] = value is True or value == 'on'

        # .. a select of a disabled stage is excluded from the POST altogether,
        # so an absent value means the stage's documented default ..
        for name in _shaping_choice_fields:
            if not input_dict[name]:
                input_dict[name] = _choice_field_defaults[name]

        # .. the PII validate checkbox is only ever absent along with its whole
        # stage, in which case its documented default holds too ..
        if not input_dict['safeguards_pii_enabled']:
            input_dict['safeguards_pii_validate'] = SafeguardConfig.pii_validate

        # .. integer fields arrive as strings and an empty input means zero ..
        for name in _shaping_int_fields:
            if value := input_dict[name]:
                input_dict[name] = int(value)
            else:
                input_dict[name] = 0

        # .. the characters-per-token ratio is a float with a well-known default ..
        if value := input_dict['characters_per_token']:
            input_dict['characters_per_token'] = float(value)
        else:
            input_dict['characters_per_token'] = Default_Characters_Per_Token

        # .. multi-selects arrive as a plain string when only one option is picked
        # and are absent when nothing is - both normalize to a list ..
        for name in _shaping_list_fields:
            value = input_dict[name]
            if not value:
                input_dict[name] = []
            elif isinstance(value, str):
                input_dict[name] = [value]

        # .. the URL allow list is a comma-separated string of host suffixes ..
        hosts = []
        if value := input_dict['safeguards_url_allow_list']:
            for host in value.split(','):
                host = host.strip()
                if host:
                    hosts.append(host)
        input_dict['safeguards_url_allow_list'] = hosts

        # Collect services from the badge picker hidden inputs ..
        service_names:'strlist' = []

        for key in self.req.POST:
            if key.startswith(_service_input_prefix):
                service_names.append(self.req.POST[key])

        # .. and store them so they end up in opaque data.
        input_dict['services'] = service_names

        # Collect each connection group's picks the same way - one allow list per group,
        # stored in the opaque config under the group's own key.
        for source in Connection_Source_List:

            input_prefix = f'mcp_{source.key}_'
            connection_names:'strlist' = []

            for post_key in self.req.POST:
                if post_key.startswith(input_prefix):
                    connection_names.append(self.req.POST[post_key])

            input_dict[source.config_key] = connection_names

        # Collect the skills the gateway serves as MCP prompts ..
        skill_names:'strlist' = []

        for key in self.req.POST:
            if key.startswith(_skill_input_prefix):
                skill_names.append(self.req.POST[key])

        # .. and store them so they end up in opaque data too.
        input_dict['skills'] = skill_names

        # Collect security definitions from the security badge picker ..
        member_id_list:'strlist' = []

        for key in self.req.POST:
            if key.startswith(_security_input_prefix):
                member_id_list.append(self.req.POST[key])

        # .. auto-create or update the gateway's own security group with the picked members
        # and store the group ID so the hook can assign it to the HTTPSOAP channel.
        group_id = save_security_group(self.req, input_dict['name'], member_id_list)
        input_dict['security_groups'] = [group_id]

# ################################################################################################################################

    def post_process_return_data(self, return_data:'strdict') -> 'strdict':

        # Count the services that were submitted ..
        service_count = 0

        for key in self.req.POST:
            if key.startswith(_service_input_prefix):
                service_count += 1

        # .. and count the security definitions ..
        security_count = 0

        for key in self.req.POST:
            if key.startswith(_security_input_prefix):
                security_count += 1

        # .. attach both counts for the JS data table to display.
        return_data['service_count'] = service_count
        return_data['security_count'] = security_count

        out = return_data
        return out

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        out = f'Successfully {self.verb} MCP gateway `{item.name}`'
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'gateway-mcp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'gateway-mcp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'gateway-mcp-delete'
    error_message = 'Could not delete MCP gateway'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################
