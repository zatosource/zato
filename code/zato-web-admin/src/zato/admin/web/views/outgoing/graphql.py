# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.forms.outgoing.graphql import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
    method_allowed, ping_connection, SecurityList
from zato.common.api import GENERIC, generic_attrs, SEC_DEF_TYPE
from zato.common.model.graphql_ import GraphQLConfigObject

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-graphql'
    template = 'zato/outgoing/graphql.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = GraphQLConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'is_internal', 'address', 'security_id', \
        'pool_size', 'security_name'
    output_optional = ('extra', 'default_query_timeout') + generic_attrs
    output_repeated = True

# ################################################################################################################################

    def handle(self):

        security_list = SecurityList.from_service(
            self.req.zato.client,
            self.cluster_id,
            sec_type=[SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.OAUTH, SEC_DEF_TYPE.APIKEY],
            needs_def_type_name_label=True
        )

        return {
            'create_form': CreateForm(self.req, security_list),
            'edit_form': EditForm(self.req, security_list, prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_internal', 'address', 'security_id', 'pool_size'
    input_optional = ('is_active', 'extra', 'default_query_timeout') + generic_attrs
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_GRAPHQL
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['recv_timeout'] = 250

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict):
        input_dict['pool_size'] = int(input_dict['pool_size'])

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} GraphQL outgoing connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-graphql-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-graphql-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-graphql-delete'
    error_message = 'Could not delete GraphQL outgoing connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password', success_msg='Password updated')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'GraphQL connection')

# ################################################################################################################################
