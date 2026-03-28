# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from typing import List

# Zato
from zato.common.file_transfer.const import ProcessingStatus
from zato.common.file_transfer.model import Transaction

# ################################################################################################################################
# ################################################################################################################################

def get_sample_transactions() -> 'List[Transaction]':

    now = time.time()
    hour = 3600
    day = 24 * hour

    return [

        Transaction(
            id='TXN-00847',
            created=now - (2 * hour),
            completed=now - (2 * hour) + 0.234,
            filename='invoice_2026_Q1.csv',
            file_size=2516582,
            source_checksum='a3f2c8d1e5b7f9a2c4d6e8f0a1b3c5d7e9f1a2b4c6d8e0f2a4b6c8d0e2f4a6b8',
            dest_checksum='a3f2c8d1e5b7f9a2c4d6e8f0a1b3c5d7e9f1a2b4c6d8e0f2a4b6c8d0e2f4a6b8',
            source_protocol='sftp',
            source_detail='acme-sftp-in:/inbound/financial/',
            doc_type_id='dt-002',
            sender='Acme Corp',
            receiver='Enterprise',
            document_id='INV-2026-Q1',
            processing_status=ProcessingStatus.Done,
            user_status='Processed',
            matched_rule_id='rule-002',
            has_errors=False,
            duration_ms=234,
            content_saved=True,
            custom_attrs={'order_amount': '15420.00', 'region': 'US'},
        ),

        Transaction(
            id='TXN-00846',
            created=now - (3 * hour),
            completed=now - (3 * hour) + 0.456,
            filename='order_batch_771.xml',
            file_size=45678,
            source_checksum='b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5',
            source_protocol='sftp',
            source_detail='globex-sftp-in:/orders/',
            doc_type_id='dt-001',
            sender='Globex Inc',
            receiver='Enterprise',
            document_id='ORD-771',
            processing_status=ProcessingStatus.Done_W_Errors,
            user_status='Needs review',
            matched_rule_id='rule-001',
            has_errors=True,
            duration_ms=456,
            content_saved=True,
            custom_attrs={'order_amount': '8750.00'},
        ),

        Transaction(
            id='TXN-00845',
            created=now - (5 * hour),
            completed=now - (5 * hour) + 1.234,
            filename='shipment_manifest.edi',
            file_size=12345,
            source_checksum='c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6',
            source_protocol='ftp',
            source_detail='initech-ftp:/outbound/',
            doc_type_id='dt-003',
            sender='Initech',
            receiver='Acme Corp',
            document_id='SHP-2026-001',
            processing_status=ProcessingStatus.Failed,
            user_status='Delivery failed',
            matched_rule_id='rule-005',
            has_errors=True,
            duration_ms=1234,
            content_saved=True,
        ),

        Transaction(
            id='TXN-00844',
            created=now - (1 * hour),
            filename='employee_data.pgp',
            file_size=567890,
            source_checksum='d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7',
            source_protocol='sftp',
            source_detail='enterprise-sftp:/hr/exports/',
            doc_type_id='dt-005',
            sender='Enterprise',
            receiver='Payroll Svc Ltd',
            processing_status=ProcessingStatus.Queued,
            user_status='Delivering',
            matched_rule_id='rule-008',
            has_errors=False,
            content_saved=True,
        ),

        Transaction(
            id='TXN-00843',
            created=now - (6 * hour),
            completed=now - (6 * hour) + 0.567,
            filename='catalog_update_v3.json',
            file_size=234567,
            source_checksum='e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8',
            dest_checksum='e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8',
            source_protocol='https',
            source_detail='api.vandelay.com/catalog/export',
            doc_type_id='dt-004',
            sender='Vandelay Ind',
            receiver='Enterprise',
            document_id='CAT-V3-2026',
            processing_status=ProcessingStatus.Done,
            user_status='Imported',
            matched_rule_id='rule-003',
            has_errors=False,
            duration_ms=567,
            content_saved=True,
            custom_attrs={'catalog_version': 'v3.2026'},
        ),

        Transaction(
            id='TXN-00842',
            created=now - (30 * 60),
            filename='compliance_report.pdf',
            file_size=1234567,
            source_checksum='f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9',
            source_protocol='sftp',
            source_detail='enterprise-sftp:/compliance/',
            doc_type_id='dt-008',
            sender='Enterprise',
            receiver='RegAuth Central',
            document_id='COMP-2026-Q1',
            processing_status=ProcessingStatus.Queued,
            user_status='Scheduled 14:00',
            matched_rule_id='rule-007',
            has_errors=False,
            content_saved=True,
        ),

        Transaction(
            id='TXN-00841',
            created=now - (8 * hour),
            completed=now - (8 * hour) + 0.345,
            filename='price_list_EU.xlsx',
            file_size=89012,
            source_checksum='a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0',
            dest_checksum='a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0',
            source_protocol='sftp',
            source_detail='acme-sftp-in:/pricing/',
            doc_type_id='dt-006',
            sender='Acme Corp',
            receiver='Enterprise',
            document_id='PRICE-EU-2026',
            processing_status=ProcessingStatus.Done,
            user_status='Processed',
            matched_rule_id='rule-004',
            has_errors=False,
            duration_ms=345,
            content_saved=True,
        ),

        Transaction(
            id='TXN-00840',
            created=now - (45 * 60),
            filename='ack_order_771.xml',
            file_size=5678,
            source_checksum='b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1',
            source_protocol='internal',
            source_detail='order-processing-service',
            doc_type_id='dt-007',
            sender='Enterprise',
            receiver='Globex Inc',
            document_id='ACK-771',
            processing_status=ProcessingStatus.Queued,
            user_status='Attempt 2/3',
            matched_rule_id='rule-006',
            has_errors=True,
            content_saved=True,
        ),

    ]

# ################################################################################################################################
# ################################################################################################################################

def get_sample_user_statuses() -> 'List[str]':

    return [
        'Processed',
        'Needs review',
        'Approved',
        'Rejected',
        'Ignored',
        'Imported',
        'Delivery failed',
        'Queued',
        'Delivering',
    ]

# ################################################################################################################################
# ################################################################################################################################
