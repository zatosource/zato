# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import hashlib
import time

# Zato
from zato.common.file_transfer.actions import ActionExecutor
from zato.common.file_transfer.const import ActivityClass, ProcessingStatus, Severity
from zato.common.file_transfer.extraction import ExtractionEngine
from zato.common.file_transfer.model import ActivityLogEntry, ExtractionResult, Transaction
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

        tx = self._phase1_receipt(filename, content, source_protocol, source_detail)

        doc_type = self._phase2_recognition(tx, filename, content)

        extracted_attrs = self._phase3_extraction(tx, content, doc_type)

        self._phase4_preprocessing(tx, content, doc_type, extracted_attrs, companion_checksum)

        matched_rule = self._phase5_rule_evaluation(tx)

        self._phase6_action_execution(tx, matched_rule, content)

        self._phase7_completion(tx, start_time)

        return tx

# ################################################################################################################################

    def _phase1_receipt(
        self,
        filename:'str',
        content:'bytes',
        source_protocol:'str',
        source_detail:'str',
    ) -> 'Transaction':

        tx_id = self.store.next_tx_id()
        checksum = hashlib.sha256(content).hexdigest()
        now = time.time()

        tx = Transaction(
            id=tx_id,
            created=now,
            filename=filename,
            file_size=len(content),
            source_checksum=checksum,
            source_protocol=source_protocol,
            source_detail=source_detail,
            processing_status=ProcessingStatus.New,
        )

        self.store.create_transaction(tx)

        self._log(tx, ActivityClass.Receipt, Severity.Info,
                  f'File received: {filename}, {len(content)} bytes, checksum {checksum[:16]}...')

        return tx

# ################################################################################################################################

    def _phase2_recognition(
        self,
        tx:'Transaction',
        filename:'str',
        content:'bytes',
    ) -> 'any_ | None':

        doc_types = self.store.list_enabled_document_types()
        doc_type = self.recognition_engine.recognize(filename, content, doc_types)

        if doc_type:
            tx.doc_type_id = doc_type.id
            self._log(tx, ActivityClass.Recognition, Severity.Info,
                      f'Document recognized as: {doc_type.name}')
        else:
            tx.has_errors = True
            self._log(tx, ActivityClass.Recognition, Severity.Warning,
                      'Document type not recognized')

        self.store.update_transaction(tx)
        return doc_type

# ################################################################################################################################

    def _phase3_extraction(
        self,
        tx:'Transaction',
        content:'bytes',
        doc_type:'any_ | None',
    ) -> 'ExtractionResult':

        if not doc_type:
            self._log(tx, ActivityClass.Extraction, Severity.Info,
                      'Skipping extraction - no document type')
            return ExtractionResult()

        extracted = self.extraction_engine.extract(content, doc_type)

        tx.sender = extracted.sender
        tx.receiver = extracted.receiver
        tx.document_id = extracted.document_id
        tx.conversation_id = extracted.conversation_id
        tx.group_id = extracted.group_id
        tx.user_status = extracted.user_status
        tx.custom_attrs = extracted.custom_attrs

        if extracted.errors:
            tx.has_errors = True
            for err in extracted.errors:
                self._log(tx, ActivityClass.Extraction, Severity.Warning, err)
        else:
            self._log(tx, ActivityClass.Extraction, Severity.Info,
                      f'Extracted: sender={tx.sender}, receiver={tx.receiver}, doc_id={tx.document_id}')

        self.store.update_transaction(tx)
        return extracted

# ################################################################################################################################

    def _phase4_preprocessing(
        self,
        tx:'Transaction',
        content:'bytes',
        doc_type:'any_ | None',
        extracted_attrs:'ExtractionResult',
        companion_checksum:'str',
    ) -> 'None':

        if not doc_type:
            settings = self.store.get_settings()
            self.store.save_content(tx.id, content)
            tx.content_saved = True
            self._log(tx, ActivityClass.Pre_Processing, Severity.Info,
                      'Content saved (no document type)')
            self.store.update_transaction(tx)
            return

        preprocess_result = self.preprocessor.run_all_steps(
            tx.id,
            content,
            doc_type,
            extracted_attrs,
            companion_checksum,
        )

        if preprocess_result.checksum:
            tx.source_checksum = preprocess_result.checksum

        tx.content_saved = True

        if preprocess_result.errors:
            tx.has_errors = True
            for step, error in preprocess_result.errors:
                self._log(tx, ActivityClass.Pre_Processing, Severity.Error,
                          f'{step}: {error}')
        else:
            self._log(tx, ActivityClass.Pre_Processing, Severity.Info,
                      'Pre-processing completed successfully')

        self.store.update_transaction(tx)

# ################################################################################################################################

    def _phase5_rule_evaluation(self, tx:'Transaction') -> 'any_ | None':

        rules = self.store.list_enabled_processing_rules()
        matched_rule = self.rule_evaluator.evaluate(tx, rules)

        if matched_rule:
            tx.matched_rule_id = matched_rule.id
            self._log(tx, ActivityClass.Rule_Evaluation, Severity.Info,
                      f'Matched rule: {matched_rule.name} (ordinal {matched_rule.ordinal})')
        else:
            tx.processing_status = ProcessingStatus.Not_Routed
            self._log(tx, ActivityClass.Rule_Evaluation, Severity.Warning,
                      'No processing rule matched')

        self.store.update_transaction(tx)
        return matched_rule

# ################################################################################################################################

    def _phase6_action_execution(
        self,
        tx:'Transaction',
        matched_rule:'any_ | None',
        content:'bytes',
    ) -> 'None':

        if not matched_rule:
            return

        for action in matched_rule.actions:
            result = self.action_executor.execute(action, tx, content)

            action_type = action.type.value if hasattr(action.type, 'value') else str(action.type)

            if result.is_ok:
                self._log(tx, ActivityClass.Action, Severity.Info,
                          f'Action executed: {action_type}')
            else:
                tx.has_errors = True
                self._log(tx, ActivityClass.Action, Severity.Error,
                          f'Action failed: {action_type} - {result.error}')

        self.store.update_transaction(tx)

# ################################################################################################################################

    def _phase7_completion(self, tx:'Transaction', start_time:'float') -> 'None':

        end_time = time.time()
        tx.completed = end_time
        tx.duration_ms = int((end_time - start_time) * 1000)

        if tx.processing_status == ProcessingStatus.Not_Routed:
            pass
        elif tx.has_errors:
            tx.processing_status = ProcessingStatus.Done_W_Errors
        else:
            tx.processing_status = ProcessingStatus.Done

        self._log(tx, ActivityClass.Completion, Severity.Info,
                  f'Processing complete: status={tx.processing_status.value}, duration={tx.duration_ms}ms')

        self.store.update_transaction(tx)

# ################################################################################################################################

    def resubmit(self, tx_id:'str') -> 'Transaction | None':

        original_tx = self.store.get_transaction(tx_id)
        if not original_tx:
            return None

        content = self.store.get_content(tx_id)
        if not content:
            return None

        new_tx = self.process_file(
            original_tx.filename,
            content,
            original_tx.source_protocol,
            original_tx.source_detail,
        )

        new_tx.resubmitted_from = tx_id
        self.store.update_transaction(new_tx)

        return new_tx

# ################################################################################################################################

    def reprocess(self, tx_id:'str') -> 'Transaction | None':

        tx = self.store.get_transaction(tx_id)
        if not tx:
            return None

        content = self.store.get_content(tx_id)

        start_time = time.time()

        self._log(tx, ActivityClass.Receipt, Severity.Info,
                  f'Reprocessing transaction {tx_id}')

        matched_rule = self._phase5_rule_evaluation(tx)

        self._phase6_action_execution(tx, matched_rule, content)

        self._phase7_completion(tx, start_time)

        return tx

# ################################################################################################################################

    def _log(
        self,
        tx:'Transaction',
        activity_class:'ActivityClass',
        severity:'Severity',
        message:'str',
        detail:'str'='',
    ) -> 'None':

        seq = self.store.next_log_seq(tx.id)
        entry_id = f'{tx.id}:{seq:04d}'

        entry = ActivityLogEntry(
            id=entry_id,
            transaction_id=tx.id,
            timestamp=time.time(),
            activity_class=activity_class,
            severity=severity,
            message=message,
            detail=detail,
        )

        self.store.create_log_entry(entry)

# ################################################################################################################################
# ################################################################################################################################
