# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from time import time

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.api import EMAIL as EMail_Common, Zato_None
from zato.common.broker_message import EMAIL
from zato.common.odb.model import IMAP
from zato.common.odb.query import email_imap_list
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_
    from zato.server.service import Service

# ################################################################################################################################

elem = 'email_imap'
model = IMAP
label = 'an IMAP connection'
get_list_docs = 'IMAP connections'
broker_message = EMAIL
broker_message_prefix = 'IMAP_'
list_func = email_imap_list
create_edit_input_optional_extra = ['server_type', AsIs('tenant_id'), AsIs('client_id'), 'filter_criteria']
output_optional_extra = ['server_type', 'server_type_human', AsIs('tenant_id'), AsIs('client_id'), 'filter_criteria']

# ################################################################################################################################

def instance_hook(service:'Service', input:'Bunch', instance:'any_', attrs:'any_'):
    if attrs.is_create_edit:
        instance.username = input.username or '' # So it's not stored as None/NULL
        instance.host = input.host or Zato_None

# ################################################################################################################################

def response_hook(service:'Service', input:'Bunch', instance:'any_', attrs:'any_', hook_type:'str'):

    if hook_type == 'get_list':

        for item in service.response.payload:

            # This may be None ..
            server_type = item.get('server_type')

            # .. in which case we can assume a default one ..
            if not server_type:
                item.server_type = EMail_Common.IMAP.ServerType.Generic

            # .. and now we can obtain a human-friendly name.
            item.server_type_human = EMail_Common.IMAP.ServerTypeHuman[item.server_type]

            # This should be cleared out in case there is no user-set value
            if item.host == Zato_None:
                item.host = ''

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = IMAP.name,

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

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an IMAP connection.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_email_imap_change_password_request'
        response_elem = 'zato_email_imap_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(IMAP, _auth, EMAIL.IMAP_CHANGE_PASSWORD.value)

# ################################################################################################################################

class Ping(AdminService):
    """ Pings an IMAP connection to check its configuration.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_email_imap_ping_request'
        response_elem = 'zato_email_imap_ping_response'
        input_required = 'id'
        output_optional = 'info'

    def handle(self):

        with closing(self.odb.session()) as session:
            item = session.query(IMAP).filter_by(id=self.request.input.id).one()

        start_time = time()

        if not self.email:
            self.response.payload.info = 'Could not ping connection; is component_enabled.email set to True in server.conf?'
        else:
            self.email.imap.get(item.name, True).conn.ping()
            response_time = time() - start_time

            self.response.payload.info = 'Ping NOOP submitted, took:`{0:03.4f} s`, check server logs for details.'.format(
                response_time)

# ################################################################################################################################
