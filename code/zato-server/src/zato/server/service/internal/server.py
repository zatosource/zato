# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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
from contextlib import closing
from datetime import datetime
from traceback import format_exc

# Bunch
from bunch import Bunch

# Zato
from zato.common import DEPLOYMENT_STATUS, ZatoException
from zato.common.odb.model import Cluster, Server
from zato.server.service.internal import AdminService

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
                    
                    self.server.singleton_server.scheduler.delete(Bunch(name='zato.EnsureClusterWideSingleton'))
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
    class SimpleIO:
        input_required = ('id', 'name')
        output_optional = ('id', 'name', 'host', 'up_status', 'up_mod_date')

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
                
                self.response.payload.id = item.id
                self.response.payload.name = item.name
                self.response.payload.host = item.host
                self.response.payload.up_status = item.up_status
                self.response.payload.up_mod_date = item.up_mod_date
                
            except Exception, e:
                msg = 'Could not update the server, id:[{}], e:[{}]'.format(self.request.input.id, format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            
class GetByID(AdminService):
    """ Returns a particular server
    """
    class SimpleIO:
        input_required = ('id',)
        output_required = ('id', 'cluster_id', 'name', 'host')
        output_optional = ('last_join_status', 'last_join_mod_date', 'last_join_mod_by', 'up_status', 'up_mod_date')
        
    def get_data(self, session):
        return session.query(Server).\
            filter(Server.id==self.request.input.id).\
            one()

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)
