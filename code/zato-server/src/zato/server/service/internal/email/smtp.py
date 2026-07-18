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
from zato.server.service import Boolean
from zato.server.service.internal import AdminService, ChangePasswordBase
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
create_edit_input_optional_extra = [Boolean('needs_tls_verify'), 'ca_certs_path', 'helo_hostname', 'from_address']
output_optional_extra = [Boolean('needs_tls_verify'), 'ca_certs_path', 'helo_hostname', 'from_address']

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

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        return self._handle(SMTP, _auth, EMAIL.SMTP_CHANGE_PASSWORD.value)

# ################################################################################################################################

class Ping(AdminService):
    """ Pings an SMTP connection to check its configuration.
    """
    input = 'id',
    output = 'info',

    def handle(self):

        with closing(self.odb.session()) as session:
            item = session.query(SMTP).filter_by(id=self.request.input.id).one()

        conn = self.email.smtp.get(item.name, True).conn

        # Check the connection at the protocol level first, without sending any message ..
        start_time = time()
        server_response = conn.ping()
        response_time = time() - start_time

        info = 'Ping OK, took:`{0:03.4f} s`, server responded with:\n{1}'.format(response_time, server_response)

        # .. and follow up with an actual test message, but only if there is an address to send it to.
        if item.ping_address:

            # The connection's own From address takes precedence, with the ping address as the default
            from_address = conn.config.from_address
            if not from_address:
                from_address = item.ping_address

            msg = SMTPMessage()
            msg.from_ = from_address
            msg.to = item.ping_address
            msg.subject = 'Zato SMTP ping (Α Β Γ Δ Ε Ζ Η)'
            msg.headers['Charset'] = 'utf-8'

            msg.body = f'Hello from {version}\nUTF-8 test: Α Β Γ Δ Ε Ζ Η'.encode('utf-8')

            msg.attach('utf-8.txt', 'Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω'.encode('utf-8'))
            msg.attach('ascii.txt', 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z')

            is_sent = conn.send(msg)

            if is_sent:
                info += f'\nTest message sent to `{item.ping_address}`, check server logs for details.'
            else:
                info += f'\nTest message to `{item.ping_address}` could not be sent, check server logs for details.'

        self.response.payload.info = info

# ################################################################################################################################
