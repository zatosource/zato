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
    New = 'New'
    Done = 'Done'
    Done_W_Errors = 'Done_W_Errors'
    Failed = 'Failed'
    Queued = 'Queued'
    Not_Routed = 'Not_Routed'
    Aborted = 'Aborted'

# ################################################################################################################################
# ################################################################################################################################

class TaskStatus(str, Enum):
    New = 'New'
    Pending = 'Pending'
    Delivering = 'Delivering'
    Done = 'Done'
    Failed = 'Failed'
    Stopped = 'Stopped'

# ################################################################################################################################
# ################################################################################################################################

class ActivityClass(str, Enum):
    Receipt = 'Receipt'
    Recognition = 'Recognition'
    Extraction = 'Extraction'
    Pre_Processing = 'Pre_Processing'
    Rule_Evaluation = 'Rule_Evaluation'
    Action = 'Action'
    Delivery = 'Delivery'
    Completion = 'Completion'
    Error = 'Error'

# ################################################################################################################################
# ################################################################################################################################

class Severity(str, Enum):
    Info = 'Info'
    Warning = 'Warning'
    Error = 'Error'

# ################################################################################################################################
# ################################################################################################################################

class FileType(str, Enum):
    Xml = 'Xml'
    Json = 'Json'
    Flat_File = 'Flat_File'
    Binary = 'Binary'
    Edi = 'Edi'

# ################################################################################################################################
# ################################################################################################################################

class ActionType(str, Enum):
    Execute_Service = 'Execute_Service'
    Deliver = 'Deliver'
    Notify = 'Notify'
    Change_Status = 'Change_Status'

# ################################################################################################################################
# ################################################################################################################################

class ExecMode(str, Enum):
    Synchronous = 'Synchronous'
    Asynchronous = 'Asynchronous'
    Reliable = 'Reliable'

# ################################################################################################################################
# ################################################################################################################################

class PreprocessSavePolicy(str, Enum):
    All = 'All'
    Unique = 'Unique'
    None_ = 'None'

# ################################################################################################################################
# ################################################################################################################################

class CriteriaMatch(str, Enum):
    Any = 'Any'
    Unknown = 'Unknown'
    Specific = 'Specific'

# ################################################################################################################################
# ################################################################################################################################

class ErrorCriteria(str, Enum):
    Any = 'Any'
    No_Errors = 'No_Errors'
    Has_Errors = 'Has_Errors'

# ################################################################################################################################
# ################################################################################################################################

class RecognitionRuleType(str, Enum):
    Filename_Glob = 'Filename_Glob'
    Content_Regex = 'Content_Regex'
    Xml_Root_Tag = 'Xml_Root_Tag'
    Json_Path = 'Json_Path'
    Pgp_Header = 'Pgp_Header'
    Edi_Segment = 'Edi_Segment'

# ################################################################################################################################
# ################################################################################################################################

class ExtractionQueryType(str, Enum):
    Xpath = 'Xpath'
    Jsonpath = 'Jsonpath'
    Regex = 'Regex'
    Fixed = 'Fixed'

# ################################################################################################################################
# ################################################################################################################################

class AttributeType(str, Enum):
    System = 'System'
    Custom = 'Custom'

# ################################################################################################################################
# ################################################################################################################################

class DataType(str, Enum):
    String = 'String'
    Number = 'Number'
    Date = 'Date'

# ################################################################################################################################
# ################################################################################################################################

class DeliveryMethod(str, Enum):
    Sftp = 'Sftp'
    Ftp = 'Ftp'
    Ftps = 'Ftps'
    Http = 'Http'
    Https = 'Https'
    Amqp = 'Amqp'
    Smtp = 'Smtp'
    S3 = 'S3'
    Azure_Blob = 'Azure_Blob'
    Receiver_Preferred = 'Receiver_Preferred'

# ################################################################################################################################
# ################################################################################################################################

class NotificationChannel(str, Enum):
    Email = 'Email'
    Webhook = 'Webhook'
    Pubsub = 'Pubsub'

# ################################################################################################################################
# ################################################################################################################################

class TaskType(str, Enum):
    Delivery = 'Delivery'
    Service_Execution = 'Service_Execution'

# ################################################################################################################################
# ################################################################################################################################

class PreprocessStep(str, Enum):
    Validate = 'Validate'
    Dedup = 'Dedup'
    Pgp_Verify = 'Pgp_Verify'
    Checksum = 'Checksum'
    Save = 'Save'

# ################################################################################################################################
# ################################################################################################################################

class PreprocessOverride(str, Enum):
    Defer = 'Defer'
    Force_On = 'Force_On'
    Force_Off = 'Force_Off'

# ################################################################################################################################
# ################################################################################################################################

class ExtendedCriteriaOperator(str, Enum):
    Equals = 'Equals'
    Not_Equals = 'Not_Equals'
    Contains = 'Contains'
    Begins_With = 'Begins_With'
    Ends_With = 'Ends_With'
    Is_Null = 'Is_Null'
    Is_Not_Null = 'Is_Not_Null'
    Greater_Than = 'Greater_Than'
    Less_Than = 'Less_Than'
    Greater_Or_Equal = 'Greater_Or_Equal'
    Less_Or_Equal = 'Less_Or_Equal'
    Before = 'Before'
    After = 'After'

# ################################################################################################################################
# ################################################################################################################################

class PostProcessingAction(str, Enum):
    Move = 'Move'
    Delete = 'Delete'
    None_ = 'None'

# ################################################################################################################################
# ################################################################################################################################

class KeyType(str, Enum):
    Public = 'Public'
    Private = 'Private'

# ################################################################################################################################
# ################################################################################################################################

class KeyUsage(str, Enum):
    Encrypt = 'Encrypt'
    Decrypt = 'Decrypt'
    Sign = 'Sign'
    Verify = 'Verify'

# ################################################################################################################################
# ################################################################################################################################

class PickupSourceType(str, Enum):
    Sftp = 'Sftp'
    Ftp = 'Ftp'
    S3 = 'S3'
    Azure_Blob = 'Azure_Blob'
    Imap = 'Imap'
    Smtp = 'Smtp'

# ################################################################################################################################
# ################################################################################################################################

REDIS_KEY_PREFIX = 'zato:file-transfer'

# ################################################################################################################################
# ################################################################################################################################

class RedisKey:

    @staticmethod
    def tx(cluster_id, tx_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:tx:{tx_id}'

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
    def log_entry(cluster_id, tx_id, seq):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:log:{tx_id}:{seq:04d}'

    @staticmethod
    def pgp_key(cluster_id, key_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:pgp-key:{key_id}'

    @staticmethod
    def content(cluster_id, tx_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:content:{tx_id}'

    @staticmethod
    def settings(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:settings'

    @staticmethod
    def seq_tx(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:seq:tx'

    @staticmethod
    def seq_task(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:seq:task'

    @staticmethod
    def seq_log(cluster_id, tx_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:seq:log:{tx_id}'

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
    def idx_tx_by_created(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:tx:by-created'

    @staticmethod
    def idx_tx_by_status(cluster_id, status):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:tx:by-status:{status}'

    @staticmethod
    def idx_tx_by_sender(cluster_id, sender):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:tx:by-sender:{sender}'

    @staticmethod
    def idx_tx_by_receiver(cluster_id, receiver):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:tx:by-receiver:{receiver}'

    @staticmethod
    def idx_tx_by_doc_type(cluster_id, dt_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:tx:by-doc-type:{dt_id}'

    @staticmethod
    def idx_tx_by_exchange(cluster_id, exchange_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:tx:by-exchange:{exchange_id}'

    @staticmethod
    def idx_tx_by_group(cluster_id, group_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:tx:by-group:{group_id}'

    @staticmethod
    def idx_task_by_status(cluster_id, status):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:task:by-status:{status}'

    @staticmethod
    def idx_task_by_tx(cluster_id, tx_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:task:by-tx:{tx_id}'

    @staticmethod
    def idx_task_retry_schedule(cluster_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:task:retry-schedule'

    @staticmethod
    def idx_log_by_tx(cluster_id, tx_id):
        return f'{REDIS_KEY_PREFIX}:{cluster_id}:idx:log:by-tx:{tx_id}'

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
