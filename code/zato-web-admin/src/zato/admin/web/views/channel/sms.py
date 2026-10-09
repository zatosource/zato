# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.http import HttpResponseServerError

# Zato
from zato.admin.web import delivery_tab, sms_tab
from zato.admin.web.forms import add_select_from_service
from zato.admin.web.forms.channel.sms import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.api import GENERIC, SMS
from zato.common.exception import ZatoException
from zato.common.ext.bunch import Bunch
from zato.common.sms.config import get_webhook_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_scheduler = SMS.Scheduler

# The retry fields, stored in the channel's opaque attributes
_retry_field_names = tuple(delivery_tab.retry_field_defaults)

# The use_queue field and the DLQ config of the Delivery tab, stored in the channel's opaque attributes
_delivery_field_names = tuple(delivery_tab.field_defaults)

# The channel's own fields beyond its name
_sms_required_field_names = sms_tab.Channel_Required_Field_Names
_sms_optional_field_names = sms_tab.Channel_Optional_Field_Names
_sms_field_names = (SMS.Field_Outconn_Name,) + _sms_required_field_names + _sms_optional_field_names

# The fields of the Provider section, which the form posts for the channel's outgoing connection
_outconn_form_field_names = (sms_tab.Outconn_ID_Field_Name,) + sms_tab.Provider_Field_Names + sms_tab.Secret_Field_Names

# The services that create, edit and delete the channel's outgoing connection
_outconn_create_service = 'zato.generic.connection.create'
_outconn_edit_service = 'zato.generic.connection.edit'
_outconn_delete_service = 'zato.generic.connection.delete'
_outconn_list_service = 'zato.generic.connection.get-list'

# ################################################################################################################################
# ################################################################################################################################

def _list_outconns(req:'any_', cluster_id:'any_', query:'str') -> 'anylist':
    """ The outgoing SMS connections whose name matches the query, every connection when the query is empty.
    """
    request = {
        'cluster_id': cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_SMS,
        'paginate': False,
        'query': query,
    }

    response = req.zato.client.invoke(_outconn_list_service, request)
    out = response.data

    return out

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-sms'
    template = 'zato/channel/sms.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active'
    output_optional = _sms_field_names + _retry_field_names + _delivery_field_names
    output_repeated = True

    def __init__(self) -> 'None':
        super().__init__()

        # The outgoing connections of the channels, by name
        self.outconns:'anydict' = {}

# ################################################################################################################################

    def before_invoke_admin_service(self) -> 'None':

        # Each channel's row has the provider fields of its outgoing connection
        for item in _list_outconns(self.req, self.cluster_id, ''):
            self.outconns[item['name']] = item

# ################################################################################################################################

    def on_before_append_item(self, item:'any_') -> 'any_':

        item.receive_mode_human = SMS.Receive_Mode_Human[item.receive_mode]
        item.webhook_path = get_webhook_path(item.name)
        item.scheduler_run_unit = sms_tab.poll_unit_for_form(item.scheduler_run_unit)

        # The provider fields of the channel's outgoing connection - a connection deleted on its own page
        # leaves the channel with none to show
        if item.outconn_name in self.outconns:
            outconn = self.outconns[item.outconn_name]
            item.outconn_id = outconn['id']
            item.provider_human = SMS.ProviderHuman[outconn[SMS.Field_Provider]]

            for name in sms_tab.Provider_Field_Names:
                item[name] = outconn[name]
        else:
            item.outconn_id = ''
            item.provider_human = ''

            for name in sms_tab.Provider_Field_Names:
                item[name] = ''

        # The retry fields are opaque attributes ..
        delivery_tab.fill_retry_row(item)

        # .. and so are the Delivery tab's fields.
        delivery_tab.fill_row(item, item)
        delivery_tab.split_unit_fields(item)

        return item

# ################################################################################################################################

    def handle(self) -> 'anydict':

        create_form = CreateForm(self.req)
        edit_form = EditForm(self.req, prefix='edit')

        # The DLQ forward-to select lists topics by name
        add_select_from_service(create_form, self.req, 'zato.pubsub.topic.get-list', 'dlq_forward_to', by_id=False)
        add_select_from_service(edit_form, self.req, 'zato.pubsub.topic.get-list', 'dlq_forward_to', by_id=False)

        out = {
            'show_search_form': True,
            'create_form': create_form,
            'edit_form': edit_form,
            'delivery_tab_config': delivery_tab.get_delivery_tab_config(),
            'sms_config': _get_sms_config(),
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_sms_config() -> 'anydict':
    """ The channel data of the page's JavaScript - the provider data, the receive modes and the webhook path prefix.
    """
    out = sms_tab.get_provider_config()
    out['receive_mode_webhook'] = SMS.Receive_Mode.Webhook
    out['receive_mode_polling'] = SMS.Receive_Mode.Polling
    out['webhook_path_prefix'] = SMS.Webhook_Path_Prefix

    return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = ('name',) + _sms_required_field_names
    input_optional = ('is_active',) + _sms_optional_field_names + _retry_field_names + _delivery_field_names + \
        _outconn_form_field_names
    output_required = 'id', 'name'

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        # The outgoing connection created for a new channel, deleted when the channel itself cannot be created
        self.created_outconn_id = 0

# ################################################################################################################################

    def __call__(self, req:'any_', *args:'any_', **kwargs:'any_') -> 'any_':

        self.created_outconn_id = 0
        out = super().__call__(req, *args, **kwargs)

        if isinstance(out, HttpResponseServerError):
            if self.created_outconn_id:
                request = {'cluster_id': self.cluster_id, 'id': self.created_outconn_id}
                _ = self.req.zato.client.invoke(_outconn_delete_service, request)

        return out

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict:'anydict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_SMS
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

# ################################################################################################################################

    def sync_outconn(self, input_dict:'anydict') -> 'None':
        """ Creates or edits the channel's outgoing connection from the Provider section of the form.
        """
        raise NotImplementedError('Must be implemented by a subclass')

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict:'anydict') -> 'None':

        # The provider fields belong to the outgoing connection, not to the channel
        for name in _outconn_form_field_names:
            del input_dict[name]

        # The outgoing connection is named after the channel
        self.sync_outconn(input_dict)
        input_dict[SMS.Field_Outconn_Name] = input_dict['name']

        # The scheduler names a unit in the plural
        input_dict[_scheduler.Field_Run_Unit] = sms_tab.poll_unit_for_scheduler(input_dict[_scheduler.Field_Run_Unit])

        # The retry fields are stored as integers
        delivery_tab.type_retry_fields(input_dict)

        # The Delivery tab's fields, durations joined into seconds
        input_dict.update(delivery_tab.get_message_fields(self.req.POST, self.form_prefix))
        delivery_tab.join_unit_fields(self.req.POST, self.form_prefix, input_dict)

# ################################################################################################################################

    def invoke_outconn(self, service_name:'str', request:'anydict') -> 'any_':
        """ Invokes one of the outgoing connection's services, raising with the server's message when it fails.
        """
        response = self.req.zato.client.invoke(service_name, request)

        if not response.ok:
            raise ZatoException(msg=response.details)

        return response.data

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        out = 'Successfully {} SMS channel `{}`'.format(self.verb, item.name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-sms-create'
    service_name = 'zato.generic.connection.create'

    def sync_outconn(self, input_dict:'anydict') -> 'None':

        request = sms_tab.build_outconn_create_input(self.cluster_id, input_dict['name'], input_dict['is_active'], self.input)
        data = self.invoke_outconn(_outconn_create_service, request)

        self.created_outconn_id = data['id']

# ################################################################################################################################

    def post_process_return_data(self, return_data:'anydict') -> 'anydict':
        return_data[sms_tab.Outconn_ID_Field_Name] = self.created_outconn_id
        return_data[SMS.Field_Outconn_Name] = self.input_dict['name']
        return return_data

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-sms-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

    def sync_outconn(self, input_dict:'anydict') -> 'None':

        outconn_id = int(self.input[sms_tab.Outconn_ID_Field_Name])
        outconns = _list_outconns(self.req, self.cluster_id, self.input[SMS.Field_Outconn_Name])
        stored = sms_tab.find_outconn(outconns, outconn_id)

        request = sms_tab.build_outconn_edit_input(
            self.cluster_id, input_dict['name'], input_dict['is_active'], self.input, stored)

        _ = self.invoke_outconn(_outconn_edit_service, request)

# ################################################################################################################################

    def post_process_return_data(self, return_data:'anydict') -> 'anydict':
        return_data[sms_tab.Outconn_ID_Field_Name] = self.input[sms_tab.Outconn_ID_Field_Name]
        return_data[SMS.Field_Outconn_Name] = self.input_dict['name']
        return return_data

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-sms-delete'
    error_message = 'Could not delete SMS channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################
