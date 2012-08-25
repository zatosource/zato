# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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
from threading import RLock
from traceback import format_exc

# pyfilesystem
from fs.ftpfs import FTPFS, _GLOBAL_DEFAULT_TIMEOUT

# Zato
from zato.common import ZatoException

logger = logging.getLogger(__name__)

class FTPFacade(FTPFS):
    """ A thin wrapper around fs's FTPFS so it looks like the other Zato connection objects.
    """
    def conn(self):
        return self

class FTPStore(object):
    """ An object through which services access FTP connections.
    """
    def __init__(self):
        self.conn_params = {}
        self._lock = RLock()
        
    def _add(self, params):
        """ Adds one set of params to the list of connection parameters. Must not
        be called without holding onto self._lock
        """
        self.conn_params[params.name] = params
        
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
    
    def get(self, name):
        with self._lock:
            params = self.conn_params[name]
            if params.is_active:
                timeout = params.timeout if params.timeout else _GLOBAL_DEFAULT_TIMEOUT
                return FTPFacade(params.host, params.user, params.get('password'), params.acct, timeout, int(params.port), params.dircache)
            else:
                raise ZatoException('FTP connection [{0}] is not active'.format(params.name))
        
    def create_edit(self, params, old_name):
        with self._lock:
            if params:
                _name = old_name if old_name else params.name
                ftp = params.get(_name)
                try:
                    if ftp:
                        ftp.close()
                except Exception, e:
                    msg = 'Could not close the FTP connection [{0}], e [{1}]'.format(params.name, format_exc(e))
                    logger.warn(msg)
                finally:
                    self._add(params)
                        
            if old_name:
                del self.conn_params[old_name]
                msg = 'FTP connection updated, name:[{}], old_name:[{}]'.format(params.name, old_name)
            else:
                msg = 'FTP connection created, name:[{}]'.format(params.name)
                
            logger.debug(msg)
                
    def change_password(self, name, password):
        with self._lock:
            self.conn_params[name].password = password
            logger.debug('Password updated - FTP connection [{}]'.format(name))

    def delete(self, name):
        with self._lock:
            del self.conn_params[name]
            logger.debug('FTP connection [{}] deleted'.format(name))
