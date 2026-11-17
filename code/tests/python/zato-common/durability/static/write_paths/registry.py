# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The registry of the functions of production code that write to a database, each with the category of its write path.
# A function is named by its module and its qualified name, never by a line number.

# Zato
from zato.common.test.durability.linked import get_linked_entries, ModuleCtx as LinkedModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

class Category:

    # A function that CommitQueue calls with a batch, or that such a function calls within the same transaction
    Group_Commit_Batch = 'group_commit_batch'

    # A function passed to call_database or execute_write, or that such a function calls within the same transaction
    Serialized_Write = 'serialized_write'

    # Cleanup, retention, index merge, checkpoint and rollup, started by their runners
    Maintenance = 'maintenance'

    # Schema creation and its seed rows
    Schema = 'schema'

    # The generation raise and its audit event
    Takeover = 'takeover'

    # Customer outgoing connections to databases that are not databases of Zato
    External_Database = 'external_database'

    # Synchronous writes of the configuration of Zato, in the configuration database and in the settings database,
    # by services, the command line and the server, never to the tables of pub/sub and of the audit log
    Configuration = 'configuration'

    # The engine factory, the connection settings, the replicated connection and the fence of the database layer
    Infrastructure = 'infrastructure'

# ################################################################################################################################
# ################################################################################################################################

# Each module with its functions that write and the category of each one
Write_Sites = [
    ('zato.cli.create_initial_data', {
        'Create.add_alert_notification_connections': Category.Configuration,
        'Create.add_django_channel': Category.Configuration,
        'Create.add_ide_publisher_channel': Category.Configuration,
        'Create.add_metrics_channel': Category.Configuration,
        'Create.add_ping_service': Category.Configuration,
        'Create.add_pubsub_rest_channels': Category.Configuration,
        'Create.add_streaming_channels': Category.Configuration,
        'Create.execute': Category.Configuration,
    }),
    ('zato.cli.create_odb', {
        'Create.execute': Category.Schema,
    }),
    ('zato.cli.create_server', {
        'Create.execute': Category.Configuration,
    }),
    ('zato.cli.delete_odb', {
        'Delete.execute': Category.Schema,
    }),
    ('zato.cli.enmasse.client', {
        'cleanup': Category.Configuration,
    }),
    ('zato.cli.enmasse.importer.delete', {
        'DeleteSync._delete_in_session': Category.Configuration,
        'DeleteSync._delete_through_service': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.alert_config', {
        'AlertConfigImporter.sync_alert_notifications': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.amqp', {
        'ChannelAMQPImporter.create_channel_definition': Category.Configuration,
        'ChannelAMQPImporter.sync_channel_definitions': Category.Configuration,
        'ChannelAMQPImporter.update_channel_definition': Category.Configuration,
        'OutgoingAMQPImporter.create_connection_definition': Category.Configuration,
        'OutgoingAMQPImporter.sync_connection_definitions': Category.Configuration,
        'OutgoingAMQPImporter.update_connection_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.audit_extraction', {
        'AuditExtractionImporter.sync_extraction_rules': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.audit_retention', {
        'AuditRetentionImporter.sync_retention_policies': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.channel_mllp', {
        'ChannelMLLPImporter._clear_other_defaults': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.channel_openapi', {
        'ChannelOpenAPIImporter.create_definition': Category.Configuration,
        'ChannelOpenAPIImporter.sync_channel_openapi': Category.Configuration,
        'ChannelOpenAPIImporter.update_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.channel_rest', {
        'ChannelImporter.create_channel_rest': Category.Configuration,
        'ChannelImporter.sync_channel_rest': Category.Configuration,
        'ChannelImporter.update_channel_rest': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.channel_soap', {
        'ChannelSOAPImporter.create_channel_soap': Category.Configuration,
        'ChannelSOAPImporter.sync_channel_soap': Category.Configuration,
        'ChannelSOAPImporter.update_channel_soap': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.email_imap', {
        'IMAPImporter.create_imap_definition': Category.Configuration,
        'IMAPImporter.sync_imap_definitions': Category.Configuration,
        'IMAPImporter.update_imap_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.email_smtp', {
        'SMTPImporter.create_smtp_definition': Category.Configuration,
        'SMTPImporter.sync_smtp_definitions': Category.Configuration,
        'SMTPImporter.update_smtp_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.generic', {
        'GenericConnectionImporter._sync_schedules': Category.Configuration,
        'GenericConnectionImporter.create_definition': Category.Configuration,
        'GenericConnectionImporter.sync_definitions': Category.Configuration,
        'GenericConnectionImporter.update_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.group', {
        'GroupImporter.create_group': Category.Configuration,
        'GroupImporter.update_group': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.odoo', {
        'OdooImporter.create_odoo_definition': Category.Configuration,
        'OdooImporter.sync_odoo_definitions': Category.Configuration,
        'OdooImporter.update_odoo_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.on_prem_gateway', {
        'OnPremGatewayImporter.sync_on_prem_gateways': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.outgoing_rest', {
        'OutgoingRESTImporter.create_outgoing_rest': Category.Configuration,
        'OutgoingRESTImporter.sync_outgoing_rest': Category.Configuration,
        'OutgoingRESTImporter.update_outgoing_rest': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.outgoing_soap', {
        'OutgoingSOAPImporter.create_outgoing_soap': Category.Configuration,
        'OutgoingSOAPImporter.sync_outgoing_soap': Category.Configuration,
        'OutgoingSOAPImporter.update_outgoing_soap': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.pubsub_permission', {
        'PubSubPermissionImporter.create_pubsub_permission_definition': Category.Configuration,
        'PubSubPermissionImporter.update_pubsub_permission_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.pubsub_subscription', {
        'PubSubSubscriptionImporter.create_pubsub_subscription_definition': Category.Configuration,
        'PubSubSubscriptionImporter.update_pubsub_subscription_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.pubsub_topic', {
        'PubSubTopicImporter.create_pubsub_topic_definition': Category.Configuration,
        'PubSubTopicImporter.update_pubsub_topic_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.quota_tier', {
        'QuotaTierImporter.sync_quota_tiers': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.scheduler', {
        'SchedulerImporter.create_job_definition': Category.Configuration,
        'SchedulerImporter.sync_job_definitions': Category.Configuration,
        'SchedulerImporter.update_job_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.security', {
        'SecurityImporter._encrypt_kept_passwords': Category.Configuration,
        'SecurityImporter.create_security_definition': Category.Configuration,
        'SecurityImporter.sync_security_definitions': Category.Configuration,
        'SecurityImporter.update_security_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.importers.sql', {
        'SQLImporter.create_sql_definition': Category.Configuration,
        'SQLImporter.sync_sql_definitions': Category.Configuration,
        'SQLImporter.update_sql_definition': Category.Configuration,
    }),
    ('zato.cli.enmasse.util.secrets', {
        'encrypt_kept_opaque_secrets': Category.Configuration,
    }),
    ('zato.common.alerting.explain.store', {
        'ExplanationStore.create': Category.Configuration,
    }),
    ('zato.common.alerting.notification_config', {
        'set_notification_config': Category.Configuration,
    }),
    ('zato.common.alerting.store', {
        'raise_alert': Category.Serialized_Write,
    }),
    ('zato.common.analytics.rollup', {
        '_advance_watermark': Category.Maintenance,
        '_get_newest_settled_event_id': Category.Maintenance,
        '_get_watermark': Category.Maintenance,
        '_upsert_group': Category.Maintenance,
        'run_rollup': Category.Maintenance,
    }),
    ('zato.common.audit_log.api', {
        'AuditLog._insert_batch': Category.Group_Commit_Batch,
        'AuditLog.add_links': Category.Serialized_Write,
    }),
    ('zato.common.audit_log.bulk_insert', {
        '_insert_by_commit_id': Category.Group_Commit_Batch,
        '_insert_returning': Category.Group_Commit_Batch,
        'insert_rows': Category.Group_Commit_Batch,
    }),
    ('zato.common.audit_log.dedup', {
        'acquire_dedup_key': Category.Serialized_Write,
        'complete_dedup_key': Category.Serialized_Write,
        'release_dedup_key': Category.Serialized_Write,
    }),
    ('zato.common.audit_log.event_count', {
        'compact_event_counts': Category.Maintenance,
    }),
    ('zato.common.audit_log.export.api', {
        'AuditExport.emit_row': Category.Serialized_Write,
    }),
    ('zato.common.audit_log.file_transfer_run', {
        '_write_body': Category.Serialized_Write,
        'update_run_event': Category.Serialized_Write,
    }),
    ('zato.common.audit_log.retention', {
        '_delete_events': Category.Maintenance,
        '_prune_content': Category.Maintenance,
    }),
    ('zato.common.audit_log.scheduler', {
        '_mark_run_timed_out': Category.Serialized_Write,
        'append_job_log_entry': Category.Serialized_Write,
        'record_job_complete': Category.Serialized_Write,
    }),
    ('zato.common.audit_log.search_index_merge', {
        'SearchIndexMerger.merge': Category.Maintenance,
    }),
    ('zato.common.common_db.store', {
        '_create': Category.Serialized_Write,
        '_delete': Category.Serialized_Write,
        '_get': Category.Serialized_Write,
        '_list': Category.Serialized_Write,
        '_update': Category.Serialized_Write,
    }),
    ('zato.common.db_env.connection', {
        '_show': Category.Infrastructure,
        'set_postgresql_session': Category.Infrastructure,
        'verify_postgresql_server': Category.Infrastructure,
    }),
    ('zato.common.db_env.engine', {
        '_create_sqlite_schema': Category.Schema,
        '_execute_in_transaction': Category.Serialized_Write,
        'connect_sqlite_file': Category.Infrastructure,
        'create_schemas': Category.Schema,
    }),
    ('zato.common.db_env.pg8000_copy', {
        'copy_rows': Category.Infrastructure,
    }),
    ('zato.common.db_env.plain_sql', {
        'PlainStatement.execute': Category.Infrastructure,
        'PlainStatement.insert_rows': Category.Infrastructure,
    }),
    ('zato.common.db_env.sqlite_checkpoint', {
        'WALCheckpointer.checkpoint': Category.Maintenance,
    }),
    ('zato.common.demo.seed', {
        '_BulkAuditLog.write_collected': Category.Serialized_Write,
        '_delete_demo_rows': Category.Serialized_Write,
        'purge_demo_data': Category.Serialized_Write,
        'seed_demo_data': Category.Serialized_Write,
    }),
    ('zato.common.ha.sqlite', {
        'ReplicatedConnection.execute': Category.Infrastructure,
        'ReplicatedConnection.executemany': Category.Infrastructure,
    }),
    ('zato.common.mssql_direct', {
        'MSSQLDirectAPI._return_proc_rows': Category.External_Database,
        'MSSQLDirectAPI._yield_proc_rows': Category.External_Database,
        'MSSQLDirectAPI.execute': Category.External_Database,
    }),
    ('zato.common.odb.api', {
        'ODBManager.drop_deployed_services': Category.Configuration,
        'ODBManager.encrypt_sec_base': Category.Configuration,
        'ODBManager.hot_deploy': Category.Configuration,
        'ODBManager.on_deployment_finished': Category.Configuration,
        'SessionWrapper._execute': Category.Configuration,
    }),
    ('zato.common.odb.query.generic', {
        'GenericObjectWrapper.store': Category.Configuration,
    }),
    ('zato.common.pubsub.sql.admin', {
        'SQLAdminAPI._clear_queue_batch': Category.Serialized_Write,
        'SQLAdminAPI._delete_message': Category.Serialized_Write,
        'SQLAdminAPI._delete_topic_rows_batch': Category.Serialized_Write,
        'SQLAdminAPI._update_topic_name_batch': Category.Serialized_Write,
        'SQLAdminAPI.delete_topic': Category.Serialized_Write,
        'SQLAdminAPI.rename_topic': Category.Serialized_Write,
        'SQLAdminAPI.update_message': Category.Serialized_Write,
    }),
    ('zato.common.pubsub.sql.backend', {
        'SQLPubSubBackend._subscribe': Category.Serialized_Write,
        'SQLPubSubBackend._unsubscribe_batch': Category.Serialized_Write,
        'SQLPubSubBackend.unsubscribe': Category.Serialized_Write,
    }),
    ('zato.common.pubsub.sql.cleanup', {
        'PubSubCleanup._compact_counts': Category.Maintenance,
        'PubSubCleanup._delete_message_batch': Category.Maintenance,
        'PubSubCleanup._sweep_aged_traces': Category.Maintenance,
        'PubSubCleanup._sweep_empty_counts': Category.Maintenance,
        'PubSubCleanup._sweep_expired': Category.Maintenance,
        'PubSubCleanup._sweep_over_cap_traces': Category.Maintenance,
    }),
    ('zato.common.pubsub.sql.core', {
        'SQLBackendCore.record_attempt': Category.Serialized_Write,
        'SQLBackendCore.record_attempts': Category.Serialized_Write,
    }),
    ('zato.common.pubsub.sql.fenced_ack', {
        'delete_fenced': Category.Group_Commit_Batch,
    }),
    ('zato.common.pubsub.sql.generation', {
        'GenerationGuard.before_cursor_execute': Category.Infrastructure,
        '_GenerationRaiser.run': Category.Takeover,
        '_terminate_blockers': Category.Takeover,
    }),
    ('zato.common.pubsub.sql.pull', {
        'lease_messages': Category.Group_Commit_Batch,
    }),
    ('zato.common.pubsub.sql.writes', {
        'PubSubWriter._insert_deliveries': Category.Group_Commit_Batch,
        'PubSubWriter._write_transaction': Category.Group_Commit_Batch,
    }),
    ('zato.common.rule_engine.sql.approvals', {
        'ApprovalStore._approve_rows': Category.Serialized_Write,
        'ApprovalStore._set_config_field_rows': Category.Serialized_Write,
    }),
    ('zato.common.rule_engine.sql.decisions', {
        'DecisionStore._delete_chunk': Category.Serialized_Write,
        'DecisionStore._insert_rows': Category.Serialized_Write,
    }),
    ('zato.common.rule_engine.sql.definitions', {
        'DefinitionStore._archive_rows': Category.Serialized_Write,
        'DefinitionStore._create_rows': Category.Serialized_Write,
        'DefinitionStore._rename_rows': Category.Serialized_Write,
    }),
    ('zato.common.rule_engine.sql.follows', {
        'FollowStore._follow_rows': Category.Serialized_Write,
        'FollowStore._mark_seen_row': Category.Serialized_Write,
        'FollowStore._unfollow_rows': Category.Serialized_Write,
    }),
    ('zato.common.rule_engine.sql.notifications', {
        'NotificationStore._add_destination_row': Category.Serialized_Write,
        'NotificationStore._delete_destination_row': Category.Serialized_Write,
        'NotificationStore._set_chat_config_row': Category.Serialized_Write,
        'NotificationStore._set_job_cursor_row': Category.Serialized_Write,
        'NotificationStore._update_destination_row': Category.Serialized_Write,
    }),
    ('zato.common.rule_engine.sql.reference_index', {
        'ReferenceIndex._rebuild_rows': Category.Serialized_Write,
    }),
    ('zato.common.rule_engine.sql.store_common', {
        'add_event': Category.Serialized_Write,
    }),
    ('zato.common.rule_engine.sql.versions', {
        'VersionStore._create_rows': Category.Serialized_Write,
        'VersionStore._publish_rows': Category.Serialized_Write,
        'VersionStore._restore_rows': Category.Serialized_Write,
    }),
    ('zato.common.rule_engine.sql.views', {
        'ViewStore._delete_row': Category.Serialized_Write,
        'ViewStore._save_row': Category.Serialized_Write,
        'ViewStore._touch_recent_row': Category.Serialized_Write,
    }),
    ('zato.common.rule_engine.sql.writer', {
        'DecisionBatchWriter._insert_batch': Category.Group_Commit_Batch,
        'DecisionBatchWriter._upsert_rollups': Category.Group_Commit_Batch,
    }),
    ('zato.common.settings_db', {
        'SettingsDB.create_db': Category.Schema,
        'SettingsDB.set': Category.Configuration,
    }),
    ('zato.common.util.channel', {
        'create_openapi_channel': Category.Configuration,
        'ensure_openapi_channel_exists': Category.Configuration,
    }),
    ('zato.common.util.file_transfer_scheduler', {
        'set_schedule_list': Category.Configuration,
    }),
    ('zato.common.util.gateway', {
        'ensure_mcp_gateway_exists': Category.Configuration,
        'ensure_mcp_oauth_metadata_channel_exists': Category.Configuration,
        'ensure_mcp_rest_channel': Category.Configuration,
    }),
    ('zato.common.util.imap_scheduler', {
        'clear_imap_scheduler_fields': Category.Configuration,
        'update_imap_scheduler_fields': Category.Configuration,
    }),
    ('zato.common.util.rest_invocation', {
        'clear_connection_opaque_fields': Category.Configuration,
        'update_connection_opaque_fields': Category.Configuration,
    }),
    ('zato.common.util.rule_engine_api', {
        'ensure_rule_engine_api_channel': Category.Configuration,
    }),
    ('zato.common.util.scheduler', {
        '_ensure_interval_job_exists': Category.Configuration,
        'add_startup_jobs_to_odb_by_odb': Category.Configuration,
        'ensure_alerting_job_exists': Category.Configuration,
        'set_job_active': Category.Configuration,
    }),
    ('zato.server.base.parallel', {
        'ParallelServer._pre_initialize': Category.Configuration,
    }),
    ('zato.server.base.parallel.config', {
        'ConfigLoader._encrypt_secrets': Category.Configuration,
    }),
    ('zato.server.connection.cloud.microsoft_fabric.sql', {
        '_fetch_rows': Category.External_Database,
    }),
    ('zato.server.demo_config', {
        '_claim_startup_marker': Category.Configuration,
    }),
    ('zato.server.demo_mcp.warehouse', {
        '_create_database': Category.Schema,
    }),
    ('zato.server.groups.base', {
        'GroupsManager.add_members_to_group': Category.Configuration,
        'GroupsManager.create_group': Category.Configuration,
        'GroupsManager.delete_group': Category.Configuration,
        'GroupsManager.edit_group': Category.Configuration,
        'GroupsManager.remove_members_from_group': Category.Configuration,
        'GroupsManager.set_group_quota_tier': Category.Configuration,
    }),
    ('zato.server.on_prem_gateway', {
        'OnPremGatewayManager.create': Category.Configuration,
        'OnPremGatewayManager.delete': Category.Configuration,
        'OnPremGatewayManager.edit': Category.Configuration,
    }),
    ('zato.server.quota_tiers', {
        'QuotaTiersManager.create_tier': Category.Configuration,
        'QuotaTiersManager.delete_tier': Category.Configuration,
        'QuotaTiersManager.edit_tier': Category.Configuration,
    }),
    ('zato.server.service.internal', {
        'ChangePasswordBase._handle': Category.Configuration,
    }),
    ('zato.server.service.internal.alerting', {
        'AlertingSetNotificationConfig.handle': Category.Configuration,
        'AlertingSetTestTransferState.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.channel.amqp_', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.common.delete', {
        'DeleteMany._delete': Category.Configuration,
        'DeleteMany.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.common.import_', {
        'ImportObjects.create_basic_auth': Category.Configuration,
        'ImportObjects.handle': Category.Configuration,
        'ImportObjects.update_objects': Category.Configuration,
    }),
    ('zato.server.service.internal.generic.connection', {
        '_CreateEdit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.generic.rest_wrapper', {
        'ChangePassword.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.http_soap', {
        'Delete.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.http_soap.create', {
        'Create.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.http_soap.edit', {
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.http_soap.rate_limiting', {
        'RateLimitingSave._save_opaque': Category.Configuration,
        'ResponseCacheSave.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.outgoing.amqp_', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.outgoing.sql', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.pubsub.permission', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.pubsub.subscription', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.pubsub.topic', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.scheduler', {
        'Delete.handle': Category.Configuration,
        '_create_edit': Category.Configuration,
    }),
    ('zato.server.service.internal.security.apikey', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.security.basic_auth', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.security.mtls', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.security.ntlm', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.security.oauth', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.security.rate_limiting', {
        '_RateLimitingSaveBase._save_opaque': Category.Configuration,
    }),
    ('zato.server.service.internal.security.spnego', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.security.wss', {
        'Create.handle': Category.Configuration,
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.internal.service', {
        'Delete.handle': Category.Configuration,
        'Edit.handle': Category.Configuration,
    }),
    ('zato.server.service.meta', {
        'CreateEditMeta.handle.handle_impl': Category.Configuration,
        'DeleteMeta.handle.handle_impl': Category.Configuration,
    }),
    ('zato.server.service.store', {
        'ServiceStore._store_in_odb': Category.Configuration,
        'ServiceStore.import_services_from_anywhere': Category.Configuration,
    }),
]

# ################################################################################################################################
# ################################################################################################################################

def get_registry() -> 'dict[tuple[str, str], str]':
    """ Returns the category of each registered function, of the installation and of each linked repository,
    by its module and its qualified name.
    """
    out:'dict[tuple[str, str], str]' = {}

    entries:'list[tuple[str, strdict]]' = Write_Sites + get_linked_entries(LinkedModuleCtx.Write_Sites)

    for module_name, functions in entries:
        for qualname, category in functions.items():
            out[module_name, qualname] = category

    return out

# ################################################################################################################################
# ################################################################################################################################
