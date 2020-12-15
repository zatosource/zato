# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from bunch import bunchify

# Zato
from zato.common.api import FILE_TRANSFER
from zato.common.util.file_transfer import parse_extra_into_list
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

class FileTransfer(WorkerImpl):
    """ Handles broker messages related to file transfer.
    """
    def __init__(self):
        super(FileTransfer, self).__init__()

# ################################################################################################################################

    def _file_transfer_get_scheduler_job_by_id(self, job_id):

        # This returns a SimpleIO payload object ..
        response = self.server.invoke('zato.scheduler.job.get-by-id', {
            'cluster_id': self.server.cluster_id,
            'id': job_id,
        }, needs_response=False)

        # .. this returns a dict ..
        response = response.getvalue()

        # .. and this returns a Bunch.
        return bunchify(response)

# ################################################################################################################################

    def _file_transfer_get_scheduler_job_list(self):

        # This returns a SimpleIO payload object ..
        response = self.server.invoke('zato.scheduler.job.get-list', {
            'cluster_id': self.server.cluster_id,
            'service_name': FILE_TRANSFER.SCHEDULER_SERVICE,
        }, needs_response=False)

        # .. this returns a dict with a single key ..
        response = response.getvalue()

        # .. and we return the key's list data only.
        return response['zato_scheduler_job_get_list_response']

# ################################################################################################################################

    def _file_transfer_save_scheduler_job(self, data):
        data['cluster_id'] = self.server.cluster_id
        data['service'] = data.service_name
        self.server.invoke('zato.scheduler.job.edit', data)

# ################################################################################################################################

    def _file_transfer_modify_scheduler_job(self, job, job_id, channel_id, add_or_remove):
        """ Finds a job along with its extra data and either adds or removes a file transfer channel for it.
        """
        # We store IDs as string objects but we compare then as integers
        channel_id = int(channel_id)

        # Get a scheduler's job by its id if we were not given a job on input
        job = job or self._file_transfer_get_scheduler_job_by_id(job_id)

        # This is where keep information about channels to run
        extra = job.extra if isinstance(job.extra, str) else job.extra.decode('utf8')

        # Holds all channel IDs to run
        extra_set = set()

        # If it exists at all ..
        if extra:

            # .. it will be a semicolon-separated list of IDs ..
            extra = parse_extra_into_list(job.extra)

            # .. turn the list into a set ..
            extra_set.update(extra)

        # .. now, we can just add or remove our own key, no matter if extra existed or not ..
        if add_or_remove:
            extra_set.add(channel_id)
        else:
            try:
                extra_set.remove(channel_id)
            except KeyError:
                # This is fine, apparently the channel was not assigned to extra before
                pass

        # .. serialise the set back to a semicolong-separated list ..
        extra = '; '.join(sorted(str(elem) for elem in extra_set))

        # .. assign it to our job dict ..
        job['extra'] = extra

        # .. and save it back in ODB.
        self._file_transfer_save_scheduler_job(job)

# ################################################################################################################################

    def _create_file_transfer_channel(self, msg):

        # Our caller in generic.py has already created the channel object
        # so we only need to associate ourselves with a scheduler's job, if any.
        if msg.scheduler_job_id:
            self._file_transfer_modify_scheduler_job(None, msg.scheduler_job_id, msg.id, True)

# ################################################################################################################################

    def _disassociate_channel_from_scheduler_jobs(self, msg):

        for item in self._file_transfer_get_scheduler_job_list():
            item = bunchify(item)
            self._file_transfer_modify_scheduler_job(item, None, msg.id, False)

# ################################################################################################################################

    def _edit_file_transfer_channel(self, msg):
        # type: (Bunch) -> None

        # If we have a scheduler job on input ..
        if msg.scheduler_job_id:
            self._file_transfer_modify_scheduler_job(None, msg.scheduler_job_id, msg.id, True)

        # .. otherwise, without a job ID on input, we still need to look up
        # all scheduler jobs and disassociate our channel from any of the existing jobs ..
        else:
            self._disassociate_channel_from_scheduler_jobs(msg)

        # .. finally, we can edit the channel itself.
        self.file_transfer_api.edit(msg)

# ################################################################################################################################

    def _delete_file_transfer_channel(self, msg):

        # Our caller in generic.py has already created the channel object
        # so we only need to disassociate ourselves with a scheduler's job, if any.
        self._disassociate_channel_from_scheduler_jobs(msg)

# ################################################################################################################################

    def get_file_transfer_channel_by_id(self, channel_id):
        return self._find_conn_info(channel_id)

# ################################################################################################################################
# ################################################################################################################################
