# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService
from zato.server.service.internal.outgoing.file_transfer.process import process_files

# ################################################################################################################################
# ################################################################################################################################

class ProcessFiles(AdminService):
    """ Invoked by the scheduler on behalf of one file transfer schedule of an SMB connection -
    looks into the schedule's directory and invokes the target service once per each file that is ready.
    """

    def handle(self) -> 'None':

        # The scheduler job carries the connection's identity and the full schedule in its extra data,
        # which arrives here as a dict no matter if the invocation came from the scheduler or over HTTP.
        process_files(self, self.request.payload)

# ################################################################################################################################
# ################################################################################################################################
