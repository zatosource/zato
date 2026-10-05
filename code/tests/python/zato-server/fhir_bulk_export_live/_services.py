# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# Where the receiver writes what it was handed - one JSON line per file, at a path the server was started with
Receiver_Path_Env = 'Zato_Test_FHIR_Bulk_Export_Receiver_Path'

# ################################################################################################################################
# ################################################################################################################################

class BulkExportReceiver(Service):
    """ A service destination of a bulk export - records each file it is handed, with the resources read off it,
    so that a test can assert on what arrived without reading server logs.
    """
    name = 'test.fhir.bulk.export.receiver'

    def handle(self) -> 'None':

        file = self.request.input

        ids = []
        for resource in file:
            ids.append(resource.get('id', ''))

        record = {
            'job_id': file.job_id,
            'connection_name': file.connection_name,
            'resource_type': file.resource_type,
            'count': file.count,
            'file_name': file.file_name,
            'is_error_file': file.is_error_file,
            'ids': ids,
        }

        with open(os.environ[Receiver_Path_Env], 'a') as receiver_file:
            _ = receiver_file.write(dumps(record) + '\n')

# ################################################################################################################################
# ################################################################################################################################

class BulkExportStart(Service):
    """ Starts an export through the connection's client, the way a user's own service would, and reports the job's id.
    """
    name = 'test.fhir.bulk.export.start'

    def handle(self) -> 'None':

        request = self.request.raw_request

        client = self.fhir[request['conn_name']]

        job_id = client.export(
            level=request['level'],
            patient_ids=request['patient_ids'],
            types=request['types'],
        )

        self.response.payload = {'job_id': job_id}

# ################################################################################################################################
# ################################################################################################################################
