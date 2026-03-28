# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.engine import FileTransferEngine
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class Submit(Service):
    name = 'file-transfer.submit'

    def handle(self):
        input = self.request.raw_request or {}
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        engine = FileTransferEngine(store)

        filename = input.get('filename')
        content = input.get('content')

        if isinstance(content, str):
            content = content.encode('utf-8')

        txn = engine.process_file(
            filename=filename,
            content=content,
            source_protocol=input.get('source_protocol', 'api'),
            source_detail=input.get('source_detail', 'file-transfer.submit'),
            companion_checksum=input.get('companion_checksum', ''),
        )

        self.response.payload = {'transaction_id': txn.id}

# ################################################################################################################################
# ################################################################################################################################
