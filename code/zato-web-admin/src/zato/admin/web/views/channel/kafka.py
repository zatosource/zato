# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web import delivery_tab, kafka_consumer_tab
from zato.admin.web.forms import add_select_from_service
from zato.admin.web.forms.channel.kafka import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, SecurityList, SKIP_VALUE
from zato.common.api import GENERIC, KAFKA, SEC_DEF_TYPE
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_consumer = KAFKA.Consumer

# The security definition types a Kafka connection can authenticate with.
_security_type_list = [SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.OAUTH]

# The retry fields, stored in the channel's opaque attributes
_retry_field_names = tuple(delivery_tab.retry_field_defaults)

# The DLQ config of the Delivery tab, stored in the channel's opaque attributes
_delivery_field_names = tuple(delivery_tab.field_defaults)

_ssl_field_names = 'ssl', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file'
_security_field_names = 'security_id', 'sasl_mechanism'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-kafka'
    template = 'zato/channel/kafka.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'address', 'group_id', 'service'
    output_optional = ('topic', 'security_name', 'auth_type') + _ssl_field_names + _security_field_names + \
        _consumer.FieldList + _retry_field_names + _delivery_field_names
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item:'any_') -> 'any_':

        # The server gives a channel its auth type along with its security definition,
        # so a channel without SASL has neither and its row shows no security.
        if 'security_id' in item:
            item.sec_type = item.auth_type

        # The Consumer and Routing tabs' fields are opaque attributes ..
        kafka_consumer_tab.fill_row(item)

        # .. and so are the retry fields ..
        delivery_tab.fill_retry_row(item)

        # .. and the Delivery tab's fields.
        delivery_tab.fill_row(item, item)
        delivery_tab.split_unit_fields(item)

        return item

# ################################################################################################################################

    def handle(self):

        security_list = SecurityList.from_service(
            self.req.zato.client,
            self.cluster_id,
            security_type_list=_security_type_list,
            needs_definition_type_name_label=True
        )

        create_form = CreateForm(self.req, security_list)
        edit_form = EditForm(self.req, security_list, prefix='edit')

        # The DLQ forward-to select lists topics by name
        add_select_from_service(create_form, self.req, 'zato.pubsub.topic.get-list', 'dlq_forward_to', by_id=False)
        add_select_from_service(edit_form, self.req, 'zato.pubsub.topic.get-list', 'dlq_forward_to', by_id=False)

        return {
            'show_search_form': True,
            'create_form': create_form,
            'edit_form': edit_form,
            'delivery_tab_config': delivery_tab.get_delivery_tab_config(),
            'consumer_tab_config': kafka_consumer_tab.get_consumer_tab_config(),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'address', 'group_id', 'service'
    input_optional = ('is_active', KAFKA.Field_SSL_Key_Password) + _ssl_field_names + _security_field_names + \
        _consumer.FieldList + _retry_field_names + _delivery_field_names
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_KAFKA
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False

# ################################################################################################################################

    def pre_process_item(self, name:'str', value:'any_') -> 'any_':

        # An empty key password keeps the current one.
        if name == KAFKA.Field_SSL_Key_Password:
            if not value:
                return SKIP_VALUE

        return value

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict:'anydict') -> 'None':

        # The Consumer and Routing tabs' fields
        input_dict.update(kafka_consumer_tab.get_consumer_fields(self.req.POST, self.form_prefix))

        # `topic` is the first entry of the list.
        topics = kafka_consumer_tab.split_topics(input_dict[_consumer.Field_Topics])

        if topics:
            input_dict['topic'] = topics[0]
        else:
            input_dict['topic'] = ''

        # The retry fields are stored as integers
        delivery_tab.type_retry_fields(input_dict)

        # The Delivery tab's fields, durations joined into seconds
        input_dict.update(delivery_tab.get_message_fields(self.req.POST, self.form_prefix))
        delivery_tab.join_unit_fields(self.req.POST, self.form_prefix, input_dict)

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} Kafka channel `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-kafka-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-kafka-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-kafka-delete'
    error_message = 'Could not delete Kafka channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def import_demo_config(req):
    response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'import_demo_kafka'})
    out = HttpResponse()
    out.content = str(response.data)
    return out

# ################################################################################################################################
# ################################################################################################################################
