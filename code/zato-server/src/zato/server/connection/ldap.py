# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from copy import deepcopy
from threading import RLock
from traceback import format_exc

import ldap
from time import time

# Zato
from zato.common import Inactive, PASSWORD_SHADOW
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)


class LDAPFacade(object):
    conn = None
    logger = logger

    def __init__(self, name, host, port, bind_dn, bind_pass=None):
        self.server_uri = "ldap://{}:{}".format(host, port)
	self.name = name

        conn = ldap.initialize(self.server_uri)
        try:
            conn.simple_bind_s(bind_dn, bind_pass)
        except ldap.INVALID_CREDENTIALS:
            pass
        else:
            self.conn = conn

    def ping(self):
        self.logger.debug('About to ping the LDAP connection:[{}] ({})'.format(self.name, self.server_uri))

        start_time = time()
	self.conn.search_s('', ldap.SCOPE_BASE, filterstr='(objectClass=nonsense)', attrlist=[])
        response_time = time() - start_time

        self.logger.debug('Ping OK, pool:[{0}], response_time:[{1:03.4f} s]'.format(self.name, response_time))

        return response_time


class LDAPStore(object):
    """ An object through which services access LDAP connections.
    """
    def __init__(self):
        self.conn_params = {}
        self._lock = RLock()

    def _add(self, params):
        """ Adds one set of params to the list of connection parameters. Must not
        be called without holding onto self._lock
        """
        self.conn_params[params.name] = params

        msg = 'LDAP params added:[{!r}]'

        if logger.isEnabledFor(TRACE1):
            logger.log(TRACE1, msg.format(params))

        elif logger.isEnabledFor(logging.DEBUG):
            params = deepcopy(params)
            params['password'] = PASSWORD_SHADOW
            logger.debug(params)

    def add_params(self, params_list):
        with self._lock:
            for params in params_list:
                self._add(params)

    def get_conn_names(self):
        """ Returns a list of UTF-8 connection names this store contains,
        sorted in ascending order.
        """
        with self._lock:
            return [elem.encode('utf-8') for elem in sorted(self.conn_params)]

    def get(self, name, default=False):
        with self._lock:
            params = self.conn_params[name]
            if params.is_active:
                return LDAPFacade(name, params.host, int(params.port), params.bind_dn, params.get('password'))
            else:
                raise Inactive(params.name)

    def create_edit(self, params, old_name):
        with self._lock:
            if params:
                _name = old_name if old_name else params.name
                ldap = params.get(_name)
                try:
                    if ldap:
                        ldap.close()
                except Exception, e:
                    msg = 'Could not close the LDAP connection [{0}], e [{1}]'.format(params.name, format_exc(e))
                    logger.warn(msg)
                finally:
                    self._add(params)

            if old_name and old_name != params.name:
                del self.conn_params[old_name]

            msg = 'LDAP connection stored, name:[{}], old_name:[{}]'.format(params.name, old_name)
            logger.info(msg)

    def change_password(self, name, password):
        with self._lock:
            self.conn_params[name].password = password
            logger.info('Password updated - LDAP connection [{}]'.format(name))

    def delete(self, name):
        with self._lock:
            del self.conn_params[name]
            logger.info('LDAP connection [{}] deleted'.format(name))
