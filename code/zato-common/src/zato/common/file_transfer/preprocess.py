# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import hashlib
import json

# lxml
from lxml import etree

# Zato
from zato.common.file_transfer.const import FileType, PreprocessSavePolicy
from zato.common.file_transfer.model import ActionResult, ChecksumResult, DedupResult, DocumentType, PreprocessResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.file_transfer.redis_store import FileTransferRedisStore
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class PreProcessor:

    def __init__(self, store:'FileTransferRedisStore') -> 'None':
        self.store = store

# ################################################################################################################################

    def validate_structure(
        self,
        content:'bytes',
        schema_ref:'str',
        file_type:'FileType',
    ) -> 'ActionResult':

        if not schema_ref:
            return ActionResult()

        file_type_val = file_type.value if isinstance(file_type, FileType) else file_type

        if file_type_val == FileType.Xml.value:
            return self._validate_xml_schema(content, schema_ref)

        elif file_type_val == FileType.Json.value:
            return self._validate_json_schema(content, schema_ref)

        elif file_type_val == FileType.Flat_File.value:
            return self._validate_csv_columns(content, schema_ref)

        return ActionResult()

# ################################################################################################################################

    def _validate_xml_schema(self, content:'bytes', schema_ref:'str') -> 'ActionResult':
        try:
            try:
                with open(schema_ref, 'rb') as f:
                    schema_content = f.read()
                schema_doc = etree.fromstring(schema_content)
                schema = etree.XMLSchema(schema_doc)
            except Exception as e:
                return ActionResult(is_ok=False, error=f'Could not load XML schema: {e}')

            doc = etree.fromstring(content)
            if schema.validate(doc):
                return ActionResult()
            else:
                errors = [str(err) for err in schema.error_log]
                return ActionResult(is_ok=False, error=f'XML validation failed: {"; ".join(errors)}')
        except Exception as e:
            return ActionResult(is_ok=False, error=f'XML validation error: {e}')

# ################################################################################################################################

    def _validate_json_schema(self, content:'bytes', schema_ref:'str') -> 'ActionResult':
        try:
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')

            data = json.loads(text)

            try:
                with open(schema_ref, 'r') as f:
                    schema = json.load(f)
            except Exception as e:
                return ActionResult(is_ok=False, error=f'Could not load JSON schema: {e}')

            try:
                import jsonschema
                jsonschema.validate(instance=data, schema=schema)
                return ActionResult()
            except ImportError:
                return ActionResult()
            except jsonschema.ValidationError as e:
                return ActionResult(is_ok=False, error=f'JSON validation failed: {e.message}')

        except json.JSONDecodeError as e:
            return ActionResult(is_ok=False, error=f'Invalid JSON: {e}')
        except Exception as e:
            return ActionResult(is_ok=False, error=f'JSON validation error: {e}')

# ################################################################################################################################

    def _validate_csv_columns(self, content:'bytes', schema_ref:'str') -> 'ActionResult':
        try:
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')

            lines = text.strip().split('\n')
            if not lines:
                return ActionResult(is_ok=False, error='Empty CSV file')

            try:
                expected_columns = int(schema_ref)
            except ValueError:
                return ActionResult()

            first_line = lines[0]
            actual_columns = len(first_line.split(','))

            if actual_columns != expected_columns:
                return ActionResult(is_ok=False, error=f'Expected {expected_columns} columns, found {actual_columns}')

            return ActionResult()
        except Exception as e:
            return ActionResult(is_ok=False, error=f'CSV validation error: {e}')

# ################################################################################################################################

    def check_duplicate(
        self,
        doc_id:'str',
        sender:'str',
        doc_type_id:'str',
        dedup_window_days:'int',
    ) -> 'DedupResult':

        if not doc_id:
            return DedupResult()

        existing_txn_id = self.store.check_duplicate(doc_id, sender, doc_type_id)

        if existing_txn_id:
            return DedupResult(is_ok=False, error=f'Duplicate document: already processed as {existing_txn_id}', existing_txn_id=existing_txn_id)

        return DedupResult()

# ################################################################################################################################

    def set_dedup_marker(
        self,
        doc_id:'str',
        sender:'str',
        doc_type_id:'str',
        txn_id:'str',
        dedup_window_days:'int',
    ) -> 'None':

        if doc_id:
            ttl_seconds = dedup_window_days * 24 * 60 * 60
            self.store.set_dedup_key(doc_id, sender, doc_type_id, txn_id, ttl_seconds)

# ################################################################################################################################

    def verify_pgp_signature(
        self,
        content:'bytes',
        expected_key_id:'str',
    ) -> 'ActionResult':

        if not expected_key_id:
            return ActionResult()

        pgp_key = self.store.get_pgp_key(expected_key_id)
        if not pgp_key:
            return ActionResult(is_ok=False, error=f'PGP key not found: {expected_key_id}')

        try:
            from zato.common.file_transfer.pgp import PGPManager
            pgp_manager = PGPManager()
            result = pgp_manager.verify(content, pgp_key.key_data)
            if result.is_ok:
                return ActionResult()
            else:
                return ActionResult(is_ok=False, error='PGP signature verification failed')
        except ImportError:
            return ActionResult()
        except Exception as e:
            return ActionResult(is_ok=False, error=f'PGP verification error: {e}')

# ################################################################################################################################

    def verify_checksum(
        self,
        content:'bytes',
        companion_checksum:'str',
        algorithm:'str'='SHA-256',
    ) -> 'ChecksumResult':

        if algorithm.upper() == 'SHA-256':
            computed = hashlib.sha256(content).hexdigest()
        elif algorithm.upper() == 'SHA-512':
            computed = hashlib.sha512(content).hexdigest()
        else:
            computed = hashlib.sha256(content).hexdigest()

        if companion_checksum:
            companion_checksum = companion_checksum.strip().lower()
            if computed.lower() != companion_checksum:
                return ChecksumResult(is_ok=False, error=f'Checksum mismatch: expected {companion_checksum}, computed {computed}', checksum=computed)

        return ChecksumResult(checksum=computed)

# ################################################################################################################################

    def save_content(
        self,
        txn_id:'str',
        content:'bytes',
        policy:'PreprocessSavePolicy',
        doc_id:'str'='',
        sender:'str'='',
        doc_type_id:'str'='',
    ) -> 'ActionResult':

        policy_val = policy.value if isinstance(policy, PreprocessSavePolicy) else policy

        if policy_val == PreprocessSavePolicy.None_.value:
            return ActionResult()

        if policy_val == PreprocessSavePolicy.Unique.value:
            if doc_id:
                existing = self.store.check_duplicate(doc_id, sender, doc_type_id)
                if existing:
                    return ActionResult()

        try:
            self.store.save_content(txn_id, content)
            return ActionResult()
        except Exception as e:
            return ActionResult(is_ok=False, error=f'Failed to save content: {e}')

# ################################################################################################################################

    def run_all_steps(
        self,
        txn_id:'str',
        content:'bytes',
        doc_type:'DocumentType',
        extracted_attrs:'dict',
        companion_checksum:'str'='',
    ) -> 'PreprocessResult':

        errors = []
        computed_checksum = ''

        if doc_type.preprocess_validate:
            result = self.validate_structure(
                content,
                doc_type.preprocess_validate_schema,
                doc_type.file_type,
            )
            if not result.is_ok:
                errors.append(('validate', result.error))

        if doc_type.preprocess_dedup:
            doc_id = extracted_attrs.get('document_id', '')
            sender = extracted_attrs.get('sender', '')
            result = self.check_duplicate(
                doc_id,
                sender,
                doc_type.id,
                doc_type.preprocess_dedup_window_days,
            )
            if not result.is_ok:
                errors.append(('dedup', result.error))
            else:
                self.set_dedup_marker(
                    doc_id,
                    sender,
                    doc_type.id,
                    txn_id,
                    doc_type.preprocess_dedup_window_days,
                )

        if doc_type.preprocess_pgp_verify:
            result = self.verify_pgp_signature(
                content,
                doc_type.preprocess_pgp_key_id,
            )
            if not result.is_ok:
                errors.append(('pgp_verify', result.error))

        if doc_type.preprocess_checksum:
            settings = self.store.get_settings()
            result = self.verify_checksum(
                content,
                companion_checksum,
                settings.checksum_algorithm,
            )
            computed_checksum = result.checksum
            if not result.is_ok:
                errors.append(('checksum', result.error))

        result = self.save_content(
            txn_id,
            content,
            doc_type.preprocess_save,
            extracted_attrs.get('document_id', ''),
            extracted_attrs.get('sender', ''),
            doc_type.id,
        )
        if not result.is_ok:
            errors.append(('save', result.error))

        has_errors = len(errors) > 0
        return PreprocessResult(is_ok=not has_errors, errors=errors, checksum=computed_checksum)

# ################################################################################################################################
# ################################################################################################################################
