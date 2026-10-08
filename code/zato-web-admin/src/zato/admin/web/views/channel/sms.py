# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web import delivery_tab
from zato.admin.web.forms import add_select_from_service
from zato.admin.web.forms.channel.sms import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.api import GENERIC, SMS
from zato.common.ext.bunch import Bunch
from zato.common.sms.config import get_webhook_path
from zato.common.util.mcp_oauth import get_server_address

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_scheduler = SMS.Scheduler

# The retry fields, stored in the channel's opaque attributes
_retry_field_names = tuple(delivery_tab.retry_field_defaults)

# The queue switch and the DLQ config of the Delivery tab, stored in the channel's opaque attributes
_delivery_field_names = tuple(delivery_tab.field_defaults)

# The channel's own fields beyond its name
_sms_required_field_names = (SMS.Field_Outconn_Name, SMS.Field_Service, SMS.Field_Receive_Mode)
_sms_optional_field_names = (_scheduler.Field_Run_Every, _scheduler.Field_Run_Unit)
_sms_field_names = _sms_required_field_names + _sms_optional_field_names

# ################################################################################################################################
# ################################################################################################################################

def _add_outconn_select(form:'any_', req:'any_') -> 'None':
    """ Fills the outgoing connection select with the outgoing SMS connections that exist.
    """
    service_extra = {'type_': GENERIC.CONNECTION.TYPE.OUTCONN_SMS, 'paginate': False}
    add_select_from_service(form, req, 'zato.generic.connection.get-list', SMS.Field_Outconn_Name, by_id=False,
        service_extra=service_extra)

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

# ################################################################################################################################

    def on_before_append_item(self, item:'any_') -> 'any_':

        item.receive_mode_human = SMS.Receive_Mode_Human[item.receive_mode]
        item.webhook_url = get_server_address() + get_webhook_path(item.name)

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

        _add_outconn_select(create_form, self.req)
        _add_outconn_select(edit_form, self.req)

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
    """ What the page's JavaScript knows about the channel - the receive modes and where the webhook URL opens.
    """
    out = {
        'receive_mode_webhook': SMS.Receive_Mode.Webhook,
        'receive_mode_polling': SMS.Receive_Mode.Polling,
        'webhook_url_prefix': get_server_address() + SMS.Webhook_Path_Prefix,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = ('name',) + _sms_required_field_names
    input_optional = ('is_active',) + _sms_optional_field_names + _retry_field_names + _delivery_field_names
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict:'anydict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_SMS
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict:'anydict') -> 'None':

        # The retry fields are stored as integers
        delivery_tab.type_retry_fields(input_dict)

        # The Delivery tab's fields, durations joined into seconds
        input_dict.update(delivery_tab.get_message_fields(self.req.POST, self.form_prefix))
        delivery_tab.join_unit_fields(self.req.POST, self.form_prefix, input_dict)

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        out = 'Successfully {} SMS channel `{}`'.format(self.verb, item.name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-sms-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-sms-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-sms-delete'
    error_message = 'Could not delete SMS channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################
