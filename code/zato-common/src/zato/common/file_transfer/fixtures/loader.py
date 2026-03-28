# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.file_transfer.fixtures.doc_types import get_sample_doc_types
from zato.common.file_transfer.fixtures.rules import get_sample_rules
from zato.common.file_transfer.fixtures.transactions import get_sample_transactions, get_sample_user_statuses
from zato.common.file_transfer.model import Settings

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.file_transfer.redis_store import FileTransferRedisStore
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def load_fixtures(store:'FileTransferRedisStore', include_transactions:'bool'=True) -> 'None':

    logger.info('Loading file transfer fixtures...')

    settings = Settings()
    store.update_settings(settings)
    logger.info('Loaded default settings')

    for status in get_sample_user_statuses():
        store.add_user_status(status)
    logger.info('Loaded %d user statuses', len(get_sample_user_statuses()))

    doc_types = get_sample_doc_types()
    for dt in doc_types:
        store.create_document_type(dt)
    logger.info('Loaded %d document types', len(doc_types))

    rules = get_sample_rules()
    for rule in rules:
        store.create_processing_rule(rule)
    logger.info('Loaded %d processing rules', len(rules))

    if include_transactions:
        transactions = get_sample_transactions()
        for txn in transactions:
            store.create_transaction(txn)
        logger.info('Loaded %d sample transactions', len(transactions))

    logger.info('File transfer fixtures loaded successfully')

# ################################################################################################################################
# ################################################################################################################################

def clear_fixtures(store:'FileTransferRedisStore') -> 'None':

    logger.info('Clearing file transfer fixtures...')

    for dt in store.list_document_types():
        store.delete_document_type(dt.id)

    for rule in store.list_processing_rules():
        store.delete_processing_rule(rule.id)

    for status in store.get_user_statuses():
        store.remove_user_status(status)

    logger.info('File transfer fixtures cleared')

# ################################################################################################################################
# ################################################################################################################################
