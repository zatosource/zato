# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import OrderedDict
from dataclasses import dataclass
from http.client import BAD_REQUEST, FORBIDDEN, OK, UNAUTHORIZED
from http.client import responses as http_responses
from numbers import Number

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.defaults import http_plain_server_port

# ################################################################################################################################

if 0:
    from zato.common.documents.model import doclist
    from zato.common.ext.imbox import Imbox
    from zato.common.typing_ import any_, iterator_, stranydict, strnone
    doclist = doclist
    Imbox = Imbox
    iterator_ = iterator_
    stranydict = stranydict
    strnone = strnone

# ################################################################################################################################

# SQL ODB
engine_def = '{engine}://{username}:{password}@{host}:{port}/{db_name}'
engine_def_sqlite = 'sqlite:///{sqlite_path}'

# Snowflake has no port segment - the host field holds the account identifier.
engine_def_snowflake = '{engine}://{username}:{password}@{host}/{db_name}'

# Convenience access functions and constants.

class OS_Env:
    Zato_Enable_Memory_Profiler = 'Zato_Enable_Memory_Profiler'

megabyte = 10 ** 6

# Hook methods whose func.im_func.func_defaults contains this argument will be assumed to have not been overridden by users
# and ServiceStore will be allowed to override them with None so that they will not be called in Service.update_handle
# which significantly improves performance (~30%).
zato_no_op_marker = 'zato_no_op_marker'

SECRET_SHADOW = '******'
Secret_Shadow = SECRET_SHADOW

# TRACE1 logging level, even more details than DEBUG
TRACE1 = 6

SECONDS_IN_DAY = 86400 # 60 seconds * 60 minutes * 24 hours (and we ignore leap seconds)

scheduler_date_time_format = '%Y-%m-%d %H:%M:%S'

# TODO: Classes that have this attribute defined (no matter the value) will not be deployed
# onto servers.
DONT_DEPLOY_ATTR_NAME = 'zato_dont_import'

# A convenient constant used in several places, simplifies passing around
# arguments which are, well, not given (as opposed to being None, an empty string etc.)
ZATO_NOT_GIVEN = b'ZATO_NOT_GIVEN'
ZatoNotGiven = b'ZatoNotGiven'

# Separates command line arguments in shell commands.
CLI_ARG_SEP = 'Zato_Zato_Zato'

# Also used in a couple of places.
ZATO_OK = 'ZATO_OK'
ZATO_ERROR = 'ZATO_ERROR'
ZATO_WARNING = 'ZATO_WARNING'
ZATO_NONE = 'ZATO_NONE'
ZATO_DEFAULT = 'ZATO_DEFAULT'
Zato_None = ZATO_NONE
Zato_No_Security = 'zato-no-security'

# Used when there's a need for encrypting/decrypting a well-known data.
# TODO: Move it to MISC
ZATO_CRYPTO_WELL_KNOWN_DATA = 'ZATO'

# Used if it could not be established what remote address a request came from
NO_REMOTE_ADDRESS = '(None)'

# Pattern matching order
TRUE_FALSE = 'true_false'
FALSE_TRUE = 'false_true'

simple_types = (bytes, str, dict, list, tuple, bool, Number)

# ################################################################################################################################
# ################################################################################################################################

query_parameters = ('-paginate', '-cur_page', '-query')

# ################################################################################################################################
# ################################################################################################################################

generic_attrs = (
    'data_encoding',
    'max_msg_size', 'read_buffer_size', 'recv_timeout', 'logging_level', 'should_log_messages', 'start_seq', 'end_seq',
    'max_wait_time', 'oauth_def', 'ping_interval', 'pings_missed_threshold', 'socket_read_timeout', 'socket_write_timeout',
    'security_group_count', 'security_group_member_count', 'gateway_service_list', 'rest_channel_list', 'url_path', 'is_public',
    'is_audit_log_active',
)

# ################################################################################################################################
# ################################################################################################################################

# These are used by web-admin only because servers and scheduler use sql.conf
ping_queries = {
    'db2': 'SELECT current_date FROM sysibm.sysdummy1',
    'mssql': 'SELECT 1',
    'mysql+pymysql': 'SELECT 1+1',
    'oracle': 'SELECT 1 FROM dual',
    'postgresql': 'SELECT 1',
    'postgresql+pg8000': 'SELECT 1',
    'redshift+redshift_connector': 'SELECT 1',
    'snowflake': 'SELECT 1',
    'sqlite': 'SELECT 1',
}

engine_display_name = {
    'db2': 'DB2',
    'mssql': 'MS SQL',
    'zato+mssql1': 'MS SQL',
    'mysql+pymysql': 'MySQL',
    'oracle': 'Oracle',
    'postgresql': 'PostgreSQL',
    'postgresql+pg8000': 'PostgreSQL',
    'redshift+redshift_connector': 'Amazon Redshift',
    'snowflake': 'Snowflake',
    'sqlite': 'SQLite',
}

# ################################################################################################################################
# ################################################################################################################################

class EnvVariable:
    Key_Prefix = 'Zato_Config'
    Key_Missing_Suffix = '_Missing'
    Log_Env_Details = 'Zato_Log_Env_Details'

    # What stands in for a value whose environment variable was not set when a configuration
    # was imported. The rest of the placeholder names that variable and adds a unique suffix,
    # so a value that begins with this is a value that was never provided.
    Missing_Value_Prefix = 'Missing_'

# ################################################################################################################################
# ################################################################################################################################

class EnvFile:
    Default = 'env.ini'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EnvConfigCtx:
    component:'str'
    file_name:'str'
    missing_suffix:'str' = EnvVariable.Key_Missing_Suffix

# ################################################################################################################################
# ################################################################################################################################

class API_Key:
    Env_Key = 'Zato_API_Key_Name'
    Default_Header = 'X-API-Key'

# ################################################################################################################################
# ################################################################################################################################

# All URL types Zato understands.
class URL_TYPE:
    SOAP       = 'soap' # Used only by outgoing connections
    PLAIN_HTTP = 'plain_http'
    AS2        = 'as2'
    AS4        = 'as4'

    def __iter__(self):
        return iter([self.PLAIN_HTTP])

# ################################################################################################################################
# ################################################################################################################################

class AS4:
    """ Constants for AS4 channels and outgoing connections.
    """
    class Profile:
        EDelivery1 = 'edelivery1'
        EDelivery2 = 'edelivery2'
        Peppol     = 'peppol'
        ICS2       = 'ics2'

    class Default:
        Profile        = 'edelivery1'
        Inbound_Topic  = 'zato.as4.inbound'
        Outbound_Topic = 'zato.as4.outbound'

        # Where receipts and errors that arrive on their own go - they are about an earlier message
        # of ours rather than about a payload, so they do not share the inbound topic.
        Signal_Topic   = 'zato.as4.signal'

        # The MIME type payloads are sent with unless the caller says otherwise.
        Payload_MIME_Type = 'application/xml'

        # How long information about an already-processed eb:MessageId is kept
        # for duplicate detection, in seconds.
        Duplicate_Detection_TTL = 172800

        # The cache key prefix that duplicate detection stores eb:MessageId values under.
        Duplicate_Cache_Prefix = 'zato.as4.msg.'

    # The service that delivers messages published to the outbound topic.
    Delivery_Service = 'zato.outgoing.as4.deliver'

    # The service that scheduler-driven pull jobs invoke.
    Pull_Service = 'zato.outgoing.as4.pull'

    class Resend:
        """ The automatic resend job - the sending half of AS4 reception awareness. A message whose
        receipt has not arrived goes out again under its original eb:MessageId, which is what makes
        the receiving side's duplicate detection the thing that decides whether the payload is
        delivered once or twice.
        """
        # The interval job every server ensures exists, the service it invokes
        # and how often it runs.
        Job_Name             = 'zato.as4.resend'
        Job_Interval_Minutes = 5
        Service              = 'zato.as4.resend.run'

        # How many messages one run resends, so that a partner outage does not turn one run
        # into a burst of every message sent during it.
        Batch_Size = 50

    class Alerting:
        """ What the B2B alerting sweep reports about AS4 - the exchanges nobody acknowledged and
        the certificates the exchanges themselves rest on.
        """
        # A certificate expiring within this many days raises a finding. An access point certificate
        # is renewed yearly on most networks, so the window is what turns that into a task in time.
        Cert_Warning_Days = 30

    class TokenType:
        """ How the signing certificate travels inside a message, as the Dashboard names the choices.
        An empty value leaves the profile preset's own choice in place.
        """
        X509v3   = 'x509v3'
        PKIPath  = 'pkipath'
        SAML20   = 'saml20'

    # The AS4 configuration fields shared by channels and outgoing connections.
    Common_Fields = ('as4_profile', 'as4_from_party', 'as4_to_party', 'as4_service', 'as4_action', 'as4_agreement',
        'as4_mpc', 'as4_original_sender', 'as4_final_recipient', 'as4_extra_pmodes', 'as4_token_type',
        'as4_username', 'as4_password', 'as4_signing_key', 'as4_signing_cert_chain', 'as4_decryption_key',
        'as4_saml_assertion', 'as4_peer_signing_cert', 'as4_peer_encryption_cert', 'as4_trust_anchors')

    # The fields that only outgoing AS4 connections use - the reception awareness parameters
    # among them, because repeating a delivery is something only the sending side does.
    Outgoing_Fields = ('as4_use_discovery', 'as4_sml_domain', 'as4_retry_max_attempts', 'as4_retry_interval',
        'as4_missing_receipt_after')

    # The integer fields, which arrive from the Dashboard as text and are declared as numbers
    # so that everything downstream reads them as the numbers they are.
    Numeric_Fields = ('as4_retry_max_attempts', 'as4_retry_interval', 'as4_missing_receipt_after')

    # The fields that only AS4 channels use.
    Channel_Fields = ('as4_serviced_participants', 'as4_inbound_topic')

    # The fields that hold secrets - they are encrypted at rest.
    Secret_Fields = ('as4_signing_key', 'as4_decryption_key', 'as4_password')

# ################################################################################################################################
# ################################################################################################################################

class AS2:
    """ Constants for AS2 channels and outgoing connections.
    """
    class Default:
        Inbound_Topic = 'zato.as2.inbound'

        # For how many days an already-processed Message-ID and its stored MDN
        # are kept for duplicate detection.
        Duplicate_Window_Days = 30

        # How many pooled connections one outgoing AS2 connection keeps.
        Pool_Size = 1

        # The channel every server creates on startup for incoming AS2 messages.
        Channel_Name     = 'zato.channel.as2'
        Channel_URL_Path = '/zato/as2'

        # The channel every server creates on startup for incoming asynchronous MDNs.
        MDN_Channel_Name     = 'zato.channel.as2.mdn'
        MDN_Channel_URL_Path = '/zato/as2/mdn'

        # The interval job every server ensures exists for completing partner certificate
        # rotations, the service the job invokes and how often the job runs.
        Rotation_Job_Name           = 'zato.outgoing.as2.complete-rotation'
        Rotation_Job_Interval_Hours = 1
        Rotation_Service            = 'zato.generic.connection.complete-as2-rotation'

    class Async_MDN:
        """ The delivery queue of asynchronous MDNs - a receipt the sender asked to have delivered
        to a separate URL is persisted before the inbound POST is answered, so that a restart
        resumes the delivery instead of losing the receipt.
        """
        # The interval job every server ensures exists, the service it invokes
        # and how often it runs.
        Job_Name             = 'zato.as2.async-mdn'
        Job_Interval_Minutes = 1
        Service              = 'zato.as2.async-mdn.deliver'

        # How many receipts one drain of the queue delivers, so that a long outage
        # does not turn the drain into a run over the whole queue at once.
        Batch_Size = 100

        # How many attempts one receipt gets before it is given up on.
        Max_Attempts = 10

        # How long the wait is after the first failed attempt and the ceiling it doubles up to,
        # both in seconds - the ceiling keeps a receipt going out hourly for as long as
        # the queue holds it.
        First_Retry_Seconds = 30
        Max_Retry_Seconds   = 3600

        # After this many days an undelivered receipt is dropped from the queue - the sender
        # has long since alerted on the missing MDN and resent the message itself.
        Retention_Days = 7

    class Resend:
        """ The automatic resend job - a sent message whose MDN is overdue goes out again under
        the same Message-ID, which is what makes the receiver's duplicate detection the thing
        that decides whether the document is delivered once or twice.
        """
        # The interval job every server ensures exists, the service it invokes
        # and how often it runs.
        Job_Name             = 'zato.as2.resend'
        Job_Interval_Minutes = 5
        Service              = 'zato.as2.resend.run'

        # How many messages one run resends, so that a partner outage does not turn one run
        # into a burst of every message sent during it.
        Batch_Size = 50

        # How many times an overdue MDN triggers a resend for partners
        # that do not set resend_max_retries.
        Default_Max_Retries = 3

    class Alerting:
        """ The B2B alerting job - overdue acknowledgments, pending MDNs, expiring certificates
        and missing ship notices raise one email digest per run.
        """
        # The interval job every server ensures exists, the service it invokes
        # and how often it runs.
        Job_Name           = 'zato.b2b.alerting'
        Job_Interval_Hours = 1
        Service            = 'zato.b2b.alerting.run'

        # A certificate expiring within this many days raises a finding.
        Cert_Warning_Days = 30

        # The overdue window for partners that do not set ack_overdue_after, in seconds.
        Default_Ack_Overdue_Seconds = 4 * 3600

        # The keys the scheduler job's extra data may carry - which SMTP connection
        # sends the digest, its addressing and the Dashboard address the links point to.
        Extra_SMTP_Conn     = 'smtp_conn'
        Extra_From          = 'from'
        Extra_To            = 'to'
        Extra_Dashboard_URL = 'dashboard_url'

    # The AS2 configuration fields shared by channels and outgoing connections.
    Common_Fields = ('as2_signing_key', 'as2_signing_cert_chain', 'as2_decryption_key', 'as2_next_decryption_key',
        'as2_next_decryption_cert', 'as2_peer_signing_cert', 'as2_peer_encryption_cert', 'as2_trust_anchors')

    # The fields that only AS2 channels use.
    Channel_Fields = ('as2_inbound_topic', 'as2_duplicate_window_days')

    # The fields that hold private keys - they are encrypted at rest.
    Secret_Fields = ('as2_signing_key', 'as2_decryption_key', 'as2_next_decryption_key')

    # The fields that make up our own keystore, stored on the inbound AS2 channel -
    # the signing pair, the current decryption key and the next decryption pair
    # staged for rotation.
    Keystore_Fields = ('as2_signing_key', 'as2_signing_cert_chain', 'as2_decryption_key', 'as2_next_decryption_key',
        'as2_next_decryption_cert')

# ################################################################################################################################
# ################################################################################################################################

ZATO_FIELD_OPERATORS = {
    'is-equal-to': '==',
    'is-not-equal-to': '!=',
}

# ################################################################################################################################
# ################################################################################################################################

ZMQ_OUTGOING_TYPES = ('PUSH', 'PUB')

# ################################################################################################################################
# ################################################################################################################################

ZATO_ODB_POOL_NAME = 'ZATO_ODB'

# ################################################################################################################################
# ################################################################################################################################

SOAP_VERSIONS = ('1.1', '1.2')
SOAP_CHANNEL_VERSIONS = ('1.1', '1.2')

# ################################################################################################################################
# ################################################################################################################################

class ES:

    class Default:
        Address_List = 'http://127.0.0.1:9200'
        Timeout = 90

# ################################################################################################################################
# ################################################################################################################################

class GRPC:

    class Default:
        Address = 'localhost:50051'

        # How many seconds to wait for the channel to become ready when pinging.
        Ping_Timeout = 10

        # The biggest message that can be sent or received, in bytes (100 MB).
        Max_Message_Size = 104_857_600

    # The name of the subdirectory of the server's work directory
    # where modules generated out of .proto files are kept.
    Stub_Dir = 'grpc-stubs'

# ################################################################################################################################
# ################################################################################################################################

class SEC_DEF_TYPE:
    APIKEY = 'apikey'
    BASIC_AUTH = 'basic_auth'
    MTLS = 'mtls'
    NTLM = 'ntlm'
    OAUTH = 'oauth'
    SPNEGO = 'spnego'
    WSS = 'wss'

Sec_Def_Type = SEC_DEF_TYPE

# ################################################################################################################################
# ################################################################################################################################

Sec_Def_Type_Name = {
    SEC_DEF_TYPE.APIKEY: 'API key',
    SEC_DEF_TYPE.BASIC_AUTH: 'Basic Auth',
    SEC_DEF_TYPE.MTLS: 'mTLS',
    SEC_DEF_TYPE.NTLM: 'NTLM',
    SEC_DEF_TYPE.OAUTH: 'Bearer token',
    SEC_DEF_TYPE.SPNEGO: 'Kerberos (SPNEGO)',
    SEC_DEF_TYPE.WSS: 'WS-Security',
}

All_Sec_Def_Types = sorted(Sec_Def_Type_Name)

# ################################################################################################################################
# ################################################################################################################################

class AUTH_RESULT:
    class BASIC_AUTH:
        INVALID_PREFIX = 'invalid-prefix'
        NO_AUTH = 'no-auth'

# ################################################################################################################################
# ################################################################################################################################

class BATCH_DEFAULTS:
    PAGE_NO = 1
    SIZE = 25
    MAX_SIZE = 1000

# ################################################################################################################################
# ################################################################################################################################

class MSG_SOURCE:
    DUPLEX = 'duplex'

# ################################################################################################################################
# ################################################################################################################################

class NameId:
    """ Wraps both an attribute's name and its ID.
    """
    def __init__(self, name:'str', id:'str'=''):
        self.name = name
        self.id = id or name

    def __repr__(self):
        return '<{} at {}; name={}; id={}>'.format(self.__class__.__name__, hex(id(self)), self.name, self.id)

# ################################################################################################################################
# ################################################################################################################################

class KAFKA:
    """ Kafka-specific constants.
    """
    class SASL_MECHANISM:
        """ SASL mechanisms a Kafka connection can authenticate with.
        """
        PLAIN = NameId('PLAIN', 'PLAIN')
        SCRAM_SHA_256 = NameId('SCRAM-SHA-256', 'SCRAM-SHA-256')
        SCRAM_SHA_512 = NameId('SCRAM-SHA-512', 'SCRAM-SHA-512')
        OAUTHBEARER = NameId('OAUTHBEARER', 'OAUTHBEARER')

        def __iter__(self) -> 'iterator_':
            return iter((self.PLAIN, self.SCRAM_SHA_256, self.SCRAM_SHA_512, self.OAUTHBEARER))

    # The security definition type each mechanism takes its credentials from.
    Mechanism_Sec_Def_Type = {
        SASL_MECHANISM.PLAIN.id: SEC_DEF_TYPE.BASIC_AUTH,
        SASL_MECHANISM.SCRAM_SHA_256.id: SEC_DEF_TYPE.BASIC_AUTH,
        SASL_MECHANISM.SCRAM_SHA_512.id: SEC_DEF_TYPE.BASIC_AUTH,
        SASL_MECHANISM.OAUTHBEARER.id: SEC_DEF_TYPE.OAUTH,
    }

    class COMPRESSION:
        """ Codecs an outgoing connection compresses messages with.
        """
        NONE = NameId('None', 'none')
        GZIP = NameId('gzip', 'gzip')
        SNAPPY = NameId('Snappy', 'snappy')
        LZ4 = NameId('LZ4', 'lz4')
        ZSTD = NameId('Zstandard', 'zstd')

        def __iter__(self) -> 'iterator_':
            return iter((self.NONE, self.GZIP, self.SNAPPY, self.LZ4, self.ZSTD))

    class ACKS:
        """ How many brokers acknowledge a message before a send counts as done.
        """
        ALL = NameId('All Kafka instances', 'all')
        LEADER = NameId('One Kafka instance', '1')
        NONE = NameId('No confirmation', '0')

        def __iter__(self) -> 'iterator_':
            return iter((self.ALL, self.LEADER, self.NONE))

    class Producer:
        """ The producer settings of an outgoing connection.
        """
        Field_Compression = 'compression'
        Field_Acks = 'acks'
        Field_Is_Idempotent = 'is_idempotent'
        Field_Max_Message_Size = 'max_message_size'
        Field_Linger_Ms = 'linger_ms'
        Field_Send_Timeout = 'send_timeout'

        Default_Compression = 'none' # KAFKA.COMPRESSION.NONE
        Default_Acks = 'all' # KAFKA.ACKS.ALL
        Default_Is_Idempotent = True
        Default_Max_Message_Size = 1_000_000
        Default_Linger_Ms = 0
        Default_Send_Timeout = 5

        FieldList = (
            Field_Compression,
            Field_Acks,
            Field_Is_Idempotent,
            Field_Max_Message_Size,
            Field_Linger_Ms,
            Field_Send_Timeout,
        )

        IntFieldList = (Field_Max_Message_Size, Field_Linger_Ms, Field_Send_Timeout)

        Defaults = {
            Field_Compression: Default_Compression,
            Field_Acks: Default_Acks,
            Field_Is_Idempotent: Default_Is_Idempotent,
            Field_Max_Message_Size: Default_Max_Message_Size,
            Field_Linger_Ms: Default_Linger_Ms,
            Field_Send_Timeout: Default_Send_Timeout,
        }

    class AUTO_OFFSET_RESET:
        """ Where a consumer group without a committed offset starts reading a topic from.
        """
        LATEST = NameId('Latest', 'latest')
        EARLIEST = NameId('Earliest', 'earliest')

        def __iter__(self) -> 'iterator_':
            out = iter((self.LATEST, self.EARLIEST))
            return out

    class Consumer:
        """ The consumer settings of a channel.
        """
        Field_Topics = 'topics'
        Field_Auto_Offset_Reset = 'auto_offset_reset'
        Field_Max_Message_Size = 'max_message_size'
        Field_Max_In_Flight = 'max_in_flight'
        Field_Should_Deliver_Tombstones = 'should_deliver_tombstones'
        Field_Dedup_Header = 'dedup_header'
        Field_Dedup_TTL = 'dedup_ttl'
        Field_Routing = 'routing'

        Default_Topics = ''
        Default_Auto_Offset_Reset = 'latest'
        Default_Max_Message_Size = 1_000_000
        Default_Max_In_Flight = 100
        Default_Should_Deliver_Tombstones = False
        Default_Dedup_Header = ''
        Default_Dedup_TTL = 86_400 * 7
        Default_Routing = ''

        FieldList = (
            Field_Topics,
            Field_Auto_Offset_Reset,
            Field_Max_Message_Size,
            Field_Max_In_Flight,
            Field_Should_Deliver_Tombstones,
            Field_Dedup_Header,
            Field_Dedup_TTL,
            Field_Routing,
        )

        IntFieldList = (Field_Max_Message_Size, Field_Max_In_Flight, Field_Dedup_TTL)
        BoolFieldList = (Field_Should_Deliver_Tombstones,)

        Defaults = {
            Field_Topics: Default_Topics,
            Field_Auto_Offset_Reset: Default_Auto_Offset_Reset,
            Field_Max_Message_Size: Default_Max_Message_Size,
            Field_Max_In_Flight: Default_Max_In_Flight,
            Field_Should_Deliver_Tombstones: Default_Should_Deliver_Tombstones,
            Field_Dedup_Header: Default_Dedup_Header,
            Field_Dedup_TTL: Default_Dedup_TTL,
            Field_Routing: Default_Routing,
        }

        # The Redis key prefix of a channel's dedup values, the channel's id and the value follow.
        Dedup_Key_Prefix = 'zato:kafka:dedup:'

    class Routing:
        """ The keys of one routing rule of a channel - the rules travel as a JSON list of such mappings.
        """
        Key_Topic = 'topic'
        Key_Header_Name = 'header_name'
        Key_Header_Value = 'header_value'
        Key_Service = 'service'

        KeyList = (Key_Topic, Key_Header_Name, Key_Header_Value, Key_Service)

    class Header:
        """ The headers a service receives next to a message's own, and the ones a send can carry.
        """
        Key = 'kafka.key'
        Topic = 'kafka.topic'
        Partition = 'kafka.partition'
        Offset = 'kafka.offset'
        Timestamp = 'kafka.timestamp'
        Is_Tombstone = 'kafka.is_tombstone'
        Channel = 'kafka.channel'

        # A header whose value is not text arrives base64-encoded under its name with this suffix.
        B64_Suffix = '.b64'

        # The bridge's value of a tombstone header.
        Is_Tombstone_True = 'true'

    class Default:
        Address = 'localhost:9092'

    # The password of the client's TLS key, stored encrypted and never listed back
    Field_SSL_Key_Password = 'ssl_key_password'

# ################################################################################################################################
# ################################################################################################################################

class NotGiven:
    pass

# ################################################################################################################################
# ################################################################################################################################

class Attrs(type):
    """ A container for class attributes that can be queried for an existence
    of an attribute using the .has class-method.
    """
    attrs = NotGiven

    @classmethod
    def has(cls, attr:'any_') -> 'bool':
        if cls.attrs is NotGiven:
            cls.attrs = []
            for cls_attr in dir(cls):
                if cls_attr == cls_attr.upper():
                    cls.attrs.append(getattr(cls, cls_attr))

        return attr in cls.attrs

# ################################################################################################################################
# ################################################################################################################################

class DATA_FORMAT(Attrs):
    CSV = 'csv'
    DICT = 'dict'
    FORM_DATA = 'form'
    HL7 = 'hl7'
    HL7_CCDA = 'hl7-ccda'
    JSON = 'json'
    POST = 'post'

    def __iter__(self):
        # Note that DICT and other attributes aren't included because they're never exposed to the external world as-is,
        # they may at most only used so that services can invoke each other directly
        return iter((self.JSON, self.CSV, self.POST))

Data_Format = DATA_FORMAT

# ################################################################################################################################
# ################################################################################################################################

class DEPLOYMENT_STATUS(Attrs):
    DEPLOYED = 'deployed'
    AWAITING_DEPLOYMENT = 'awaiting-deployment'
    IGNORED = 'ignored'

# ################################################################################################################################
# ################################################################################################################################

class SERVER_JOIN_STATUS(Attrs):
    ACCEPTED = 'accepted'

# ################################################################################################################################
# ################################################################################################################################

class SERVER_UP_STATUS(Attrs):
    RUNNING = 'running'
    CLEAN_DOWN = 'clean-down'

# ################################################################################################################################
# ################################################################################################################################

class SCHEDULER:

    class OUTCOME:
        OK = 'ok'
        ERROR = 'error'
        TIMEOUT = 'timeout'
        RUNNING = 'running'
        SKIPPED_ALREADY_IN_FLIGHT = 'skipped_already_in_flight'
        All = 'all'

    InitialSleepTime = 0.1
    EmbeddedIndicator      = 'zato_embedded'
    EmbeddedIndicatorBytes = EmbeddedIndicator.encode('utf8')

    # This is what a server will invoke
    DefaultHost = '127.0.0.1'
    DefaultPort = 31530

    # This is what a scheduler will invoke
    Default_Server_Host = '127.0.0.1'
    Default_Server_Port = http_plain_server_port

    # This is what a scheduler will bind to
    DefaultBindHost = '0.0.0.0'
    DefaultBindPort = DefaultPort

    # This is the username of an API client that servers
    # will use when they invoke their scheduler.
    Default_API_Client_For_Server_Auth_Required = True
    Default_API_Client_For_Server_Username = 'server_api_client1'

    class Status:
        Active = 'Active'
        Paused = 'Paused'

    class Interval_Unit:
        """ The units an interval-based job's period can be expressed in.
        """
        Seconds = 'seconds'
        Minutes = 'minutes'
        Hours = 'hours'
        Days = 'days'
        Weeks = 'weeks'

    class Env:

        # Basic information about where the scheduler can be found
        Host = 'Zato_Scheduler_Host'
        Port = 'Zato_Scheduler_Port'

        # Whether the scheduler is active or paused
        Status = 'Zato_Scheduler_Status'

        Bind_Host = 'Zato_Scheduler_scheduler_conf_bind_host'
        Bind_Port = 'Zato_Scheduler_Bind_Port'
        Path_Action_Prefix = 'Zato_Scheduler_Path_Action_'

        # These are used by servers to invoke the scheduler
        Server_Username = 'Zato_Scheduler_API_Client_For_Server_Username'
        Server_Password = 'Zato_Scheduler_API_Client_For_Server_Password'
        Server_Auth_Required = 'Zato_Scheduler_API_Client_For_Server_Auth_Required'

    class ConfigCommand:
        Pause = 'pause'
        Resume = 'resume'
        SetServer = 'set_server'

    JobsToIgnore = {}

    class JOB_TYPE(Attrs):
        ONE_TIME = 'one_time'
        INTERVAL_BASED = 'interval_based'

    class ON_MAX_RUNS_REACHED:
        DELETE = 'delete'
        INACTIVATE = 'inactivate'

# ################################################################################################################################
# ################################################################################################################################

class CHANNEL(Attrs):
    AMQP = 'amqp'
    DELIVERY = 'delivery'
    FANOUT_CALL = 'fanout-call'
    FANOUT_ON_FINAL = 'fanout-on-final'
    FANOUT_ON_TARGET = 'fanout-on-target'
    HL7_MLLP = 'hl7-mllp'
    HTTP_SOAP = 'http-soap'
    INTERNAL_CHECK = 'internal-check'
    INVOKE = 'invoke'
    INVOKE_ASYNC = 'invoke-async'
    INVOKE_ASYNC_CALLBACK = 'invoke-async-callback'
    NEW_INSTANCE = 'new-instance'
    PARALLEL_EXEC_CALL = 'parallel-exec-call'
    PARALLEL_EXEC_ON_TARGET = 'parallel-exec-on_target'
    PUBLISH = 'publish'
    SCHEDULER = 'scheduler'
    SCHEDULER_AFTER_ONE_TIME = 'scheduler-after-one-time'
    SERVICE = 'service'
    STARTUP_SERVICE = 'startup-service'
    URL_DATA = 'url-data'

# ################################################################################################################################
# ################################################################################################################################

class CONNECTION:
    CHANNEL = 'channel'
    OUTGOING = 'outgoing'

# ################################################################################################################################
# ################################################################################################################################

class BROKER:
    DEFAULT_EXPIRATION = 15 # In seconds

# ################################################################################################################################
# ################################################################################################################################

class MISC:
    DEFAULT_HTTP_METHOD = ''
    DEFAULT_HTTP_TIMEOUT = 10

    # The HTTP method an outgoing connection pings a resource with.
    DEFAULT_HTTP_PING_METHOD = 'HEAD'

    # How many connections an outgoing HTTP connection keeps pooled - a per-connection setting that
    # applies to plain HTTP and to SOAP alike.
    DEFAULT_HTTP_POOL_SIZE = 20

    OAUTH_SIG_METHODS = ['HMAC-SHA1', 'PLAINTEXT']
    PIDFILE = 'pidfile'
    SEPARATOR = ':::'
    DefaultAdminInvokeChannel = 'zato.api.invoke'
    Default_Cluster_ID = 1

# ################################################################################################################################
# ################################################################################################################################

class OpenAPI_Console_Auth:
    """ How a caller of the OpenAPI console authenticated - the values travel in console commands
    over Redis Streams.
    """
    Type_Credentials = 'credentials'
    Type_Entra = 'entra'

# ################################################################################################################################
# ################################################################################################################################

class HTTP_SOAP:

    UNUSED_MARKER = 'unused'

    class ACCEPT:
        ANY = '*/*'
        ANY_INTERNAL = 'haany'

    class METHOD:
        ANY_INTERNAL = 'hmany'

    class Invocation:
        """ Declarative invocation config of outgoing REST and SOAP connections - the Request, Response,
        Callback and Scheduler tabs. All the fields are stored in the connection's opaque attributes.
        """

        class Unit:
            Seconds = 'seconds'
            Minutes = 'minutes'
            Hours = 'hours'
            Days = 'days'

        UnitList = (Unit.Seconds, Unit.Minutes, Unit.Hours, Unit.Days)

        class CallbackType:
            Service = 'service'
            Topic = 'topic'
            REST = 'rest'

        CallbackTypeList = (CallbackType.Service, CallbackType.Topic, CallbackType.REST)

        class ValueMode:
            Text = 'text'
            JSONata = 'jsonata'

        ValueModeList = (ValueMode.Text, ValueMode.JSONata)

        class ResponseMapMode:
            JSONata = 'jsonata'
            XPath = 'xpath'

        ResponseMapModeList = (ResponseMapMode.JSONata, ResponseMapMode.XPath)

        # Prefixes of the names of the jobs that are auto-created for outgoing connections
        Job_Prefix_REST = 'rest.'
        Job_Prefix_SOAP = 'soap.'

        # Name of the internal service that the auto-created jobs invoke to run the connection
        Dispatch_Service = 'zato.http-soap.scheduler.process-request'

        # Names of the keys in the extra data that an auto-created job carries
        Extra_Conn_ID = 'conn_id'
        Extra_Conn_Name = 'conn_name'
        Extra_Transport = 'transport'

        # Request tab - REST
        Field_Request_Method = 'request_method'
        Field_Request_Query_String = 'request_query_string'
        Field_Request_Path_Params = 'request_path_params'
        Field_Request_Headers = 'request_headers'
        Field_Request_Data = 'request_data'
        Field_Request_Data_Mode = 'request_data_mode'

        # Request tab - SOAP
        Field_Request_Operation = 'request_operation'
        Field_Request_Message = 'request_message'
        Field_Request_Message_Map = 'request_message_map'
        Field_Request_SOAP_Headers = 'request_soap_headers'

        # Request tab - the WS-Addressing values injected into every SOAP envelope
        Field_WSA_Action = 'wsa_action'
        Field_WSA_To = 'wsa_to'
        Field_WSA_Reply_To = 'wsa_reply_to'

        # Response tab
        Field_Response_Map = 'response_map'
        Field_Response_Map_Mode = 'response_map_mode'

        # Callback tab
        Field_Callback_Type = 'callback_type'
        Field_Callback_Name = 'callback_name'

        # Scheduler tab
        Field_Run_Every = 'scheduler_run_every'
        Field_Run_Unit = 'scheduler_run_unit'
        Field_Start_Date = 'scheduler_start_date'
        Field_Job_ID = 'scheduler_job_id'

        SchedulerFieldList = (Field_Run_Every, Field_Run_Unit, Field_Start_Date, Field_Job_ID)

        RequestFieldListREST = (Field_Request_Method, Field_Request_Query_String, Field_Request_Path_Params,
            Field_Request_Headers, Field_Request_Data, Field_Request_Data_Mode)

        RequestFieldListSOAP = (Field_Request_Operation, Field_Request_Message, Field_Request_Message_Map,
            Field_Request_SOAP_Headers, Field_WSA_Action, Field_WSA_To, Field_WSA_Reply_To)

        ResponseFieldList = (Field_Response_Map, Field_Response_Map_Mode)

        CallbackFieldList = (Field_Callback_Type, Field_Callback_Name)

        FieldList = RequestFieldListREST + RequestFieldListSOAP + ResponseFieldList + CallbackFieldList + SchedulerFieldList

    class Retry:
        """ Retry config of outgoing REST and SOAP connections - how many times to retry a failed invocation
        and how long to sleep between attempts. All the fields are stored in the connection's opaque attributes.
        """

        # Names of the fields, as stored in the opaque attributes and sent through enmasse
        Field_Max_Retries = 'max_retries'
        Field_Sleep_Time = 'retry_sleep_time'
        Field_Backoff_Threshold = 'retry_backoff_threshold'
        Field_Backoff_Multiplier = 'retry_backoff_multiplier'

        # By default, there are no retries at all
        Default_Max_Retries = 0

        # How many seconds to sleep before the first retry
        Default_Sleep_Time = 2

        # A cap on the total sleep time across all the retries, in seconds
        Default_Backoff_Threshold = 60

        # Each retry sleeps this many times longer than the previous one
        Default_Backoff_Multiplier = 2

        # The longest single sleep between attempts, in seconds
        Max_Sleep_Time = 8

        # A connection's schedule is exactly what its fields say
        Jitter_Percent = 0

        FieldList = (Field_Max_Retries, Field_Sleep_Time, Field_Backoff_Threshold, Field_Backoff_Multiplier)

    class Queue:
        """ The queue switch of outgoing connections and channels, stored in the opaque attributes.
        """

        Field_Use_Queue = 'use_queue'

        Default_Use_Queue = False

        FieldList = (Field_Use_Queue,)

        # The static response a channel with the queue on returns, stored in the opaque attributes
        Field_Queue_Response = 'queue_response'

        Default_Queue_Response = ''

        # The elements of the default acknowledgement of a queued request
        Ack_Is_OK = 'is_ok'
        Ack_CID = 'cid'

    class DLQ:
        """ The DLQ config of outgoing connections, stored in the opaque attributes.
        """

        Field_Use_DLQ = 'use_dlq'
        Field_Action = 'dlq_action'
        Field_Retries = 'dlq_retries'
        Field_Retry_Interval = 'dlq_retry_interval'
        Field_Forward_To = 'dlq_forward_to'
        Field_Keep_Header = 'dlq_keep_header'

        class Action:
            Keep = 'keep'
            Retry = 'retry'
            Forward = 'forward'
            Discard = 'discard'

        Default_Use_DLQ = True
        Default_Action = Action.Keep
        Default_Retries = 3
        Default_Retry_Interval = 60
        Default_Forward_To = ''
        Default_Keep_Header = True

        FieldList = (Field_Use_DLQ, Field_Action, Field_Retries, Field_Retry_Interval, Field_Forward_To, Field_Keep_Header)

    class ResponseCache:
        """ Declarative response caching config of REST and SOAP channels - the whole block is stored
        in the channel's opaque attributes under the Opaque_Key name.
        """

        # The name of the key in the channel's opaque attributes
        Opaque_Key = 'response_cache'

        # Cached entries live under this per-channel prefix, which makes purging a channel a prefix delete
        Key_Prefix = 'cache:channel:{}:'

        class TTLUnit:
            Seconds = 'seconds'
            Minutes = 'minutes'
            Hours = 'hours'

        TTLUnitList = (TTLUnit.Seconds, TTLUnit.Minutes, TTLUnit.Hours)

        Default_Is_Enabled = False
        Default_TTL = 5
        Default_TTL_Unit = TTLUnit.Minutes
        Default_Is_Shared_Across_Callers = False
        Default_Include_Body_In_Key = False
        Default_Max_Body_Size = 1_000_000
        Default_Cache_On_Second_Request = True
        Default_Needs_ETag = False
        Default_Coalesce_Timeout = 15

        @staticmethod
        def get_default_config() -> 'stranydict':
            """ Returns a new dict with every response caching field set to its default value.
            """
            out = {
                'is_enabled': HTTP_SOAP.ResponseCache.Default_Is_Enabled,
                'ttl': HTTP_SOAP.ResponseCache.Default_TTL,
                'ttl_unit': HTTP_SOAP.ResponseCache.Default_TTL_Unit,
                'is_shared_across_callers': HTTP_SOAP.ResponseCache.Default_Is_Shared_Across_Callers,
                'vary_by_headers': [],
                'ignored_query_parameters': [],
                'include_body_in_key': HTTP_SOAP.ResponseCache.Default_Include_Body_In_Key,
                'max_body_size': HTTP_SOAP.ResponseCache.Default_Max_Body_Size,
                'cache_on_second_request': HTTP_SOAP.ResponseCache.Default_Cache_On_Second_Request,
                'needs_etag': HTTP_SOAP.ResponseCache.Default_Needs_ETag,
                'coalesce_timeout': HTTP_SOAP.ResponseCache.Default_Coalesce_Timeout,
            }
            return out

    class HealthCheck:
        """ Scheduled health checks of connections - a generic component attachable to any connection type
        that has a ping, starting with outgoing REST and SOAP. All the fields are stored in the connection's
        opaque attributes.
        """

        # Prefix of the names of the jobs that are auto-created for health checks
        Job_Prefix = 'health.'

        # Name of the internal service that the auto-created jobs invoke to ping a connection
        Dispatch_Service = 'zato.connection.health-check.run'

        # Names of the keys in the extra data that an auto-created job carries
        Extra_Conn_ID = 'conn_id'
        Extra_Conn_Name = 'conn_name'
        Extra_Conn_Type = 'conn_type'

        # Names of the opaque attributes that a connection carries to describe its health check - how often
        # it pings, and the job that does. A check's outcome reaches people through the connection's alerts.
        Field_Run_Every = 'health_check_run_every'
        Field_Run_Unit = 'health_check_run_unit'
        Field_Job_ID = 'health_check_job_id'

        FieldList = (Field_Run_Every, Field_Run_Unit, Field_Job_ID)

# ################################################################################################################################
# ################################################################################################################################

class SchedulerLink:
    """ A scheduler job auto-created for a connection carries these opaque attributes to point back
    to the connection it was created for, no matter the connection type.
    """

    # The connection object type, e.g. an outgoing REST or SOAP connection
    Conn_Type = 'link_conn_type'

    # The database ID of the linked connection
    Conn_ID = 'link_conn_id'

    # What field set on the connection the job describes - a scheduled invocation or a health check
    Kind = 'link_kind'

    class ConnType:
        REST_Outgoing = 'rest_outgoing'
        SOAP_Outgoing = 'soap_outgoing'
        FHIR_Outgoing = 'fhir_outgoing'
        SMS_Channel = 'sms_channel'

    ConnTypeList = (ConnType.REST_Outgoing, ConnType.SOAP_Outgoing, ConnType.FHIR_Outgoing, ConnType.SMS_Channel)

    class KindType:
        Scheduler = 'scheduler'
        HealthCheck = 'health_check'
        BulkExport = 'bulk_export'

    KindList = (KindType.Scheduler, KindType.HealthCheck, KindType.BulkExport)

    FieldList = (Conn_Type, Conn_ID, Kind)

# ################################################################################################################################
# ################################################################################################################################

class ADAPTER_PARAMS:
    APPLY_AFTER_REQUEST = 'apply-after-request'
    APPLY_BEFORE_REQUEST = 'apply-before-request'

# ################################################################################################################################
# ################################################################################################################################

class INFO_FORMAT:
    DICT = 'dict'
    TEXT = 'text'
    JSON = 'json'
    YAML = 'yaml'

# ################################################################################################################################
# ################################################################################################################################

class URL_PARAMS_PRIORITY:
    PATH_OVER_QS = 'path-over-qs'
    QS_OVER_PATH = 'qs-over-path'
    DEFAULT = QS_OVER_PATH

# ################################################################################################################################
# ################################################################################################################################

class PARAMS_PRIORITY:
    CHANNEL_PARAMS_OVER_MSG = 'channel-params-over-msg'
    MSG_OVER_CHANNEL_PARAMS = 'msg-over-channel-params'
    DEFAULT = CHANNEL_PARAMS_OVER_MSG

    def __iter__(self):
        return iter((self.CHANNEL_PARAMS_OVER_MSG, self.MSG_OVER_CHANNEL_PARAMS, self.DEFAULT))

# ################################################################################################################################
# ################################################################################################################################

class EMAIL:
    class DEFAULT:
        TIMEOUT = 10
        GET_CRITERIA = 'UNSEEN'
        FILTER_CRITERIA = 'isRead ne true'
        IMAP_DEBUG_LEVEL = 0
        SMTP_PORT = 587

    class IMAP:

        class MODE:
            PLAIN = 'plain'
            SSL = 'ssl'

            def __iter__(self):
                return iter((self.SSL, self.PLAIN))

        class ServerType:
            Generic = 'generic'
            Microsoft365 = 'microsoft_365'

        ServerTypeHuman = {
            ServerType.Generic: 'Generic IMAP',
            ServerType.Microsoft365: 'Microsoft 365',
        }

        class Scheduler:

            class Unit:
                Seconds = 'seconds'
                Minutes = 'minutes'
                Hours = 'hours'
                Days = 'days'

            UnitList = (Unit.Seconds, Unit.Minutes, Unit.Hours, Unit.Days)

            class InvokeWith:
                Message = 'message'
                EachAttachment = 'each_attachment'

            InvokeWithHuman = {
                InvokeWith.Message: 'Message',
                InvokeWith.EachAttachment: 'Each attachment',
            }

            InvokeWithList = (InvokeWith.Message, InvokeWith.EachAttachment)

            # Prefix of the names of the jobs that are auto-created for IMAP connections
            Job_Prefix = 'imap.'

            # Name of the opaque attribute that a job carries to point back to its IMAP connection
            Conn_ID_Attr = 'imap_conn_id'

            # Name of the internal service that the auto-created jobs invoke to poll a mailbox
            Dispatch_Service = 'zato.email.imap.process-messages'

            # Names of the keys in the extra data that an auto-created job carries
            Extra_Conn_ID = 'imap_conn_id'
            Extra_Conn_Name = 'imap_conn_name'
            Extra_Service = 'service'
            Extra_Invoke_With = 'invoke_with'

            # Names of the opaque attributes that an IMAP connection carries to describe its linked job
            Field_Run_Every = 'scheduler_run_every'
            Field_Run_Unit = 'scheduler_run_unit'
            Field_Start_Date = 'scheduler_start_date'
            Field_Service = 'scheduler_service'
            Field_Invoke_With = 'scheduler_invoke_with'
            Field_Job_ID = 'scheduler_job_id'

            FieldList = (Field_Run_Every, Field_Run_Unit, Field_Start_Date, Field_Service, Field_Invoke_With, Field_Job_ID)

    class SMTP:
        class MODE:
            PLAIN = 'plain'
            SSL = 'ssl'
            STARTTLS = 'starttls'

            def __iter__(self):
                return iter((self.STARTTLS, self.SSL, self.PLAIN))

        class ServerType:
            Generic = 'generic'
            Microsoft365 = 'microsoft_365'

        ServerTypeHuman = {
            ServerType.Generic: 'Generic SMTP',
            ServerType.Microsoft365: 'Microsoft 365',
        }

        # Default ports matching each connection mode
        ModePort = {
            MODE.PLAIN: 25,
            MODE.SSL: 465,
            MODE.STARTTLS: 587,
        }

        # Preset connection details for commonly used SMTP relay providers
        ProviderList = (
            {'name': 'Generic', 'host': '', 'port': 587, 'mode': MODE.STARTTLS, 'username_hint': ''},
            {'name': 'Amazon SES', 'host': 'email-smtp.us-east-1.amazonaws.com', 'port': 587, 'mode': MODE.STARTTLS,
                'username_hint': 'SMTP credentials access key'},
            {'name': 'Brevo', 'host': 'smtp-relay.brevo.com', 'port': 587, 'mode': MODE.STARTTLS,
                'username_hint': 'SMTP login address'},
            {'name': 'Google Workspace', 'host': 'smtp-relay.gmail.com', 'port': 587, 'mode': MODE.STARTTLS,
                'username_hint': 'Sender address'},
            {'name': 'Mailgun', 'host': 'smtp.mailgun.org', 'port': 587, 'mode': MODE.STARTTLS,
                'username_hint': 'postmaster@your-domain'},
            {'name': 'Microsoft 365', 'host': 'smtp.office365.com', 'port': 587, 'mode': MODE.STARTTLS,
                'username_hint': 'Full mailbox address'},
            {'name': 'Postmark', 'host': 'smtp.postmarkapp.com', 'port': 587, 'mode': MODE.STARTTLS,
                'username_hint': 'Server API token'},
            {'name': 'SendGrid', 'host': 'smtp.sendgrid.net', 'port': 587, 'mode': MODE.STARTTLS,
                'username_hint': 'apikey'},
        )

# ################################################################################################################################
# ################################################################################################################################

class CommonObject:

    Prefix_Invalid = 'prefix-invalid'

    Invalid = 'invalid-invalid'
    Security_Basic_Auth = 'security-basic-auth'

# ################################################################################################################################
# ################################################################################################################################

class ODOO:

    class CLIENT_TYPE:
        OPENERP_CLIENT_LIB = 'openerp-client-lib'

    class DEFAULT:
        PORT = 8069
        POOL_SIZE = 3

    class PROTOCOL:
        XML_RPC = NameId('XML-RPC', 'xmlrpc')
        XML_RPCS = NameId('XML-RPCS', 'xmlrpcs')
        JSON_RPC = NameId('JSON-RPC', 'jsonrpc')
        JSON_RPCS = NameId('JSON-RPCS', 'jsonrpcs')

        def __iter__(self):
            return iter((self.XML_RPC, self.XML_RPCS, self.JSON_RPC, self.JSON_RPCS))

# ################################################################################################################################
# ################################################################################################################################

CONTENT_TYPE = Bunch(
    JSON = 'application/json',
    PLAIN_XML = 'application/xml',
    SOAP11 = 'text/xml; charset=UTF-8',
    SOAP12 = 'application/soap+xml; charset=utf-8',
) # type: Bunch

class ContentType:
    FormURLEncoded = 'application/x-www-form-urlencoded'

# ################################################################################################################################
# ################################################################################################################################

class AMQP:
    class DEFAULT:
        POOL_SIZE = 10
        PRIORITY = 5
        PREFETCH_COUNT = 0

    class ACK_MODE:
        ACK = NameId('Ack', 'ack')
        REJECT = NameId('Reject', 'reject')

        def __iter__(self):
            return iter((self.ACK, self.REJECT))

# ################################################################################################################################
# ################################################################################################################################

class REDIS:
    class DEFAULT:
        HOST = 'localhost'
        PORT = 6379
        DB = 0

# ################################################################################################################################
# ################################################################################################################################

class SERVER_STARTUP:
    class PHASE:
        FS_CONFIG_ONLY = 'fs-config-only'
        IMPL_BEFORE_RUN = 'impl-before-run'
        ON_STARTING = 'on-starting'
        BEFORE_POST_FORK = 'before-post-fork'
        AFTER_POST_FORK = 'after-post-fork'
        IN_PROCESS_FIRST = 'in-process-first'
        IN_PROCESS_OTHER = 'in-process-other'
        AFTER_STARTED = 'after-started'

# ################################################################################################################################
# ################################################################################################################################

class GENERIC:
    ATTR_NAME = 'opaque1'
    DeleteReason = 'DeleteGenericConnection'
    DeleteReasonBytes = DeleteReason.encode('utf8')
    InitialReason = 'ReasonInitial'

    class CONNECTION:
        class TYPE:
            CHANNEL_IBM_MQ = 'channel-ibm-mq'
            CHANNEL_OPENAPI = 'channel-openapi'
            CHANNEL_KAFKA = 'channel-kafka'
            CHAT_DISCORD = 'chat-discord'
            CHAT_MICROSOFT_TEAMS = 'chat-microsoft-teams'
            CHAT_SLACK = 'chat-slack'
            CLOUD_AWS = 'cloud-aws'
            CLOUD_CONFLUENCE = 'cloud-confluence'
            CLOUD_JIRA = 'cloud-jira'
            CLOUD_MICROSOFT_365 = 'cloud-microsoft-365'
            CLOUD_MICROSOFT_FABRIC = 'cloud-microsoft-fabric'
            CLOUD_MICROSOFT_POWER_AUTOMATE = 'cloud-microsoft-power-automate'
            CLOUD_SALESFORCE = 'cloud-salesforce'
            GATEWAY_MCP = 'gateway-mcp'
            GATEWAY_RULE_ENGINE = 'gateway-rule-engine'
            OUTCONN_AS2 = 'outconn-as2'
            OUTCONN_ES = 'outconn-es'
            OUTCONN_FTP = 'outconn-ftp'
            OUTCONN_LDAP = 'outconn-ldap'
            OUTCONN_LLM = 'outconn-llm'
            CHANNEL_HL7_MLLP = 'channel-hl7-mllp'
            OUTCONN_HL7_FHIR = 'outconn-hl7-fhir'
            OUTCONN_HL7_MLLP = 'outconn-hl7-mllp'
            OUTCONN_GRAPHQL = 'outconn-graphql'
            OUTCONN_GRPC = 'outconn-grpc'
            OUTCONN_IBM_MQ = 'outconn-ibm-mq'
            OUTCONN_KAFKA = 'outconn-kafka'
            OUTCONN_MONGODB = 'outconn-mongodb'
            OUTCONN_ODATA = 'outconn-odata'
            OUTCONN_SAP = 'outconn-sap'
            OUTCONN_SFTP = 'outconn-sftp'
            OUTCONN_SMB = 'outconn-smb'
            CHANNEL_SMS = 'channel-sms'
            OUTCONN_SMS = 'outconn-sms'

# ################################################################################################################################
# ################################################################################################################################

class SMS:
    """ SMS-specific constants - the providers an outgoing connection can send through, the two ways a channel
    receives, and the scheduler job a polling channel owns.
    """
    class Provider:
        Twilio = 'twilio'
        Vonage = 'vonage'
        Infobip = 'infobip'
        Africas_Talking = 'africas-talking'

    ProviderList = (Provider.Twilio, Provider.Vonage, Provider.Infobip, Provider.Africas_Talking)

    ProviderHuman = {
        Provider.Twilio: 'Twilio',
        Provider.Vonage: 'Vonage',
        Provider.Infobip: 'Infobip',
        Provider.Africas_Talking: "Africa's Talking",
    }

    # The public address of each provider's API - Infobip accounts each have their own base URL, so Infobip has none.
    Default_Host = {
        Provider.Twilio: 'https://api.twilio.com',
        Provider.Vonage: 'https://api.nexmo.com',
        Provider.Infobip: '',
        Provider.Africas_Talking: 'https://api.africastalking.com',
    }

    # The provider whose callbacks are signed with a secret of their own
    Providers_With_Signature_Secret = (Provider.Vonage,)

    # The provider whose host has no default and is required on input
    Providers_Requiring_Host = (Provider.Infobip,)

    class Receive_Mode:
        Webhook = 'webhook'
        Polling = 'polling'

    Receive_Mode_List = (Receive_Mode.Webhook, Receive_Mode.Polling)

    Receive_Mode_Human = {
        Receive_Mode.Webhook: 'Webhook',
        Receive_Mode.Polling: 'Polling',
    }

    # The path prefix of the internal REST channel that receives every SMS channel's callbacks - the channel's name follows
    Webhook_Path_Prefix = '/zato/sms/'

    # The name of the internal REST channel and of the service behind it
    Webhook_Channel_Name = 'zato.channel.sms.receive'
    Webhook_Service = 'zato.channel.sms.receive'

    # The service the Dashboard's Invoke dialog of an outgoing connection calls
    Invoke_Service = 'zato.outgoing.sms.invoke'

    # The response header through which the webhook returns the correlation ID of each callback it accepted
    Header_Callback_CID = 'X-Zato-CID'

    # The outgoing connection's own fields
    Field_Provider = 'provider'
    Field_Host = 'host'
    Field_Username = 'username'
    Field_Sender = 'sender'
    Field_Signature_Secret = 'signature_secret'
    Field_Channel_Name = 'channel_name'
    Field_Pool_Size = 'pool_size'
    Field_Timeout = 'timeout'

    # The secret is stored in the connection's secret column and reaches the wrapper under this name,
    # while an enmasse file gives it under the other one
    Field_Secret = 'secret'
    Field_Password = 'password'

    # The channel's own fields
    Field_Outconn_Name = 'outconn_name'
    Field_Service = 'service'
    Field_Receive_Mode = 'receive_mode'
    Field_Poll_State = 'poll_state'

    Default_Pool_Size = 10
    Default_Timeout = 30

    # The number of received events a channel records to drop a resent callback, and their expiry
    Received_Events_Max = 10_000
    Received_Events_Expiry_Seconds = 48 * 3600

    class Scheduler:

        # Prefix of the names of the jobs that are auto-created for polling SMS channels
        Job_Prefix = 'sms.'

        # Name of the internal service that the auto-created jobs invoke to poll a provider
        Dispatch_Service = 'zato.channel.sms.poll'

        # Names of the keys in the extra data of an auto-created job
        Extra_Conn_ID = 'sms_channel_id'
        Extra_Conn_Name = 'sms_channel_name'

        # Names of the opaque attributes that describe an SMS channel's linked job
        Field_Run_Every = 'scheduler_run_every'
        Field_Run_Unit = 'scheduler_run_unit'
        Field_Job_ID = 'scheduler_job_id'

        Default_Run_Every = 1
        Default_Run_Unit = 'minutes'

        FieldList = (Field_Run_Every, Field_Run_Unit, Field_Job_ID)

# ################################################################################################################################
# ################################################################################################################################

class MCP:
    """ MCP protocol revisions the gateways speak - the session-based one negotiated
    through initialize and the stateless one where each request is self-contained.
    """
    Protocol_Version_Sessions  = '2025-06-18'
    Protocol_Version_Stateless = '2026-07-28'

    Protocol_Versions_Supported = [Protocol_Version_Sessions, Protocol_Version_Stateless]

    # The most bytes one JSON-RPC request body may carry
    Max_Request_Size = 1_000_000

    # The most container levels one JSON-RPC request body may nest
    Max_Request_Depth = 200

    # How many seconds one tools/call invocation may run for before it times out -
    # each gateway may override it through its invoke_timeout option.
    Default_Invoke_Timeout = 90

    # The opaque-config keys under which a gateway lists the connections
    # it exposes as tools, one key per connection group.
    Connection_List_Keys = [
        'rest_connections',
        'soap_connections',
        'sql_connections',
        'microsoft_365_connections',
        'microsoft_teams_connections',
        'microsoft_fabric_connections',
        'microsoft_power_automate_connections',
        'sap_connections',
        'confluence_connections',
        'odoo_connections',
        'es_connections',
    ]

# ################################################################################################################################
# ################################################################################################################################

class FileTransfer:
    """ File transfer schedules - each one polls a remote directory of an SFTP, SMB or FTP connection
    and invokes a target service once per each file received.
    """

    class ConnType:
        SFTP = GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
        SMB = GENERIC.CONNECTION.TYPE.OUTCONN_SMB
        FTP = GENERIC.CONNECTION.TYPE.OUTCONN_FTP

    ConnTypeList = (ConnType.SFTP, ConnType.SMB, ConnType.FTP)

    # Which attribute of a service holds the facade of each connection type, e.g. self.sftp or self.smb
    Facade_Attr = {
        ConnType.SFTP: 'sftp',
        ConnType.SMB: 'smb',
        ConnType.FTP: 'ftp',
    }

    class Scheduler:

        class Unit:
            Seconds = 'seconds'
            Minutes = 'minutes'
            Hours = 'hours'
            Days = 'days'
            Weeks = 'weeks'

        UnitList = (Unit.Seconds, Unit.Minutes, Unit.Hours, Unit.Days, Unit.Weeks)

        # How a schedule decides that a file's upload is complete
        class ReadyHow:
            Stability = 'stability'
            Marker = 'marker'

        ReadyHowList = (ReadyHow.Stability, ReadyHow.Marker)

        ReadyHowHuman = {
            ReadyHow.Stability: 'When it stops changing',
            ReadyHow.Marker: 'Marker file',
        }

        # What happens to a file once the target service has finished with it
        class OnSuccess:
            Move = 'move'
            Delete = 'delete'

        OnSuccessList = (OnSuccess.Move, OnSuccess.Delete)

        OnSuccessHuman = {
            OnSuccess.Move: 'Move it away',
            OnSuccess.Delete: 'Delete it',
        }

        # Name of the opaque attribute that a connection carries with its list of schedules
        Schedules_Field = 'scheduler_schedules'

        # Prefixes of the names of the jobs that are auto-created for schedules, one per connection type
        Job_Prefix = {
            GENERIC.CONNECTION.TYPE.OUTCONN_SFTP: 'sftp.',
            GENERIC.CONNECTION.TYPE.OUTCONN_SMB: 'smb.',
            GENERIC.CONNECTION.TYPE.OUTCONN_FTP: 'ftp.',
        }

        # Names of the internal services that the auto-created jobs invoke to poll a directory
        Dispatch_Service = {
            GENERIC.CONNECTION.TYPE.OUTCONN_SFTP: 'zato.outgoing.sftp.process-files',
            GENERIC.CONNECTION.TYPE.OUTCONN_SMB: 'zato.outgoing.smb.process-files',
            GENERIC.CONNECTION.TYPE.OUTCONN_FTP: 'zato.outgoing.ftp.process-files',
        }

        # Names of the keys in the extra data that an auto-created job carries - the schedule itself
        # travels in full under Extra_Schedule so a fire event is self-contained.
        Extra_Conn_ID = 'conn_id'
        Extra_Conn_Name = 'conn_name'
        Extra_Conn_Type = 'conn_type'
        Extra_Schedule = 'schedule'

        # What a schedule starts out with before the user changes anything -
        # an arrival window of zero means no arrival expectation is declared.
        Default_Pattern = '*'
        Default_Marker_Suffix = '.done'
        Default_Move_Directory = 'processed'
        Default_Stability_Delay = 2
        Default_Arrival_Window = 0

        # The suffix a file is renamed to when a schedule claims it for itself
        Claim_Suffix = '.processing'

        # What a file is given on top of its own name when the destination it is moved into
        # already holds something of that name - the moment it arrived tells the two apart.
        Collision_Suffix_Format = '%Y%m%d-%H%M%S-%f'

# ################################################################################################################################
# ################################################################################################################################

class Groups:
    class Type:
        Group_Parent    = 'zato-group'
        Group_Member    = 'zato-group-member'
        API_Clients     = 'zato-api-creds'
        Organizations   = 'zato-org'

    class Membership_Action:
        Add    = 'add'
        Remove = 'remove'

# ################################################################################################################################
# ################################################################################################################################

class Quota_Tiers:
    class Type:
        Quota_Tier = 'zato-quota-tier'

# ################################################################################################################################
# ################################################################################################################################

class On_Prem_Gateway:
    """ On-prem gateways - each one is a process running on the customer's own network
    that Zato reaches on-prem systems through.
    """
    class Type:
        On_Prem_Gateway = 'zato-on-prem-gateway'

    # The ports the gateway hub listens on inside the container, both of them loopback only.
    class Port:
        Hub   = 11226
        Admin = 11227

    # The environment variables a deployment may set to move the two ports and to say how
    # the instance is reached from the outside, which is what an enrollment token carries.
    class Env:
        Hub_Port       = 'Zato_Port_On_Prem_Gateway_Hub'
        Admin_Port     = 'Zato_Port_On_Prem_Gateway_Admin'
        Public_Address = 'Zato_On_Prem_Gateway_Public_Address'

    # The values applied when a gateway definition does not state them.
    class Default:

        # An enrolled gateway enrolls again only after its key has been reset in the Dashboard.
        Is_Key_Reset_Required = True

    # Where the container keeps the gateway binary and where new releases of it are published.
    class Update:
        Binary_Path  = '/opt/zato/on-prem-gateway/zato-on-prem-gateway'
        Log_File     = 'on-prem-gateway.log'
        Latest_URL   = 'https://github.com/zatosource/zato-on-prem-gateway/releases/latest'
        Download_URL = 'https://github.com/zatosource/zato-on-prem-gateway/releases/download/{version}/' + \
            'zato-on-prem-gateway-linux-{architecture}'

# ################################################################################################################################
# ################################################################################################################################

class Lets_Encrypt:
    """ Certificates obtained from Let's Encrypt, or from another ACME server, and presented on all the TLS ports.
    """

    # The environment variables that turn the feature on and point it at its files and servers.
    class Env:
        Use_Lets_Encrypt = 'Zato_Use_Lets_Encrypt'
        Subject_Alt_Name = 'Zato_SSL_Subject_Alt_Name'
        SSL_Dir          = 'Zato_SSL_Dir'
        Server           = 'Zato_Lets_Encrypt_Server'
        Staging_Server   = 'Zato_Lets_Encrypt_Staging_Server'
        CA_File          = 'Zato_Lets_Encrypt_CA_File'
        Public_IP        = 'Zato_Lets_Encrypt_Public_IP'
        Port             = 'Zato_Lets_Encrypt_Port'
        HAProxy_Config   = 'Zato_Lets_Encrypt_HAProxy_Config'
        Check_Interval   = 'Zato_Lets_Encrypt_Check_Interval'

    # The values used when the corresponding environment variables are not set.
    class Default:
        SSL_Dir        = '/opt/hot-deploy/ssl'
        Server         = 'https://acme-v02.api.letsencrypt.org/directory'
        Staging_Server = 'https://acme-staging-v02.api.letsencrypt.org/directory'
        Public_IP_URL  = 'https://checkip.amazonaws.com'
        Port           = 11228
        HAProxy_Config = '/opt/zato/env/qs-1/haproxy.cfg'
        Check_Interval = 43200

    # The files in the SSL directory - HAProxy reads the user one, which is a copy of one of the others.
    class File:
        User_PEM = 'user.pem'
        Auto_PEM = 'auto.pem'
        Own_PEM  = 'zato.pem'
        Data_Dir = 'lets-encrypt'
        Settings = 'settings.json'
        Status   = 'status.json'
        Progress = 'progress.json'
        Lock     = 'lock'

    # What a running check is doing, recorded in the lock file while it holds the lock.
    class Operation:
        Certificate = 'certificate'
        Port        = 'port'

    # The steps of enabling Let's Encrypt, in the order the Dashboard shows them.
    class Step:
        Port    = 'port'
        Connect = 'connect'
        Request = 'request'
        Install = 'install'

    # How far a step got, which is what the Dashboard shows next to the slider.
    class Progress_State:
        Running = 'running'
        Done    = 'done'
        Error   = 'error'

    # The name the ACME client stores the certificate under, the profile that IP address certificates require
    # and the one of DNS names, which is always requested by name because a CA may pick any profile for orders without one.
    Cert_Name   = 'zato'
    IP_Profile  = 'shortlived'
    DNS_Profile = 'classic'

    # The services behind the SSL config page in the Dashboard.
    class Service:
        Get                 = 'zato.ssl-config.get'
        Get_Public_Endpoint = 'zato.ssl-config.get-public-endpoint'
        Set_Lets_Encrypt    = 'zato.ssl-config.set-lets-encrypt'
        Check_Port          = 'zato.ssl-config.check-port'

# ################################################################################################################################
# ################################################################################################################################

class Audit_Config:
    """ Generic-object types storing audit-related definitions - the retention
    policy and per-channel attribute-extraction rules.
    """
    class Type:
        Retention_Policy = 'zato-audit-retention-policy'
        Extraction_Rules = 'zato-audit-extraction-rules'

    # The object types config-change events are filed under.
    class Object_Type:
        Generic_Connection = 'generic-connection'
        Quota_Tier         = 'quota-tier'
        On_Prem_Gateway    = 'on-prem-gateway'

# ################################################################################################################################
# ################################################################################################################################

class Alerting:
    """ The generic alerting sweep - collectors measure the audit database and live
    channel metrics into facts, the alerts ruleset in the rule engine decides which
    facts matter, and matches dispatch through the actions their outcomes name.
    """

    # The interval job every server ensures exists, the service it invokes
    # and how often the job runs.
    Job_Name             = 'zato.alerting'
    Job_Interval_Minutes = 1
    Service              = 'zato.alerting.run'

    # The probe jobs - each measures a fact no per-call audit event can produce
    # and writes ordinary audit events the collectors read. The test transfer ships
    # inactive because it writes to remote systems - activating it is the opt-in.
    Cert_Job_Name            = 'zato.alerting.cert-check'
    Cert_Job_Interval_Hours  = 24
    Cert_Service             = 'zato.alerting.cert-check.run'

    Health_Job_Name             = 'zato.alerting.microsoft-health'
    Health_Job_Interval_Minutes = 15
    Health_Service              = 'zato.alerting.microsoft-health.run'

    Test_Transfer_Job_Name             = 'zato.alerting.test-transfer'
    Test_Transfer_Job_Interval_Minutes = 15
    Test_Transfer_Service              = 'zato.alerting.test-transfer.run'

    # The service the config screen's test transfers checkbox drives - it flips
    # the test transfer job's active flag in ODB, next to the Test_Transfer_Failing rule's own flip.
    Set_Test_Transfer_State_Service = 'zato.alerting.set-test-transfer-state'

    # The keys the scheduler job's extra data may carry - the email addressing,
    # where the catch-all digest goes, the Dashboard address the links point to
    # and the default plain-webhook URL a rule without its own delivers through.
    # Email, Slack and Teams themselves go out through the connections that share
    # the default notification name, so the connection and webhook keys stay only
    # for the read-write contract of the config services and enmasse.
    Extra_Email_Connection = 'email_connection'
    Extra_LLM_Connection   = 'llm_connection'
    Extra_From             = 'from'
    Extra_Default_To       = 'default_to'
    Extra_Dashboard_URL    = 'dashboard_url'
    Extra_Slack_Webhook    = 'slack_webhook'
    Extra_Teams_Webhook    = 'teams_webhook'
    Extra_Webhook_URL      = 'webhook_url'

    # The services the config screen's notifications row goes through - one reads
    # the current values from the sweep job's extra, the other writes them back.
    Get_Notification_Config_Service = 'zato.alerting.get-notification-config'
    Set_Notification_Config_Service = 'zato.alerting.set-notification-config'

    # The rule engine rulesets the alert rules live in and the vocabulary their editor completes
    # from. Every ruleset whose name is the prefix itself or starts with the prefix plus
    # an underscore belongs to alerting - alerts_rest, alerts_sql and so on - and the sweep
    # matches facts through all of them.
    Ruleset_Prefix  = 'alerts'
    Vocabulary_Name = 'alerting'

    # Explanations - an alert the LLM explains goes to this service instead of its own action,
    # the service explains it with the skill of the alert's source and the evidence the collectors
    # measured, and then runs the rule's own action itself. The explanation is stored as a generic
    # object of this type next to the alert - there is no lifecycle, it travels out with the
    # alert's notifications and whatever happens next lives in the receiving system.
    Service_Explain  = 'zato.alerting.explain'
    Explanation_Type = 'zato-alert-explanation'

    # The name shared by the notification connections - one Slack, one Microsoft Teams, one SMTP,
    # all created when the environment is, inactive and with placeholder details, and the
    # environment variable that renames them.
    Notification_Conn_Name     = 'default.alerts.notifications'
    Env_Notification_Conn_Name = 'Zato_Alerts_Connection'

    # The keys a rule's action_config may carry to say where the Slack and Teams actions deliver.
    Config_Slack_Channel = 'slack_channel'
    Config_Teams_To      = 'teams_to'

    # The remediation an explanation may propose where the skill of the source allows it -
    # it repeats the failed deliveries through the same connection.
    Remediation_Resubmit = 'resubmit'

# ################################################################################################################################
# ################################################################################################################################

class LDAP:

    class DEFAULT:
        CONNECT_TIMEOUT  = 10
        POOL_EXHAUST_TIMEOUT = 5
        POOL_KEEP_ALIVE = 30
        POOL_LIFETIME = 3600
        POOL_MAX_CYCLES  = 1
        POOL_SIZE = 1
        Server_List = 'localhost:1389'
        Username = 'cn=admin,dc=example,dc=org'

    class AUTH_TYPE:
        NTLM   = NameId('NTLM', 'NTLM')
        SIMPLE = NameId('Simple', 'SIMPLE')

        def __iter__(self):
            return iter((self.SIMPLE, self.NTLM))

    class AUTO_BIND:
        DEFAULT         = NameId('Default', 'DEFAULT')
        NO_TLS          = NameId('No TLS', 'NO_TLS')
        NONE            = NameId('None', 'NONE')
        TLS_AFTER_BIND  = NameId('Bind -> TLS', 'TLS_AFTER_BIND')
        TLS_BEFORE_BIND = NameId('TLS -> Bind', 'TLS_BEFORE_BIND')

        def __iter__(self):
            return iter((self.DEFAULT, self.NONE, self.NO_TLS, self.TLS_AFTER_BIND, self.TLS_BEFORE_BIND))

    class GET_INFO:
        ALL    = NameId('All', 'ALL')
        DSA    = NameId('DSA', 'DSA')
        NONE   = NameId('None', 'NONE')
        SCHEMA = NameId('Schema', 'SCHEMA')
        OFFLINE_EDIR_8_8_8  = NameId('EDIR 8.8.8', 'OFFLINE_EDIR_8_8_8')
        OFFLINE_AD_2012_R2  = NameId('AD 2012.R2', 'OFFLINE_AD_2012_R2')
        OFFLINE_SLAPD_2_4   = NameId('SLAPD 2.4', 'OFFLINE_SLAPD_2_4')
        OFFLINE_DS389_1_3_3 = NameId('DS 389.1.3.3', 'OFFLINE_DS389_1_3_3')

        def __iter__(self):
            return iter((self.NONE, self.ALL, self.SCHEMA, self.DSA,
                self.OFFLINE_EDIR_8_8_8, self.OFFLINE_AD_2012_R2, self.OFFLINE_SLAPD_2_4, self.OFFLINE_DS389_1_3_3))

    class IP_MODE:
        IP_V4_ONLY        = NameId('Only IPv4', 'IP_V4_ONLY')
        IP_V6_ONLY        = NameId('Only IPv6', 'IP_V6_ONLY')
        IP_V4_PREFERRED   = NameId('Prefer IPv4', 'IP_V4_PREFERRED')
        IP_V6_PREFERRED   = NameId('Prefer IPv6', 'IP_V6_PREFERRED')
        IP_SYSTEM_DEFAULT = NameId('System default', 'IP_SYSTEM_DEFAULT')

        def __iter__(self):
            return iter((self.IP_V4_ONLY, self.IP_V6_ONLY, self.IP_V4_PREFERRED, self.IP_V6_PREFERRED, self.IP_SYSTEM_DEFAULT))

    class POOL_HA_STRATEGY:
        FIRST       = NameId('First', 'FIRST')
        RANDOM      = NameId('Random', 'RANDOM')
        ROUND_ROBIN = NameId('Round robin', 'ROUND_ROBIN')

        def __iter__(self):
            return iter((self.FIRST, self.RANDOM, self.ROUND_ROBIN))

    class SASL_MECHANISM:
        GSSAPI = NameId('GSS-API', 'GSSAPI')
        EXTERNAL = NameId('External', 'EXTERNAL')

        def __iter__(self):
            return iter((self.EXTERNAL, self.GSSAPI))

# ################################################################################################################################
# ################################################################################################################################

class LLM:

    class DEFAULT:
        POOL_SIZE = 50
        TIMEOUT = 60
        MAX_TOKENS = 1024
        MAX_HISTORY_TURNS = 20
        CHAT_EXPIRY = 86400

    # The base API URL of each provider's protocol
    class ADDRESS:
        CLAUDE = 'https://api.anthropic.com'
        OPENAI = 'https://api.openai.com/v1'
        GEMINI = 'https://generativelanguage.googleapis.com/v1beta'

    class PROVIDER:
        OPENAI = NameId('OpenAI', 'openai')
        CLAUDE = NameId('Claude', 'claude')
        GEMINI = NameId('Gemini', 'gemini')

# ################################################################################################################################
# ################################################################################################################################

class ODATA:

    class DEFAULT:
        ODATA_VERSION = '4.0'
        PAGE_SIZE = 0
        POOL_SIZE = 1
        TIMEOUT = 60

    class VERSION:
        V4 = NameId('OData 4.0', '4.0')
        V2 = NameId('OData 2.0', '2.0')

        def __iter__(self):
            return iter((self.V4, self.V2))

    class AUTH_TYPE:
        NO_AUTH = NameId('No auth', 'no-auth')
        BASIC   = NameId('Basic', 'basic')
        BEARER  = NameId('Bearer', 'bearer')
        OAUTH2  = NameId('OAuth2', 'oauth2')

        def __iter__(self):
            return iter((self.NO_AUTH, self.BASIC, self.BEARER, self.OAUTH2))

# ################################################################################################################################
# ################################################################################################################################

# Each subtype is one full deployment of the OData implementation - the same client, screens and enmasse code
# serve every subtype, differing only in what this configuration describes.
ODATA_Subtype = {
    'odata': {
        'label': 'OData',
        'url_prefix': 'out-odata',
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_ODATA,
        'odata_version': ODATA.VERSION.V4.id,
        'needs_csrf_token': False,
    },
    'sap': {
        'label': 'SAP',
        'url_prefix': 'out-sap',
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_SAP,
        'odata_version': ODATA.VERSION.V2.id,
        'needs_csrf_token': True,
    },
}

# ################################################################################################################################
# ################################################################################################################################

# Each subtype is one full deployment of the AMQP implementation - the same connector, screens and enmasse code
# serve every subtype, differing only in what this configuration describes. The subtype of a connection
# is stored in its opaque attributes, and a connection without one is a plain AMQP connection.
AMQP_Subtype_Plain = 'amqp'
AMQP_Subtype_Azure_Service_Bus = 'azure-service-bus'

AMQP_Subtype = {
    AMQP_Subtype_Plain: {
        'label': 'AMQP',
        'url_prefix_outgoing': 'out-amqp',
        'url_prefix_channel': 'channel-amqp',
        'address_example': 'localhost:5672',
    },
    AMQP_Subtype_Azure_Service_Bus: {
        'label': 'Azure Service Bus',
        'url_prefix_outgoing': 'out-azure-service-bus',
        'url_prefix_channel': 'channel-azure-service-bus',
        'address_example': 'my-namespace.servicebus.windows.net:5671',
    },
}

# ################################################################################################################################
# ################################################################################################################################

class MongoDB:

    class Default:
        Server_List = 'localhost:27017'
        Auth_Source = 'admin'
        App_Name = 'Zato'
        Pool_Size_Max = 10
        Connect_Timeout = 10
        Server_Select_Timeout = 5

# ################################################################################################################################
# ################################################################################################################################

class SMB:

    class DEFAULT:
        PORT = 445

# ################################################################################################################################
# ################################################################################################################################

class FTP:

    class DEFAULT:
        PORT = 21

# ################################################################################################################################
# ################################################################################################################################

class SFTP:

    class DEFAULT:
        BUFFER_SIZE = 32768
        COMMAND_SFTP = 'sftp'
        COMMAND_PING = 'ls .'
        PORT = 22

    class LOG_LEVEL:
        LEVEL0 = NameId('0', '0')
        LEVEL1 = NameId('1', '1')
        LEVEL2 = NameId('2', '2')
        LEVEL3 = NameId('3', '3')
        LEVEL4 = NameId('4', '4')

        def __iter__(self):
            return iter((self.LEVEL0, self.LEVEL1, self.LEVEL2, self.LEVEL3, self.LEVEL4))

        def is_valid(self, value:'any_') -> 'bool':
            return value in (elem.id for elem in self)

# ################################################################################################################################
# ################################################################################################################################

# We need to use such a constant because we can sometimes be interested in setting
# default values which evaluate to boolean False.
NO_DEFAULT_VALUE = 'NO_DEFAULT_VALUE'
PLACEHOLDER = 'zato_placeholder'

# ################################################################################################################################
# ################################################################################################################################

class MS_SQL:
    ZATO_DIRECT = 'zato+mssql1'
    EXTRA_KWARGS = 'login_timeout', 'appname', 'blocksize', 'use_mars', 'readonly', 'use_tz', 'bytes_to_unicode', \
        'cafile', 'validate_host'

# ################################################################################################################################
# ################################################################################################################################

class SALESFORCE:

    class Default:
        Address = 'https://example.my.salesforce.com'
        API_Version = '54.0'
        Pool_Size = 20
        Recv_Timeout = 250

# ################################################################################################################################
# ################################################################################################################################

class AWS:

    class Default:
        Region = 'us-east-1'
        Pool_Size = 20
        Recv_Timeout = 250

# ################################################################################################################################
# ################################################################################################################################

class Atlassian:

    class Default:
        Address = 'https://example.atlassian.net'
        API_Version = '3'

# ################################################################################################################################
# ################################################################################################################################

class Microsoft365:

    class Default:
        Address = 'https://graph.microsoft.com'
        Auth_Server_URL = 'https://login.microsoftonline.com'
        Auth_Redirect_URL = 'https://zato.io/ext/redirect/oauth2'
        Scopes = [
            'https://graph.microsoft.com/.default'
        ]
        Verify_TLS = True

# ################################################################################################################################
# ################################################################################################################################

class Discord:

    class Default:
        Address = 'https://discord.com/api/v10'
        Ready_Timeout = 60
        Timeout = 30

# ################################################################################################################################
# ################################################################################################################################

class Slack:

    class Default:
        Address = 'https://slack.com/api'
        Pool_Size = 20

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftPowerAutomate:

    class Default:
        Address = 'https://api.flow.microsoft.com'
        API_Version = '2016-11-01'
        Login_URL = 'https://login.microsoftonline.com'
        Pool_Size = 20
        Scope = 'https://service.flow.microsoft.com/.default'
        Trigger_Name = 'manual'

# ################################################################################################################################
# ################################################################################################################################

class MicrosoftFabric:

    class Default:
        Address = 'https://api.fabric.microsoft.com/v1'
        Eventhouse_Query_Path = '/v1/rest/query'
        Eventhouse_Scope = 'https://kusto.kusto.windows.net/.default'
        Job_Poll_Interval = 10.0
        Job_Timeout = 1800
        Livy_API_Version = '2023-12-01'
        Login_URL = 'https://login.microsoftonline.com'
        OneLake_Address = 'https://onelake.dfs.fabric.microsoft.com'
        OneLake_Scope = 'https://storage.azure.com/.default'
        Operation_Poll_Interval = 2.0
        Operation_Timeout = 600
        Pool_Size = 20
        Scope = 'https://api.fabric.microsoft.com/.default'
        Spark_Session_Timeout = 600
        SQL_Login_Timeout = 30
        SQL_Pool_Size = 5
        SQL_Port = 1433
        SQL_Schema = 'dbo'
        SQL_Scope = 'https://database.windows.net/.default'
        Table_Chunk_Rows = 100000
        Table_Files_Prefix = 'Files/zato'

    class Operation_Status:
        Failed = 'Failed'
        Succeeded = 'Succeeded'

    class Job_Status:
        Completed = 'Completed'
        In_Progress = 'InProgress'
        Not_Started = 'NotStarted'

    class Sync_Status:
        Failure = 'Failure'

    class Spark_State:
        Available = 'available'
        Cancelled = 'cancelled'
        Dead = 'dead'
        Error = 'error'
        Idle = 'idle'
        Killed = 'killed'

    class Spark_Output_Status:
        Error = 'error'

# ################################################################################################################################
# ################################################################################################################################

class OAuth:

    class Client_Auth_Method:
        Client_Secret = 'client_secret'
        Private_Key_JWT = 'private_key_jwt'

    class JWT_Algorithm:
        RS256 = 'RS256'
        RS384 = 'RS384'
        PS256 = 'PS256'
        ES384 = 'ES384'

    # The algorithms a client assertion can be signed with, in the order the Dashboard lists them.
    JWT_Algorithms = (JWT_Algorithm.RS384, JWT_Algorithm.RS256, JWT_Algorithm.PS256, JWT_Algorithm.ES384)

    # The RFC 7523 value of client_assertion_type in a token request.
    Assertion_Type = 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'

    # How long a client assertion stays valid, measured from the moment it is signed.
    Assertion_Lifetime_Seconds = 300

    # The opaque fields of a definition that are stored encrypted and never returned.
    Secret_Fields = ('private_key',)

    class Default:
        Auth_Server_URL = 'https://example.com/oauth2/token'
        Scopes = [] # There are no default scopes
        Client_ID_Field = 'client_id'
        Client_Secret_Field = 'client_secret'
        Grant_Type = 'client_credentials'
        Client_Auth_Method = 'client_secret'
        JWT_Algorithm = 'RS384'

# ################################################################################################################################
# ################################################################################################################################

# TODO: IO.FORMAT should be removed in favour of plain DATA_FORMAT
class IO:

    class FORMAT(Attrs):
        FORM_DATA = DATA_FORMAT.FORM_DATA
        JSON = DATA_FORMAT.JSON

    COMMON_FORMAT = OrderedDict()
    COMMON_FORMAT[DATA_FORMAT.JSON] = 'JSON'

    HTTP_SOAP_FORMAT = OrderedDict()
    HTTP_SOAP_FORMAT[DATA_FORMAT.JSON] = 'JSON'
    HTTP_SOAP_FORMAT[DATA_FORMAT.FORM_DATA] = 'Form data'

    Bearer_Token_Format = [
        NameId('JSON', DATA_FORMAT.JSON),
        NameId('Form data', DATA_FORMAT.FORM_DATA)
    ]

    Bearer_Token_Client_Auth_Method = [
        NameId('Client secret', OAuth.Client_Auth_Method.Client_Secret),
        NameId('Private key JWT', OAuth.Client_Auth_Method.Private_Key_JWT),
    ]

    Bearer_Token_JWT_Algorithm = [
        NameId(OAuth.JWT_Algorithm.RS384),
        NameId(OAuth.JWT_Algorithm.RS256),
        NameId(OAuth.JWT_Algorithm.PS256),
        NameId(OAuth.JWT_Algorithm.ES384),
    ]

# ################################################################################################################################
# ################################################################################################################################

class UNITTEST:
    SQL_ENGINE = 'zato+unittest'
    HTTP       = 'zato+unittest'

class HotDeploy:
    UserPrefix = 'hot-deploy.user'
    UserConfPrefix = 'user_conf'
    Source_Directory = 'src'
    User_Conf_Directory = 'user-conf'
    Enmasse_File_Pattern = 'enmasse'
    Default_Patterns = [User_Conf_Directory, Enmasse_File_Pattern]

    class Env:
        Pickup_Patterns = 'Zato_Hot_Deploy_Pickup_Patterns'

# ################################################################################################################################
# ################################################################################################################################

ZATO_INFO_FILE = '.zato-info'

# ################################################################################################################################
# ################################################################################################################################

class SourceCodeInfo:
    """ Attributes describing the service's source code file.
    """
    __slots__ = 'source', 'source_html', 'len_source', 'path', 'hash', 'hash_method', 'server_name', 'line_number'

    def __init__(self):
        self.source = b''       # type: bytes
        self.source_html = ''   # type: str
        self.len_source = 0     # type: int
        self.path = None        # type: strnone
        self.hash = None        # type: strnone
        self.hash_method = None # type: strnone
        self.server_name = None # type: strnone
        self.line_number = 0    # type: int

# ################################################################################################################################
# ################################################################################################################################

class IDEDeploy:
    Username = 'ide_publisher'

# ################################################################################################################################
# ################################################################################################################################

class SMTPMessage:

    from_: 'any_'
    to: 'any_'
    subject: 'any_'
    body: 'any_'
    attachments: 'any_'
    cc: 'any_'
    bcc: 'any_'
    is_html: 'any_'
    headers: 'any_'
    charset: 'any_'
    is_rfc2231: 'any_'

    def __init__(self, from_:'any_'=None, to:'any_'=None, subject:'str'='', body:'str'='', attachments:'any_'=None,
            cc:'any_'=None, bcc:'any_'=None, is_html:'bool'=False, headers:'any_'=None,
            charset:'str'='utf8', is_rfc2231:'bool'=True) -> 'None':
        self.from_ = from_
        self.to = to
        self.subject = subject
        self.body = body
        self.attachments = attachments or []
        self.cc = cc
        self.bcc = bcc
        self.is_html = is_html
        self.headers = headers or {}
        self.charset = charset
        self.is_rfc2231 = is_rfc2231

    def attach(self, name:'str', contents:'any_') -> 'None':
        self.attachments.append({'name':name, 'contents':contents})

# ################################################################################################################################
# ################################################################################################################################

def _uid_as_str(uid:'any_') -> 'str':
    """ Generic IMAP servers report uids as bytes while Microsoft 365 uses str, this normalizes them.
    """
    if isinstance(uid, bytes):
        out = uid.decode('utf-8')
    else:
        out = uid

    return out

# ################################################################################################################################
# ################################################################################################################################

class IMAPMessage:
    def __init__(self, uid:'str', conn:'Imbox', data:'any_') -> 'None':
        self.uid = uid
        self.conn = conn
        self.data = data

    def __repr__(self):
        class_name = self.__class__.__name__
        self_id = hex(id(self))
        return '<{} at {}, uid:`{}`, conn.config:`{}`>'.format(class_name, self_id, self.uid, self.conn.config_no_sensitive)

    def delete(self):
        raise NotImplementedError('Must be implemented by subclasses')

    def mark_seen(self):
        raise NotImplementedError('Must be implemented by subclasses')

    def to_dict(self) -> 'stranydict':
        """ The message as a JSON-friendly dict - what the audit log records and what a service returning the message
        it received answers with. Attachments are described by name, type and size rather than carried along.
        """
        attachments = []

        for attachment in self.data.attachments:
            attachments.append({
                'filename': attachment['filename'],
                'content_type': attachment['content-type'],
                'size': attachment['size'],
            })

        out:'stranydict' = {
            'uid': _uid_as_str(self.uid),
            'subject': self.data.subject,
            'sent_from': self.data.sent_from,
            'body': self.data.body,
            'attachments': attachments,
        }
        return out

    def documents(self) -> 'doclist':
        """ The documents of every attachment of this message, in the order the attachments come in.
        """
        from zato.common.documents.unpack import read_documents

        out = []

        for attachment in self.data.attachments:
            data = attachment['content'].getvalue()
            out.extend(read_documents(data, file_name=attachment['filename'], mime_type=attachment['content-type']))

        return out

# ################################################################################################################################
# ################################################################################################################################

class IMAPAttachment:
    """ A single attachment extracted from an IMAP message, handed over to services invoked by the scheduler
    in the each-attachment mode.
    """

    def __init__(
        self,
        message:'IMAPMessage',
        filename:'str',
        content_type:'str',
        size:'int',
        data:'bytes',
        content_id:'strnone',
        ) -> 'None':

        # The parent message that this attachment was extracted from
        self.message = message
        self.msg_uid = message.uid
        self.subject = message.data.subject
        self.sent_from = message.data.sent_from

        # The attachment itself
        self.filename = filename
        self.content_type = content_type
        self.size = size
        self.data = data
        self.content_id = content_id

    def __repr__(self):
        class_name = self.__class__.__name__
        self_id = hex(id(self))
        return '<{} at {}, filename:`{}`, content_type:`{}`, size:`{}`, msg_uid:`{}`>'.format(
            class_name, self_id, self.filename, self.content_type, self.size, self.msg_uid)

    def to_dict(self) -> 'stranydict':
        """ The attachment as a JSON-friendly dict - what the audit log records and what a service returning the attachment
        it received answers with. The bytes become text, size is still the byte count.
        """
        out:'stranydict' = {
            'msg_uid': _uid_as_str(self.msg_uid),
            'subject': self.subject,
            'sent_from': self.sent_from,
            'filename': self.filename,
            'content_type': self.content_type,
            'size': self.size,
            'content_id': self.content_id,
            'data': self.data.decode('utf8', 'replace'),
        }
        return out

    def documents(self) -> 'doclist':
        """ The documents this attachment carries - the attachment itself unless it is an archive, in which case
        each file inside, and each document the metadata names if the archive is an IHE XDM package.
        """
        from zato.common.documents.unpack import read_documents

        out = read_documents(self.data, file_name=self.filename, mime_type=self.content_type)
        return out

# ################################################################################################################################
# ################################################################################################################################

class Documents:
    """ Documents arriving inside email attachments, files and archives, and how the containers they come in are read.
    """

    # What every zip archive begins with
    Zip_Magic = b'PK\x03\x04'

    # The type of a document whose container says nothing about it and whose name tells nothing either
    Default_Mime_Type = 'application/octet-stream'

    # The types that the names of clinical documents mean, the same on every system - anything else is left
    # to what the system itself knows about file names
    Mime_Types = {
        '.xml':  'application/xml',
        '.cda':  'application/cda+xml',
        '.ccda': 'application/cda+xml',
        '.pdf':  'application/pdf',
        '.json': 'application/json',
        '.txt':  'text/plain',
        '.zip':  'application/zip',
    }

    class Source:
        Attachment = 'attachment'
        Zip = 'zip'
        XDM = 'xdm'

    class Reason:
        Bad_Zip = 'bad-zip'
        No_Metadata = 'no-metadata'
        Missing_File = 'missing-file'
        Hash_Mismatch = 'hash-mismatch'
        Size_Mismatch = 'size-mismatch'

    class XDM:
        """ IHE Cross-Enterprise Document Media Interchange - a zip with the documents of each submission set
        in a subdirectory of IHE_XDM, described by the ebRIM metadata file next to them.
        """
        Dir = 'IHE_XDM'
        Metadata_File = 'METADATA.XML'

        # What a Direct message's subject carries when the message holds an XDM package
        Subject_Marker = 'XDM/1.0/DDM'

        # The metadata's XML namespaces
        NS_RIM = 'urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0'
        NS_LCM = 'urn:oasis:names:tc:ebxml-regrep:xsd:lcm:3.0'

        class Slot:
            URI = 'URI'
            Hash = 'hash'
            Size = 'size'
            Creation_Time = 'creationTime'
            Language_Code = 'languageCode'

        # The classification and identification schemes of a document entry
        class Scheme:
            Class_Code = 'urn:uuid:41a5887f-8865-4c09-adf7-e362475b143a'
            Type_Code  = 'urn:uuid:f0306f51-975f-434e-a61c-c59651d33983'
            Patient_ID = 'urn:uuid:58a6f841-87b3-4a3e-92fd-a8ffeff98427'
            Unique_ID  = 'urn:uuid:2e82c1f6-a085-4c72-9da3-8640a32e42ab'

# ################################################################################################################################
# ################################################################################################################################

class Name_Prefix:
    Keysight_Hawkeye = 'KeysightHawkeye.'
    Keysight_Vision  = 'KeysightVision.'

Wrapper_Name_Prefix_List = {
    Name_Prefix.Keysight_Hawkeye,
    Name_Prefix.Keysight_Vision,
}

# ################################################################################################################################
# ################################################################################################################################

class Wrapper_Type:
    Keysight_Hawkeye = 'KeysightHawkeye'
    Keysight_Vision  = 'KeysightVision'

# ################################################################################################################################
# ################################################################################################################################

class HAProxy:
    Default_Memory_Limit = '1024' # In megabytes = 1 GB

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class URLInfo:
    address: 'str'
    host: 'str'
    port: 'int'
    use_tls: 'bool'

# ################################################################################################################################
# ################################################################################################################################

class RESTAdapterResponse:
    def __init__(self, data:'any_', raw_response:'any_') -> 'None':
        self.data = data
        self.raw_response = raw_response

# ################################################################################################################################
# ################################################################################################################################

Default_Service_File_Data = """
# -*- coding: utf-8 -*-

# File path: {full_path}

# Zato
from zato.server.service import Service

class MyService(Service):

    # I/O definition
    input = '-name'
    output = 'salutation'

    def handle(self):

        # Local variables
        name = self.request.input.name or 'partner'

        # Our response to produce
        message = f'Howdy {{name}}!'

        # Reply to our caller
        self.response.payload.salutation = message
""".lstrip()

# ################################################################################################################################
# ################################################################################################################################

Default_Extra_Service_File_Data = """
# -*- coding: utf-8 -*-

# File path: {full_path}

# stdlib
from random import uniform
from time import sleep

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

_default_sleep_seconds = 3
_default_sleep_jitter = 1.5
_minimum_sleep_seconds = 0.1

# ################################################################################################################################
# ################################################################################################################################

class Echo(Service):
    \"\"\" Echoes back any JSON payload sent to it. Accepts arbitrary key-value pairs
    and returns them unchanged. Use this service to verify connectivity and to
    inspect how Zato processes and returns request data.
    \"\"\"

    name = 'demo.echo'

    def handle(self):

        # Log the request ..
        payload = self.request.payload
        self.logger.info(f'Received request: `{{payload}}`')

        # .. write a note with the payload as its data ..
        self.audit.write('Echoed the request back', data=payload, item_count=len(payload))

        # .. and return the payload unchanged.
        self.response.payload = payload

# ################################################################################################################################
# ################################################################################################################################

class Raise(Service):
    \"\"\" Always raises an exception. Used to verify how errors are reported to callers.
    \"\"\"

    name = 'test.raise'

    def handle(self):

        # Write an error note ..
        self.audit.write('About to raise the test exception', is_ok=False, status='Test exception')

        # .. and raise.
        raise Exception('Test exception')

# ################################################################################################################################
# ################################################################################################################################

class Sleep(Service):
    \"\"\" Sleeps for a number of seconds plus a random jitter.
    \"\"\"

    name = 'demo.sleep'
    input = '-seconds', '-jitter'
    output = 'message'

    def handle(self):

        # Read the input ..
        seconds = self.request.input.seconds or _default_sleep_seconds
        seconds = float(seconds)

        jitter_range = self.request.input.jitter or _default_sleep_jitter
        jitter_range = float(jitter_range)

        # .. draw the jitter ..
        jitter = uniform(-jitter_range, jitter_range)
        requested_seconds = seconds + jitter
        slept_seconds = max(_minimum_sleep_seconds, requested_seconds)

        # .. sleep ..
        sleep(slept_seconds)

        # .. write a note with the numbers as fields ..
        self.audit.write('Slept as requested', seconds=slept_seconds, jitter=jitter)

        # .. and reply.
        self.response.payload.message = 'OK, slept for {{:.1f}}s (jitter={{:+.1f}}s)'.format(slept_seconds, jitter)
""".lstrip()

# ################################################################################################################################
# ################################################################################################################################

Default_Demo_PubSub_Service_File_Data = """\
# -*- coding: utf-8 -*-

# stdlib
from datetime import datetime, timezone

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class DemoPubSubPublisher(Service):

    name = 'demo.pubsub.publisher'

    def handle(self):
        now = datetime.now(timezone.utc).strftime('%H:%M:%S')
        self.publish('demo.messages', {'timestamp': now})
        self.logger.info('Published 1 message to demo.messages at %s', now)

# ################################################################################################################################
# ################################################################################################################################
"""

# ################################################################################################################################
# ################################################################################################################################

class HL7:

    class Default:
        address_fhir = 'http://localhost:8080/fhir'
        channel_host = '0.0.0.0'
        channel_port = 11223
        data_encoding = 'utf-8'
        end_seq = '1c 0d'
        logging_level = 'INFO'
        max_wait_time = 5
        pool_size = 10
        read_buffer_size = 32768
        recv_timeout = 250
        start_seq = '0b'

        # How long a channel lets a connection produce nothing before closing it, in seconds
        idle_timeout = 300

        # How often the kernel probes a quiet connection, and how many unanswered probes end it
        keepalive_idle          = 60
        keepalive_interval      = 10
        keepalive_probe_count   = 6

        # The largest message accepted - channels express it as a value plus a unit,
        # outgoing connections as a byte count, and both describe the same size.
        max_msg_size_value = 2
        max_msg_size_unit  = 'mb'
        max_msg_size       = 2 * 1024 * 1024

        # Circuit breaker defaults (outbound)
        circuit_breaker_threshold_percent = 50
        circuit_breaker_window_seconds    = 60
        circuit_breaker_reset_seconds     = 60

        # Dedup defaults (inbound) - a TTL of zero means every message is delivered
        dedup_ttl_value = 0
        dedup_ttl_unit  = 'days'

        # TLS defaults
        tls_version_min = 'TLSv1.2'

    class Const:

        class Version:
            v2   = NameId('HL7 v2.x', 'hl7-v2')
            ccda = NameId('C-CDA', 'hl7-ccda')

            def __iter__(self):
                return iter((self.v2, self.ccda))

        class ImplClass:
            zato = 'zato'

        class LoggingLevel:
            DEBUG = NameId('DEBUG', 'DEBUG')
            INFO = NameId('INFO', 'INFO')
            WARNING = NameId('WARNING', 'WARNING')
            ERROR = NameId('ERROR', 'ERROR')

            def __iter__(self):
                return iter((self.DEBUG, self.INFO, self.WARNING, self.ERROR))

        class FHIR_Auth_Type:
            No_Auth = NameId('No auth', 'no-auth')
            Basic_Auth = NameId('Basic Auth', 'basic-auth')
            OAuth = NameId('OAuth', 'oauth')

            def __iter__(self):
                return iter((self.No_Auth, self.Basic_Auth, self.OAuth))

    class BulkExport:
        """ The FHIR Bulk Data $export an outgoing FHIR connection runs - its field names, the job
        that runs it and the services that start it and deliver its files.
        """

        class Level:
            Group   = 'group'
            Patient = 'patient'
            System  = 'system'

        LevelList = (Level.Group, Level.Patient, Level.System)

        # The path each level kicks the export off at - the group one has the group ID filled in
        Kickoff_Path = {
            Level.Group:   '/Group/{group_id}/$export',
            Level.Patient: '/Patient/$export',
            Level.System:  '/$export',
        }

        # Prefix of the names of the jobs auto-created for connections with a schedule
        Job_Prefix = 'bulk-export.'

        # The service a job invokes to start an export, and the one that hands each file to its destinations
        Dispatch_Service = 'zato.hl7.fhir.bulk-export.run'
        Deliver_Service  = 'zato.hl7.fhir.bulk-export.deliver'

        # Where the files are downloaded to - an environment variable, or a directory under the server's work dir
        Env_Dir     = 'Zato_FHIR_Bulk_Export_Dir'
        Default_Dir = 'fhir-bulk-export'

        # How long to wait between polls when the server does not say, and how many times a file download is tried
        Default_Retry_After = 10
        Download_Retries    = 3

        # What the output files are, and the type of the files that list what the server could not export
        Content_Type        = 'application/fhir+ndjson'
        Error_Resource_Type = 'OperationOutcome'

        # The name of the file an export's state is kept in, and of the log the program writes
        State_File_Name = 'state.json'
        Log_File_Name   = 'fhir-bulk-export.log'

        # The connection fields the tab holds
        Field_Is_Active        = 'bulk_export_is_active'
        Field_Level            = 'bulk_export_level'
        Field_Group_ID         = 'bulk_export_group_id'
        Field_Patient_IDs      = 'bulk_export_patient_ids'
        Field_Types            = 'bulk_export_types'
        Field_Since            = 'bulk_export_since'
        Field_Type_Filter      = 'bulk_export_type_filter'
        Field_Run_Every        = 'bulk_export_run_every'
        Field_Run_Unit         = 'bulk_export_run_unit'
        Field_Start_Date       = 'bulk_export_start_date'
        Field_Job_ID           = 'bulk_export_job_id'
        Field_Destinations     = 'bulk_export_destinations'
        Field_Delete_Files     = 'bulk_export_delete_files'
        Field_Delete_On_Server = 'bulk_export_delete_on_server'

        # The fields of the schedule, in the order the job sync reads them
        ScheduleFieldList = (Field_Run_Every, Field_Run_Unit, Field_Start_Date, Field_Job_ID)

        # The fields a run may be started with by hand, overriding the tab
        OverrideFieldList = ('level', 'group_id', 'patient_ids', 'types', 'since', 'type_filter', 'destinations')

        # The YAML key enmasse keeps the tab under, and the prefix stripped off each field inside it
        Enmasse_Key   = 'bulk_export'
        Field_Prefix  = 'bulk_export_'

        # The phases an export's audit events are recorded under
        class Phase:
            Kickoff  = 'kick-off'
            Poll     = 'poll'
            Manifest = 'manifest'
            Download = 'download'
            Deliver  = 'deliver'
            Cleanup  = 'cleanup'
            Done     = 'done'
            Failed   = 'failed'

        # The statuses a job goes through
        class Status:
            Running = 'running'
            Done    = 'done'
            Failed  = 'failed'

    class CCDA:
        """ The conversion of C-CDA documents to FHIR bundles - the data format of channels that convert
        on arrival and where the converter that does the work is installed.
        """

        # The data format of an HL7 REST channel that converts each document before its service runs
        Data_Format = 'hl7-ccda'

        # Where the converter is installed - an environment variable, or a directory next to the Python interpreter
        Env_Dir          = 'Zato_FHIR_Converter_Dir'
        Default_Dir_Name = 'fhir-converter'

        # The converter's binary and the directory of its templates, both under the directory above
        Binary_Name        = 'Microsoft.Health.Fhir.Liquid.Converter.Tool'
        Templates_Dir_Name = 'templates'
        Templates_Set_Name = 'Ccda'

        # How long one conversion may take, in seconds
        Timeout = 60.0

        # The template used when a document names no template of its own, and the type of the bundles returned
        Default_Root_Template = 'CCD'
        Bundle_Type           = 'transaction'

        # The content type of the documents themselves
        Content_Type = 'application/cda+xml'

        # Why a conversion did not happen
        class Reason:
            Not_Installed    = 'not-installed'
            Not_CDA          = 'not-cda'
            Converter_Failed = 'converter-failed'
            Timeout          = 'timeout'

# ################################################################################################################################
# ################################################################################################################################

class PubSub:

    Test_Redis_DB = 1

    class Topic:
        Name_Max_Len = 200

    # About 3 years if we repeat delivery attempts once per second
    Max_Repeats = 100_000_000

    # 1 year in seconds
    Max_Retry_Time = 365 * 24 * 3600

    class Timeout:

        # How many seconds a consumer will wait in its drain_events call
        Consumer = 3

        # Must be bigger than the Consumer timeout to give a consumer enough time to drain its events.
        Invoke_Sync = Consumer * 2

    class API_Client:
        Publisher = 'publisher'
        Subscriber = 'subscriber'
        Publisher_Subscriber = 'publisher-subscriber'

    class Delivery_Type:
        Pull = 'pull'
        Push = 'push'

    class Backend_Type:
        Builtin = 'builtin'
        AMQP = 'amqp'

    Backend_Type_Default = Backend_Type.Builtin

    class Push_Type:
        REST = 'rest'
        Service = 'service'

    class Prefix:
        Msg_ID = 'zpsm'
        Sub_Key = 'zpsk.rest'
        Reply_Queue = 'zato-reply'

    class Outgoing:

        # Each outgoing connection that is published to has a topic of its own under this prefix.
        Topic_Prefix = 'zato.out.to.'

        # .. and a queue of its own under this one.
        Sub_Key_Prefix = 'zato.out.'

        # Every such queue is subscribed by this one service.
        Delivery_Service = 'zato.pubsub.outgoing.deliver'

        # The DLQ topic and sub key prefixes, followed by the connection's type and name or id
        DLQ_Topic_Prefix = 'zato.out.dlq.'
        DLQ_Sub_Key_Prefix = 'zato.out.dlq.'

        # Why a message is in the DLQ
        DLQ_Reason_Retries_Exhausted = 'retries-exhausted'

        # The scheduler job that runs the DLQ rule
        DLQ_Job_Name             = 'zato.pubsub.dlq'
        DLQ_Job_Interval_Minutes = 1
        DLQ_Rule_Service         = 'zato.pubsub.dlq.run'

    class Inbound:
        """ The DLQs of channels - a channel has no queue in front of it, only the DLQ its failed messages move to.
        """

        # The DLQ topic and sub key prefixes, followed by the channel's type and name or id
        DLQ_Topic_Prefix = 'zato.in.dlq.'
        DLQ_Sub_Key_Prefix = 'zato.in.dlq.'

    class Direction:
        """ Which way a connection with a DLQ moves messages.
        """
        In = 'in'
        Out = 'out'

    class REST_Server:

        Default_Host = '0.0.0.0'
        Default_Threads = 1

        Public_Port = 44556

        Default_Port_Publish = 40100
        Default_Port_Get = 40200

    class Message:
        Priority_Min = 0
        Priority_Max = 9
        Priority_Default = 5
        Default_Expiration = 86400 * 365  # 24 hours * 365 days = 1 year in seconds
        Default_Max_Len = 20_000_000
        Default_Max_Messages = 50
        Data_Preview_Len = 100

    class Delivery:
        """ The default retry policy of a published message's push delivery - the same names HTTP_SOAP.Retry has,
        for a message whose publisher gave no retry settings of its own.
        """

        # How long to keep retrying a failed delivery before giving up (30 days)
        Max_Retry_Time = 86_400 * 30

        # How many seconds to sleep before the first retry
        Default_Sleep_Time = 3

        # Each retry sleeps this many times longer than the previous one
        Default_Backoff_Multiplier = 2

        # The longest single sleep between attempts, in seconds
        Max_Sleep_Time = 15

        # Random jitter added to each sleep, as a percentage of that sleep
        Jitter_Percent = 10

        # A cap on the total sleep time across all the retries, in seconds
        Default_Backoff_Threshold = Max_Retry_Time

        # Enough attempts for the threshold to be what ends the round
        Default_Max_Retries = Max_Retry_Time // Default_Sleep_Time

        # Seconds between two rounds of one message of an outgoing connection's queue
        Retry_Round_Wait = 8

        # How long a delivery greenlet waits after a fetch that raised
        Fetch_Error_Sleep = 3

    class Repeats:
        Max = 500

    class Status:
        OK           = f'{OK} {http_responses[OK]}'
        Bad_Request  = f'{BAD_REQUEST} {http_responses[BAD_REQUEST]}'
        Unauthorized = f'{UNAUTHORIZED} {http_responses[UNAUTHORIZED]}'
        Forbidden    = f'{FORBIDDEN} {http_responses[FORBIDDEN]}'

    class Exchange_Name:
        Pubsub_Push = 'pubsub.push.1'

# ################################################################################################################################
# ################################################################################################################################
