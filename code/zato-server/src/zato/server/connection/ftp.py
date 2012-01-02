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

# stdlib
import logging
from threading import RLock
from traceback import format_exc

# pyfilesystem
from fs.ftpfs import FTPFS, _GLOBAL_DEFAULT_TIMEOUT

# Zato
from zato.common import ZatoException

logger = logging.getLogger(__name__)

class FTPFacade(object):
    """ An object through which services access FTP resources.
    """
    def __init__(self, conn_params={}):
        self.conn_params = conn_params
        self._lock = RLock()
    
    def get(self, name):
        with self._lock:
            params = self.conn_params[name]
            if params.is_active:
                if params.get('passwd'):
                    password = params.get('passwd')
                else:
                    password = params.get('password')
                timeout = params.timeout if params.timeout else _GLOBAL_DEFAULT_TIMEOUT
                return FTPFS(params.host, params.user, password, params.acct, timeout, int(params.port), params.dircache)
            else:
                raise ZatoException('FTP connection [{0}] is not active'.format(params.name))
        
    def update(self, params, old_name):
        with self._lock:
            if params:
                _name = old_name if old_name else params.name
                ftp = params.get(_name)
                try:
                    if ftp:
                        ftp.close()
                except Exception, e:
                    msg = 'Could not close the FTP connection [{0}], e [{1}]'.format(
                        params.name, format_exc(e))
                finally:
                    self.conn_params[params.name] = params
                        
            if old_name:
                del self.conn_params[old_name]