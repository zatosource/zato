# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class Search(Service):
    name = 'file-transfer.activity-log.search'

    class SimpleIO:
        input_optional = 'date_from', 'date_to', 'activity_class', 'severity', 'limit', 'offset'
        output_optional = 'id', 'transaction_id', 'timestamp', 'activity_class', 'severity', 'message', 'detail'
        output_repeated = True

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        date_from = self.request.input.get('date_from')
        date_to = self.request.input.get('date_to')
        if date_from:
            date_from = float(date_from)
        if date_to:
            date_to = float(date_to)

        entries, total = store.search_logs(
            date_from=date_from,
            date_to=date_to,
            activity_class=self.request.input.get('activity_class'),
            severity=self.request.input.get('severity'),
            limit=int(self.request.input.get('limit', 100)),
            offset=int(self.request.input.get('offset', 0)),
        )

        self.response.payload[:] = [
            {
                'id': e.id,
                'transaction_id': e.transaction_id,
                'timestamp': e.timestamp,
                'activity_class': e.activity_class.value if hasattr(e.activity_class, 'value') else e.activity_class,
                'severity': e.severity.value if hasattr(e.severity, 'value') else e.severity,
                'message': e.message,
                'detail': e.detail,
            }
            for e in entries
        ]

# ################################################################################################################################
# ################################################################################################################################
