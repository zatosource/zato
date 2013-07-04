# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from datetime import datetime
from traceback import format_exc

# Bunch
from bunch import Bunch

# Zato
from zato.common import ZatoException
from zato.common.odb.model import Cluster, Server
from zato.server.service.internal import AdminService, AdminSIO

class ClusterWideSingletonKeepAlive(AdminService):
    """ Makes all the other servers know that this particular singleton, the one that
    manages the connectors and scheduler jobs, is indeed still alive.
    """
    def handle(self):
        s1, s2 = self.request.payload.split(';')
        server_id = int(s1.split(':')[1])
        cluster_id = int(s2.split(':')[1])
        
        with closing(self.odb.session()) as session:
            cluster = session.query(Cluster).\
                with_lockmode('update').\
                filter(Cluster.id == cluster_id).\
                one()
            
            server = session.query(Server).\
                filter(Server.id == server_id).\
                one()
            
            cluster.cw_srv_keep_alive_dt = datetime.utcnow()
            session.add(cluster)
            session.commit()

            msg = 'Cluster-wide singleton keep-alive OK, server id:[{}], name:[{}] '.format(server.id, server.name)
            self.logger.info(msg)

class EnsureClusterWideSingleton(AdminService):
    """ Initializes connectors and scheduler jobs.
    """
    def handle(self):
        if self.server.singleton_server:
            if self.server.singleton_server.is_cluster_wide:
                msg = 'Ignoring event, cid:[{}], server id:[{}], name:[{}], singleton is already cluster-wide'.format(
                    self.cid, self.server.id, self.server.name)
                self.logger.debug(msg)
            else:
                if self.server.singleton_server.become_cluster_wide(
                    self.server.connector_server_keep_alive_job_time, self.server.connector_server_grace_time,
                        self.server.id, self.server.cluster_id, False):
                    
                    self.server.singleton_server.scheduler.delete(Bunch(name='zato.server.ensure-cluster-wide-singleton'))
                    self.server.init_connectors()
                else:
                    msg = 'Not becoming a cluster-wide singleton, cid:[{}], server id:[{}], name:[{}]'.format(
                        self.cid, self.server.id, self.server.name)
                    self.logger.info(msg)
        else:
            msg = 'Ignoring event, cid:[{}], server id:[{}], name:[{}] has no singleton attached'.format(self.cid, self.server.id, self.server.name)
            self.logger.debug(msg)


class Edit(AdminService):
    """ Updates a server.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_edit_request'
        response_elem = 'zato_server_edit_response'
        input_required = ('id', 'name')
        output_required = ('id', 'cluster_id', 'name', 'host')
        output_optional = ('bind_host', 'bind_port', 'last_join_status', 
            'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date')

    def handle(self):
        with closing(self.odb.session()) as session:
            existing_one = session.query(Server).\
                filter(Server.id!=self.request.input.id).\
                filter(Server.name==self.request.input.name).\
                first()

            if existing_one:
                raise Exception('A server of that name [{0}] already exists on this cluster'.format(self.request.input.name))

            try:
                item = session.query(Server).filter_by(id=self.request.input.id).one()
                item.name = self.request.input.name

                session.add(item)
                session.commit()
                
                self.response.payload = item
                
            except Exception, e:
                msg = 'Could not update the server, id:[{}], e:[{}]'.format(self.request.input.id, format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            
class GetByID(AdminService):
    """ Returns a particular server
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_get_by_id_request'
        response_elem = 'zato_server_get_by_id_response'
        input_required = ('id',)
        output_required = ('id', 'cluster_id', 'name', 'host')
        output_optional = ('bind_host', 'bind_port', 'last_join_status', 
            'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date')
        
    def get_data(self, session):
        return session.query(Server).\
            filter(Server.id==self.request.input.id).\
            one()

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)
            
            for name in('last_join_mod_date', 'up_mod_date'):
                attr = getattr(self.response.payload, name, None)
                if attr:
                    setattr(self.response.payload, name, attr.isoformat())

class Delete(AdminService):
    """ Deletes a server.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_server_delete_request'
        response_elem = 'zato_server_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                server = session.query(Server).\
                    filter(Server.id==self.request.input.id).\
                    one()
                
                # Sanity check
                if server.id == self.server.id:
                    msg = 'A server cannot delete itself, id:[{}], name:[{}]'.format(server.id, server.name)
                    self.logger.error(msg)
                    raise ZatoException(self.cid, msg)
                
                # This will cascade and delete every related object
                session.delete(server)
                session.commit()
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the server, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
