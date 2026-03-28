# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from enum import Enum

# ################################################################################################################################
# ################################################################################################################################

class ProcessingStatus(str, Enum):
    New = 'NEW'
    Done = 'DONE'
    Done_W_Errors = 'DONE_W_ERRORS'
    Failed = 'FAILED'
    Queued = 'QUEUED'
    Not_Routed = 'NOT_ROUTED'
    Aborted = 'ABORTED'

# ################################################################################################################################
# ################################################################################################################################

class TaskStatus(str, Enum):
    New = 'NEW'
    Pending = 'PENDING'
    Delivering = 'DELIVERING'
    Done = 'DONE'
    Failed = 'FAILED'
    Stopped = 'STOPPED'

# ################################################################################################################################
# ################################################################################################################################

class ActivityClass(str, Enum):
    Receipt = 'RECEIPT'
    Recognition = 'RECOGNITION'
    Extraction = 'EXTRACTION'
    Pre_Processing = 'PRE_PROCESSING'
    Rule_Evaluation = 'RULE_EVALUATION'
    Action = 'ACTION'
    Delivery = 'DELIVERY'
    Completion = 'COMPLETION'
    Error = 'ERROR'

# ################################################################################################################################
# ################################################################################################################################

class Severity(str, Enum):
    Info = 'INFO'
    Warning = 'WARNING'
    Error = 'ERROR'

# ################################################################################################################################
# ################################################################################################################################

class FileType(str, Enum):
    Xml = 'XML'
    Json = 'JSON'
    Flat_File = 'FLAT_FILE'
    Binary = 'BINARY'
    Edi = 'EDI'

# ################################################################################################################################
# ################################################################################################################################

class ActionType(str, Enum):
    Execute_Service = 'EXECUTE_SERVICE'
    Deliver = 'DELIVER'
    Notify = 'NOTIFY'
    Change_Status = 'CHANGE_STATUS'

# ################################################################################################################################
# ################################################################################################################################

class ExecMode(str, Enum):
    Synchronous = 'SYNCHRONOUS'
    Asynchronous = 'ASYNCHRONOUS'
    Reliable = 'RELIABLE'

# ################################################################################################################################
# ################################################################################################################################

class PreprocessSavePolicy(str, Enum):
    All = 'ALL'
    Unique = 'UNIQUE'
    None_ = 'NONE'

# ################################################################################################################################
# ################################################################################################################################

class CriteriaMatch(str, Enum):
    Any = 'ANY'
    Unknown = 'UNKNOWN'
    Specific = 'SPECIFIC'

# ################################################################################################################################
# ################################################################################################################################

class ErrorCriteria(str, Enum):
    Any = 'ANY'
    No_Errors = 'NO_ERRORS'
    Has_Errors = 'HAS_ERRORS'

# ################################################################################################################################
# ################################################################################################################################

class RecognitionRuleType(str, Enum):
    Filename_Glob = 'FILENAME_GLOB'
    Content_Regex = 'CONTENT_REGEX'
    Xml_Root_Tag = 'XML_ROOT_TAG'
    Json_Path = 'JSON_PATH'
    Pgp_Header = 'PGP_HEADER'
    Edi_Segment = 'EDI_SEGMENT'

# ################################################################################################################################
# ################################################################################################################################

class ExtractionQueryType(str, Enum):
    Xpath = 'XPATH'
    Jsonpath = 'JSONPATH'
    Regex = 'REGEX'
    Fixed = 'FIXED'

# ################################################################################################################################
# ################################################################################################################################

class AttributeType(str, Enum):
    System = 'SYSTEM'
    Custom = 'CUSTOM'

# ################################################################################################################################
# ################################################################################################################################

class DataType(str, Enum):
    String = 'STRING'
    Number = 'NUMBER'
    Date = 'DATE'

# ################################################################################################################################
# ################################################################################################################################

class DeliveryMethod(str, Enum):
    Sftp = 'SFTP'
    Ftp = 'FTP'
    Ftps = 'FTPS'
    Http = 'HTTP'
    Https = 'HTTPS'
    Amqp = 'AMQP'
    Smtp = 'SMTP'
    S3 = 'S3'
    Azure_Blob = 'AZURE_BLOB'
    Receiver_Preferred = 'RECEIVER_PREFERRED'

# ################################################################################################################################
# ################################################################################################################################

class NotificationChannel(str, Enum):
    Email = 'EMAIL'
    Webhook = 'WEBHOOK'
    Pubsub = 'PUBSUB'

# ################################################################################################################################
# ################################################################################################################################

class TaskType(str, Enum):
    Delivery = 'DELIVERY'
    Service_Execution = 'SERVICE_EXECUTION'

# ################################################################################################################################
# ################################################################################################################################

class PreprocessStep(str, Enum):
    Validate = 'VALIDATE'
    Dedup = 'DEDUP'
    Pgp_Verify = 'PGP_VERIFY'
    Checksum = 'CHECKSUM'
    Save = 'SAVE'

# ################################################################################################################################
# ################################################################################################################################

class PreprocessOverride(str, Enum):
    Defer = 'DEFER'
    Force_On = 'FORCE_ON'
    Force_Off = 'FORCE_OFF'

# ################################################################################################################################
# ################################################################################################################################

class ExtendedCriteriaOperator(str, Enum):
    Equals = 'EQUALS'
    Not_Equals = 'NOT_EQUALS'
    Contains = 'CONTAINS'
    Begins_With = 'BEGINS_WITH'
    Ends_With = 'ENDS_WITH'
    Is_Null = 'IS_NULL'
    Is_Not_Null = 'IS_NOT_NULL'
    Greater_Than = 'GREATER_THAN'
    Less_Than = 'LESS_THAN'
    Greater_Or_Equal = 'GREATER_OR_EQUAL'
    Less_Or_Equal = 'LESS_OR_EQUAL'
    Before = 'BEFORE'
    After = 'AFTER'

# ################################################################################################################################
# ################################################################################################################################

class PostProcessingAction(str, Enum):
    Move = 'MOVE'
    Delete = 'DELETE'
    None_ = 'NONE'

# ################################################################################################################################
# ################################################################################################################################

class KeyType(str, Enum):
    Public = 'PUBLIC'
    Private = 'PRIVATE'

# ################################################################################################################################
# ################################################################################################################################

class KeyUsage(str, Enum):
    Encrypt = 'ENCRYPT'
    Decrypt = 'DECRYPT'
    Sign = 'SIGN'
    Verify = 'VERIFY'

# ################################################################################################################################
# ################################################################################################################################

class PickupSourceType(str, Enum):
    Sftp = 'SFTP'
    Ftp = 'FTP'
    S3 = 'S3'
    Azure_Blob = 'AZURE_BLOB'
    Imap = 'IMAP'
    Smtp = 'SMTP'

# ################################################################################################################################
# ################################################################################################################################

REDIS_KEY_PREFIX = 'zato:file-transfer'

# ################################################################################################################################
# ################################################################################################################################

class RedisKey:

    @staticmethod
    def txn(cluster_id, txn_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:txn:{txn_id}'

    @staticmethod
    def doc_type(cluster_id, dt_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:doc-type:{dt_id}'

    @staticmethod
    def rule(cluster_id, rule_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:rule:{rule_id}'

    @staticmethod
    def task(cluster_id, task_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:task:{task_id}'

    @staticmethod
    def log_entry(cluster_id, txn_id, seq):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:log:{txn_id}:{seq:04d}'

    @staticmethod
    def pgp_key(cluster_id, key_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:pgp-key:{key_id}'

    @staticmethod
    def content(cluster_id, txn_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:content:{txn_id}'

    @staticmethod
    def settings(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:settings'

    @staticmethod
    def seq_txn(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:seq:txn'

    @staticmethod
    def seq_task(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:seq:task'

    @staticmethod
    def seq_log(cluster_id, txn_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:seq:log:{txn_id}'

    @staticmethod
    def set_doc_types(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:set:doc-types'

    @staticmethod
    def set_rules(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:set:rules'

    @staticmethod
    def set_pgp_keys(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:set:pgp-keys'

    @staticmethod
    def set_user_statuses(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:set:user-statuses'

    @staticmethod
    def idx_txn_by_created(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:txn:by-created'

    @staticmethod
    def idx_txn_by_status(cluster_id, status):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:txn:by-status:{status}'

    @staticmethod
    def idx_txn_by_sender(cluster_id, sender):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:txn:by-sender:{sender}'

    @staticmethod
    def idx_txn_by_receiver(cluster_id, receiver):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:txn:by-receiver:{receiver}'

    @staticmethod
    def idx_txn_by_doc_type(cluster_id, dt_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:txn:by-doc-type:{dt_id}'

    @staticmethod
    def idx_txn_by_conv(cluster_id, conv_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:txn:by-conv:{conv_id}'

    @staticmethod
    def idx_txn_by_group(cluster_id, group_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:txn:by-group:{group_id}'

    @staticmethod
    def idx_task_by_status(cluster_id, status):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:task:by-status:{status}'

    @staticmethod
    def idx_task_by_txn(cluster_id, txn_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:task:by-txn:{txn_id}'

    @staticmethod
    def idx_task_retry_schedule(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:task:retry-schedule'

    @staticmethod
    def idx_log_by_txn(cluster_id, txn_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:log:by-txn:{txn_id}'

    @staticmethod
    def idx_log_by_class(cluster_id, activity_class):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:log:by-class:{activity_class}'

    @staticmethod
    def idx_log_by_severity(cluster_id, severity):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:log:by-severity:{severity}'

    @staticmethod
    def idx_log_global(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:log:global'

    @staticmethod
    def idx_rule_order(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:rule:order'

    @staticmethod
    def dedup(cluster_id, doc_id, sender, doc_type_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:dedup:{doc_id}:{sender}:{doc_type_id}'

    @staticmethod
    def pickup_channel(cluster_id, channel_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:pickup-channel:{channel_id}'

    @staticmethod
    def set_pickup_channels(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:set:pickup-channels'

# ################################################################################################################################
# ################################################################################################################################

DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_WAIT_MS = 60000
DEFAULT_BACKOFF_FACTOR = 2.0
DEFAULT_SAVE_POLICY = PreprocessSavePolicy.All
DEFAULT_MAX_SEARCH_RESULTS = 20000
DEFAULT_ARCHIVE_AFTER_DAYS = 90
DEFAULT_LOG_RETENTION_DAYS = 365
DEFAULT_CHECKSUM_ALGORITHM = 'SHA-256'

# ################################################################################################################################
# ################################################################################################################################
