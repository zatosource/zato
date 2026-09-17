# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps

# Zato
from zato.admin.web import alerts_tab
from zato.admin.web.forms.channel.hl7.mllp import RowEditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, get_security_id_from_select
from zato.admin.web.views.channel.hl7.mllp.common import _alert_field_names, _alert_type, _get_security_group_id, \
    _REST_Channel_Name_Prefix, _Row_Edit_Prefix, logger
from zato.common.alerting.object_config import Field_Prefix
from zato.common.api import GENERIC, generic_attrs, Groups, HL7, ZATO_NONE
from zato.common.destination.model import count_entries
from zato.common.hl7.mllp.fields import get_match_label, resolve_max_message_size, Channel_Defaults, Matcher_Labels
from zato.common.hl7.mllp.settings import describe_bounds_violations
from zato.common.model.hl7 import HL7MLLPChannelConfigObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

def get_match_values(get_value:'any_') -> 'stranydict':
    """ The matchers of one channel, gathered from wherever they are kept - a list row,
    a stored channel or what a page posted back, the caller saying how one is read.
    """
    out = {}

    for name, _ in Matcher_Labels:
        out[name] = get_value(name)

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
    ) + generic_attrs + _alert_field_names
    output_required = 'id', 'name'

# ################################################################################################################################

    def pre_process_item(self, name:'str', value:'any_') -> 'any_':
        """ A field the page leaves empty arrives with no value at all, so what travels on is
        what the field defaults to - a channel stores its own defaults rather than nulls.
        """

        # The Alerts popup's fields arrive as text and are stored typed - booleans, integers and stripped text
        if name.startswith(Field_Prefix):
            out = alerts_tab.pre_process_alert_item(_alert_type, name, value)
            return out

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

    def pre_process_input_dict(self, input_dict:'stranydict') -> 'None':

        # A duration is stored as seconds, which is what its count and unit join into
        alerts_tab.join_unit_fields(_alert_type, input_dict)

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
            resolve_max_message_size(max_msg_size, max_msg_size_unit),
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
