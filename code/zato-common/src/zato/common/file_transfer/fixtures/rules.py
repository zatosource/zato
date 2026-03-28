# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import List

# Zato
from zato.common.file_transfer.const import ActionType, CriteriaMatch, ErrorCriteria, ExecMode
from zato.common.file_transfer.model import CriteriaSpec, ProcessingRule, RuleAction

# ################################################################################################################################
# ################################################################################################################################

def get_sample_rules() -> 'List[ProcessingRule]':

    return [

        ProcessingRule(
            id='rule-001',
            name='Purchase orders from any partner',
            description='Process incoming purchase orders',
            ordinal=0,
            is_enabled=True,
            is_default=False,
            criteria_sender=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_receiver=CriteriaSpec(match=CriteriaMatch.Specific, values=['Enterprise']),
            criteria_doc_type=CriteriaSpec(match=CriteriaMatch.Specific, values=['dt-001']),
            criteria_user_status=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_errors=ErrorCriteria.No_Errors,
            actions=[
                RuleAction(
                    type=ActionType.Execute_Service,
                    service_name='mft.services.process-purchase-order',
                    exec_mode=ExecMode.Synchronous,
                ),
                RuleAction(
                    type=ActionType.Change_Status,
                    new_status='Processed',
                ),
            ],
        ),

        ProcessingRule(
            id='rule-002',
            name='Financial docs - encrypt and archive',
            description='Archive financial documents securely',
            ordinal=1,
            is_enabled=True,
            is_default=False,
            criteria_sender=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_receiver=CriteriaSpec(match=CriteriaMatch.Specific, values=['Enterprise']),
            criteria_doc_type=CriteriaSpec(match=CriteriaMatch.Specific, values=['dt-002']),
            criteria_user_status=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_errors=ErrorCriteria.No_Errors,
            actions=[
                RuleAction(
                    type=ActionType.Execute_Service,
                    service_name='mft.services.archive-financial-doc',
                    exec_mode=ExecMode.Synchronous,
                ),
                RuleAction(
                    type=ActionType.Change_Status,
                    new_status='Processed',
                ),
            ],
        ),

        ProcessingRule(
            id='rule-003',
            name='Catalog updates - validate and import',
            description='Import product catalog updates',
            ordinal=2,
            is_enabled=True,
            is_default=False,
            criteria_sender=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_receiver=CriteriaSpec(match=CriteriaMatch.Specific, values=['Enterprise']),
            criteria_doc_type=CriteriaSpec(match=CriteriaMatch.Specific, values=['dt-004']),
            criteria_user_status=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_errors=ErrorCriteria.No_Errors,
            actions=[
                RuleAction(
                    type=ActionType.Execute_Service,
                    service_name='mft.services.import-catalog',
                    exec_mode=ExecMode.Synchronous,
                ),
                RuleAction(
                    type=ActionType.Change_Status,
                    new_status='Imported',
                ),
            ],
        ),

        ProcessingRule(
            id='rule-004',
            name='Price updates - notify procurement',
            description='Notify procurement team of price updates',
            ordinal=3,
            is_enabled=True,
            is_default=False,
            criteria_sender=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_receiver=CriteriaSpec(match=CriteriaMatch.Specific, values=['Enterprise']),
            criteria_doc_type=CriteriaSpec(match=CriteriaMatch.Specific, values=['dt-006']),
            criteria_user_status=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_errors=ErrorCriteria.No_Errors,
            actions=[
                RuleAction(
                    type=ActionType.Execute_Service,
                    service_name='mft.services.notify-procurement',
                    exec_mode=ExecMode.Synchronous,
                ),
                RuleAction(
                    type=ActionType.Notify,
                    channel='EMAIL',
                    to='procurement@company.com',
                    subject='Price update received from {sender}',
                    body='File {filename} ({file_size} bytes) received. Status: {processing_status}.',
                ),
                RuleAction(
                    type=ActionType.Change_Status,
                    new_status='Processed',
                ),
            ],
        ),

        ProcessingRule(
            id='rule-005',
            name='EDI routing to partners',
            description='Route EDI shipping notices to partners',
            ordinal=4,
            is_enabled=True,
            is_default=False,
            criteria_sender=CriteriaSpec(match=CriteriaMatch.Specific, values=['Enterprise']),
            criteria_receiver=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_doc_type=CriteriaSpec(match=CriteriaMatch.Specific, values=['dt-003']),
            criteria_user_status=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_errors=ErrorCriteria.No_Errors,
            actions=[
                RuleAction(
                    type=ActionType.Deliver,
                    method='RECEIVER_PREFERRED',
                    connection='',
                    path='',
                ),
                RuleAction(
                    type=ActionType.Change_Status,
                    new_status='Delivered',
                ),
            ],
        ),

        ProcessingRule(
            id='rule-006',
            name='Acknowledgments - immediate delivery',
            description='Deliver order acknowledgments immediately via SFTP',
            ordinal=5,
            is_enabled=True,
            is_default=False,
            criteria_sender=CriteriaSpec(match=CriteriaMatch.Specific, values=['Enterprise']),
            criteria_receiver=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_doc_type=CriteriaSpec(match=CriteriaMatch.Specific, values=['dt-007']),
            criteria_user_status=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_errors=ErrorCriteria.No_Errors,
            actions=[
                RuleAction(
                    type=ActionType.Deliver,
                    method='SFTP',
                    connection='partner-sftp-out',
                    path='/inbound/acks/',
                ),
                RuleAction(
                    type=ActionType.Change_Status,
                    new_status='Delivered',
                ),
            ],
        ),

        ProcessingRule(
            id='rule-007',
            name='Regulatory filings - PGP and queue',
            description='Encrypt and queue regulatory filings',
            ordinal=6,
            is_enabled=True,
            is_default=False,
            criteria_sender=CriteriaSpec(match=CriteriaMatch.Specific, values=['Enterprise']),
            criteria_receiver=CriteriaSpec(match=CriteriaMatch.Specific, values=['RegAuth Central']),
            criteria_doc_type=CriteriaSpec(match=CriteriaMatch.Specific, values=['dt-008']),
            criteria_user_status=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_errors=ErrorCriteria.No_Errors,
            actions=[
                RuleAction(
                    type=ActionType.Execute_Service,
                    service_name='mft.services.pgp-encrypt-and-queue',
                    exec_mode=ExecMode.Synchronous,
                ),
                RuleAction(
                    type=ActionType.Change_Status,
                    new_status='Queued',
                ),
            ],
        ),

        ProcessingRule(
            id='rule-008',
            name='Encrypted HR - decrypt and forward',
            description='Decrypt and forward HR exports',
            ordinal=7,
            is_enabled=True,
            is_default=False,
            criteria_sender=CriteriaSpec(match=CriteriaMatch.Specific, values=['Enterprise']),
            criteria_receiver=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_doc_type=CriteriaSpec(match=CriteriaMatch.Specific, values=['dt-005']),
            criteria_user_status=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_errors=ErrorCriteria.No_Errors,
            actions=[
                RuleAction(
                    type=ActionType.Execute_Service,
                    service_name='mft.services.decrypt-and-deliver',
                    exec_mode=ExecMode.Synchronous,
                ),
                RuleAction(
                    type=ActionType.Change_Status,
                    new_status='Processed',
                ),
            ],
        ),

        ProcessingRule(
            id='rule-default',
            name='Default - log and ignore',
            description='Default catch-all rule for unmatched documents',
            ordinal=999,
            is_enabled=True,
            is_default=True,
            criteria_sender=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_receiver=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_doc_type=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_user_status=CriteriaSpec(match=CriteriaMatch.Any),
            criteria_errors=ErrorCriteria.Any,
            actions=[
                RuleAction(
                    type=ActionType.Change_Status,
                    new_status='Ignored',
                ),
            ],
        ),

    ]

# ################################################################################################################################
# ################################################################################################################################
