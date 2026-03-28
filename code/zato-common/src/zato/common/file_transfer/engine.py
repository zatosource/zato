# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import hashlib
import time
from typing import Optional

# Zato
from zato.common.file_transfer.actions import ActionExecutor
from zato.common.file_transfer.const import ActivityClass, ProcessingStatus, Severity
from zato.common.file_transfer.extraction import ExtractionEngine
from zato.common.file_transfer.model import ActivityLogEntry, Transaction
from zato.common.file_transfer.preprocess import PreProcessor
from zato.common.file_transfer.recognition import RecognitionEngine
from zato.common.file_transfer.rules import RuleEvaluator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.file_transfer.redis_store import FileTransferRedisStore
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

class FileTransferEngine:

    def __init__(
        self,
        store:'FileTransferRedisStore',
        service_invoker:'callable_'=None,
        delivery_handler:'callable_'=None,
        notification_sender:'callable_'=None,
    ) -> 'None':
        self.store = store
        self.recognition_engine = RecognitionEngine()
        self.extraction_engine = ExtractionEngine()
        self.preprocessor = PreProcessor(store)
        self.rule_evaluator = RuleEvaluator()
        self.action_executor = ActionExecutor(
            store,
            service_invoker=service_invoker,
            delivery_handler=delivery_handler,
            notification_sender=notification_sender,
        )

# ################################################################################################################################

    def process_file(
        self,
        filename:'str',
        content:'bytes',
        source_protocol:'str',
        source_detail:'str',
        companion_checksum:'str'='',
    ) -> 'Transaction':

        start_time = time.time()

        txn = self._phase1_receipt(filename, content, source_protocol, source_detail)

        doc_type = self._phase2_recognition(txn, filename, content)

        extracted_attrs = self._phase3_extraction(txn, content, doc_type)

        self._phase4_preprocessing(txn, content, doc_type, extracted_attrs, companion_checksum)

        matched_rule = self._phase5_rule_evaluation(txn)

        self._phase6_action_execution(txn, matched_rule, content)

        self._phase7_completion(txn, start_time)

        return txn

# ################################################################################################################################

    def _phase1_receipt(
        self,
        filename:'str',
        content:'bytes',
        source_protocol:'str',
        source_detail:'str',
    ) -> 'Transaction':

        txn_id = self.store.next_txn_id()
        checksum = hashlib.sha256(content).hexdigest()
        now = time.time()

        txn = Transaction(
            id=txn_id,
            created=now,
            filename=filename,
            file_size=len(content),
            source_checksum=checksum,
            source_protocol=source_protocol,
            source_detail=source_detail,
            processing_status=ProcessingStatus.New,
        )

        self.store.create_transaction(txn)

        self._log(txn, ActivityClass.Receipt, Severity.Info,
                  f'File received: {filename}, {len(content)} bytes, checksum {checksum[:16]}...')

        return txn

# ################################################################################################################################

    def _phase2_recognition(
        self,
        txn:'Transaction',
        filename:'str',
        content:'bytes',
    ) -> 'Optional[any_]':

        doc_types = self.store.list_enabled_document_types()
        doc_type = self.recognition_engine.recognize(filename, content, doc_types)

        if doc_type:
            txn.doc_type_id = doc_type.id
            self._log(txn, ActivityClass.Recognition, Severity.Info,
                      f'Document recognized as: {doc_type.name}')
        else:
            txn.has_errors = True
            self._log(txn, ActivityClass.Recognition, Severity.Warning,
                      'Document type not recognized')

        self.store.update_transaction(txn)
        return doc_type

# ################################################################################################################################

    def _phase3_extraction(
        self,
        txn:'Transaction',
        content:'bytes',
        doc_type:'Optional[any_]',
    ) -> 'dict':

        if not doc_type:
            self._log(txn, ActivityClass.Extraction, Severity.Info,
                      'Skipping extraction - no document type')
            return {}

        extracted = self.extraction_engine.extract(content, doc_type)

        txn.sender = extracted.get('sender', '')
        txn.receiver = extracted.get('receiver', '')
        txn.document_id = extracted.get('document_id', '')
        txn.conversation_id = extracted.get('conversation_id', '')
        txn.group_id = extracted.get('group_id', '')
        txn.user_status = extracted.get('user_status', '')
        txn.custom_attrs = extracted.get('custom_attrs', {})

        extraction_errors = extracted.get('_extraction_errors', [])
        if extraction_errors:
            txn.has_errors = True
            for err in extraction_errors:
                self._log(txn, ActivityClass.Extraction, Severity.Warning, err)
        else:
            self._log(txn, ActivityClass.Extraction, Severity.Info,
                      f'Extracted: sender={txn.sender}, receiver={txn.receiver}, doc_id={txn.document_id}')

        self.store.update_transaction(txn)
        return extracted

# ################################################################################################################################

    def _phase4_preprocessing(
        self,
        txn:'Transaction',
        content:'bytes',
        doc_type:'Optional[any_]',
        extracted_attrs:'dict',
        companion_checksum:'str',
    ) -> 'None':

        if not doc_type:
            settings = self.store.get_settings()
            self.store.save_content(txn.id, content)
            txn.content_saved = True
            self._log(txn, ActivityClass.Pre_Processing, Severity.Info,
                      'Content saved (no document type)')
            self.store.update_transaction(txn)
            return

        success, errors, computed_checksum = self.preprocessor.run_all_steps(
            txn.id,
            content,
            doc_type,
            extracted_attrs,
            companion_checksum,
        )

        if computed_checksum:
            txn.source_checksum = computed_checksum

        txn.content_saved = True

        if errors:
            txn.has_errors = True
            for step, error in errors:
                self._log(txn, ActivityClass.Pre_Processing, Severity.Error,
                          f'{step}: {error}')
        else:
            self._log(txn, ActivityClass.Pre_Processing, Severity.Info,
                      'Pre-processing completed successfully')

        self.store.update_transaction(txn)

# ################################################################################################################################

    def _phase5_rule_evaluation(self, txn:'Transaction') -> 'Optional[any_]':

        rules = self.store.list_enabled_processing_rules()
        matched_rule = self.rule_evaluator.evaluate(txn, rules)

        if matched_rule:
            txn.matched_rule_id = matched_rule.id
            self._log(txn, ActivityClass.Rule_Evaluation, Severity.Info,
                      f'Matched rule: {matched_rule.name} (ordinal {matched_rule.ordinal})')
        else:
            txn.processing_status = ProcessingStatus.Not_Routed
            self._log(txn, ActivityClass.Rule_Evaluation, Severity.Warning,
                      'No processing rule matched')

        self.store.update_transaction(txn)
        return matched_rule

# ################################################################################################################################

    def _phase6_action_execution(
        self,
        txn:'Transaction',
        matched_rule:'Optional[any_]',
        content:'bytes',
    ) -> 'None':

        if not matched_rule:
            return

        for action in matched_rule.actions:
            success, error = self.action_executor.execute(action, txn, content)

            action_type = action.type.value if hasattr(action.type, 'value') else str(action.type)

            if success:
                self._log(txn, ActivityClass.Action, Severity.Info,
                          f'Action executed: {action_type}')
            else:
                txn.has_errors = True
                self._log(txn, ActivityClass.Action, Severity.Error,
                          f'Action failed: {action_type} - {error}')

        self.store.update_transaction(txn)

# ################################################################################################################################

    def _phase7_completion(self, txn:'Transaction', start_time:'float') -> 'None':

        end_time = time.time()
        txn.completed = end_time
        txn.duration_ms = int((end_time - start_time) * 1000)

        if txn.processing_status == ProcessingStatus.Not_Routed:
            pass
        elif txn.has_errors:
            txn.processing_status = ProcessingStatus.Done_W_Errors
        else:
            txn.processing_status = ProcessingStatus.Done

        self._log(txn, ActivityClass.Completion, Severity.Info,
                  f'Processing complete: status={txn.processing_status.value}, duration={txn.duration_ms}ms')

        self.store.update_transaction(txn)

# ################################################################################################################################

    def resubmit(self, txn_id:'str') -> 'Optional[Transaction]':

        original_txn = self.store.get_transaction(txn_id)
        if not original_txn:
            return None

        content = self.store.get_content(txn_id)
        if not content:
            return None

        new_txn = self.process_file(
            original_txn.filename,
            content,
            original_txn.source_protocol,
            original_txn.source_detail,
        )

        new_txn.resubmitted_from = txn_id
        self.store.update_transaction(new_txn)

        return new_txn

# ################################################################################################################################

    def reprocess(self, txn_id:'str') -> 'Optional[Transaction]':

        txn = self.store.get_transaction(txn_id)
        if not txn:
            return None

        content = self.store.get_content(txn_id)

        start_time = time.time()

        self._log(txn, ActivityClass.Receipt, Severity.Info,
                  f'Reprocessing transaction {txn_id}')

        matched_rule = self._phase5_rule_evaluation(txn)

        self._phase6_action_execution(txn, matched_rule, content)

        self._phase7_completion(txn, start_time)

        return txn

# ################################################################################################################################

    def _log(
        self,
        txn:'Transaction',
        activity_class:'ActivityClass',
        severity:'Severity',
        message:'str',
        detail:'str'='',
    ) -> 'None':

        seq = self.store.next_log_seq(txn.id)
        entry_id = f'{txn.id}:{seq:04d}'

        entry = ActivityLogEntry(
            id=entry_id,
            transaction_id=txn.id,
            timestamp=time.time(),
            activity_class=activity_class,
            severity=severity,
            message=message,
            detail=detail,
        )

        self.store.create_log_entry(entry)

# ################################################################################################################################
# ################################################################################################################################
