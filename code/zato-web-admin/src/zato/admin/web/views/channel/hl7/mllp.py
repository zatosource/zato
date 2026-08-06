# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http import HTTPStatus
from json import dumps
from logging import getLogger
from socket import AF_INET, SOCK_STREAM, socket as socket_
from time import time
from traceback import format_exc
from urllib.parse import urlparse

# Django
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms import populate_form_initial
from zato.admin.web.forms.channel.hl7.mllp import CreateForm, EditForm, RowEditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, \
    get_http_channel_security_id, get_security_id_from_select, SecurityList
from zato.common.api import GENERIC, generic_attrs, Groups, HL7, SEC_DEF_TYPE, ZATO_NONE
from zato.common.destination.model import count_entries
from zato.common.hl7.mllp.fields import Channel_Defaults, resolve_max_msg_size
from zato.common.hl7.mllp.settings import describe_bounds_violations
from zato.common.model.hl7 import HL7MLLPChannelConfigObject
from zato.common.util.api import asbool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strlist
    any_ = any_
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# .. name prefix for backing REST channels ..
_REST_Channel_Name_Prefix = 'hl7.rest.'

# .. the multi-step wizard template, serving both the create and the edit page ..
_Wizard_Template = 'zato/channel/hl7/mllp-wizard.html'

# .. what the security selects carry in front of a definition's id, an id alone being
# .. what a channel stores under security_id ..
_MTLS_Select_Prefix = SEC_DEF_TYPE.MTLS + '/'

# .. the fields a channel matches incoming messages on, in MSH order, each with what the list
# .. calls it - the wizard's Match row is written the same way ..
_Matcher_Labels = [
    ('msh3_sending_app', 'MSH-3'),
    ('msh4_sending_facility', 'MSH-4'),
    ('msh5_receiving_app', 'MSH-5'),
    ('msh6_receiving_facility', 'MSH-6'),
    ('msh9_message_type', 'MSH-9.1'),
    ('msh9_trigger_event', 'MSH-9.2'),
    ('msh11_processing_id', 'MSH-11'),
    ('msh12_version_id', 'MSH-12'),
]

# .. what a channel with no matcher of its own is said to take ..
_Any_Message_Label = 'All messages'

# .. the two flags a row turns over on the list itself ..
_Inline_Flag_Names = ['is_active', 'is_default']

# .. what a message is handed to, which the list edits in the wizard's own panels ..
_Inline_Target_Names = ['service', 'destinations', 'respond_from', 'delivery_mode']

# .. everything a row may change without the wizard being opened ..
_Inline_Field_Names = [name for name, _ in _Matcher_Labels] + _Inline_Flag_Names + _Inline_Target_Names

# .. what the page is told when no other channel held the default flag ..
_No_Previous_Default = 0

# .. and what the fields a row is edited through are named after.
_Row_Edit_Prefix = 'mllp-row'

# ################################################################################################################################
# ################################################################################################################################

def get_match_values(get_value:'any_') -> 'stranydict':
    """ The matchers of one channel, gathered from wherever they are kept - a list row,
    a stored channel or what a page posted back, the caller saying how one is read.
    """
    out = {}

    for name, _ in _Matcher_Labels:
        out[name] = get_value(name)

    return out

# ################################################################################################################################

def get_match_label(values:'stranydict') -> 'str':
    """ Says in one line which messages a channel takes - each matcher it fills in narrows
    what reaches it, and a channel that fills in none of them takes everything.
    """
    parts = []

    for name, label in _Matcher_Labels:
        value = values[name]
        if value:
            parts.append(f'{label} = {value}')

    if not parts:
        return _Any_Message_Label

    out = ', '.join(parts)
    return out

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-hl7-mllp'
    template = 'zato/channel/hl7/mllp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = HL7MLLPChannelConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'is_internal', 'service', 'security_name'
    output_optional = (
        'should_parse_on_input', 'should_validate', 'should_return_errors',
        'should_log_messages', 'is_audit_log_active',
        'max_msg_size', 'max_msg_size_unit', 'recv_timeout', 'idle_timeout',
        'keepalive_idle', 'keepalive_interval', 'keepalive_probe_count',
        'security_id', 'allowed_networks',
        'start_seq', 'end_seq',
        'msh3_sending_app', 'msh4_sending_facility',
        'msh5_receiving_app', 'msh6_receiving_facility', 'msh9_message_type',
        'msh9_trigger_event', 'msh11_processing_id', 'msh12_version_id', 'is_default',
        'dedup_ttl_value', 'dedup_ttl_unit',
        'default_character_encoding',
        'normalize_line_endings', 'force_standard_delimiters',
        'restore_truncated_msh', 'split_concatenated_messages', 'use_msh18_encoding',
        'normalize_obx2_value_type', 'replace_invalid_obx2_value_type',
        'normalize_invalid_escape_sequences', 'normalize_obx8_abnormal_flags',
        'normalize_quadruple_quoted_empty', 'allow_short_encoding_characters',
        'fix_off_by_one_field_index',
        'destinations', 'respond_from', 'delivery_mode',
        'use_rest', 'rest_only', 'rest_channel_id',
    ) + generic_attrs
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item:'any_') -> 'any_':
        """ Counts the channel's destinations so the list can say how many there are without
        each row's stored list having to be read again by the page itself, and writes out
        the channel's match both as the line the row shows and as what the row's own
        editor opens on.
        """
        item.destination_count = count_entries(item.destinations)

        match_values = get_match_values(lambda name: getattr(item, name))

        item.match_label = get_match_label(match_values)
        item.match_json = dumps(match_values)

        return item

# ################################################################################################################################

    def handle(self):

        # Creating and editing happen on their own pages, so the list renders no dialog and
        # needs neither the forms nor the security definitions a dialog would be built from.
        # The two ports go to the page so it can tell a sending system where to connect -
        # the address itself is the browser's to say, it being the one that got here. The row
        # form is what the wizard's panels edit one row's target through.
        return {
            'show_search_form': True,
            'mllp_port': os.environ['Zato_Port_MLLP'],
            'mllps_port': os.environ['Zato_Port_MLLP_SSL'],
            'row_form': RowEditForm(self.req, _Row_Edit_Prefix),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    # A channel hands each message to a service, to its destinations, or to both, so the service
    # is not required here - what a new channel may not do is name neither of the two.
    is_target_required = True

    input_required = 'name', 'is_internal'
    input_optional = (
        'service',
        'is_active', 'should_parse_on_input', 'should_validate', 'should_return_errors',
        'should_log_messages', 'is_audit_log_active',
        'max_msg_size', 'max_msg_size_unit', 'recv_timeout', 'idle_timeout',
        'keepalive_idle', 'keepalive_interval', 'keepalive_probe_count',
        'allowed_networks',
        'start_seq', 'end_seq',
        'msh3_sending_app', 'msh4_sending_facility',
        'msh5_receiving_app', 'msh6_receiving_facility', 'msh9_message_type',
        'msh9_trigger_event', 'msh11_processing_id', 'msh12_version_id', 'is_default',
        'dedup_ttl_value', 'dedup_ttl_unit',
        'default_character_encoding',
        'normalize_line_endings', 'force_standard_delimiters',
        'restore_truncated_msh', 'split_concatenated_messages', 'use_msh18_encoding',
        'normalize_obx2_value_type', 'replace_invalid_obx2_value_type',
        'normalize_invalid_escape_sequences', 'normalize_obx8_abnormal_flags',
        'normalize_quadruple_quoted_empty', 'allow_short_encoding_characters',
        'fix_off_by_one_field_index',
        'destinations', 'respond_from', 'delivery_mode',
        'use_rest', 'rest_only', 'rest_channel_id', 'rest_url_path', 'rest_security_id',
    ) + generic_attrs
    output_required = 'id', 'name'

# ################################################################################################################################

    def pre_process_item(self, name:'str', value:'any_') -> 'any_':
        """ A field the page leaves empty arrives with no value at all, so what travels on is
        what the field defaults to - a channel stores its own defaults rather than nulls.
        """
        if value is None:
            if name in Channel_Defaults:
                default = Channel_Defaults[name]

                # The page renders every switch it has, and a switch that is off is not posted
                # at all, so nothing arriving under a switch is the switch being off - taking
                # the default here would put back the very value that was just turned off.
                if isinstance(default, bool):
                    value = False
                else:
                    value = default

        return value

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict:'stranydict') -> 'None':

        self._check_target()
        self._check_listener_bounds()

        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1
        initial_input_dict['data_format'] = HL7.Const.Version.v2.id

        # The security select carries its type along with the id, and only the id is stored
        initial_input_dict['security_id'] = self._get_security_id()

        # The backing REST channel is named after the MLLP channel and needs nothing else from it,
        # so it is settled here and its id travels with the one and only save of the MLLP channel.
        initial_input_dict['rest_channel_id'] = self._sync_rest_channel()

# ################################################################################################################################

    def _check_target(self) -> 'None':
        """ Refuses a new channel that hands each message it accepts to neither a service nor a
        destination, there being nowhere for its messages to go - the same rule the enmasse
        importer enforces, applied to what the page posts. A stored channel is not asked again,
        one that had its service and its destinations taken away being one someone meant to
        leave that way.
        """
        prefix = self.form_prefix
        post_data = self.req.POST

        service = post_data[f'{prefix}service']
        destinations = post_data[f'{prefix}destinations']

        if service:
            return

        if self.is_target_required:
            if not count_entries(destinations):
                name = post_data[f'{prefix}name']
                raise Exception(f'HL7 MLLP channel `{name}` needs a service or at least one destination')

        # The backing REST channel hands each request to a service of its own, which is the
        # channel's, so there is no bridge to build for a channel that names no service.
        if post_data.get(f'{prefix}use_rest'):
            name = post_data[f'{prefix}name']
            raise Exception(f'HL7 MLLP channel `{name}` needs a service for its REST bridge')

# ################################################################################################################################

    def _check_listener_bounds(self) -> 'None':
        """ Refuses a channel asking for more room or more time than the listener it runs on has,
        since a channel's values tune what the listener already allows.
        """
        prefix = self.form_prefix
        post_data = self.req.POST

        max_msg_size = int(post_data[f'{prefix}max_msg_size'])
        max_msg_size_unit = post_data[f'{prefix}max_msg_size_unit']
        idle_timeout = float(post_data[f'{prefix}idle_timeout'])

        violations = describe_bounds_violations(
            resolve_max_msg_size(max_msg_size, max_msg_size_unit),
            idle_timeout,
        )

        if violations:
            raise Exception(', '.join(violations))

# ################################################################################################################################

    def _get_security_id(self) -> 'int':
        """ Returns the id of the mTLS definition the channel accepts messages under, zero when
        the channel accepts a connection whatever certificate it was made with.
        """
        posted_value = self.req.POST[f'{self.form_prefix}security_id']

        # The select's placeholder and its no-security choice both mean a channel accepting
        # a connection whatever certificate it was made with
        if posted_value in ('', ZATO_NONE):
            return 0

        # What is posted otherwise is the definition's type alongside its id, and the id is
        # the only part of it a channel stores.
        raw_value = get_security_id_from_select(self.req.POST, self.form_prefix, field_name='security_id')

        out = int(raw_value)
        return out

# ################################################################################################################################

    def _get_rest_security_id(self) -> 'str':
        """ Returns what the backing REST channel authenticates its callers with, ZATO_NONE for
        a bridge taking a request whatever it was made with.
        """
        posted_value = self.req.POST[f'{self.form_prefix}rest_security_id']

        # A bridge turned on without its popover ever being opened leaves the select on the
        # placeholder it was rendered with, which says the same as picking no security does
        if posted_value in ('', ZATO_NONE):
            return ZATO_NONE

        # What is posted otherwise is the definition's type alongside its id, and the id is
        # the only part of it a REST channel is given.
        out = get_security_id_from_select(self.req.POST, self.form_prefix, field_name='rest_security_id')
        return out

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        out = 'Successfully {} HL7 MLLP channel `{}`'.format(self.verb, item.name)
        return out

# ################################################################################################################################

    def _save_security_group(self, mllp_name:'str', security_id_list:'list') -> 'int':
        """ Wraps the security definitions picked in the wizard in one group,
        kept transparently for the backing REST channel. The input values
        come from the security select, i.e. they look like basic_auth/123.
        """

        # .. the group members are keyed the way the groups page keys them ..
        member_id_list = []
        for item in security_id_list:
            member_id_list.append(item.replace('/', '-'))

        # .. the group carries the same name as the backing REST channel,
        # which the wizard has already checked for uniqueness ..
        group_name = _REST_Channel_Name_Prefix + mllp_name

        request:'stranydict' = {
            'group_type': Groups.Type.API_Clients,
            'name': group_name,
            'member_id_list': member_id_list,
        }

        # .. a channel saved again already has a group of that name, so the picks it carries
        # now replace the ones the group was left with the last time around ..
        group_id = _get_security_group_id(self.req, group_name)

        if group_id:
            request['id'] = group_id
            service_name = 'zato.groups.edit'
        else:
            service_name = 'zato.groups.create'

        response = self.req.zato.client.invoke(service_name, request)

        if not response.ok:
            logger.error('Could not save security group `%s` for `%s`: %s', group_name, mllp_name, response.details)
            raise Exception(f'Could not save security group `{group_name}`: {response.details}')

        # .. a group just created is the one case where the id comes from the server.
        if not group_id:
            group_id = response.data.id

        logger.info('Saved security group id=%s `%s` for MLLP channel `%s`', group_id, group_name, mllp_name)

        out = group_id
        return out

# ################################################################################################################################

    def _build_rest_channel_message(self, mllp_name:'str') -> 'dict':
        """ Builds the input dict for zato.http-soap.create or edit,
        .. reading REST-specific fields from POST data.
        """

        # .. extract security ID from the select widget ..
        security_id = self._get_rest_security_id()

        # .. with two or more security definitions picked in the wizard,
        # all of them arrive in this list and one group of the channel's own
        # holds them - the group secures the channel and no single
        # definition is assigned to it directly ..
        security_groups = []
        security_id_list = self.req.POST.getlist('mllp_security_id_list')
        security_id_count = len(security_id_list)

        if security_id_count > 1:
            group_id = self._save_security_group(mllp_name, security_id_list)
            security_groups.append(group_id)
            security_id = ZATO_NONE

        prefix = self.form_prefix

        out = {
            'cluster_id': self.cluster_id,
            'is_internal': False,
            'is_active': True,
            'connection': 'channel',
            'transport': 'plain_http',
            'name': _REST_Channel_Name_Prefix + mllp_name,
            'url_path': self.req.POST[prefix + 'rest_url_path'],
            'service': self.req.POST[prefix + 'service'],
            'security_id': security_id,
            'security_groups': security_groups,
            'data_format': 'hl7-v2',
            'should_parse_on_input': True,
            'match_slash': False,
            'merge_url_params_req': True,
        }

        return out

# ################################################################################################################################

    def _create_rest_channel(self, mllp_name:'str') -> 'int':
        """ Creates a backing REST channel and returns its ID.
        """
        message = self._build_rest_channel_message(mllp_name)
        response = self.req.zato.client.invoke('zato.http-soap.create', message)

        if response.ok:
            rest_channel_id = response.data.id
            logger.info('Created backing REST channel id=%s for MLLP channel `%s`', rest_channel_id, mllp_name)
            return rest_channel_id
        else:
            logger.error('Could not create backing REST channel for `%s`: %s', mllp_name, response.details)
            raise Exception(f'Could not create the backing REST channel: {response.details}')

# ################################################################################################################################

    def _edit_rest_channel(self, rest_channel_id:'int', mllp_name:'str') -> 'None':
        """ Updates the backing REST channel with current form values.
        """
        message = self._build_rest_channel_message(mllp_name)
        message['id'] = rest_channel_id
        response = self.req.zato.client.invoke('zato.http-soap.edit', message)

        if response.ok:
            logger.info('Updated backing REST channel id=%s for MLLP channel `%s`', rest_channel_id, mllp_name)
        else:
            logger.error('Could not update backing REST channel id=%s: %s', rest_channel_id, response.details)
            raise Exception(f'Could not update the backing REST channel: {response.details}')

# ################################################################################################################################

    def _delete_rest_channel(self, rest_channel_id:'int') -> 'None':
        """ Deletes the backing REST channel.
        """
        message = {
            'id': rest_channel_id,
            'cluster_id': self.cluster_id,
        }
        response = self.req.zato.client.invoke('zato.http-soap.delete', message)

        if response.ok:
            logger.info('Deleted backing REST channel id=%s', rest_channel_id)
        else:
            logger.error('Could not delete backing REST channel id=%s: %s', rest_channel_id, response.details)
            raise Exception(f'Could not delete the backing REST channel: {response.details}')

# ################################################################################################################################

    def _get_rest_channel_id(self, mllp_name:'str') -> 'int':
        """ Returns the id of the REST channel backing an MLLP channel of this name, zero if there is none.
        """

        # An MLLP channel without a backing REST channel is the regular state of affairs here
        # rather than an error - e.g. the first save of a new channel - and the get service
        # raises when no such object exists, so the lookup goes through the list instead.
        name = _REST_Channel_Name_Prefix + mllp_name

        response = self.req.zato.client.invoke('zato.http-soap.get-list', {
            'cluster_id': self.cluster_id,
            'connection': 'channel',
            'transport': 'plain_http',
            'query': name,
        })

        if response.ok and response.data:
            for item in response.data:
                if item.name == name:
                    return item.id

        return 0

# ################################################################################################################################

    def _sync_rest_channel(self) -> 'int':
        """ Brings the backing REST channel in line with what the REST bridge toggle says
        and returns the id the MLLP channel is to be saved with.
        """
        prefix = self.form_prefix
        use_rest = bool(self.req.POST.get(prefix + 'use_rest'))
        mllp_name = self.req.POST[prefix + 'name']

        # A channel that already has a backing one carries its id in the form, and that id
        # holds across a rename. Without one, the name the backing channel is always given
        # says whether an earlier save got as far as creating it ..
        rest_channel_id = self.req.POST.get('rest_channel_id')

        if rest_channel_id:
            rest_channel_id = int(rest_channel_id)
        else:
            rest_channel_id = self._get_rest_channel_id(mllp_name)

        # .. with the bridge on, that channel is either brought up to date or created ..
        if use_rest:
            if rest_channel_id:
                self._edit_rest_channel(rest_channel_id, mllp_name)
                out = rest_channel_id
            else:
                out = self._create_rest_channel(mllp_name)

        # .. and with the bridge off, whatever was created earlier goes away.
        else:
            if rest_channel_id:
                self._delete_rest_channel(rest_channel_id)
            out = 0

        return out

# ################################################################################################################################

    def post_process_return_data(self, return_data:'dict') -> 'dict':
        """ Reports the state of the REST bridge back to the page that saved the channel.
        """
        prefix = self.form_prefix

        return_data['rest_channel_id'] = self.input_dict['rest_channel_id']
        return_data['use_rest'] = bool(self.req.POST.get(prefix + 'use_rest'))

        return return_data

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-hl7-mllp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-hl7-mllp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

    # Where a stored channel's messages go is answered on the step that asks it, and each step
    # of an edit is saved on its own, so a save made on another one leaves that answer alone
    is_target_required = False

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-hl7-mllp-delete'
    error_message = 'Could not delete HL7 MLLP channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

def _get_security_group_id(req:'any_', group_name:'str') -> 'int':
    """ Returns the id of the API client group of this name, zero when there is none.
    """
    response = req.zato.client.invoke('zato.groups.get-list', {
        'group_type': Groups.Type.API_Clients,
    })

    for group in response.data:
        if group['name'] == group_name:
            out = group['id']
            break
    else:
        out = 0

    return out

# ################################################################################################################################

def _get_rest_security_key_list(req:'any_', mllp_name:'str') -> 'strlist':
    """ The definitions the channel's REST bridge authenticates its callers with, each in the
    sec_type/id form the wizard's security rows are built from. Two or more of them are kept in
    a group of the channel's own, which is where the whole list is read back from.
    """
    out = []

    group_name = _REST_Channel_Name_Prefix + mllp_name
    group_id = _get_security_group_id(req, group_name)

    if not group_id:
        return out

    response = req.zato.client.invoke('zato.groups.get-member-list', {
        'group_type': Groups.Type.API_Clients,
        'group_id': group_id,
    })

    for member in response.data:
        sec_type = member['sec_type']
        security_id = member['security_id']
        out.append(f'{sec_type}/{security_id}')

    return out

# ################################################################################################################################

def _populate_rest_bridge(req:'any_', item_dict:'stranydict', rest_channel_id:'int') -> 'None':
    """ Puts the path and the security definition of the backing REST channel under the two
    fields the wizard's REST popover opens with. An MLLP channel stores neither of them - both
    belong to the REST channel it keeps alongside itself.
    """
    response = req.zato.client.invoke('zato.http-soap.get', {
        'cluster_id': req.zato.cluster_id,
        'id': rest_channel_id,
    })

    rest_channel = response.data

    item_dict['rest_url_path'] = rest_channel.url_path
    item_dict['rest_security_id'] = get_http_channel_security_id(rest_channel)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def wizard_create(req:'any_') -> 'TemplateResponse':
    """ A multi-step wizard for a new HL7 MLLP channel.
    """
    security_list = SecurityList.from_service(req.zato.client, req.zato.cluster.id, SEC_DEF_TYPE.BASIC_AUTH)
    mtls_security_list = SecurityList.from_service(req.zato.client, req.zato.cluster.id, SEC_DEF_TYPE.MTLS)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': CreateForm(req=req, security_list=security_list, mtls_security_list=mtls_security_list),
        'is_edit': False,
        'item_id': '',
        'rest_channel_id': 0,
        'security_key_list': [],
    }

    out = TemplateResponse(req, _Wizard_Template, return_data)
    return out

# ################################################################################################################################

@method_allowed('GET')
def wizard_edit(req:'any_', id:'str') -> 'TemplateResponse':
    """ The same wizard, opened on one existing HL7 MLLP channel.
    """

    # The URL points to one channel, so one channel is what is fetched - the page renders
    # nothing about any of the others ..
    response = req.zato.client.invoke('zato.generic.connection.get-by-id', {'id': id})

    if not response.ok:
        raise Exception(f'HL7 MLLP channel with id `{id}` could not be read')

    item_dict = response.data

    # .. the mTLS select carries a definition's type alongside its id, while a channel stores
    # the id alone, so what was stored is put back into the shape the select offers ..
    if 'security_id' in item_dict:
        security_id = item_dict['security_id']
        if security_id:
            item_dict['security_id'] = f'{_MTLS_Select_Prefix}{security_id}'

    # .. the REST bridge, if there is one, says what its path and its security are ..
    rest_channel_id = 0

    if 'rest_channel_id' in item_dict:
        stored_rest_channel_id = item_dict['rest_channel_id']

        # A channel that never had a bridge may still carry the key with nothing under it,
        # and what the page is given goes into the form as text, so a null would reach
        # the save as the word it is written with rather than as no channel at all
        if stored_rest_channel_id:
            rest_channel_id = stored_rest_channel_id

    if rest_channel_id:
        _populate_rest_bridge(req, item_dict, rest_channel_id)

    security_list = SecurityList.from_service(req.zato.client, req.zato.cluster.id, SEC_DEF_TYPE.BASIC_AUTH)
    mtls_security_list = SecurityList.from_service(req.zato.client, req.zato.cluster.id, SEC_DEF_TYPE.MTLS)

    # .. the edit endpoint reads its input under the edit- prefix, which is what the form
    # .. is built with and what the wizard's own fieldPrefix mirrors ..
    form = EditForm(prefix='edit', req=req, security_list=security_list, mtls_security_list=mtls_security_list)
    populate_form_initial(form, item_dict)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'is_edit': True,
        'item_id': item_dict['id'],

        # The id of the backing REST channel travels with the save, so a channel renamed here
        # keeps the REST channel it already has rather than being given a second one
        'rest_channel_id': rest_channel_id,
        'security_key_list': _get_rest_security_key_list(req, item_dict['name']),
    }

    out = TemplateResponse(req, _Wizard_Template, return_data)
    return out

# ################################################################################################################################

def _save_channel(req:'any_', item_dict:'stranydict') -> 'None':
    """ Saves a channel the way any other edit of it would.
    """
    channel_id = item_dict['id']
    response = req.zato.client.invoke('zato.generic.connection.edit', item_dict)

    if not response.ok:
        raise Exception(f'HL7 MLLP channel with id `{channel_id}` could not be saved')

# ################################################################################################################################

def _read_channel(req:'any_', id:'str') -> 'stranydict':
    """ One channel as it currently stands.
    """
    response = req.zato.client.invoke('zato.generic.connection.get-by-id', {'id': id})

    if not response.ok:
        raise Exception(f'HL7 MLLP channel with id `{id}` could not be read')

    out = response.data
    return out

# ################################################################################################################################

def _is_default(item:'stranydict') -> 'bool':
    """ Whether a channel holds the default flag. A generic connection carries the flag only once
    something has set it, so a channel that never has is not the default.
    """
    if 'is_default' not in item:
        return False

    out = asbool(item['is_default'])
    return out

# ################################################################################################################################

def _clear_other_default(req:'any_', id:'str') -> 'int':
    """ Takes the default flag off whichever other channel held it, returning its id, zero if none did.
    """
    response = req.zato.client.invoke('zato.generic.connection.get-list', {
        'cluster_id': req.zato.cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP,
    })

    for item in response.data:

        # The channel just made the default is not the one being cleared
        if str(item['id']) == str(id):
            continue

        if _is_default(item):
            other = _read_channel(req, item['id'])
            other['is_default'] = False
            _save_channel(req, other)

            out = item['id']
            return out

    return _No_Previous_Default

# ################################################################################################################################

@method_allowed('POST')
def inline_edit(req:'any_', id:'str') -> 'JsonResponse':
    """ Stores what the channel list edited without leaving the page - only the fields posted change.
    """
    item_dict = _read_channel(req, id)

    for name in _Inline_Field_Names:
        if name in req.POST:
            value = req.POST[name]

            # A flag travels as the word it is written with, everything else as itself
            if name in _Inline_Flag_Names:
                value = asbool(value)

            item_dict[name] = value

    # A row may be left with neither a service nor a destination, one of the two being
    # cleared before the other is picked in the panel that comes next
    service = item_dict['service']

    _save_channel(req, item_dict)

    # A flag comes back from storage as the word it was written with as readily as the thing itself
    is_active = asbool(item_dict['is_active'])
    is_default = _is_default(item_dict)

    # Only one channel is the default, and the page is told which row lost it
    if is_default:
        default_cleared_id = _clear_other_default(req, id)
    else:
        default_cleared_id = _No_Previous_Default

    # What the row now says of itself
    out = JsonResponse({
        'is_active': is_active,
        'is_default': is_default,
        'match_label': get_match_label(get_match_values(lambda name: item_dict[name])),
        'default_cleared_id': default_cleared_id,
        'service': service,
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

# .. MLLP framing bytes ..
_MLLP_Start_Byte = b'\x0b'
_MLLP_End_Bytes  = b'\x1c\x0d'

# .. TCP recv buffer size ..
_Recv_Buffer_Size = 65536

# .. socket timeout in seconds ..
_Socket_Timeout = 90

# ################################################################################################################################
# ################################################################################################################################

def _resolve_mllp_listener_address(req:'any_') -> 'tuple[str, int]':
    """ Resolves where the shared MLLP listener accepts connections - the port lives
    in the server process and the listener runs on the same host as the server itself.
    """
    response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'get_hl7_mllp_port'})
    port = int(response.data)

    host = urlparse(req.zato.client.address).hostname

    return host, port

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def invoke_channel(req:'any_', id:'str') -> 'JsonResponse':
    """ Sends an MLLP-framed HL7 message to the server's MLLP listener and returns the response.
    """
    try:
        payload = req.POST['data-request']
        payload_bytes = payload.encode('utf-8')

        # .. find the listener - a port of zero means no MLLP channel is running ..
        listener_host, listener_port = _resolve_mllp_listener_address(req)

        if not listener_port:
            return JsonResponse({
                'data': 'No HL7 MLLP listener is running - create an active MLLP channel first',
                'response_time_human': '',
                'content_type': 'text/plain',
            }, status=HTTPStatus.BAD_REQUEST)

        # .. wrap in MLLP framing ..
        mllp_message = _MLLP_Start_Byte + payload_bytes + _MLLP_End_Bytes

        start = time()

        # .. open a TCP connection to the listener ..
        sock = socket_(AF_INET, SOCK_STREAM)
        sock.settimeout(_Socket_Timeout)

        try:
            sock.connect((listener_host, listener_port))
            sock.sendall(mllp_message)

            # .. read the MLLP-framed response ..
            response_data = b''
            while True:
                chunk = sock.recv(_Recv_Buffer_Size)
                if not chunk:
                    break
                response_data += chunk

                # .. stop once we see the MLLP end bytes ..
                if _MLLP_End_Bytes in response_data:
                    break

        finally:
            sock.close()

        elapsed = time() - start

        # .. strip MLLP framing from the response ..
        response_text = response_data
        if response_text.startswith(_MLLP_Start_Byte):
            response_text = response_text[1:]
        end_idx = response_text.find(_MLLP_End_Bytes)
        if end_idx != -1:
            response_text = response_text[:end_idx]

        response_body = response_text.decode('utf-8', errors='replace')

        return JsonResponse({
            'data': response_body,
            'response_time_human': '{:.1f}ms'.format(elapsed * 1000),
            'content_type': 'text/plain',
        })

    except Exception as e:
        logger.error('invoke_channel error: %s', format_exc())
        return JsonResponse({
            'data': str(e),
            'response_time_human': '',
            'content_type': 'text/plain',
        }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def import_demo_config(req:'any_') -> 'HttpResponse':
    """ Runs the HL7 demo import on the server - the demo connections, the alert
    rules, the seeded week of audit history and the live traffic burst.

    It creates all of that, so it is a POST and is covered by the cross-site request
    checks that a GET would sit outside of.
    """
    response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'import_demo_hl7'})

    out = HttpResponse()
    out.content = str(response.data)

    return out

# ################################################################################################################################
# ################################################################################################################################
