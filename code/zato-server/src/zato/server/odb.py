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
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.orm import joinedload, sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError

# Bunch
from bunch import Bunch

# Zato
from zato.common.odb.model import(ChannelURLDefinition, ChannelURLSecurity,
     Cluster, DeployedService, HTTPBasicAuth, SecurityDefinition, Server, 
     Service, TechnicalAccount, WSSDefinition)
from zato.common.odb.query import(amqp_def_list, basic_auth_list, job_list, 
    tech_acc_list, wss_list)
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
        return self._Session()
    
    def close(self):
        self._session.close()
        
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
            'tech-account': TechnicalAccount,
            'basic_auth': HTTPBasicAuth,
            'wss': WSSDefinition
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
            
            result[url_pattern] = Bunch()
            result[url_pattern].url_type = url_type
            result[url_pattern].sec_def = Bunch()
            result[url_pattern].sec_def.type = sec_def_type            
            
            if sec_def_type == 'tech-account':
                result[url_pattern].sec_def.name = sec_def.name
                result[url_pattern].sec_def.password = sec_def.password
                result[url_pattern].sec_def.salt = sec_def.salt
            elif sec_def_type == 'basic_auth':
                result[url_pattern].sec_def.name = sec_def.name
                result[url_pattern].sec_def.password = sec_def.password
                result[url_pattern].sec_def.domain = sec_def.domain
            elif sec_def_type == 'wss':
                result[url_pattern].sec_def.username = sec_def.username
                result[url_pattern].sec_def.password = sec_def.password
                result[url_pattern].sec_def.password_type = sec_def.password_type
                result[url_pattern].sec_def.reject_empty_nonce_ts = sec_def.reject_empty_nonce_ts
                result[url_pattern].sec_def.reject_stale_username = sec_def.reject_stale_username
                result[url_pattern].sec_def.expiry_limit = sec_def.expiry_limit
                result[url_pattern].sec_def.nonce_freshness = sec_def.nonce_freshness
                
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
            
    def get_job_list(self, cluster_id):
        """ Returns a list of jobs defined on the given cluster .
        """
        return job_list(self._session, cluster_id)
    
    def get_basic_auth_list(self, cluster_id):
        """ Returns a list of HTTP Basic Auth definitions existing on the given cluster .
        """
        return basic_auth_list(self._session, cluster_id)
    
    def get_tech_acc_list(self, cluster_id):
        """ Returns a list of technical accounts existing on the given cluster .
        """
        return tech_acc_list(self._session, cluster_id)
    
    def get_wss_list(self, cluster_id):
        """ Returns a list of WS-Security definitions on the given cluster .
        """
        return wss_list(self._session, cluster_id)
    
    def get_amqp_def_list(self, cluster_id):
        """ Returns a list of AMQP definitions on the given cluster .
        """
        return amqp_def_list(self._session, cluster_id)
    