# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from dataclasses import dataclass, field

# Zato
from zato.common.file_transfer.const import (
    ActionType,
    ActivityClass,
    AttributeType,
    CriteriaMatch,
    DataType,
    DeliveryMethod,
    ErrorCriteria,
    ExecMode,
    ExtractionQueryType,
    FileType,
    KeyType,
    KeyUsage,
    NotificationChannel,
    PickupSourceType,
    PostProcessingAction,
    PreprocessOverride,
    PreprocessSavePolicy,
    ProcessingStatus,
    RecognitionRuleType,
    Severity,
    TaskStatus,
    TaskType,
)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class RecognitionRule:
    type: 'RecognitionRuleType'
    pattern: 'str' = ''
    tag: 'str' = ''
    path: 'str' = ''
    segment: 'str' = ''
    transaction_set: 'str' = ''
    bytes_limit: 'int' = 0
    priority: 'int' = 1

    def to_dict(self) -> 'strdict':
        return {
            'type': self.type.value if isinstance(self.type, RecognitionRuleType) else self.type,
            'pattern': self.pattern,
            'tag': self.tag,
            'path': self.path,
            'segment': self.segment,
            'transaction_set': self.transaction_set,
            'bytes_limit': self.bytes_limit,
            'priority': self.priority,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'RecognitionRule':
        rule_type = data.get('type', '')
        if isinstance(rule_type, str):
            rule_type = RecognitionRuleType(rule_type)
        return cls(
            type=rule_type,
            pattern=data.get('pattern', ''),
            tag=data.get('tag', ''),
            path=data.get('path', ''),
            segment=data.get('segment', ''),
            transaction_set=data.get('transaction_set', ''),
            bytes_limit=int(data.get('bytes_limit', 0) or 0),
            priority=int(data.get('priority', 1) or 1),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ExtractionRule:
    attribute: 'str'
    attr_type: 'AttributeType'
    query_type: 'ExtractionQueryType'
    query: 'str' = ''
    value: 'str' = ''
    line: 'int' = 0
    data_type: 'DataType' = DataType.String
    required: 'bool' = False

    def to_dict(self) -> 'strdict':
        return {
            'attribute': self.attribute,
            'attr_type': self.attr_type.value if isinstance(self.attr_type, AttributeType) else self.attr_type,
            'query_type': self.query_type.value if isinstance(self.query_type, ExtractionQueryType) else self.query_type,
            'query': self.query,
            'value': self.value,
            'line': self.line,
            'data_type': self.data_type.value if isinstance(self.data_type, DataType) else self.data_type,
            'required': self.required,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'ExtractionRule':
        attr_type = data.get('attr_type', AttributeType.Custom)
        if isinstance(attr_type, str):
            attr_type = AttributeType(attr_type)

        query_type = data.get('query_type', ExtractionQueryType.Fixed)
        if isinstance(query_type, str):
            query_type = ExtractionQueryType(query_type)

        data_type = data.get('data_type', DataType.String)
        if isinstance(data_type, str):
            data_type = DataType(data_type)

        return cls(
            attribute=data.get('attribute', ''),
            attr_type=attr_type,
            query_type=query_type,
            query=data.get('query', ''),
            value=data.get('value', ''),
            line=int(data.get('line', 0) or 0),
            data_type=data_type,
            required=bool(data.get('required', False)),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class DocumentType:
    id: 'str'
    name: 'str'
    description: 'str' = ''
    is_enabled: 'bool' = True
    file_type: 'FileType' = FileType.Flat_File
    recognition_rules: 'list[RecognitionRule]' = field(default_factory=list)
    extraction_rules: 'list[ExtractionRule]' = field(default_factory=list)
    preprocess_validate: 'bool' = False
    preprocess_validate_schema: 'str' = ''
    preprocess_dedup: 'bool' = False
    preprocess_dedup_window_days: 'int' = 30
    preprocess_pgp_verify: 'bool' = False
    preprocess_pgp_key_id: 'str' = ''
    preprocess_checksum: 'bool' = False
    preprocess_save: 'PreprocessSavePolicy' = PreprocessSavePolicy.All

    def to_dict(self) -> 'strdict':
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_enabled': str(self.is_enabled).lower(),
            'file_type': self.file_type.value if isinstance(self.file_type, FileType) else self.file_type,
            'recognition_rules': json.dumps([r.to_dict() for r in self.recognition_rules]),
            'extraction_rules': json.dumps([r.to_dict() for r in self.extraction_rules]),
            'preprocess_validate': str(self.preprocess_validate).lower(),
            'preprocess_validate_schema': self.preprocess_validate_schema,
            'preprocess_dedup': str(self.preprocess_dedup).lower(),
            'preprocess_dedup_window_days': str(self.preprocess_dedup_window_days),
            'preprocess_pgp_verify': str(self.preprocess_pgp_verify).lower(),
            'preprocess_pgp_key_id': self.preprocess_pgp_key_id,
            'preprocess_checksum': str(self.preprocess_checksum).lower(),
            'preprocess_save': self.preprocess_save.value if isinstance(self.preprocess_save, PreprocessSavePolicy) else self.preprocess_save,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'DocumentType':
        file_type = data.get('file_type', FileType.Flat_File)
        if isinstance(file_type, str):
            file_type = FileType(file_type)

        recognition_rules_raw = data.get('recognition_rules', '[]')
        if isinstance(recognition_rules_raw, str):
            recognition_rules_raw = json.loads(recognition_rules_raw)
        recognition_rules = [RecognitionRule.from_dict(r) for r in recognition_rules_raw]

        extraction_rules_raw = data.get('extraction_rules', '[]')
        if isinstance(extraction_rules_raw, str):
            extraction_rules_raw = json.loads(extraction_rules_raw)
        extraction_rules = [ExtractionRule.from_dict(r) for r in extraction_rules_raw]

        preprocess_save = data.get('preprocess_save', PreprocessSavePolicy.All)
        if isinstance(preprocess_save, str):
            preprocess_save = PreprocessSavePolicy(preprocess_save)

        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            is_enabled=data.get('is_enabled', 'true').lower() == 'true' if isinstance(data.get('is_enabled'), str) else bool(data.get('is_enabled', True)),
            file_type=file_type,
            recognition_rules=recognition_rules,
            extraction_rules=extraction_rules,
            preprocess_validate=data.get('preprocess_validate', 'false').lower() == 'true' if isinstance(data.get('preprocess_validate'), str) else bool(data.get('preprocess_validate', False)),
            preprocess_validate_schema=data.get('preprocess_validate_schema', ''),
            preprocess_dedup=data.get('preprocess_dedup', 'false').lower() == 'true' if isinstance(data.get('preprocess_dedup'), str) else bool(data.get('preprocess_dedup', False)),
            preprocess_dedup_window_days=int(data.get('preprocess_dedup_window_days', 30) or 30),
            preprocess_pgp_verify=data.get('preprocess_pgp_verify', 'false').lower() == 'true' if isinstance(data.get('preprocess_pgp_verify'), str) else bool(data.get('preprocess_pgp_verify', False)),
            preprocess_pgp_key_id=data.get('preprocess_pgp_key_id', ''),
            preprocess_checksum=data.get('preprocess_checksum', 'false').lower() == 'true' if isinstance(data.get('preprocess_checksum'), str) else bool(data.get('preprocess_checksum', False)),
            preprocess_save=preprocess_save,
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class CriteriaSpec:
    match: 'CriteriaMatch' = CriteriaMatch.Any
    values: 'list[str]' = field(default_factory=list)

    def to_dict(self) -> 'strdict':
        return {
            'match': self.match.value if isinstance(self.match, CriteriaMatch) else self.match,
            'values': self.values,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'CriteriaSpec':
        match = data.get('match', CriteriaMatch.Any)
        if isinstance(match, str):
            match = CriteriaMatch(match)
        return cls(
            match=match,
            values=data.get('values', []),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ExtendedCriteria:
    attribute: 'str'
    operator: 'str'
    value: 'str'

    def to_dict(self) -> 'strdict':
        return {
            'attribute': self.attribute,
            'operator': self.operator,
            'value': self.value,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'ExtendedCriteria':
        return cls(
            attribute=data.get('attribute', ''),
            operator=data.get('operator', ''),
            value=data.get('value', ''),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class RuleAction:
    type: 'ActionType'
    service_name: 'str' = ''
    exec_mode: 'ExecMode' = ExecMode.Synchronous
    method: 'DeliveryMethod' = DeliveryMethod.Sftp
    connection: 'str' = ''
    path: 'str' = ''
    channel: 'NotificationChannel' = NotificationChannel.Email
    to: 'str' = ''
    subject: 'str' = ''
    body: 'str' = ''
    new_status: 'str' = ''
    max_retries: 'int' = 3
    retry_wait_ms: 'int' = 60000
    backoff_factor: 'float' = 2.0

    def to_dict(self) -> 'strdict':
        return {
            'type': self.type.value if isinstance(self.type, ActionType) else self.type,
            'service_name': self.service_name,
            'exec_mode': self.exec_mode.value if isinstance(self.exec_mode, ExecMode) else self.exec_mode,
            'method': self.method.value if isinstance(self.method, DeliveryMethod) else self.method,
            'connection': self.connection,
            'path': self.path,
            'channel': self.channel.value if isinstance(self.channel, NotificationChannel) else self.channel,
            'to': self.to,
            'subject': self.subject,
            'body': self.body,
            'new_status': self.new_status,
            'max_retries': self.max_retries,
            'retry_wait_ms': self.retry_wait_ms,
            'backoff_factor': self.backoff_factor,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'RuleAction':
        action_type = data.get('type', ActionType.Change_Status)
        if isinstance(action_type, str):
            action_type = ActionType(action_type)

        exec_mode = data.get('exec_mode', ExecMode.Synchronous)
        if isinstance(exec_mode, str):
            exec_mode = ExecMode(exec_mode)

        method = data.get('method', DeliveryMethod.Sftp)
        if isinstance(method, str):
            method = DeliveryMethod(method)

        channel = data.get('channel', NotificationChannel.Email)
        if isinstance(channel, str):
            channel = NotificationChannel(channel)

        return cls(
            type=action_type,
            service_name=data.get('service_name', ''),
            exec_mode=exec_mode,
            method=method,
            connection=data.get('connection', ''),
            path=data.get('path', ''),
            channel=channel,
            to=data.get('to', ''),
            subject=data.get('subject', ''),
            body=data.get('body', ''),
            new_status=data.get('new_status', ''),
            max_retries=int(data.get('max_retries', 3) or 3),
            retry_wait_ms=int(data.get('retry_wait_ms', 60000) or 60000),
            backoff_factor=float(data.get('backoff_factor', 2.0) or 2.0),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PreprocessOverrides:
    validate: 'PreprocessOverride' = PreprocessOverride.Defer
    dedup: 'PreprocessOverride' = PreprocessOverride.Defer
    pgp_verify: 'PreprocessOverride' = PreprocessOverride.Defer
    checksum: 'PreprocessOverride' = PreprocessOverride.Defer
    save: 'PreprocessOverride' = PreprocessOverride.Defer

    def to_dict(self) -> 'strdict':
        return {
            'validate': self.validate.value if isinstance(self.validate, PreprocessOverride) else self.validate,
            'dedup': self.dedup.value if isinstance(self.dedup, PreprocessOverride) else self.dedup,
            'pgp_verify': self.pgp_verify.value if isinstance(self.pgp_verify, PreprocessOverride) else self.pgp_verify,
            'checksum': self.checksum.value if isinstance(self.checksum, PreprocessOverride) else self.checksum,
            'save': self.save.value if isinstance(self.save, PreprocessOverride) else self.save,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'PreprocessOverrides':
        def get_override(key):
            val = data.get(key, PreprocessOverride.Defer)
            if isinstance(val, str):
                val = PreprocessOverride(val)
            return val
        return cls(
            validate=get_override('validate'),
            dedup=get_override('dedup'),
            pgp_verify=get_override('pgp_verify'),
            checksum=get_override('checksum'),
            save=get_override('save'),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ProcessingRule:
    id: 'str'
    name: 'str'
    description: 'str' = ''
    ordinal: 'int' = 0
    is_enabled: 'bool' = True
    is_default: 'bool' = False
    criteria_sender: 'CriteriaSpec' = field(default_factory=CriteriaSpec)
    criteria_receiver: 'CriteriaSpec' = field(default_factory=CriteriaSpec)
    criteria_doc_type: 'CriteriaSpec' = field(default_factory=CriteriaSpec)
    criteria_user_status: 'CriteriaSpec' = field(default_factory=CriteriaSpec)
    criteria_errors: 'ErrorCriteria' = ErrorCriteria.Any
    criteria_extended: 'list[ExtendedCriteria]' = field(default_factory=list)
    preprocess_overrides: 'PreprocessOverrides' = field(default_factory=PreprocessOverrides)
    actions: 'list[RuleAction]' = field(default_factory=list)

    def to_dict(self) -> 'strdict':
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ordinal': str(self.ordinal),
            'is_enabled': str(self.is_enabled).lower(),
            'is_default': str(self.is_default).lower(),
            'criteria_sender': json.dumps(self.criteria_sender.to_dict()),
            'criteria_receiver': json.dumps(self.criteria_receiver.to_dict()),
            'criteria_doc_type': json.dumps(self.criteria_doc_type.to_dict()),
            'criteria_user_status': json.dumps(self.criteria_user_status.to_dict()),
            'criteria_errors': self.criteria_errors.value if isinstance(self.criteria_errors, ErrorCriteria) else self.criteria_errors,
            'criteria_extended': json.dumps([c.to_dict() for c in self.criteria_extended]),
            'preprocess_overrides': json.dumps(self.preprocess_overrides.to_dict()),
            'actions': json.dumps([a.to_dict() for a in self.actions]),
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'ProcessingRule':
        criteria_sender_raw = data.get('criteria_sender', '{}')
        if isinstance(criteria_sender_raw, str):
            criteria_sender_raw = json.loads(criteria_sender_raw)
        criteria_sender = CriteriaSpec.from_dict(criteria_sender_raw)

        criteria_receiver_raw = data.get('criteria_receiver', '{}')
        if isinstance(criteria_receiver_raw, str):
            criteria_receiver_raw = json.loads(criteria_receiver_raw)
        criteria_receiver = CriteriaSpec.from_dict(criteria_receiver_raw)

        criteria_doc_type_raw = data.get('criteria_doc_type', '{}')
        if isinstance(criteria_doc_type_raw, str):
            criteria_doc_type_raw = json.loads(criteria_doc_type_raw)
        criteria_doc_type = CriteriaSpec.from_dict(criteria_doc_type_raw)

        criteria_user_status_raw = data.get('criteria_user_status', '{}')
        if isinstance(criteria_user_status_raw, str):
            criteria_user_status_raw = json.loads(criteria_user_status_raw)
        criteria_user_status = CriteriaSpec.from_dict(criteria_user_status_raw)

        criteria_errors = data.get('criteria_errors', ErrorCriteria.Any)
        if isinstance(criteria_errors, str):
            criteria_errors = ErrorCriteria(criteria_errors)

        criteria_extended_raw = data.get('criteria_extended', '[]')
        if isinstance(criteria_extended_raw, str):
            criteria_extended_raw = json.loads(criteria_extended_raw)
        criteria_extended = [ExtendedCriteria.from_dict(c) for c in criteria_extended_raw]

        preprocess_overrides_raw = data.get('preprocess_overrides', '{}')
        if isinstance(preprocess_overrides_raw, str):
            preprocess_overrides_raw = json.loads(preprocess_overrides_raw)
        preprocess_overrides = PreprocessOverrides.from_dict(preprocess_overrides_raw)

        actions_raw = data.get('actions', '[]')
        if isinstance(actions_raw, str):
            actions_raw = json.loads(actions_raw)
        actions = [RuleAction.from_dict(a) for a in actions_raw]

        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            ordinal=int(data.get('ordinal', 0) or 0),
            is_enabled=data.get('is_enabled', 'true').lower() == 'true' if isinstance(data.get('is_enabled'), str) else bool(data.get('is_enabled', True)),
            is_default=data.get('is_default', 'false').lower() == 'true' if isinstance(data.get('is_default'), str) else bool(data.get('is_default', False)),
            criteria_sender=criteria_sender,
            criteria_receiver=criteria_receiver,
            criteria_doc_type=criteria_doc_type,
            criteria_user_status=criteria_user_status,
            criteria_errors=criteria_errors,
            criteria_extended=criteria_extended,
            preprocess_overrides=preprocess_overrides,
            actions=actions,
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Transaction:
    id: 'str'
    created: 'float'
    completed: 'float | None' = None
    filename: 'str' = ''
    file_size: 'int' = 0
    source_checksum: 'str' = ''
    dest_checksum: 'str' = ''
    source_protocol: 'str' = ''
    source_detail: 'str' = ''
    doc_type_id: 'str' = ''
    sender: 'str' = ''
    receiver: 'str' = ''
    document_id: 'str' = ''
    exchange_id: 'str' = ''
    group_id: 'str' = ''
    processing_status: 'ProcessingStatus' = ProcessingStatus.New
    user_status: 'str' = ''
    matched_rule_id: 'str' = ''
    has_errors: 'bool' = False
    duration_ms: 'int' = 0
    content_saved: 'bool' = False
    resubmitted_from: 'str' = ''
    custom_attrs: 'strdict' = field(default_factory=dict)

    def to_dict(self) -> 'strdict':
        return {
            'id': self.id,
            'created': str(self.created),
            'completed': str(self.completed) if self.completed else '',
            'filename': self.filename,
            'file_size': str(self.file_size),
            'source_checksum': self.source_checksum,
            'dest_checksum': self.dest_checksum,
            'source_protocol': self.source_protocol,
            'source_detail': self.source_detail,
            'doc_type_id': self.doc_type_id,
            'sender': self.sender,
            'receiver': self.receiver,
            'document_id': self.document_id,
            'exchange_id': self.exchange_id,
            'group_id': self.group_id,
            'processing_status': self.processing_status.value if isinstance(self.processing_status, ProcessingStatus) else self.processing_status,
            'user_status': self.user_status,
            'matched_rule_id': self.matched_rule_id,
            'has_errors': str(self.has_errors).lower(),
            'duration_ms': str(self.duration_ms),
            'content_saved': str(self.content_saved).lower(),
            'resubmitted_from': self.resubmitted_from,
            'custom_attrs': json.dumps(self.custom_attrs),
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'Transaction':
        processing_status = data.get('processing_status', ProcessingStatus.New)
        if isinstance(processing_status, str):
            processing_status = ProcessingStatus(processing_status)

        custom_attrs_raw = data.get('custom_attrs', '{}')
        if isinstance(custom_attrs_raw, str):
            custom_attrs = json.loads(custom_attrs_raw)
        else:
            custom_attrs = custom_attrs_raw

        completed_raw = data.get('completed', '')
        completed = float(completed_raw) if completed_raw else None

        return cls(
            id=data.get('id', ''),
            created=float(data.get('created', 0) or 0),
            completed=completed,
            filename=data.get('filename', ''),
            file_size=int(data.get('file_size', 0) or 0),
            source_checksum=data.get('source_checksum', ''),
            dest_checksum=data.get('dest_checksum', ''),
            source_protocol=data.get('source_protocol', ''),
            source_detail=data.get('source_detail', ''),
            doc_type_id=data.get('doc_type_id', ''),
            sender=data.get('sender', ''),
            receiver=data.get('receiver', ''),
            document_id=data.get('document_id', ''),
            exchange_id=data.get('exchange_id', ''),
            group_id=data.get('group_id', ''),
            processing_status=processing_status,
            user_status=data.get('user_status', ''),
            matched_rule_id=data.get('matched_rule_id', ''),
            has_errors=data.get('has_errors', 'false').lower() == 'true' if isinstance(data.get('has_errors'), str) else bool(data.get('has_errors', False)),
            duration_ms=int(data.get('duration_ms', 0) or 0),
            content_saved=data.get('content_saved', 'false').lower() == 'true' if isinstance(data.get('content_saved'), str) else bool(data.get('content_saved', False)),
            resubmitted_from=data.get('resubmitted_from', ''),
            custom_attrs=custom_attrs,
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Task:
    id: 'str'
    transaction_id: 'str'
    task_type: 'TaskType'
    status: 'TaskStatus' = TaskStatus.New
    created: 'float' = 0.0
    updated: 'float' = 0.0
    retry_count: 'int' = 0
    max_retries: 'int' = 3
    retry_wait_ms: 'int' = 60000
    backoff_factor: 'float' = 2.0
    next_retry_at: 'float | None' = None
    error_detail: 'str' = ''
    service_name: 'str' = ''
    delivery_protocol: 'str' = ''
    delivery_detail: 'str' = ''

    def to_dict(self) -> 'strdict':
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'task_type': self.task_type.value if isinstance(self.task_type, TaskType) else self.task_type,
            'status': self.status.value if isinstance(self.status, TaskStatus) else self.status,
            'created': str(self.created),
            'updated': str(self.updated),
            'retry_count': str(self.retry_count),
            'max_retries': str(self.max_retries),
            'retry_wait_ms': str(self.retry_wait_ms),
            'backoff_factor': str(self.backoff_factor),
            'next_retry_at': str(self.next_retry_at) if self.next_retry_at else '',
            'error_detail': self.error_detail,
            'service_name': self.service_name,
            'delivery_protocol': self.delivery_protocol,
            'delivery_detail': self.delivery_detail,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'Task':
        task_type = data.get('task_type', TaskType.Delivery)
        if isinstance(task_type, str):
            task_type = TaskType(task_type)

        status = data.get('status', TaskStatus.New)
        if isinstance(status, str):
            status = TaskStatus(status)

        next_retry_at_raw = data.get('next_retry_at', '')
        next_retry_at = float(next_retry_at_raw) if next_retry_at_raw else None

        return cls(
            id=data.get('id', ''),
            transaction_id=data.get('transaction_id', ''),
            task_type=task_type,
            status=status,
            created=float(data.get('created', 0) or 0),
            updated=float(data.get('updated', 0) or 0),
            retry_count=int(data.get('retry_count', 0) or 0),
            max_retries=int(data.get('max_retries', 3) or 3),
            retry_wait_ms=int(data.get('retry_wait_ms', 60000) or 60000),
            backoff_factor=float(data.get('backoff_factor', 2.0) or 2.0),
            next_retry_at=next_retry_at,
            error_detail=data.get('error_detail', ''),
            service_name=data.get('service_name', ''),
            delivery_protocol=data.get('delivery_protocol', ''),
            delivery_detail=data.get('delivery_detail', ''),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ActivityLogEntry:
    id: 'str'
    transaction_id: 'str'
    timestamp: 'float'
    activity_class: 'ActivityClass'
    severity: 'Severity' = Severity.Info
    message: 'str' = ''
    detail: 'str' = ''

    def to_dict(self) -> 'strdict':
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'timestamp': str(self.timestamp),
            'activity_class': self.activity_class.value if isinstance(self.activity_class, ActivityClass) else self.activity_class,
            'severity': self.severity.value if isinstance(self.severity, Severity) else self.severity,
            'message': self.message,
            'detail': self.detail,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'ActivityLogEntry':
        activity_class = data.get('activity_class', ActivityClass.Receipt)
        if isinstance(activity_class, str):
            activity_class = ActivityClass(activity_class)

        severity = data.get('severity', Severity.Info)
        if isinstance(severity, str):
            severity = Severity(severity)

        return cls(
            id=data.get('id', ''),
            transaction_id=data.get('transaction_id', ''),
            timestamp=float(data.get('timestamp', 0) or 0),
            activity_class=activity_class,
            severity=severity,
            message=data.get('message', ''),
            detail=data.get('detail', ''),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PGPKey:
    id: 'str'
    name: 'str'
    key_type: 'KeyType'
    usage: 'list[KeyUsage]' = field(default_factory=list)
    key_data: 'str' = ''
    fingerprint: 'str' = ''
    algorithm: 'str' = ''
    key_size: 'int' = 0
    created_at: 'float' = 0.0
    expires_at: 'float | None' = None
    is_enabled: 'bool' = True

    def to_dict(self) -> 'strdict':
        usage_values = [u.value if isinstance(u, KeyUsage) else u for u in self.usage]
        return {
            'id': self.id,
            'name': self.name,
            'key_type': self.key_type.value if isinstance(self.key_type, KeyType) else self.key_type,
            'usage': ','.join(usage_values),
            'key_data': self.key_data,
            'fingerprint': self.fingerprint,
            'algorithm': self.algorithm,
            'key_size': str(self.key_size),
            'created_at': str(self.created_at),
            'expires_at': str(self.expires_at) if self.expires_at else '',
            'is_enabled': str(self.is_enabled).lower(),
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'PGPKey':
        key_type = data.get('key_type', KeyType.Public)
        if isinstance(key_type, str):
            key_type = KeyType(key_type)

        usage_raw = data.get('usage', '')
        if isinstance(usage_raw, str):
            usage_parts = [u.strip() for u in usage_raw.split(',') if u.strip()]
            usage = [KeyUsage(u) for u in usage_parts]
        else:
            usage = usage_raw

        expires_at_raw = data.get('expires_at', '')
        expires_at = float(expires_at_raw) if expires_at_raw else None

        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            key_type=key_type,
            usage=usage,
            key_data=data.get('key_data', ''),
            fingerprint=data.get('fingerprint', ''),
            algorithm=data.get('algorithm', ''),
            key_size=int(data.get('key_size', 0) or 0),
            created_at=float(data.get('created_at', 0) or 0),
            expires_at=expires_at,
            is_enabled=data.get('is_enabled', 'true').lower() == 'true' if isinstance(data.get('is_enabled'), str) else bool(data.get('is_enabled', True)),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Settings:
    default_retry_count: 'int' = 3
    default_retry_wait_ms: 'int' = 60000
    default_backoff_factor: 'float' = 2.0
    default_save_policy: 'PreprocessSavePolicy' = PreprocessSavePolicy.All
    max_search_results: 'int' = 20000
    archive_after_days: 'int' = 90
    log_retention_days: 'int' = 365
    checksum_algorithm: 'str' = 'SHA-256'

    def to_dict(self) -> 'strdict':
        return {
            'default_retry_count': str(self.default_retry_count),
            'default_retry_wait_ms': str(self.default_retry_wait_ms),
            'default_backoff_factor': str(self.default_backoff_factor),
            'default_save_policy': self.default_save_policy.value if isinstance(self.default_save_policy, PreprocessSavePolicy) else self.default_save_policy,
            'max_search_results': str(self.max_search_results),
            'archive_after_days': str(self.archive_after_days),
            'log_retention_days': str(self.log_retention_days),
            'checksum_algorithm': self.checksum_algorithm,
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'Settings':
        default_save_policy = data.get('default_save_policy', PreprocessSavePolicy.All)
        if isinstance(default_save_policy, str):
            default_save_policy = PreprocessSavePolicy(default_save_policy)

        return cls(
            default_retry_count=int(data.get('default_retry_count', 3) or 3),
            default_retry_wait_ms=int(data.get('default_retry_wait_ms', 60000) or 60000),
            default_backoff_factor=float(data.get('default_backoff_factor', 2.0) or 2.0),
            default_save_policy=default_save_policy,
            max_search_results=int(data.get('max_search_results', 20000) or 20000),
            archive_after_days=int(data.get('archive_after_days', 90) or 90),
            log_retention_days=int(data.get('log_retention_days', 365) or 365),
            checksum_algorithm=data.get('checksum_algorithm', 'SHA-256'),
        )

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PickupChannel:
    id: 'str'
    name: 'str'
    source_type: 'PickupSourceType'
    connection_name: 'str' = ''
    remote_path: 'str' = ''
    file_pattern: 'str' = '*'
    poll_interval_seconds: 'int' = 60
    post_processing_action: 'PostProcessingAction' = PostProcessingAction.Move
    archive_path: 'str' = ''
    is_enabled: 'bool' = True

    def to_dict(self) -> 'strdict':
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type.value if isinstance(self.source_type, PickupSourceType) else self.source_type,
            'connection_name': self.connection_name,
            'remote_path': self.remote_path,
            'file_pattern': self.file_pattern,
            'poll_interval_seconds': str(self.poll_interval_seconds),
            'post_processing_action': self.post_processing_action.value if isinstance(self.post_processing_action, PostProcessingAction) else self.post_processing_action,
            'archive_path': self.archive_path,
            'is_enabled': str(self.is_enabled).lower(),
        }

    @classmethod
    def from_dict(cls, data:'strdict') -> 'PickupChannel':
        source_type = data.get('source_type', PickupSourceType.Sftp)
        if isinstance(source_type, str):
            source_type = PickupSourceType(source_type)

        post_processing_action = data.get('post_processing_action', PostProcessingAction.Move)
        if isinstance(post_processing_action, str):
            post_processing_action = PostProcessingAction(post_processing_action)

        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            source_type=source_type,
            connection_name=data.get('connection_name', ''),
            remote_path=data.get('remote_path', ''),
            file_pattern=data.get('file_pattern', '*'),
            poll_interval_seconds=int(data.get('poll_interval_seconds', 60) or 60),
            post_processing_action=post_processing_action,
            archive_path=data.get('archive_path', ''),
            is_enabled=data.get('is_enabled', 'true').lower() == 'true' if isinstance(data.get('is_enabled'), str) else bool(data.get('is_enabled', True)),
        )

# ################################################################################################################################
# ################################################################################################################################
