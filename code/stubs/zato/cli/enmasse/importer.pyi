from typing import Any, TYPE_CHECKING

import logging
import os
import sys
import yaml
from zato.cli.enmasse.config import ModuleCtx
from zato.cli.enmasse.client import wait_for_services, Default_Service_Wait_Timeout
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.cache import CacheImporter
from zato.cli.enmasse.importers.email_smtp import SMTPImporter
from zato.cli.enmasse.importers.email_imap import IMAPImporter
from zato.cli.enmasse.importers.es import ElasticSearchImporter
from zato.cli.enmasse.importers.odoo import OdooImporter
from zato.cli.enmasse.importers.scheduler import SchedulerImporter
from zato.cli.enmasse.importers.sql import SQLImporter
from zato.cli.enmasse.importers.confluence import ConfluenceImporter
from zato.cli.enmasse.importers.jira import JiraImporter
from zato.cli.enmasse.importers.ldap import LDAPImporter
from zato.cli.enmasse.importers.microsoft_365 import Microsoft365Importer
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.cli.enmasse.importers.outgoing_soap import OutgoingSOAPImporter
from zato.cli.enmasse.importers.pubsub_topic import PubSubTopicImporter
from zato.cli.enmasse.importers.pubsub_permission import PubSubPermissionImporter
from zato.cli.enmasse.importers.pubsub_subscription import PubSubSubscriptionImporter
from zato.cli.enmasse.importers.channel_openapi import ChannelOpenAPIImporter
from zato.common.odb.model import Cluster
from sqlalchemy.orm.session import Session as SASession
from zato.common.typing_ import any_, stranydict


class EnmasseYAMLImporter:
    cluster_id: Any
    object_type: Any
    object_alias: Any
    sec_defs: Any
    group_defs: Any
    cache_defs: Any
    odoo_defs: Any
    smtp_defs: Any
    imap_defs: Any
    es_defs: Any
    sql_defs: Any
    job_defs: Any
    confluence_defs: Any
    jira_defs: Any
    ldap_defs: Any
    microsoft_365_defs: Any
    outgoing_rest_defs: Any
    outgoing_soap_defs: Any
    pubsub_topic_defs: Any
    pubsub_permission_defs: Any
    pubsub_subscription_defs: Any
    channel_openapi_defs: Any
    objects: Any
    cluster: Any
    created_objects: Any
    updated_objects: Any
    security_importer: SecurityImporter
    channel_importer: ChannelImporter
    group_importer: GroupImporter
    cache_importer: CacheImporter
    odoo_importer: OdooImporter
    smtp_importer: SMTPImporter
    imap_importer: IMAPImporter
    es_importer: ElasticSearchImporter
    sql_importer: SQLImporter
    scheduler_importer: SchedulerImporter
    confluence_importer: ConfluenceImporter
    jira_importer: JiraImporter
    ldap_importer: LDAPImporter
    microsoft_365_importer: Microsoft365Importer
    outgoing_rest_importer: OutgoingRESTImporter
    outgoing_soap_importer: OutgoingSOAPImporter
    pubsub_topic_importer: PubSubTopicImporter
    pubsub_permission_importer: PubSubPermissionImporter
    pubsub_subscription_importer: PubSubSubscriptionImporter
    channel_openapi_importer: ChannelOpenAPIImporter
    def __init__(self: Any) -> None: ...
    def get_cluster(self: Any, session: SASession) -> any_: ...
    def from_path(self: Any, path: str) -> stranydict: ...
    def from_string(self: Any, yaml_string: str) -> stranydict: ...
    def _process_includes(self: Any, config: stranydict, base_dir: str, processed_paths: set | None = ...) -> stranydict: ...
    def _merge_configs(self: Any, target: stranydict, source: stranydict) -> None: ...
    def _process_config(self: Any, config: stranydict) -> stranydict: ...
    def sync_security(self: Any, security_list: list, session: SASession) -> tuple: ...
    def sync_groups(self: Any, group_list: list, session: SASession) -> tuple: ...
    def sync_channel_rest(self: Any, channel_list: list, session: SASession) -> tuple: ...
    def sync_cache(self: Any, cache_list: list, session: SASession) -> tuple: ...
    def sync_odoo(self: Any, odoo_list: list, session: SASession) -> tuple: ...
    def sync_smtp(self: Any, smtp_list: list, session: SASession) -> tuple: ...
    def sync_imap(self: Any, imap_list: list, session: SASession) -> tuple: ...
    def sync_sql(self: Any, sql_list: list, session: SASession) -> tuple: ...
    def sync_scheduler(self: Any, job_list: list, session: SASession) -> tuple: ...
    def sync_confluence(self: Any, confluence_list: list, session: SASession) -> tuple: ...
    def sync_jira(self: Any, jira_list: list, session: SASession) -> tuple: ...
    def sync_ldap(self: Any, ldap_list: list, session: SASession) -> tuple: ...
    def sync_microsoft_365(self: Any, microsoft_365_list: list, session: SASession) -> tuple: ...
    def sync_es(self: Any, es_list: list, session: SASession) -> tuple: ...
    def sync_pubsub_topic(self: Any, topic_list: list, session: SASession) -> tuple: ...
    def sync_outgoing_rest(self: Any, outgoing_list: list, session: SASession) -> tuple: ...
    def sync_outgoing_soap(self: Any, outgoing_list: list, session: SASession) -> tuple: ...
    def sync_pubsub_permission(self: Any, permission_list: list, session: SASession) -> tuple: ...
    def sync_pubsub_subscription(self: Any, subscription_list: list, session: SASession) -> tuple: ...
    def sync_channel_openapi(self: Any, channel_list: list, session: SASession) -> tuple: ...
    def sync_from_yaml(self: Any, yaml_config: stranydict, session: SASession, server_dir: str | None = ..., wait_for_services_timeout: int | None = ...) -> tuple: ...
