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

class ConnectorServerKeepAlive(AdminService):
    """ Makes all the other servers know that this particular one, the one that
    manages the connectors, is indeed still alive.
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
            
            if server_id == cluster.cn_srv_id:
                cluster.cn_srv_keep_alive_dt = datetime.utcnow()
                session.add(cluster)
                session.commit()
            else:
                raise ZatoException(self.cid,
                    'Could not set the connector server keep alive timestamp, current server_id:[{}] != cluster.cn_srv_id:[{}]'.format(
                        server_id, cluster.cn_srv_id))

class EnsureConnectorServer(AdminService):
    """ Makes all the other servers know that this particular one, the one that
    manages the connectors, is indeed still alive.
    """
    def handle(self):
        if self.server.singleton_server:
            if self.server.singleton_server.become_connector_server(
                self.server.connector_server_keep_alive_job_time, self.server.connector_server_grace_time,
                self.server.id, self.server.cluster_id, False):
                self.server.singleton_server.scheduler.delete(Bunch(name='zato.EnsureConnectorServer'))

                self.server.init_connectors()
        else:
            msg = 'Ignoring event, server id:[{}], name:[{}] has no singleton attached'.format(
                self.server.id, self.server.name)
            logger.debug(msg)
