# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import base64
import logging

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

logger = logging.getLogger(__name__)

class Submit(Service):
    name = 'file-transfer.submit'

    def handle(self):
        logger.info('Submit.handle called')

        input = self.request.raw_request or {}
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        engine = FileTransferEngine(store)

        filename = input.get('filename')
        content = input.get('content')
        is_base64 = input.get('is_base64', False)

        logger.info('filename=%s, is_base64=%s, content_type=%s', filename, is_base64, type(content))

        if isinstance(content, str):
            if is_base64:
                content = base64.b64decode(content)
            else:
                content = content.encode('utf-8')

        logger.info('Calling engine.process_file with content_length=%d', len(content) if content else 0)

        tx = engine.process_file(
            filename=filename,
            content=content,
            source_protocol=input.get('source_protocol', 'api'),
            source_detail=input.get('source_detail', 'file-transfer.submit'),
            companion_checksum=input.get('companion_checksum', ''),
        )

        logger.info('Transaction created: id=%s, status=%s', tx.id, tx.processing_status)

        self.response.payload = {'transaction_id': tx.id}

# ################################################################################################################################
# ################################################################################################################################
