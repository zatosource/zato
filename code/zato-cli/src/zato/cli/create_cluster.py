# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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
from copy import deepcopy
from datetime import datetime
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.cli import ZatoCommand, common_odb_opts, broker_opts
from zato.common.defaults import http_plain_server_port
from zato.common.odb.model import Cluster

class Create(ZatoCommand):
    opts = deepcopy(common_odb_opts)
    opts += deepcopy(broker_opts)
    
    opts.append({'name':'lb_host', 'help':"Load-balancer host"})
    opts.append({'name':'lb_port', 'help':'Load-balancer port'})
    opts.append({'name':'lb_agent_port', 'help':'Load-balancer agent host'})
    opts.append({'name':'cluster_name', 'help':'Name of the cluster to create'})

    def execute(self, args):
        
        engine = self._get_engine(args)
        session = self._get_session(engine)
        
        cluster = Cluster()
        cluster.name = args.cluster_name
        cluster.description = 'Created by {} on {} (UTC)'.format(self._get_user_host(), datetime.utcnow().isoformat())
        
        for name in('odb_type', 'odb_host', 'odb_port', 'odb_user', 'odb_db_name', 
            'broker_host', 'broker_port', 'lb_host', 'lb_port', 'lb_agent_port'):
            setattr(cluster, name, getattr(args, name))
        
        session.add(cluster)
        
        try:
            session.commit()
        except IntegrityError, e:
            msg = 'Cluster name [{}] already exists'.format(cluster.name)
            if self.verbose:
                msg += '. Caught an exception:[{}]'.format(format_exc(e))
                self.logger.error(msg)
            self.logger.error(msg)
            session.rollback()
            
            return self.SYS_ERROR.CLUSTER_NAME_ALREADY_EXISTS

        if self.verbose:
            msg = 'Successfully created a new cluster [{}]'.format(args.cluster_name)
            self.logger.debug(msg)
        else:
            self.logger.info('OK')
