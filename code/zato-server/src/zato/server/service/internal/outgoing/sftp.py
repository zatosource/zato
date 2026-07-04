# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.util.sql import get_instance_by_id
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

class Execute(AdminService):
    """ Executes SFTP command(s) using a relevant connection.
    """
    input = Int('id'), 'data', Int('log_level')
    output = '-is_ok', '-response_time', '-stdout', '-stderr', Int('-command_no')

    def handle(self) -> 'None':

        # Look up the connection's name by its ID ..
        with closing(self.odb.session()) as session:
            instance = get_instance_by_id(session, ModelGenericConn, self.request.input.id)
            name = instance.name

        # .. obtain the connection object ..
        conn = self.sftp[name]

        # .. execute the commands given on input ..
        response = conn.execute(self.request.input.data, self.request.input.log_level, raise_on_error=False)

        # .. and return the result to our caller.
        self.response.payload.is_ok = response.is_ok
        self.response.payload.response_time = response.response_time
        self.response.payload.stdout = response.stdout
        self.response.payload.stderr = response.stderr
        self.response.payload.command_no = response.command_no

# ################################################################################################################################
# ################################################################################################################################
