# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from time import time

# Zato
from zato.common.broker_message import EMAIL
from zato.common.odb.model import IMAP
from zato.common.odb.query import email_imap_list
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

elem = 'email_imap'
model = IMAP
label = 'an IMAP connection'
get_list_docs = 'IMAP connections'
broker_message = EMAIL
broker_message_prefix = 'IMAP_'
list_func = email_imap_list

# ################################################################################################################################

def instance_hook(service, input, instance, attrs):
    if attrs.is_create_edit:
        instance.username = input.username or '' # So it's not stored as None/NULL

# ################################################################################################################################

class GetList(AdminService):
    _filter_by = IMAP.name,
    __metaclass__ = GetListMeta

# ################################################################################################################################

class Create(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Edit(AdminService):
    __metaclass__ = CreateEditMeta

# ################################################################################################################################

class Delete(AdminService):
    __metaclass__ = DeleteMeta

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

    class SimpleIO(AdminSIO):
        request_elem = 'zato_email_imap_ping_request'
        response_elem = 'zato_email_imap_ping_response'
        input_required = ('id',)
        output_required = ('info',)

    def handle(self):

        with closing(self.odb.session()) as session:
            item = session.query(IMAP).filter_by(id=self.request.input.id).one()

        start_time = time()
        self.email.imap.get(item.name, True).conn.ping()
        response_time = time() - start_time

        self.response.payload.info = 'Ping NOOP submitted, took:`{0:03.4f} s`, check server logs for details.'.format(
            response_time)

# ################################################################################################################################
