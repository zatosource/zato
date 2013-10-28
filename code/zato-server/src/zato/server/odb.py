# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from contextlib import closing
from datetime import datetime, timedelta
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Paste
from paste.util.multidict import MultiDict

# Bunch
from bunch import Bunch

# Zato
from zato.common import DEPLOYMENT_STATUS, MISC, ZATO_NONE, ZATO_ODB_POOL_NAME
from zato.common.odb.model import Cluster, DeployedService, DeploymentPackage, \
     DeploymentStatus, HTTPBasicAuth, Server, Service, TechnicalAccount, WSSDefinition
from zato.common.odb.query import channel_amqp, channel_amqp_list, channel_jms_wmq, \
    channel_jms_wmq_list, channel_zmq, channel_zmq_list, def_amqp, def_amqp_list, \
    def_jms_wmq, def_jms_wmq_list, basic_auth_list, http_soap_list, http_soap_security_list, \
    internal_channel_list, job_list, out_amqp, out_amqp_list, out_ftp, out_ftp_list, \
    out_jms_wmq, out_jms_wmq_list, out_sql, out_sql_list, out_zmq, out_zmq_list, tech_acc_list, wss_list
from zato.common.util import current_host, security_def_type, TRACE1
from zato.server.connection.sql import SessionWrapper

logger = logging.getLogger(__name__)

class ODBManager(SessionWrapper):
    """ Manages connections to the server's Operational Database.
    """
    def __init__(self, well_known_data=None, token=None, crypto_manager=None, 
                 server=None, cluster=None, pool=None):
        super(ODBManager, self).__init__()
        self.well_known_data = well_known_data
        self.token = token
        self.crypto_manager = crypto_manager
        self.server = server
        self.cluster = cluster
        self.pool = pool
        
    def fetch_server(self, odb_config):
        """ Fetches the server from the ODB. Also sets the 'cluster' attribute
        to the value pointed to by the server's .cluster attribute.
        """
        if not self.session_initialized:
            self.init_session(ZATO_ODB_POOL_NAME, odb_config, self.pool, False)
            
        try:
            self.server = self._session.query(Server).\
                   filter(Server.token == self.token).\
                   one()
            self.cluster = self.server.cluster
            return self.server
        except Exception:
            msg = 'Could not find the server in the ODB, token:[{0}]'.format(
                self.token)
            logger.error(msg)
            raise
        
    def server_up_down(self, token, status, update_host=False, bind_host=None, bind_port=None):
        """ Updates the information regarding the server is RUNNING or CLEAN_DOWN etc.
        and what host it's running on.
        """
        with closing(self.session()) as session:
            server = session.query(Server).\
                filter(Server.token==token).\
                one()

            server.up_status = status
            server.up_mod_date = datetime.utcnow()
            
            if update_host:
                server.host = current_host()
                server.bind_host = bind_host
                server.bind_port = bind_port
            
            session.add(server)
            session.commit()

    def get_url_security(self, cluster_id, connection=None):
        """ Returns the security configuration of HTTP URLs.
        """

        # What DB class to fetch depending on the string value of the security type.
        sec_type_db_class = {
            'tech_acc': TechnicalAccount,
            'basic_auth': HTTPBasicAuth,
            'wss': WSSDefinition
            }

        result = {}

        query = http_soap_security_list(self._session, cluster_id, connection)
        columns = Bunch()
        
        # So ConfigDict has its data in the format it expects
        for c in query.statement.columns:
            columns[c.name] = None
            
        for item in query.all():
            target = '{}{}{}'.format(item.soap_action, MISC.SEPARATOR, item.url_path)
            
            result[target] = Bunch()
            result[target].is_active = item.is_active
            result[target].transport = item.transport
            result[target].data_format = item.data_format

            if item.security_id:
                result[target].sec_def = Bunch()
                
                # Will raise KeyError if the DB gets somehow misconfigured.
                db_class = sec_type_db_class[item.sec_type]
    
                sec_def = self._session.query(db_class).\
                        filter(db_class.id==item.security_id).\
                        one()

                # Common things first
                result[target].sec_def.name = sec_def.name    
                result[target].sec_def.password = sec_def.password
                result[target].sec_def.sec_type = item.sec_type
    
                if item.sec_type == security_def_type.tech_account:
                    result[target].sec_def.salt = sec_def.salt
                elif item.sec_type == security_def_type.basic_auth:
                    result[target].sec_def.username = sec_def.username
                    result[target].sec_def.password = sec_def.password
                    result[target].sec_def.realm = sec_def.realm
                elif item.sec_type == security_def_type.wss:
                    result[target].sec_def.username = sec_def.username
                    result[target].sec_def.password = sec_def.password
                    result[target].sec_def.password_type = sec_def.password_type
                    result[target].sec_def.reject_empty_nonce_creat = sec_def.reject_empty_nonce_creat
                    result[target].sec_def.reject_stale_tokens = sec_def.reject_stale_tokens
                    result[target].sec_def.reject_expiry_limit = sec_def.reject_expiry_limit
                    result[target].sec_def.nonce_freshness_time = sec_def.nonce_freshness_time
            else:
                result[target].sec_def = ZATO_NONE

        return result, columns

    def add_service(self, name, impl_name, is_internal, deployment_time, details, source_info):
        """ Adds information about the server's service into the ODB.
        """
        try:
            service = Service(None, name, True, impl_name, is_internal, self.cluster)
            self._session.add(service)
            try:
                self._session.commit()
            except IntegrityError, e:
                logger.log(TRACE1, 'IntegrityError (Service), e:[{e}]'.format(e=format_exc(e)))
                self._session.rollback()
                
                service = self._session.query(Service).\
                    join(Cluster, Service.cluster_id==Cluster.id).\
                    filter(Service.name==name).\
                    filter(Cluster.id==self.cluster.id).\
                    one()

            self.add_deployed_service(deployment_time, details, service, source_info)
            
            return service.id, service.is_active, service.slow_threshold

        except Exception, e:
            msg = 'Could not add service, name:[{}], e:[{}]'.format(name, format_exc(e))
            logger.error(msg)
            self._session.rollback()

    def drop_deployed_services(self, server_id):
        """ Removes all the deployed services from a server.
        """
        self._session.query(DeployedService).\
            filter(DeployedService.server_id==server_id).\
            delete()
        self._session.commit()
        
    def add_deployed_service(self, deployment_time, details, service, source_info):
        """ Adds information about the server's deployed service into the ODB.
        """
        try:
            ds = DeployedService(deployment_time, details, self.server, service, 
                source_info.source, source_info.path, source_info.hash, source_info.hash_method)
            self._session.add(ds)
            try:
                self._session.commit()
            except IntegrityError, e:
                
                logger.log(TRACE1, 'IntegrityError (DeployedService), e:[{e}]'.format(e=format_exc(e)))
                self._session.rollback()

                ds = self._session.query(DeployedService).\
                    filter(DeployedService.service_id==service.id).\
                    filter(DeployedService.server_id==self.server.id).\
                    one()
                
                ds.deployment_time = deployment_time
                ds.details = details
                ds.source = source_info.source
                ds.source_path = source_info.path
                ds.source_hash = source_info.hash
                ds.source_hash_method = source_info.hash_method

                self._session.add(ds)                
                self._session.commit()
                
        except Exception, e:
            msg = 'Could not add the DeployedService, e:[{e}]'.format(e=format_exc(e))
            logger.error(msg)
            self._session.rollback()
            
    def is_service_active(self, service_id):
        """ Returns whether the given service is active or not.
        """
        return self._session.query(Service.is_active).\
            filter(Service.id==service_id).\
            one()[0]
            
    def hot_deploy(self, deployment_time, details, payload_name, payload, server_id):
        """ Inserts a hot-deployed data into the DB along with setting the preliminary
        AWAITING_DEPLOYMENT status for each of the servers this server's cluster
        is aware of.
        """
        # Create the deployment package info ..
        dp = DeploymentPackage()
        dp.deployment_time = deployment_time
        dp.details = details
        dp.payload_name = payload_name
        dp.payload = payload
        dp.server_id = server_id
        
        # .. add it to the session ..
        self._session.add(dp)

        # .. for each of the servers in this cluster set the initial status ..
        #servers = self._session.
        servers = self._session.query(Cluster).\
               filter(Cluster.id == self.server.cluster_id).\
               one().servers
        
        for server in servers:
            ds = DeploymentStatus()
            ds.package_id = dp.id
            ds.server_id = server.id
            ds.status = DEPLOYMENT_STATUS.AWAITING_DEPLOYMENT
            ds.status_change_time = datetime.utcnow()
            
            self._session.add(ds)
        
        self._session.commit()
        
        return dp.id

    def _become_cluster_wide(self, cluster, session):
        """ Update all the Cluster's attributes that are related to connector servers.
        """
        cluster.cw_srv_id = self.server.id
        cluster.cw_srv_keep_alive_dt = datetime.utcnow()

        session.add(cluster)
        session.commit()
        
        msg = 'Server id:[{}], name:[{}] is now a connector server for cluster id:[{}], name:[{}]'.format(
            self.server.id, self.server.name, cluster.id, cluster.name)
        logger.info(msg)
        
        return True
    
    def conn_server_past_grace_time(self, cluster, grace_time):
        """ Whether it's already past the grace time the connector server had
        for updating its keep-alive timestamp.
        """
        last_keep_alive = cluster.cw_srv_keep_alive_dt
        max_allowed = last_keep_alive + timedelta(seconds=grace_time)
        now = datetime.utcnow()
        
        msg = 'last_keep_alive:[{}], grace_time:[{}], max_allowed:[{}], now:[{}]'.format(
            last_keep_alive, grace_time, max_allowed, now)
        logger.info(msg)

        # Return True if 'now' is past what it's allowed
        return now > max_allowed

    def become_cluster_wide(self, grace_time):
        """ Makes an attempt for the server to become a connector one, that is,
        the server to start all the connectors.
        """
        with closing(self.session()) as session:
            cluster = session.query(Cluster).\
                with_lockmode('update').\
                filter(Cluster.id == self.server.cluster_id).\
                one()
            
            # No cluster-wide singleton server at all so we made it first
            if not cluster.cw_srv_id:
                return self._become_cluster_wide(cluster, session)
            elif self.conn_server_past_grace_time(cluster, grace_time):
                return self._become_cluster_wide(cluster, session)
            else:
                session.rollback()
                msg = ('Server id:[{}], name:[{}] will not be a connector server for '
                'cluster id:[{}], name:[{}], cluster.cw_srv_id:[{}], cluster.cw_srv_keep_alive_dt:[{}]').format(
                    self.server.id, self.server.name, cluster.id, cluster.name, cluster.cw_srv_id, cluster.cw_srv_keep_alive_dt)
                logger.debug(msg)
            
    def clear_cluster_wide(self):
        """ Invoked when the cluster-wide singleton server is making a clean shutdown, sets
        all the relevant data to NULL in the ODB.
        """
        with closing(self.session()) as session:
            cluster = session.query(Cluster).\
                with_lockmode('update').\
                filter(Cluster.id == self.server.cluster_id).\
                one()
            
            cluster.cw_srv_id = None
            cluster.cw_srv_keep_alive_dt = None
    
            session.add(cluster)
            session.commit()
            
    def add_delivery(self, deployment_time, details, service, source_info):
        """ Adds information about the server's deployed service into the ODB.
        """
        dp = DeliveryPayload
        self._session.add(dp)
        self._session.commit()

# ##############################################################################

    def get_internal_channel_list(self, cluster_id, needs_columns=False):
        """ Returns the list of internal HTTP/SOAP channels, that is, 
        channels pointing to internal services.
        """
        return internal_channel_list(self._session, cluster_id, needs_columns)
    
    def get_http_soap_list(self, cluster_id, connection=None, transport=None, needs_columns=False):
        """ Returns the list of all HTTP/SOAP channels.
        """
        return http_soap_list(self._session, cluster_id, connection, transport, needs_columns)

# ##############################################################################

    def get_job_list(self, cluster_id, needs_columns=False):
        """ Returns a list of jobs defined on the given cluster.
        """
        return job_list(self._session, cluster_id, needs_columns)

# ##############################################################################

    def get_basic_auth_list(self, cluster_id, needs_columns=False):
        """ Returns a list of HTTP Basic Auth definitions existing on the given cluster.
        """
        return basic_auth_list(self._session, cluster_id, needs_columns)

    def get_tech_acc_list(self, cluster_id, needs_columns=False):
        """ Returns a list of technical accounts existing on the given cluster.
        """
        return tech_acc_list(self._session, cluster_id, needs_columns)

    def get_wss_list(self, cluster_id, needs_columns=False):
        """ Returns a list of WS-Security definitions on the given cluster.
        """
        return wss_list(self._session, cluster_id, needs_columns)

# ##############################################################################

    def get_def_amqp(self, cluster_id, def_id):
        """ Returns an AMQP definition's details.
        """
        return def_amqp(self._session, cluster_id, def_id)

    def get_def_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AMQP definitions on the given cluster.
        """
        return def_amqp_list(self._session, cluster_id, needs_columns)

    def get_out_amqp(self, cluster_id, out_id):
        """ Returns an outgoing AMQP connection's details.
        """
        return out_amqp(self._session, cluster_id, out_id)

    def get_out_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing AMQP connections.
        """
        return out_amqp_list(self._session, cluster_id, needs_columns)

    def get_channel_amqp(self, cluster_id, channel_id):
        """ Returns a particular AMQP channel.
        """
        return channel_amqp(self._session, cluster_id, channel_id)

    def get_channel_amqp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of AMQP channels.
        """
        return channel_amqp_list(self._session, cluster_id, needs_columns)

# ##############################################################################

    def get_def_jms_wmq(self, cluster_id, def_id):
        """ Returns an JMS WebSphere MQ definition's details.
        """
        return def_jms_wmq(self._session, cluster_id, def_id)

    def get_def_jms_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of JMS WebSphere MQ definitions on the given cluster.
        """
        return def_jms_wmq_list(self._session, cluster_id, needs_columns)

    def get_out_jms_wmq(self, cluster_id, out_id):
        """ Returns an outgoing JMS WebSphere MQ connection's details.
        """
        return out_jms_wmq(self._session, cluster_id, out_id)

    def get_out_jms_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing JMS WebSphere MQ connections.
        """
        return out_jms_wmq_list(self._session, cluster_id, needs_columns)

    def get_channel_jms_wmq(self, cluster_id, channel_id):
        """ Returns a particular JMS WebSphere MQ channel.
        """
        return channel_jms_wmq(self._session, cluster_id, channel_id)

    def get_channel_jms_wmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of JMS WebSphere MQ channels.
        """
        return channel_jms_wmq_list(self._session, cluster_id, needs_columns)

# ##############################################################################

    def get_out_zmq(self, cluster_id, out_id):
        """ Returns an outgoing ZMQ connection's details.
        """
        return out_zmq(self._session, cluster_id, out_id)

    def get_out_zmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing ZMQ connections.
        """
        return out_zmq_list(self._session, cluster_id, needs_columns)

    def get_channel_zmq(self, cluster_id, channel_id):
        """ Returns a particular ZMQ channel.
        """
        return channel_zmq(self._session, cluster_id, channel_id)

    def get_channel_zmq_list(self, cluster_id, needs_columns=False):
        """ Returns a list of ZMQ channels.
        """
        return channel_zmq_list(self._session, cluster_id, needs_columns)

# ##############################################################################

    def get_out_sql(self, cluster_id, out_id):
        """ Returns an outgoing SQL connection's details.
        """
        return out_sql(self._session, cluster_id, out_id)

    def get_out_sql_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing SQL connections.
        """
        return out_sql_list(self._session, cluster_id, needs_columns)

# ##############################################################################

    def get_out_ftp(self, cluster_id, out_id):
        """ Returns an outgoing FTP connection's details.
        """
        return out_ftp(self._session, cluster_id, out_id)

    def get_out_ftp_list(self, cluster_id, needs_columns=False):
        """ Returns a list of outgoing FTP connections.
        """
        return out_ftp_list(self._session, cluster_id, needs_columns)

# ##############################################################################
