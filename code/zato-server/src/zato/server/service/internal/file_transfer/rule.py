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

    class SimpleIO:
        output_optional = 'id', 'name', 'description', 'ordinal', 'is_enabled', 'is_default'
        output_repeated = True

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)
        rules = store.list_processing_rules()

        self.response.payload[:] = [
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

    class SimpleIO:
        input_required = 'id',
        output_optional = 'id', 'name', 'description', 'ordinal', 'is_enabled', 'is_default', \
            'criteria_sender', 'criteria_receiver', 'criteria_doc_type', 'criteria_user_status', \
            'criteria_errors', 'criteria_extended', 'preprocess_overrides', 'actions'

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)
        rule = store.get_processing_rule(self.request.input.id)

        if not rule:
            self.response.payload = {}
            return

        self.response.payload = rule.to_dict()

# ################################################################################################################################
# ################################################################################################################################

class Create(Service):
    name = 'file-transfer.rule.create'

    class SimpleIO:
        input_required = 'name',
        input_optional = 'description', 'ordinal', 'is_enabled', 'is_default', \
            'criteria_sender', 'criteria_receiver', 'criteria_doc_type', 'criteria_user_status', \
            'criteria_errors', 'criteria_extended', 'preprocess_overrides', 'actions'
        output_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)

        rule_id = f'rule-{uuid4().hex[:8]}'

        existing_rules = store.list_processing_rules()
        max_ordinal = max((r.ordinal for r in existing_rules), default=-1)

        data = {
            'id': rule_id,
            'name': self.request.input.name,
            'ordinal': self.request.input.get('ordinal', max_ordinal + 1),
        }

        for field in ('description', 'is_enabled', 'is_default', 'criteria_sender', 'criteria_receiver',
                      'criteria_doc_type', 'criteria_user_status', 'criteria_errors', 'criteria_extended',
                      'preprocess_overrides', 'actions'):
            value = getattr(self.request.input, field, None)
            if value is not None:
                data[field] = value

        rule = ProcessingRule.from_dict(data)
        store.create_processing_rule(rule)

        self.response.payload.id = rule_id

# ################################################################################################################################
# ################################################################################################################################

class Edit(Service):
    name = 'file-transfer.rule.edit'

    class SimpleIO:
        input_required = 'id',
        input_optional = 'name', 'description', 'ordinal', 'is_enabled', 'is_default', \
            'criteria_sender', 'criteria_receiver', 'criteria_doc_type', 'criteria_user_status', \
            'criteria_errors', 'criteria_extended', 'preprocess_overrides', 'actions'
        output_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)

        rule = store.get_processing_rule(self.request.input.id)
        if not rule:
            raise ValueError(f'Processing rule not found: {self.request.input.id}')

        for field in ('name', 'description', 'ordinal', 'is_enabled', 'is_default', 'criteria_sender',
                      'criteria_receiver', 'criteria_doc_type', 'criteria_user_status', 'criteria_errors',
                      'criteria_extended', 'preprocess_overrides', 'actions'):
            value = getattr(self.request.input, field, None)
            if value is not None:
                setattr(rule, field, value)

        store.update_processing_rule(rule)
        self.response.payload.id = rule.id

# ################################################################################################################################
# ################################################################################################################################

class Delete(Service):
    name = 'file-transfer.rule.delete'

    class SimpleIO:
        input_required = 'id',

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)

        rule = store.get_processing_rule(self.request.input.id)
        if rule and rule.is_default:
            raise ValueError('Cannot delete the default rule')

        store.delete_processing_rule(self.request.input.id)

# ################################################################################################################################
# ################################################################################################################################

class Reorder(Service):
    name = 'file-transfer.rule.reorder'

    class SimpleIO:
        input_required = 'ordered_ids',

    def handle(self):
        store = FileTransferRedisStore(self.server.kvdb.conn, self.server.cluster_id)

        ordered_ids = self.request.input.ordered_ids
        if isinstance(ordered_ids, str):
            ordered_ids = [x.strip() for x in ordered_ids.split(',')]

        store.reorder_rules(ordered_ids)

# ################################################################################################################################
# ################################################################################################################################
