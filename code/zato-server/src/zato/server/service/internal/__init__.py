# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from contextlib import closing
from traceback import format_exc
from urlparse import parse_qs

# Zato
from zato.common import ZatoException, ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE
from zato.server.service import _get_params, Service

success_code = 0
success = '<error_code>{}</error_code>'.format(success_code)

logger = logging.getLogger(__name__)

class AdminService(Service):
    def __init__(self):
        super(AdminService, self).__init__()
        
        # Whether the responses are to be wrapped in a SOAP message
        self.needs_xml = True
        
    def handle(self, *args, **kwargs):
        raise NotImplementedError("Should be overridden by subclasses.")

class Ping(AdminService):

    def handle(self, *args, **kwargs):
        pass
    
class Ping2(Ping):
    pass

class ChangePasswordBase(AdminService):
    """ A base class for handling the changing of any of the ODB passwords.
    """
    def _handle(self, class_, auth_func, action, name_func=None, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB,
                *args, **kwargs):

        with closing(self.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id', 'password1', 'password2']
                params = _get_params(payload, request_params, 'data.')

                params['id'] = int(params['id'])
                password1 = params.get('password1')
                password2 = params.get('password2')

                if not password1:
                    raise Exception('Password must not be empty')

                if not password2:
                    raise Exception('Password must be repeated')

                if password1 != password2:
                    raise Exception('Passwords need to be the same')

                auth = session.query(class_).\
                    filter(class_.id==params['id']).\
                    one()

                auth_func(auth, password1)

                session.add(auth)
                session.commit()

                if msg_type:
                    name = name_func(auth) if name_func else auth.name

                    params['action'] = action
                    params['name'] = name
                    params['password'] = auth.password
                    params['salt'] = kwargs.get('salt')
                    self.broker_client.send_json(params, msg_type=msg_type)

            except Exception, e:
                msg = "Could not update the password, e=[{e}]".format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
