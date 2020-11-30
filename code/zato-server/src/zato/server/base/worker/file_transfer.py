# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.odb.query.generic_object_ import generic_object
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

class FileTransfer(WorkerImpl):
    """ Handles broker messages related to file transfer.
    """
    def __init__(self):
        super(FileTransfer, self).__init__()

# ################################################################################################################################

    def _edit_file_transfer_channel(self, msg):
        # type: (Bunch) -> None

        '''
        print()
        for key, value in sorted(msg.items()):
            print(111, key, value)
        print()
        '''

        # Get a scheduler's job associated with this channel
        if msg.scheduler_job_id:
            response = self.server.invoke('zato.scheduler.job.get-by-id', {
                'cluster_id': self.server.cluster_id,
                'id': msg.scheduler_job_id
                #'name': 'Transfer Invoices Job',
            }, needs_response=False)

            response = response.getvalue()

            print()
            print(222, response)
            print(333, dir(response))
            print()

# ################################################################################################################################
# ################################################################################################################################
