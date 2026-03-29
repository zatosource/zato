# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.file_transfer.const import ProcessingStatus, RedisKey
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class GetSummary(Service):
    name = 'file-transfer.dashboard.get-summary'

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        date_from = self.request.input.get('date_from')
        date_to = self.request.input.get('date_to')

        if date_from:
            date_from = float(date_from)
        else:
            date_from = time.time() - (24 * 60 * 60)

        if date_to:
            date_to = float(date_to)
        else:
            date_to = time.time()

        cluster_id = store.cluster_id

        total = store.redis.zcount(RedisKey.idx_tx_by_created(cluster_id), date_from, date_to)

        done_count = store.redis.zcount(
            RedisKey.idx_tx_by_status(cluster_id, ProcessingStatus.Done.value),
            date_from, date_to
        )

        done_w_errors_count = store.redis.zcount(
            RedisKey.idx_tx_by_status(cluster_id, ProcessingStatus.Done_W_Errors.value),
            date_from, date_to
        )

        failed_count = store.redis.zcount(
            RedisKey.idx_tx_by_status(cluster_id, ProcessingStatus.Failed.value),
            date_from, date_to
        )

        success_count = done_count + done_w_errors_count

        if total > 0:
            success_rate = round((success_count / total) * 100, 2)
        else:
            success_rate = 0.0

        result = store.search_transactions(
            date_from=date_from,
            date_to=date_to,
            limit=1000,
        )

        total_duration = 0
        duration_count = 0
        sender_counts = {}
        doc_type_counts = {}

        for tx in result.items:
            if tx.duration_ms:
                total_duration += tx.duration_ms
                duration_count += 1

            if tx.sender:
                sender_counts[tx.sender] = sender_counts.get(tx.sender, 0) + 1

            if tx.doc_type_id:
                doc_type_counts[tx.doc_type_id] = doc_type_counts.get(tx.doc_type_id, 0) + 1

        avg_duration = round(total_duration / duration_count, 2) if duration_count > 0 else 0

        top_senders = sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_doc_types = sorted(doc_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        failed_result = store.search_transactions(
            date_from=date_from,
            date_to=date_to,
            status=ProcessingStatus.Failed.value,
            limit=10,
        )

        recent_failures = [
            {
                'id': t.id,
                'filename': t.filename,
                'created': t.created,
            }
            for t in failed_result.items
        ]

        self.response.payload = {
            'total_transactions': total,
            'success_count': success_count,
            'failed_count': failed_count,
            'success_rate': success_rate,
            'avg_duration_ms': avg_duration,
            'top_senders': top_senders,
            'top_doc_types': top_doc_types,
            'recent_failures': recent_failures,
        }

# ################################################################################################################################
# ################################################################################################################################
