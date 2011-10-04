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
from contextlib import closing
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.orm import joinedload, sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.odb.model import ChannelURLDefinition, ChannelURLSecurity, \
     Cluster, DeployedService, SecurityDefinition, Server, Service, \
     TechnicalAccount
from zato.server.pool.sql import ODBConnectionPool

logger = logging.getLogger(__name__)

ZATO_ODB_POOL_NAME = 'ZATO_ODB'

class ODBManager(object):
    """ Manages connections to the server's Operational Database.
    """
    def __init__(self, well_known_data=None, odb_data=None, odb_config=None,
                 crypto_manager=None, pool=None, server=None, cluster=None):
        self.well_known_data = well_known_data
        self.odb_data = odb_data
        self.odb_config = odb_data
        self.crypto_manager = crypto_manager
        self.pool = pool
        self.server = server
        self.cluster = cluster
        
    def session(self):
        with closing(self._Session()) as session:
            return session
        
    '''
    def query(self, *args, **kwargs):
        return self._session.query(*args, **kwargs)
    
    def add(self, *args, **kwargs):
        return self._session.add(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        return self._session.delete(*args, **kwargs)
    
    def commit(self, *args, **kwargs):
        return self._session.commit(*args, **kwargs)
    
    def rollback(self, *args, **kwargs):
        return self._session.rollback(*args, **kwargs)
    '''
        
    def fetch_server(self):
        """ Fetches the server from the ODB. Also sets the 'cluster' attribute
        to the value pointed to by the server's .cluster attribute.
        """
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
        
        self._Session = scoped_session(sessionmaker(bind=engine))
        self._session = self._Session()
        
        try:
            self.server = self._session.query(Server).\
                   filter(Server.odb_token == self.odb_data['token']).\
                   one()
            self.cluster = self.server.cluster
            return self.server
        except Exception, e:
            msg = 'Could not find the server in the ODB, token=[{0}]'.format(
                self.odb_data['token'])
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
        
        sec_def_q = self._session.query(SecurityDefinition.id, 
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
            
            sec_def = self._session.query(db_class).\
                    filter(db_class.security_def_id==sec_def_id).\
                    one()
            
            result[url_pattern] = {'sec_def':sec_def, 'sec_def_type':sec_def_type,
                                   'url_type':url_type}
            
        return result
    
    def add_service(self, name, impl_name, is_internal, deployment_time, details):
        """ Adds information about the server's service into the ODB. 
        """
        try:
            service = Service(None, name, impl_name, is_internal, True, self.cluster)
            self._session.add(service)
            try:
                self._session.commit()
            except IntegrityError, e:
                logger.debug('IntegrityError (Service), e=[{e}]'.format(e=format_exc(e)))
                self._session.rollback()

                # We know the service exists in the ODB so we can now add 
                # information about its deployment status.
                service = self._session.query(Service).\
                    filter(Service.name==name).\
                    filter(Cluster.id==self.cluster.id).\
                    one()
                self.add_deployed_service(deployment_time, details, service)
                
        except Exception, e:
            msg = 'Could not add the Service, e=[{e}]'.format(e=format_exc(e))
            logger.error(msg)
            self._session.rollback()
            
    def add_deployed_service(self, deployment_time, details, service):
        """ Adds information about the server's deployed service into the ODB. 
        """
        try:
            service = DeployedService(deployment_time, details, self.server, service)
            self._session.add(service)
            try:
                self._session.commit()
            except IntegrityError, e:
                logger.debug('IntegrityError (DeployedService), e=[{e}]'.format(e=format_exc(e)))
                self._session.rollback()
        except Exception, e:
            msg = 'Could not add the DeployedService, e=[{e}]'.format(e=format_exc(e))
            logger.error(msg)
            self._session.rollback()