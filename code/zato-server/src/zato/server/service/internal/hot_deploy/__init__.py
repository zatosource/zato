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
from traceback import format_exc

# Zato
from zato.common import DEPLOYMENT_STATUS
from zato.common.odb.model import DeploymentPackage, DeploymentStatus
from zato.server.service.internal import AdminService

class Create(AdminService):
    """ Creates all the needed filesystem directories and files out of a deployment
    package stored in the ODB and starts all the services contained within the
    package.
    """
    class SimpleIO:
        input_required = ('package_id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            dp = session.query(DeploymentPackage).\
                filter(id=self.request.input.package_id).\
                one()
