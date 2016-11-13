# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import TLSChannelSecurity
from zato.common.odb.query import tls_channel_sec_list
from zato.common.util import parse_tls_channel_security_definition
from zato.server.service.internal import AdminService
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

elem = 'security_tls_channel'
model = TLSChannelSecurity
label = 'a TLS channel security definition'
broker_message = SECURITY
broker_message_prefix = 'TLS_CHANNEL_SEC_'
list_func = tls_channel_sec_list
create_edit_input_required_extra = ['value']
skip_input_params = ['sec_type']

def instance_hook(self, input, instance, attrs):

    # Parsing returns a generator which we exhaust be converting it into a list.
    # An exception is raised on any parsing error.
    list(parse_tls_channel_security_definition(self.request.input.value))

    # So that username, an artificial and inherited field, is not an empty string.
    instance.username = input.username = input.name

def broker_message_hook(self, input, instance, attrs, service_type):
    input.sec_type = SEC_DEF_TYPE.TLS_CHANNEL_SEC

class GetList(AdminService):
    _filter_by = TLSChannelSecurity.name,
    __metaclass__ = GetListMeta

class Delete(AdminService):
    __metaclass__ = DeleteMeta

class Create(AdminService):
    __metaclass__ = CreateEditMeta

class Edit(AdminService):
    __metaclass__ = CreateEditMeta
