# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from time import time
from uuid import uuid4

# Python 2/3 compatibility
from six import add_metaclass

# Zato
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingSAP
from zato.common.odb.query import out_sap_list
from zato.common.util import ping_sap
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

# ################################################################################################################################
# ################################################################################################################################

class Execute(AdminService):
    """ Executes SFTP command(s) using a relevant connector.
    """
    class SimpleIO(AdminSIO):
        input_required = 'name', 'data'
        output_optional = 'response_time', 'stdout', 'stderr'

    def handle(self):
        conn = self.out.sftp[self.request.input.name]
        out = conn.execute(self.request.input.data)
        self.response.payload = out.to_dict()

# ################################################################################################################################
# ################################################################################################################################
