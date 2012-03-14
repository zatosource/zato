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
from zato.common import zato_path, ZatoException, ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE
from zato.server.service import Service

success_code = 0
success = "<error_code>%s</error_code>" % success_code

# Need to use such a constant because we can sometimes be interested in setting
# default values which evaluate to boolean False.
# TODO: Move it to zatocommon.
ZATO_NO_DEFAULT_VALUE = "ZATO_NO_DEFAULT_VALUE"

logger = logging.getLogger("zato.server.service.internal")

def _get_params(payload, request_params, path_prefix="", default_value=ZATO_NO_DEFAULT_VALUE,
                force_type=None, force_type_params=[], use_text=True):
    """ Gets all requested parameters from a message. Will raise an exception
    if any is missing.
    """
    params = {}
    for param in request_params:

        elem = zato_path(path_prefix + param, True).get_from(payload)

        if use_text:
            value = elem.text # We are interested in the text the elem contains ..
        else:
            return elem # .. or in the elem itself.

        # Use a default value if an element is empty and we're allowed to
        # substitute its (empty) value with the default one.
        if default_value != ZATO_NO_DEFAULT_VALUE and not value:
            value = default_value
        else:
            if value is not None:
                value = unicode(value)

        # Should the value be of a specific type?
        if force_type and param in force_type_params:
            if force_type == bool:
                # TODO: Those should be stored in the app context
                if value.lower() in("0", "false"):
                    value = False
                elif value.lower() in("1", "true"):
                    value = True
                else:
                    msg = "Don't know how to convert param [%s], value [%s], into a bool." % (
                        param, value)
                    logger.error(msg)
                    raise ZatoException(msg)
            else:
                value = force_type(value)

        params[param] = value

    return params

def _parse_extra_params(payload):
    """ Turns a query string with extra parameters into a dictionary.
    """
    extra_dict = {}

    # Extra parameters are not mandatory.
    if zato_path("pool.extra_list").get_from(payload) is not None:
        for extra_elem in payload.pool.extra_list.extra:

            extra_elem_dict = parse_qs(unicode(extra_elem), True)
            param_name, param_value = extra_elem_dict.items()[0]
            param_name = str(param_name)
            param_value = param_value[0]

            if not param_value:
                msg = "Extra parameter [%s] has no value" % param_name
                logger.error(msg)
                raise ZatoException(msg)

            if param_name in extra_dict:
                msg = "Extra parameter [%s] specified more than once" % param_name
                logger.error(msg)
                raise ZatoException(msg)

            extra_dict[param_name] = param_value

    logger.debug("Returning extra parameters [%s]" % extra_dict)

    return extra_dict

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
