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
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError

# Bunch
from bunch import SimpleBunch

# Zato
from zato.common import ZATO_NONE
from zato.common.odb.model import(Cluster, DeployedService, HTTPBasicAuth, Server, 
    Service, TechnicalAccount, WSSDefinition)
from zato.common.odb.query import(channel_amqp, channel_amqp_list, channel_jms_wmq,
    channel_jms_wmq_list, channel_zmq, channel_zmq_list, def_amqp, def_amqp_list, 
    def_jms_wmq, def_jms_wmq_list, basic_auth_list,  http_soap_list, http_soap_security_list, 
    internal_channel_list, job_list,  out_amqp, out_amqp_list, out_ftp, out_ftp_list, out_jms_wmq, 
    out_jms_wmq_list, out_s3, out_s3_list, out_zmq, out_zmq_list, tech_acc_list, wss_list)
from zato.common.util import security_def_type
from zato.server.pool.sql import ODBConnectionPool

logger = logging.getLogger(__name__)

ZATO_ODB_POOL_NAME = 'ZATO_ODB'

class ODBManager(object):
    """ Manages connections to the server's Operational Database.
    """
    def __init__(self, well_known_data=None, odb_data=None, odb_config=None,
                 crypto_manager=None, pool=None, server=None, cluster=None,
                 init=True):
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
            'tech_acc': TechnicalAccount,
            'basic_auth': HTTPBasicAuth,
            'wss': WSSDefinition
            }

        result = {}

        query = http_soap_security_list(self._session, server.cluster_id)
        columns = SimpleBunch()
        
        # So ConfigDict has its data in the format it expects
        for c in query.statement.columns:
            columns[c.name] = None
            
        for item in query.all():
            
            result[item.url_path] = SimpleBunch()
            result[item.url_path].transport = item.transport
            result[item.url_path].sec_def = SimpleBunch()

            if item.security_id:
                result[item.url_path].sec_def = SimpleBunch()
                result[item.url_path].sec_def.type = item.sec_type
                
                # Will raise KeyError if the DB gets somehow misconfigured.
                db_class = sec_type_db_class[item.sec_type]
    
                sec_def = self._session.query(db_class).\
                        filter(db_class.id==item.security_id).\
                        one()

                # Common things first
                result[item.url_path].sec_def.name = sec_def.name    
                result[item.url_path].sec_def.password = sec_def.password
    
                if item.sec_type == security_def_type.tech_account:
                    result[item.url_path].sec_def.salt = sec_def.salt
                elif item.sec_type == security_def_type.basic_auth:
                    result[item.url_path].sec_def.password = sec_def.password
                    result[item.url_path].sec_def.realm = sec_def.realm
                elif item.sec_type == security_def_type.wss:
                    result[item.url_path].sec_def.username = sec_def.username
                    result[item.url_path].sec_def.password = sec_def.password
                    result[item.url_path].sec_def.password_type = sec_def.password_type
                    result[item.url_path].sec_def.reject_empty_nonce_creat = sec_def.reject_empty_nonce_creat
                    result[item.url_path].sec_def.reject_stale_tokens = sec_def.reject_stale_tokens
                    result[item.url_path].sec_def.reject_expiry_limit = sec_def.reject_expiry_limit
                    result[item.url_path].sec_def.nonce_freshness_time = sec_def.nonce_freshness_time
            else:
                result[item.url_path].sec_def = ZATO_NONE

        return result, columns

    def add_service(self, name, impl_name, is_internal, deployment_time, details):
        """ Adds information about the server's service into the ODB.
        """
        try:
            service = Service(None, name, True, impl_name, is_internal, self.cluster)
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


# ##############################################################################

    def get_internal_channel_list(self, cluster_id, needs_columns=False):
        """ Returns the list of internal HTTP/SOAP channels, that is, 
        channels pointing to internal services.
        """
        return internal_channel_list(self._session, cluster_id, needs_columns)
    
    def get_http_soap_list(self, cluster_id, connection=None, transport=None):
        """ Returns the list of all HTTP/SOAP channels.
        """
        return http_soap_list(self._session, cluster_id, connection, transport)

# ##############################################################################

    def get_job_list(self, cluster_id, needs_columns=False):
        """ Returns a list of jobs defined on the given cluster.
        """
        return job_list(self._session, cluster_id)

# ##############################################################################

    def get_basic_auth_list(self, cluster_id, needs_columns=False):
        """ Returns a list of HTTP Basic Auth definitions existing on the given cluster.
        """
        return basic_auth_list(self._session, cluster_id)

    def get_tech_acc_list(self, cluster_id, needs_columns=False):
        """ Returns a list of technical accounts existing on the given cluster.
        """
        return tech_acc_list(self._session, cluster_id, needs_columns)

    def get_wss_list(self, cluster_id, needs_columns=False):
        """ Returns a list of WS-Security definitions on the given cluster.
        """
        return wss_list(self._session, cluster_id, needs_columns)

# ##############################################################################

    def get_def_amqp(self, cluster_id, def_id, needs_columns=False):
        """ Returns an AMQP definition's details.
        """
        return def_amqp(self._session, cluster_id, def_id)

    def get_def_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AMQP definitions on the given cluster.
        """
        return def_amqp_list(self._session, cluster_id)

    def get_out_amqp(self, cluster_id, out_id, needs_columns=False):
        """ Returns an outgoing AMQP connection's details.
        """
        return out_amqp(self._session, cluster_id, out_id)

    def get_out_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing AMQP connections.
        """
        return out_amqp_list(self._session, cluster_id, needs_columns)

    def get_channel_amqp(self, cluster_id, channel_id, needs_columns=False):
        """ Returns a particular AMQP channel.
        """
        return channel_amqp(self._session, cluster_id, channel_id)

    def get_channel_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AMQP channels.
        """
        return channel_amqp_list(self._session, cluster_id)

# ##############################################################################

    def get_def_jms_wmq(self, cluster_id, def_id, needs_columns=False):
        """ Returns an JMS WebSphere MQ definition's details.
        """
        return def_jms_wmq(self._session, cluster_id, def_id)

    def get_def_jms_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of JMS WebSphere MQ definitions on the given cluster.
        """
        return def_jms_wmq_list(self._session, cluster_id)

    def get_out_jms_wmq(self, cluster_id, out_id, needs_columns=False):
        """ Returns an outgoing JMS WebSphere MQ connection's details.
        """
        return out_jms_wmq(self._session, cluster_id, out_id)

    def get_out_jms_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing JMS WebSphere MQ connections.
        """
        return out_jms_wmq_list(self._session, cluster_id, needs_columns)

    def get_channel_jms_wmq(self, cluster_id, channel_id, needs_columns=False):
        """ Returns a particular JMS WebSphere MQ channel.
        """
        return channel_jms_wmq(self._session, cluster_id, channel_id)

    def get_channel_jms_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of JMS WebSphere MQ channels.
        """
        return channel_jms_wmq_list(self._session, cluster_id)

# ##############################################################################

    def get_out_zmq(self, cluster_id, out_id, needs_columns=False):
        """ Returns an outgoing ZMQ connection's details.
        """
        return out_zmq(self._session, cluster_id, out_id)

    def get_out_zmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing ZMQ connections.
        """
        return out_zmq_list(self._session, cluster_id, needs_columns)

    def get_channel_zmq(self, cluster_id, channel_id, needs_columns=False):
        """ Returns a particular ZMQ channel.
        """
        return channel_zmq(self._session, cluster_id, channel_id)

    def get_channel_zmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of ZMQ channels.
        """
        return channel_zmq_list(self._session, cluster_id)

# ##############################################################################

    def get_out_s3(self, cluster_id, out_id, needs_columns=False):
        """ Returns an outgoing S3 connection's details.
        """
        return out_s3(self._session, cluster_id, out_id)

    def get_out_s3_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing S3 connections.
        """
        return out_s3_list(self._session, cluster_id, needs_columns)

# ##############################################################################

    def get_out_ftp(self, cluster_id, out_id, needs_columns=False):
        """ Returns an outgoing FTP connection's details.
        """
        return out_ftp(self._session, cluster_id, out_id, needs_columns)

    def get_out_ftp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing FTP connections.
        """
        return out_ftp_list(self._session, cluster_id, needs_columns)

# ##############################################################################