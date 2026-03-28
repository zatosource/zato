# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.model import Settings
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class Get(Service):
    name = 'file-transfer.settings.get'

    class SimpleIO:
        output_optional = 'default_retry_count', 'default_retry_wait_ms', 'default_backoff_factor', \
            'default_save_policy', 'max_search_results', 'archive_after_days', 'log_retention_days', 'checksum_algorithm'

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)
        settings = store.get_settings()
        self.response.payload = settings.to_dict()

# ################################################################################################################################
# ################################################################################################################################

class Update(Service):
    name = 'file-transfer.settings.update'

    class SimpleIO:
        input_optional = 'default_retry_count', 'default_retry_wait_ms', 'default_backoff_factor', \
            'default_save_policy', 'max_search_results', 'archive_after_days', 'log_retention_days', 'checksum_algorithm'

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)

        settings = store.get_settings()

        for field in ('default_retry_count', 'default_retry_wait_ms', 'default_backoff_factor',
                      'default_save_policy', 'max_search_results', 'archive_after_days',
                      'log_retention_days', 'checksum_algorithm'):
            value = getattr(self.request.input, field, None)
            if value is not None:
                setattr(settings, field, value)

        store.update_settings(settings)

# ################################################################################################################################
# ################################################################################################################################
