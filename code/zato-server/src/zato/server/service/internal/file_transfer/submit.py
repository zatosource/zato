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

    class SimpleIO:
        input_required = 'filename', 'content'
        input_optional = 'source_protocol', 'source_detail', 'companion_checksum'
        output_required = 'transaction_id',

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)
        engine = FileTransferEngine(store)

        content = self.request.input.content
        if isinstance(content, str):
            content = content.encode('utf-8')

        txn = engine.process_file(
            filename=self.request.input.filename,
            content=content,
            source_protocol=self.request.input.get('source_protocol', 'api'),
            source_detail=self.request.input.get('source_detail', 'file-transfer.submit'),
            companion_checksum=self.request.input.get('companion_checksum', ''),
        )

        self.response.payload.transaction_id = txn.id

# ################################################################################################################################
# ################################################################################################################################
