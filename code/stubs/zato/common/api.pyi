from typing import Any

from collections import OrderedDict
from dataclasses import dataclass
from numbers import Number
from bunch import Bunch
from zato.common.defaults import http_plain_server_port
from zato.common.ext.imbox import Imbox
from zato.common.typing_ import any_

class OS_Env:
    Zato_Enable_Memory_Profiler: Any

class EnvVariable:
    Key_Prefix: Any
    Key_Missing_Suffix: Any
    Log_Env_Details: Any

class EnvFile:
    Default: Any

class EnvConfigCtx:
    component: str
    file_name: str
    missing_suffix: str

class API_Key:
    Env_Key: Any
    Default_Header: Any

class URL_TYPE:
    SOAP: Any
    PLAIN_HTTP: Any
    def __iter__(self: Any) -> None: ...

class SEARCH:
    ...

class SEC_DEF_TYPE:
    APIKEY: Any
    BASIC_AUTH: Any
    NTLM: Any
    OAUTH: Any

class AUTH_RESULT:
    ...

class BATCH_DEFAULTS:
    PAGE_NO: Any
    SIZE: Any
    MAX_SIZE: Any

class MSG_SOURCE:
    DUPLEX: Any

class NameId:
    name: Any
    id: Any
    def __init__(self: Any, name: str, id: str = ...) -> None: ...
    def __repr__(self: Any) -> None: ...

class NotGiven:
    ...

class Attrs(type):
    attrs: Any
    @classmethod
    def has(cls: Any, attr: Any) -> None: ...

class DATA_FORMAT(Attrs):
    CSV: Any
    DICT: Any
    FORM_DATA: Any
    JSON: Any
    POST: Any
    def __iter__(self: Any) -> None: ...

class DEPLOYMENT_STATUS(Attrs):
    DEPLOYED: Any
    AWAITING_DEPLOYMENT: Any
    IGNORED: Any

class SERVER_JOIN_STATUS(Attrs):
    ACCEPTED: Any

class SERVER_UP_STATUS(Attrs):
    RUNNING: Any
    CLEAN_DOWN: Any

class CACHE:
    API_USERNAME: Any

class SCHEDULER:
    InitialSleepTime: Any
    EmbeddedIndicator: Any
    EmbeddedIndicatorBytes: Any
    DefaultHost: Any
    DefaultPort: Any
    Default_Server_Host: Any
    Default_Server_Port: Any
    DefaultBindHost: Any
    DefaultBindPort: Any
    Default_API_Client_For_Server_Auth_Required: Any
    Default_API_Client_For_Server_Username: Any
    TLS_Enabled: Any
    TLS_Verify: Any
    TLS_Client_Certs: Any
    TLS_Private_Key_Location: Any
    TLS_Public_Key_Location: Any
    TLS_Cert_Location: Any
    TLS_CA_Certs_Key_Location: Any
    TLS_Version_Default_Linux: Any
    TLS_Version_Default_Windows: Any
    TLS_Ciphers_13: Any
    TLS_Ciphers_12: Any
    JobsToIgnore: Any

class CHANNEL(Attrs):
    AMQP: Any
    DELIVERY: Any
    FANOUT_CALL: Any
    FANOUT_ON_FINAL: Any
    FANOUT_ON_TARGET: Any
    HTTP_SOAP: Any
    INTERNAL_CHECK: Any
    INVOKE: Any
    INVOKE_ASYNC: Any
    INVOKE_ASYNC_CALLBACK: Any
    NEW_INSTANCE: Any
    PARALLEL_EXEC_CALL: Any
    PARALLEL_EXEC_ON_TARGET: Any
    PUBLISH: Any
    SCHEDULER: Any
    SCHEDULER_AFTER_ONE_TIME: Any
    SERVICE: Any
    STARTUP_SERVICE: Any
    URL_DATA: Any
    WORKER: Any

class CONNECTION:
    CHANNEL: Any
    OUTGOING: Any

class BROKER:
    DEFAULT_EXPIRATION: Any

class MISC:
    DEFAULT_HTTP_METHOD: Any
    DEFAULT_HTTP_TIMEOUT: Any
    OAUTH_SIG_METHODS: Any
    PIDFILE: Any
    SEPARATOR: Any
    DefaultAdminInvokeChannel: Any
    Default_Cluster_ID: Any

class HTTP_SOAP:
    UNUSED_MARKER: Any

class ADAPTER_PARAMS:
    APPLY_AFTER_REQUEST: Any
    APPLY_BEFORE_REQUEST: Any

class INFO_FORMAT:
    DICT: Any
    TEXT: Any
    JSON: Any
    YAML: Any

class URL_PARAMS_PRIORITY:
    PATH_OVER_QS: Any
    QS_OVER_PATH: Any
    DEFAULT: Any

class PARAMS_PRIORITY:
    CHANNEL_PARAMS_OVER_MSG: Any
    MSG_OVER_CHANNEL_PARAMS: Any
    DEFAULT: Any
    def __iter__(self: Any) -> None: ...

class HTTP_SOAP_SERIALIZATION_TYPE:
    STRING_VALUE: Any
    SUDS: Any
    DEFAULT: Any
    def __iter__(self: Any) -> None: ...

class EMAIL:
    ...

class CommonObject:
    Prefix_Invalid: Any
    Invalid: Any
    Security_Basic_Auth: Any

class ODOO:
    ...

class SAP:
    ...

class ContentType:
    FormURLEncoded: Any

class AMQP:
    ...

class REDIS:
    ...

class SERVER_STARTUP:
    ...

class GENERIC:
    ATTR_NAME: Any
    DeleteReason: Any
    DeleteReasonBytes: Any
    InitialReason: Any

class Groups:
    ...

class TOTP:
    default_label: Any

class LDAP:
    ...

class MONGODB:
    ...

class MS_SQL:
    ZATO_DIRECT: Any
    EXTRA_KWARGS: Any

class SALESFORCE:
    ...

class Atlassian:
    ...

class Microsoft365:
    ...

class OAuth:
    ...

class SIMPLE_IO:
    COMMON_FORMAT: Any
    HTTP_SOAP_FORMAT: Any
    Bearer_Token_Format: Any

class UNITTEST:
    SQL_ENGINE: Any
    HTTP: Any

class HotDeploy:
    UserPrefix: Any
    UserConfPrefix: Any
    Source_Directory: Any
    User_Conf_Directory: Any
    Enmasse_File_Pattern: Any
    Default_Patterns: Any

class SourceCodeInfo:
    __slots__: Any
    source: Any
    source_html: Any
    len_source: Any
    path: Any
    hash: Any
    hash_method: Any
    server_name: Any
    line_number: Any
    def __init__(self: Any) -> None: ...

class IDEDeploy:
    Username: Any

class SMTPMessage:
    from_: any_
    to: any_
    subject: any_
    body: any_
    attachments: any_
    cc: any_
    bcc: any_
    is_html: any_
    headers: any_
    charset: any_
    is_rfc2231: any_
    from_: Any
    to: Any
    subject: Any
    body: Any
    attachments: Any
    cc: Any
    bcc: Any
    is_html: Any
    headers: Any
    charset: Any
    is_rfc2231: Any
    def __init__(self: Any, from_: Any = ..., to: Any = ..., subject: Any = ..., body: Any = ..., attachments: Any = ..., cc: Any = ..., bcc: Any = ..., is_html: Any = ..., headers: Any = ..., charset: Any = ..., is_rfc2231: Any = ...) -> None: ...
    def attach(self: Any, name: Any, contents: Any) -> None: ...

class IMAPMessage:
    uid: Any
    conn: Any
    data: Any
    def __init__(self: Any, uid: Any, conn: Any, data: Any) -> None: ...
    def __repr__(self: Any) -> None: ...
    def delete(self: Any) -> None: ...
    def mark_seen(self: Any) -> None: ...

class Name_Prefix:
    Keysight_Hawkeye: Any
    Keysight_Vision: Any

class Wrapper_Type:
    Keysight_Hawkeye: Any
    Keysight_Vision: Any

class HAProxy:
    Default_Memory_Limit: Any

class URLInfo:
    address: str
    host: str
    port: int
    use_tls: bool

class RESTAdapterResponse:
    data: Any
    raw_response: Any
    def __init__(self: Any, data: any_, raw_response: any_) -> None: ...

class PubSub:
    Max_Repeats: Any
    Max_Retry_Time: Any
