# -# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from time import time

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.api import SMTPMessage
from zato.common.broker_message import EMAIL
from zato.common.odb.model import SMTP
from zato.common.version import get_version
from zato.common.odb.query import email_smtp_list
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################

version = get_version()

# ################################################################################################################################

elem = 'email_smtp'
model = SMTP
label = 'an SMTP connection'
get_list_docs = 'SMTP connections'
broker_message = EMAIL
broker_message_prefix = 'SMTP_'
list_func = email_smtp_list

# ################################################################################################################################

def instance_hook(service, input, instance, attrs):
    if attrs.is_create_edit:
        instance.username = input.username or '' # So it's not stored as None/NULL

# ################################################################################################################################

@add_metaclass(GetListMeta)
class GetList(AdminService):
    _filter_by = SMTP.name,

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
    """ Changes the password of an SMTP connection.
    """
    password_required = False

    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_email_smtp_change_password_request'
        response_elem = 'zato_email_smtp_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(SMTP, _auth, EMAIL.SMTP_CHANGE_PASSWORD.value)

# ################################################################################################################################

class Ping(AdminService):
    """ Pings an SMTP connection to check its configuration.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_email_smtp_ping_request'
        response_elem = 'zato_email_smtp_ping_response'
        input_required = ('id',)
        output_required = ('info',)

    def handle(self):

        with closing(self.odb.session()) as session:
            item = session.query(SMTP).filter_by(id=self.request.input.id).one()

        msg = SMTPMessage()
        msg.from_ = item.ping_address
        msg.to = item.ping_address
        msg.cc = item.ping_address
        msg.bcc = item.ping_address
        msg.subject = 'Zato SMTP ping (Α Β Γ Δ Ε Ζ Η)'
        msg.headers['Charset'] = 'utf-8'

        msg.body = 'Hello from {}\nUTF-8 test: Α Β Γ Δ Ε Ζ Η'.format(version).encode('utf-8')

        msg.attach('utf-8.txt', 'Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω'.encode('utf-8'))
        msg.attach('ascii.txt', 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z')

        start_time = time()
        self.email.smtp.get(item.name, True).conn.send(msg)
        response_time = time() - start_time

        self.response.payload.info = 'Ping submitted, took:`{0:03.4f} s`, check server logs for details.'.format(response_time)

# ################################################################################################################################
