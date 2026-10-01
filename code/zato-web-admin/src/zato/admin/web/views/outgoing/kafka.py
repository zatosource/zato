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
from zato.admin.web import delivery_tab, kafka_producer_tab
from zato.admin.web.forms import add_select_from_service
from zato.admin.web.forms.outgoing.kafka import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, SecurityList, SKIP_VALUE
from zato.common.api import GENERIC, KAFKA, SEC_DEF_TYPE
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_producer = KAFKA.Producer

# The security definition types a Kafka connection can authenticate with.
_security_type_list = [SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.OAUTH]

# The retry fields, stored in the connection's opaque attributes
_retry_field_names = tuple(delivery_tab.retry_field_defaults)

# The queue switch and the DLQ config of the Delivery tab, stored in the connection's opaque attributes
_delivery_field_names = tuple(delivery_tab.field_defaults)

_ssl_field_names = 'ssl', 'ssl_ca_file', 'ssl_cert_file', 'ssl_key_file'
_security_field_names = 'security_id', 'sasl_mechanism'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-kafka'
    template = 'zato/outgoing/kafka.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'address', 'topic'
    output_optional = _ssl_field_names + _security_field_names + ('security_name', 'auth_type') + _producer.FieldList + \
        _retry_field_names + _delivery_field_names
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item:'any_') -> 'any_':

        # The server gives a connection its auth type along with its security definition,
        # so a connection without SASL has neither and its row shows no security.
        if 'security_id' in item:
            item.sec_type = item.auth_type

        # The Producer tab's fields are opaque attributes - a connection that predates them carries no values, so the defaults
        # show, and each stored number is split into a count and a unit
        kafka_producer_tab.fill_row(item)

        # The retry fields are opaque attributes too
        delivery_tab.fill_retry_row(item)

        # The Delivery tab's fields are shown with their defaults and durations split into a count and a unit
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

        create_form = CreateForm(security_list)
        edit_form = EditForm(security_list, prefix='edit')

        # A message from the DLQ is forwarded to a pub/sub topic, selected by name from the topics that currently exist
        add_select_from_service(create_form, self.req, 'zato.pubsub.topic.get-list', 'dlq_forward_to', by_id=False)
        add_select_from_service(edit_form, self.req, 'zato.pubsub.topic.get-list', 'dlq_forward_to', by_id=False)

        return {
            'show_search_form': True,
            'create_form': create_form,
            'edit_form': edit_form,
            'delivery_tab_config': delivery_tab.get_delivery_tab_config(),
            'producer_tab_config': kafka_producer_tab.get_producer_tab_config(),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'address', 'topic'
    input_optional = ('is_active', KAFKA.Field_SSL_Key_Password) + _ssl_field_names + _security_field_names + \
        _producer.FieldList + _retry_field_names + _delivery_field_names
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_KAFKA
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True

# ################################################################################################################################

    def pre_process_item(self, name, value):

        # An empty key password on input means the current one is to be kept,
        # which is why the field cannot be sent to the backend at all.
        if name == KAFKA.Field_SSL_Key_Password:
            if not value:
                return SKIP_VALUE

        return value

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict):

        # The Producer tab's fields arrive as text and are stored typed, with each count and its unit joined into the stored number
        input_dict.update(kafka_producer_tab.get_producer_fields(self.req.POST, self.form_prefix))

        # The retry fields arrive as strings and the backend expects integers,
        # with the shared defaults filling in for anything left empty in a form.
        delivery_tab.type_retry_fields(input_dict)

        # The Delivery tab's fields arrive as text and are stored typed, with each duration's count and unit joined
        # into seconds - the retry durations among them, which is why the join runs over the whole input
        input_dict.update(delivery_tab.get_message_fields(self.req.POST, self.form_prefix))
        delivery_tab.join_unit_fields(self.req.POST, self.form_prefix, input_dict)

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} outgoing Kafka connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-kafka-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-kafka-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-kafka-delete'
    error_message = 'Could not delete outgoing Kafka connection'
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
