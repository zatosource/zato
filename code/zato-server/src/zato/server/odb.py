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

# Zato
from zato.server.pool.sql import ODBConnectionPool

ZATO_ODB_POOL_NAME = 'ZATO_ODB'

class ODBManager(object):
    """ Manages connections to the server's Operational Database.
    """
    def __init__(self, well_known_data=None, odb_data=None, odb_config=None,
                 crypto_manager=None, pool=None):
        self.well_known_data = well_known_data
        self.odb_data = odb_data
        self.odb_config = odb_data
        self.crypto_manager = crypto_manager
        self.pool = pool
        
    def connect(self):
        if not self.pool:
            if not self.odb_config:
                odb_data = dict(self.odb_data.items())
                
                if not odb_data['extra']:
                    odb_data['extra'] = {}
                    
                odb_data['pool_size'] = int(odb_data['pool_size'])
                    
                self.odb_config = {ZATO_ODB_POOL_NAME: odb_data}
                
            self.pool = ODBConnectionPool(self.odb_config, True, self.crypto_manager)
            self.pool.init()
            self.pool.get(ZATO_ODB_POOL_NAME)
            
        self.pool.ping({'pool_name': ZATO_ODB_POOL_NAME})