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

# SQLAlchemy
from sqlalchemy.orm import joinedload, sessionmaker

# Zato
from zato.common.odb.model import ChannelURLDefinition, ChannelURLSecurity, \
     Cluster, SecurityDefinition, Server, TechnicalAccount
from zato.server.pool.sql import ODBConnectionPool

logger = logging.getLogger(__name__)

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
        
    def fetch_server(self):
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
        engine = self.pool.get(ZATO_ODB_POOL_NAME)
        
        Session = sessionmaker(bind=engine)
        self.session = Session()
        
        try:
            return self.session.query(Server).filter(Server.odb_token == self.odb_data['token']).one()
        except Exception, e:
            msg = 'Could not find the server in the ODB'
            logger.error(msg)
            raise
        
    def get_url_security(self, server):
        """ Returns the security configuration of HTTP URLs.
        """
        
        # What DB class to fetch depending on the string value of the security type.
        sec_type_db_class = {
            'tech-account': TechnicalAccount
            }
        
        result = {}
        
        sec_def_q = self.session.query(SecurityDefinition.id, 
                            SecurityDefinition.security_def_type, 
                            ChannelURLDefinition.url_pattern,
                            ChannelURLDefinition.url_type).\
               filter(SecurityDefinition.id==ChannelURLSecurity.security_def_id).\
               filter(ChannelURLSecurity.channel_url_def_id==ChannelURLDefinition.id).\
               filter(ChannelURLDefinition.cluster_id==Cluster.id).\
               filter(Cluster.id==server.cluster_id).\
               all()
        
        for sec_def_id, sec_def_type, url_pattern, url_type in sec_def_q:
            
            # Will raise KeyError if the DB gets somehow misconfigured.
            db_class = sec_type_db_class[sec_def_type]
            
            sec_def = self.session.query(db_class).\
                    filter(db_class.security_def_id==sec_def_id).\
                    one()
            
            result[url_pattern] = {'sec_def':sec_def, 'sec_def_type':sec_def_type,
                                   'url_type':url_type}
            
        return result