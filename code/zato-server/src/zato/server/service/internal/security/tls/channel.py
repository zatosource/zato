# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import TLSChannelSecurity
from zato.common.odb.query import tls_channel_sec_list
from zato.common.util.api import parse_tls_channel_security_definition
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_tls_channel'
model = TLSChannelSecurity
label = 'a TLS channel security definition'
get_list_docs = 'TLS channel security definitions'
broker_message = SECURITY
broker_message_prefix = 'TLS_CHANNEL_SEC_'
list_func = tls_channel_sec_list
create_edit_input_required_extra = ['value']
skip_input_params = ['sec_type']

# ################################################################################################################################

def instance_hook(self, input, instance, attrs):

    if attrs.is_create_edit:

        # Parsing returns a generator which we exhaust be converting it into a list.
        # An exception is raised on any parsing error.
        list(parse_tls_channel_security_definition(self.request.input.value))

        # So that username, an artificial and inherited field, is not an empty string.
        instance.username = input.username = input.name
        instance.value = (input.get('value') or '').encode('utf8')

# ################################################################################################################################

def broker_message_hook(self, input, instance, attrs, service_type):
    input.sec_type = SEC_DEF_TYPE.TLS_CHANNEL_SEC

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = TLSChannelSecurity.name,

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Create(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(CreateEditMeta)
class Edit(AdminService):
    pass

# ################################################################################################################################

@add_metaclass(DeleteMeta)
class Delete(AdminService):
    pass

# ################################################################################################################################
