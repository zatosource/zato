# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing

# Zato
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.util.sql import get_instance_by_id
from zato.server.service import Int
from zato.server.service.internal import AdminService, AdminSIO

# ################################################################################################################################
# ################################################################################################################################

class Execute(AdminService):
    """ Executes SFTP command(s) using a relevant connector.
    """
    class SimpleIO(AdminSIO):
        input_required = 'id', 'data', Int('log_level')
        output_optional = 'response_time', 'stdout', 'stderr', 'command_no'
        response_elem = None

    def handle(self):
        msg = self.request.input.deepcopy()
        msg['action'] = OUTGOING.SFTP_EXECUTE.value
        msg['cid'] = self.cid

        with closing(self.odb.session()) as session:
            instance = get_instance_by_id(session, ModelGenericConn, self.request.input.id)
            conn = self.out.sftp[instance.name].conn
            response = conn.execute(self.request.input.data, self.request.input.log_level)
            self.response.payload = response.to_dict()

# ################################################################################################################################
# ################################################################################################################################
