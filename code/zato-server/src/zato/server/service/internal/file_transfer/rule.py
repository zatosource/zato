# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# Zato
from zato.common.file_transfer.model import ProcessingRule
from zato.common.file_transfer.redis_store import FileTransferRedisStore
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

class GetList(Service):
    name = 'file-transfer.rule.get-list'

    def handle(self):
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        rules = store.list_processing_rules()

        self.response.payload = [
            {
                'id': r.id,
                'name': r.name,
                'description': r.description,
                'ordinal': r.ordinal,
                'is_enabled': r.is_enabled,
                'is_default': r.is_default,
            }
            for r in rules
        ]

# ################################################################################################################################
# ################################################################################################################################

class Get(Service):
    name = 'file-transfer.rule.get'

    def handle(self):
        input = self.request.raw_request or {}
        rule_id = input.get('id')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)
        rule = store.get_processing_rule(rule_id)

        if not rule:
            self.response.payload = {}
            return

        self.response.payload = rule.to_dict()

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    name = 'file-transfer.rule.create'

    def handle(self):
        input = self.request.raw_request or {}
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        rule_id = f'rule-{uuid4().hex[:8]}'

        existing_rules = store.list_processing_rules()
        max_ordinal = max((r.ordinal for r in existing_rules), default=-1)

        data = {
            'id': rule_id,
            'name': input.get('name'),
            'ordinal': input.get('ordinal', max_ordinal + 1),
        }

        for field in ('description', 'is_enabled', 'is_default', 'criteria_sender', 'criteria_receiver',
                      'criteria_doc_type', 'criteria_user_status', 'criteria_errors', 'criteria_extended',
                      'preprocess_overrides', 'actions'):
            value = input.get(field)
            if value is not None:
                data[field] = value

        rule = ProcessingRule.from_dict(data)
        store.create_processing_rule(rule)

        self.response.payload = {'id': rule_id}

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    name = 'file-transfer.rule.edit'

    def handle(self):
        input = self.request.raw_request or {}
        rule_id = input.get('id')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        rule = store.get_processing_rule(rule_id)
        if not rule:
            raise ValueError(f'Processing rule not found: {rule_id}')

        for field in ('name', 'description', 'ordinal', 'is_enabled', 'is_default', 'criteria_sender',
                      'criteria_receiver', 'criteria_doc_type', 'criteria_user_status', 'criteria_errors',
                      'criteria_extended', 'preprocess_overrides', 'actions'):
            value = input.get(field)
            if value is not None:
                setattr(rule, field, value)

        store.update_processing_rule(rule)
        self.response.payload = {'id': rule.id}

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    name = 'file-transfer.rule.delete'

    def handle(self):
        input = self.request.raw_request or {}
        rule_id = input.get('id')
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        rule = store.get_processing_rule(rule_id)
        if rule and rule.is_default:
            raise ValueError('Cannot delete the default rule')

        store.delete_processing_rule(rule_id)

# ################################################################################################################################
# ################################################################################################################################

class Reorder(Service):
    name = 'file-transfer.rule.reorder'

    def handle(self):
        input = self.request.raw_request or {}
        store = FileTransferRedisStore(self.server.broker_client.redis, self.server.cluster_id)

        ordered_ids = input.get('ordered_ids')
        if isinstance(ordered_ids, str):
            ordered_ids = [x.strip() for x in ordered_ids.split(',')]

        store.reorder_rules(ordered_ids)

# ################################################################################################################################
# ################################################################################################################################
