from typing import Any

from datetime import datetime, timezone
from ftplib import FTP_PORT
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, LargeBinary, Sequence, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import backref, relationship
from zato.common.api import AMQP, CACHE, HTTP_SOAP_SERIALIZATION_TYPE, MISC, ODOO, SAP, SCHEDULER, PARAMS_PRIORITY, URL_PARAMS_PRIORITY
from zato.common.json_internal import json_dumps
from zato.common.odb.model.base import Base, _JSON
from zato.common.typing_ import any_, boolnone, floatnone, intnone, strnone
from zato.common.util.search import SearchResults
from sqlalchemy.orm.query import Query

def _to_str(item: Any) -> None: ...

def _to_json(model: any_, return_as_dict: bool = ...) -> any_: ...

def to_json(data: any_, return_as_dict: bool = ...) -> any_: ...

def _utcnow(_utc_zone: Any = ...) -> None: ...

class AlembicRevision(Base):
    __tablename__: Any
    version_num: Any
    version_num: Any
    def __init__(self: Any, version_num: Any = ...) -> None: ...

class ZatoInstallState(Base):
    __tablename__: Any
    id: Any
    version: Any
    install_time: Any
    source_host: Any
    source_user: Any
    opaque1: Any
    id: Any
    version: Any
    install_time: Any
    source_host: Any
    source_user: Any
    def __init__(self: Any, id: Any = ..., version: Any = ..., install_time: Any = ..., source_host: Any = ..., source_user: Any = ...) -> None: ...

class Cluster(Base):
    __tablename__: Any
    id: Any
    name: Any
    description: Any
    odb_type: Any
    odb_host: Any
    odb_port: Any
    odb_user: Any
    odb_db_name: Any
    odb_schema: Any
    broker_host: Any
    broker_port: Any
    cw_srv_id: Any
    cw_srv_keep_alive_dt: Any
    opaque1: Any
    id: Any
    name: Any
    description: Any
    odb_type: Any
    odb_host: Any
    odb_port: Any
    odb_user: Any
    odb_db_name: Any
    odb_schema: Any
    broker_host: Any
    broker_port: Any
    cw_srv_id: Any
    cw_srv_keep_alive_dt: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., description: Any = ..., odb_type: Any = ..., odb_host: Any = ..., odb_port: Any = ..., odb_user: Any = ..., odb_db_name: Any = ..., odb_schema: Any = ..., broker_host: Any = ..., broker_port: Any = ..., cw_srv_id: Any = ..., cw_srv_keep_alive_dt: Any = ...) -> None: ...
    def to_json(self: Any) -> None: ...

class Server(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    host: Any
    bind_host: Any
    bind_port: Any
    preferred_address: Any
    crypto_use_tls: Any
    last_join_status: Any
    last_join_mod_date: Any
    last_join_mod_by: Any
    up_status: Any
    up_mod_date: Any
    token: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any
    id: Any
    name: Any
    cluster: Any
    token: Any
    last_join_status: Any
    last_join_mod_date: Any
    last_join_mod_by: Any
    may_be_deleted: Any
    up_mod_date_user: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., cluster: Any = ..., token: Any = ..., last_join_status: Any = ..., last_join_mod_date: Any = ..., last_join_mod_by: Any = ...) -> None: ...

class SecurityBase(Base):
    __tablename__: Any
    __table_args__: Any
    __mapper_args__: Any
    id: Any
    name: Any
    username: Any
    password: Any
    password_type: Any
    is_active: Any
    sec_type: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any

class MultiSecurity(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    is_active: Any
    is_internal: Any
    priority: Any
    conn_id: Any
    conn_type: Any
    is_channel: Any
    is_outconn: Any
    opaque1: Any
    security_id: Any
    security: Any
    cluster_id: Any
    cluster: Any

class HTTPBasicAuth(SecurityBase):
    __tablename__: Any
    __mapper_args__: Any
    id: Any
    realm: Any
    id: Any
    name: Any
    is_active: Any
    username: Any
    realm: Any
    password: Any
    cluster: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., username: Any = ..., realm: Any = ..., password: Any = ..., cluster: Any = ...) -> None: ...

class OAuth(SecurityBase):
    __tablename__: Any
    __mapper_args__: Any
    id: Any
    proto_version: Any
    sig_method: Any
    max_nonce_log: Any
    id: Any
    name: Any
    is_active: Any
    username: Any
    password: Any
    proto_version: Any
    sig_method: Any
    max_nonce_log: Any
    cluster: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., username: Any = ..., password: Any = ..., proto_version: Any = ..., sig_method: Any = ..., max_nonce_log: Any = ..., cluster: Any = ...) -> None: ...
    def to_json(self: Any) -> None: ...

class NTLM(SecurityBase):
    __tablename__: Any
    __mapper_args__: Any
    id: Any
    id: Any
    name: Any
    is_active: Any
    username: Any
    cluster: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., username: Any = ..., password: Any = ..., cluster: Any = ...) -> None: ...
    def to_json(self: Any) -> None: ...

class APIKeySecurity(SecurityBase):
    __tablename__: Any
    __mapper_args__: Any
    id: Any
    id: Any
    name: Any
    is_active: Any
    username: Any
    password: Any
    cluster: Any
    header: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., username: Any = ..., password: Any = ..., cluster: Any = ...) -> None: ...
    def to_json(self: Any) -> None: ...

class HTTPSOAP(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    is_internal: Any
    connection: Any
    transport: Any
    host: Any
    url_path: Any
    method: Any
    content_encoding: Any
    soap_action: Any
    soap_version: Any
    data_format: Any
    content_type: Any
    ping_method: Any
    pool_size: Any
    serialization_type: Any
    timeout: Any
    merge_url_params_req: Any
    url_params_pri: Any
    params_pri: Any
    cache_expiry: Any
    opaque1: Any
    security_id: Any
    security: Any
    cache_id: Any
    cache: Any
    service_id: Any
    service: Any
    cluster_id: Any
    cluster: Any
    id: Any
    name: Any
    is_active: Any
    is_internal: Any
    connection: Any
    transport: Any
    host: Any
    url_path: Any
    method: Any
    soap_action: Any
    soap_version: Any
    data_format: Any
    ping_method: Any
    pool_size: Any
    merge_url_params_req: Any
    url_params_pri: Any
    params_pri: Any
    serialization_type: Any
    timeout: Any
    service_id: Any
    service: Any
    security: Any
    cluster_id: Any
    cluster: Any
    service_name: Any
    security_id: Any
    security_name: Any
    content_type: Any
    cache_id: Any
    cache_type: Any
    cache_expiry: Any
    cache_name: Any
    content_encoding: Any
    match_slash: Any
    http_accept: Any
    validate_tls: Any
    opaque1: Any
    is_wrapper: Any
    wrapper_type: Any
    password: Any
    security_groups_count: Any
    security_groups_member_count: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., is_internal: Any = ..., connection: Any = ..., transport: Any = ..., host: Any = ..., url_path: Any = ..., method: Any = ..., soap_action: Any = ..., soap_version: Any = ..., data_format: Any = ..., ping_method: Any = ..., pool_size: Any = ..., merge_url_params_req: Any = ..., url_params_pri: Any = ..., params_pri: Any = ..., serialization_type: Any = ..., timeout: Any = ..., service_id: Any = ..., service: Any = ..., security: Any = ..., cluster_id: Any = ..., cluster: Any = ..., service_name: Any = ..., security_id: Any = ..., security_name: Any = ..., content_type: Any = ..., cache_id: Any = ..., cache_type: Any = ..., cache_expiry: Any = ..., cache_name: Any = ..., content_encoding: Any = ..., match_slash: Any = ..., http_accept: Any = ..., validate_tls: Any = ..., opaque: Any = ..., **kwargs: Any) -> None: ...

class SQLConnectionPool(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    username: Any
    password: Any
    db_name: Any
    engine: Any
    extra: Any
    host: Any
    port: Any
    pool_size: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any
    engine_display_name: Any
    id: Any
    name: Any
    is_active: Any
    db_name: Any
    username: Any
    engine: Any
    extra: Any
    host: Any
    port: Any
    pool_size: Any
    cluster: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., db_name: Any = ..., username: Any = ..., engine: Any = ..., extra: Any = ..., host: Any = ..., port: Any = ..., pool_size: Any = ..., cluster: Any = ...) -> None: ...

class Service(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    impl_name: Any
    is_internal: Any
    slow_threshold: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any
    id: Any
    name: Any
    is_active: Any
    impl_name: Any
    is_internal: Any
    cluster: Any
    wsdl: Any
    wsdl_name: Any
    plain_http_channels: Any
    soap_channels: Any
    amqp_channels: Any
    scheduler_jobs: Any
    deployment_info: Any
    source_info: Any
    may_be_deleted: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., impl_name: Any = ..., is_internal: Any = ..., cluster: Any = ..., wsdl: Any = ..., wsdl_name: Any = ...) -> None: ...

class DeployedService(Base):
    __tablename__: Any
    __table_args__: Any
    deployment_time: Any
    details: Any
    source: Any
    source_path: Any
    source_hash: Any
    source_hash_method: Any
    opaque1: Any
    server_id: Any
    server: Any
    service_id: Any
    service: Any
    deployment_time: Any
    details: Any
    server_id: Any
    service_id: Any
    source: Any
    source_path: Any
    source_hash: Any
    source_hash_method: Any
    def __init__(self: Any, deployment_time: Any, details: Any, server_id: Any, service_id: Any, source: Any, source_path: Any, source_hash: Any, source_hash_method: Any) -> None: ...

class Job(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    job_type: Any
    start_date: Any
    extra: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any
    service_id: Any
    service: Any
    name: Any
    is_active: Any
    job_type: Any
    start_date: Any
    extra: Any
    cluster: Any
    cluster_id: Any
    service: Any
    service_id: Any
    service_name: Any
    interval_based: Any
    definition_text: Any
    job_type_friendly: Any
    id: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., job_type: Any = ..., start_date: Any = ..., extra: Any = ..., cluster: Any = ..., cluster_id: Any = ..., service: Any = ..., service_id: Any = ..., service_name: Any = ..., interval_based: Any = ..., definition_text: Any = ..., job_type_friendly: Any = ...) -> None: ...

class IntervalBasedJob(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    job_id: Any
    weeks: Any
    days: Any
    hours: Any
    minutes: Any
    seconds: Any
    repeats: Any
    opaque1: Any
    job_id: Any
    job: Any
    job: Any
    weeks: Any
    days: Any
    hours: Any
    minutes: Any
    seconds: Any
    repeats: Any
    definition_text: Any
    id: Any
    def __init__(self: Any, id: Any = ..., job: Any = ..., weeks: Any = ..., days: Any = ..., hours: Any = ..., minutes: Any = ..., seconds: Any = ..., repeats: Any = ..., definition_text: Any = ...) -> None: ...

class CacheBuiltin(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    is_default: Any
    cache_type: Any
    max_size: Any
    max_item_size: Any
    extend_expiry_on_get: Any
    extend_expiry_on_set: Any
    sync_method: Any
    persistent_storage: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any
    cluster: Any
    def __init__(self: Any, cluster: Any = ...) -> None: ...

class OutgoingAMQP(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    address: Any
    username: Any
    password: Any
    delivery_mode: Any
    priority: Any
    content_type: Any
    content_encoding: Any
    expiration: Any
    user_id: Any
    app_id: Any
    pool_size: Any
    frame_max: Any
    heartbeat: Any
    opaque1: Any
    id: Any
    name: Any
    is_active: Any
    delivery_mode: Any
    priority: Any
    content_type: Any
    content_encoding: Any
    expiration: Any
    user_id: Any
    app_id: Any
    delivery_mode_text: Any
    def_name: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., delivery_mode: Any = ..., priority: Any = ..., content_type: Any = ..., content_encoding: Any = ..., expiration: Any = ..., user_id: Any = ..., app_id: Any = ..., delivery_mode_text: Any = ..., def_name: Any = ...) -> None: ...

class OutgoingFTP(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    host: Any
    user: Any
    password: Any
    acct: Any
    timeout: Any
    port: Any
    dircache: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any
    id: Any
    name: Any
    is_active: Any
    host: Any
    user: Any
    password: Any
    acct: Any
    timeout: Any
    port: Any
    dircache: Any
    cluster_id: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., host: Any = ..., user: Any = ..., password: Any = ..., acct: Any = ..., timeout: Any = ..., port: Any = ..., dircache: Any = ..., cluster_id: Any = ...) -> None: ...

class OutgoingOdoo(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    host: Any
    port: Any
    user: Any
    database: Any
    protocol: Any
    pool_size: Any
    password: Any
    client_type: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any
    cluster: Any
    protocol_name: Any
    def __init__(self: Any, cluster: Any = ...) -> None: ...

class OutgoingSAP(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    host: Any
    sysnr: Any
    user: Any
    client: Any
    sysid: Any
    password: Any
    pool_size: Any
    router: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any
    cluster: Any
    def __init__(self: Any, cluster: Any = ...) -> None: ...

class ChannelAMQP(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    address: Any
    username: Any
    password: Any
    queue: Any
    consumer_tag_prefix: Any
    pool_size: Any
    ack_mode: Any
    prefetch_count: Any
    data_format: Any
    frame_max: Any
    heartbeat: Any
    opaque1: Any
    service_id: Any
    service: Any
    id: Any
    name: Any
    is_active: Any
    queue: Any
    consumer_tag_prefix: Any
    service_name: Any
    data_format: Any
    def __init__(self: Any, id: Any = ..., name: Any = ..., is_active: Any = ..., queue: Any = ..., consumer_tag_prefix: Any = ..., service_name: Any = ..., data_format: Any = ...) -> None: ...

class DeploymentPackage(Base):
    __tablename__: Any
    id: Any
    deployment_time: Any
    details: Any
    payload_name: Any
    payload: Any
    opaque1: Any
    server_id: Any
    server: Any
    id: Any
    deployment_time: Any
    details: Any
    payload_name: Any
    payload: Any
    def __init__(self: Any, id: Any = ..., deployment_time: Any = ..., details: Any = ..., payload_name: Any = ..., payload: Any = ...) -> None: ...

class DeploymentStatus(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    opaque1: Any
    package_id: Any
    package: Any
    server_id: Any
    server: Any
    status: Any
    status_change_time: Any
    package_id: Any
    server_id: Any
    status: Any
    status_change_time: Any
    def __init__(self: Any, package_id: Any = ..., server_id: Any = ..., status: Any = ..., status_change_time: Any = ...) -> None: ...

class ElasticSearch(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    hosts: Any
    timeout: Any
    body_as: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any

class SMTP(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    host: Any
    port: Any
    timeout: Any
    is_debug: Any
    username: Any
    password: Any
    mode: Any
    ping_address: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any

class IMAP(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    is_active: Any
    host: Any
    port: Any
    timeout: Any
    debug_level: Any
    username: Any
    password: Any
    mode: Any
    get_criteria: Any
    opaque1: Any
    cluster_id: Any
    cluster: Any

class GenericObject(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    type_: Any
    subtype: Any
    category_id: Any
    subcategory_id: Any
    creation_time: Any
    last_modified: Any
    category_name: Any
    subcategory_name: Any
    parent_object_id: Any
    parent_id: Any
    parent_type: Any
    opaque1: Any
    generic_conn_def_id: Any
    generic_conn_def_sec_id: Any
    generic_conn_id: Any
    generic_conn_sec_id: Any
    generic_conn_client_id: Any
    cluster_id: Any
    cluster: Any

class GenericConnDef(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    type_: Any
    is_active: Any
    is_internal: Any
    cache_expiry: Any
    address: Any
    port: Any
    timeout: Any
    data_format: Any
    opaque1: Any
    is_channel: Any
    is_outconn: Any
    version: Any
    extra: Any
    pool_size: Any
    username: Any
    username_type: Any
    secret: Any
    secret_type: Any
    cache_id: Any
    cache: Any
    cluster_id: Any
    cluster: Any

class GenericConnDefSec(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    opaque1: Any
    conn_def_id: Any
    conn_def: Any
    sec_base_id: Any
    sec_base: Any
    cluster_id: Any
    cluster: Any

class GenericConn(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    type_: Any
    is_active: Any
    is_internal: Any
    cache_expiry: Any
    address: Any
    port: Any
    timeout: Any
    data_format: Any
    opaque1: Any
    is_channel: Any
    is_outconn: Any
    version: Any
    extra: Any
    pool_size: Any
    username: Any
    username_type: Any
    secret: Any
    secret_type: Any
    conn_def_id: Any
    conn_def: Any
    cache_id: Any
    cache: Any
    cluster_id: Any
    cluster: Any

class GenericConnSec(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    opaque1: Any
    conn_id: Any
    conn: Any
    sec_base_id: Any
    sec_base: Any
    cluster_id: Any
    cluster: Any

class GenericConnClient(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    is_internal: Any
    pub_client_id: Any
    ext_client_id: Any
    ext_client_name: Any
    local_address: Any
    peer_address: Any
    peer_fqdn: Any
    connection_time: Any
    last_seen: Any
    server_proc_pid: Any
    server_name: Any
    conn_id: Any
    conn: Any
    server_id: Any
    server: Any
    cluster_id: Any
    cluster: Any

class PubSubTopic(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    description: Any
    is_active: Any
    created: Any
    last_updated: Any
    cluster_id: Any
    cluster: Any

class PubSubPermission(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    pattern: Any
    access_type: Any
    is_active: Any
    created: Any
    last_updated: Any
    cluster_id: Any
    cluster: Any
    sec_base_id: Any
    sec_base: Any

class PubSubSubscription(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    sub_key: Any
    created: Any
    last_updated: Any
    is_pub_active: Any
    is_delivery_active: Any
    delivery_type: Any
    push_type: Any
    cluster_id: Any
    cluster: Any
    sec_base_id: Any
    sec_base: Any
    rest_push_endpoint_id: Any
    rest_push_endpoint: Any
    push_service_name: Any
    topic_name_list: Any
    topic_link_list: Any

class PubSubSubscriptionTopic(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    pattern_matched: Any
    is_pub_enabled: Any
    is_delivery_enabled: Any
    subscription_id: Any
    subscription: Any
    topic_id: Any
    topic: Any
    cluster_id: Any
    cluster: Any
