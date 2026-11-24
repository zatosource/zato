# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The registries of the static scans of SQL conformance for the code of this installation. The repositories linked
# to the installation add their own entries of the same shapes through their registry modules.

# stdlib
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strtuple

    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The modules that build every engine and every connection of a database of Zato, the second one
    # for the connections of the sqlite3 module that a process opens without SQLAlchemy
    Engine_Factory_Modules = ('zato.common.db_env.engine', 'zato.common.sqlite_connection')

    # The modules in which SQLite pragmas and PostgreSQL session settings that concern durability are set
    Setting_Module_Paths = (
        'code/zato-common/src/zato/common/db_env/connection.py',
        'code/zato-common/src/zato/common/sqlite_connection.py',
    )

# ################################################################################################################################
# ################################################################################################################################

# The functions that connect to the databases of the customers, each by its module and its qualified name,
# and the calls that construct an engine or a connection, each by its full dotted name.
Customer_Engine_Sites = (
    ('zato.common.odb.api', 'SQLConnectionPool._create_engine'),
    ('zato.server.connection.cloud.microsoft_fabric.sql', 'SQLPool._connect'),
    ('zato.server.generic.api.outconn_mongodb', 'OutconnMongoDBWrapper._init_impl'),
)

Engine_Constructors = (
    'sqlalchemy.create_engine',
    'sqlalchemy.engine.create_engine',
    'sqlalchemy.ext.asyncio.create_async_engine',
    'sqlite3.connect',
    'sqlite3.dbapi2.connect',
    'pg8000.connect',
    'pg8000.dbapi.connect',
    'pg8000.native.Connection',
    'psycopg2.connect',
    'psycopg.connect',
    'asyncpg.connect',
    'pymysql.connect',
    'MySQLdb.connect',
    'mysql.connector.connect',
    'mssql_python.connect',
    'pyodbc.connect',
    'pymssql.connect',
    'oracledb.connect',
    'cx_Oracle.connect',
    'pymongo.MongoClient',
)

# ################################################################################################################################
# ################################################################################################################################

# The words in the name of an environment variable that may change when or how a write becomes durable.
Environment_Variable_Keywords = ('Flush', 'Buffer', 'Async', 'Batch', 'Delay', 'Synchronous', 'Durab')

# Each environment variable of production code whose name contains one of the words, with what it controls,
# none of which acknowledges a write before its commit.
Environment_Variables = (
    ('Zato_Audit_Log_Export_Batch_Size',        'How many committed events one OTLP export request carries'),
    ('Zato_Audit_Log_Export_Max_Batch_Size',    'The upper limit of the OTLP export batch size'),
    ('Zato_Audit_Log_Export_Flush_Interval_Ms', 'How often committed events are exported over OTLP'),
    ('Zato_HL7_MLLP_Read_Buffer_Size',          'The size of the socket read buffer of an MLLP listener'),
    ('Zato_PubSub_Batch_Size',                  'How many rows one bulk statement of pub/sub touches'),
    ('Zato_PubSub_DB_Batch_Size',               'The alias under which Zato_PubSub_Batch_Size is read when it is not set'),
)

# ################################################################################################################################
# ################################################################################################################################

# The functions that run a mechanism of the write path, each by its module, its qualified name and the member of Mechanism
# that it marks its work with, or an empty name for the function that marks it with the mechanism of its caller.
Mechanism_Functions = (
    ('zato.common.db_env.commit_queue',     'CommitQueue._commit',          'Group_Commit'),
    ('zato.common.db_env.engine',           'call_database',                ''),
    ('zato.common.db_env.engine',           '_create_sqlite_schema',        'Schema'),
    ('zato.common.db_env.engine',           'create_schemas',               'Schema'),
    ('zato.common.pubsub.sql.cleanup',      'PubSubCleanup.sweep_once',     'Maintenance'),
    ('zato.common.audit_log.retention',     'run_retention',                'Maintenance'),
    ('zato.common.audit_log.event_count',   'compact_event_counts',         'Maintenance'),
    ('zato.common.analytics.rollup',        'run_rollup',                   'Maintenance'),
    ('zato.common.pubsub.sql.generation',   '_GenerationRaiser.run',        'Takeover'),
    ('zato.common.demo.seed',               'seed_demo_data',               'Seed'),
    ('zato.common.demo.seed',               'purge_demo_data',              'Seed'),
)

# The module that defines the write path, with the names through which a function marks its work as that of a mechanism
Write_Path_Module = 'zato.common.db_env.write_path'
Write_Path_Markers = (
    'zato.common.db_env.write_path.write_path',
    'zato.common.db_env.write_path.run_in_write_path',
)

# The prefix of the full name of a member of Mechanism
Mechanism_Prefix = 'zato.common.db_env.write_path.Mechanism.'

# The full name of Mechanism itself
Mechanism_Name = 'zato.common.db_env.write_path.Mechanism'

# The tests that set the marks of the write path themselves, which the tests of the guard of the write path alone do
Write_Path_Mark_Tests = (
    ('code/tests/python/zato-common/sql_conformance/writers/test_write_path.py', 'The refusal of writes outside a mechanism'),
)

# The function that runs the work of a seed, with the module that defines it
Run_Seed_Name = 'zato.common.test.direct_sql.seed.run_seed'
Run_Seed_Path = 'code/zato-common/src/zato/common/test/direct_sql/seed.py'

# The tables of the audit log that its own writes alone may change, which are every table of its schema but the alerts,
# which the alerting store writes through a serialized write
Audit_Log_Schema_Path = 'code/zato-common/src/zato/common/audit_log/common.py'
Write_Path_Path = 'code/zato-common/src/zato/common/db_env/write_path.py'
Audit_Tables_Name = 'Audit_Tables'
Audit_Tables_Not_Guarded = ('alert',)

@dataclass(frozen=True)
class RustWriter:
    """ A writer on SQLite that writes in Rust through the handle of the connection of the driver, outside the guard
    of the write path that SQLAlchemy runs. The module that defines it alone builds it, under the name of its instance,
    and the entry function of that module alone calls its method that writes, after the entry function checks
    each statement of the list of statements against the guard. The keys are those under which the writer receives
    its statements, the Rust sources are the files whose code runs them, and the handle function is the one through
    which the writer opens its connection over the handle of the driver.
    """
    name:            'str'
    class_name:      'str'
    path:            'str'
    instance:        'str'
    entry:           'str'
    method:          'str'
    statements_name: 'str'
    statement_keys:  'strtuple'
    sources:         'strtuple'
    handle_function: 'strtuple'

# The guard of the write path that each Rust writer runs its statements through
Rust_Writer_Guard = 'zato.common.db_env.write_path.check_write_path'

# The function through which the Rust writers open their connections over the handle of the driver
_rust_handle_function = ('code/zato-rust/zato_common_core/src/audit_insert.rs', 'open_handle')

# The Rust writers - the writer of the audit log and the writer of the items of pub/sub batches.
Rust_Writers = (
    RustWriter(
        name='audit-log',
        class_name='zato_common_core.zato_common_core.SQLiteAuditWriter',
        path='code/zato-common/src/zato/common/audit_log/sqlite_insert.py',
        instance='zato.common.audit_log.sqlite_insert._writer',
        entry='insert_pending_events_sqlite',
        method='insert_events',
        statements_name='_write_statements',
        statement_keys=('insert_event', 'select_payload', 'insert_payload', 'insert_attr', 'insert_body', 'insert_link'),
        sources=('code/zato-rust/zato_common_core/src/audit_insert.rs',),
        handle_function=_rust_handle_function,
    ),
    RustWriter(
        name='pubsub',
        class_name='zato_common_core.zato_common_core.SQLitePubSubWriter',
        path='code/zato-common/src/zato/common/pubsub/sql/sqlite_write.py',
        instance='zato.common.pubsub.sql.sqlite_write._writer',
        entry='write_items_sqlite',
        method='write_items',
        statements_name='_write_statements',
        statement_keys=(
            'begin', 'select_subscribers', 'insert_topic_sub', 'upsert_dedup_record', 'select_dedup_record', 'update_dedup_fingerprint',
            'insert_message', 'select_existing_message', 'insert_delivery', 'select_message_id', 'select_ack_delivery',
            'delete_delivery', 'record_attempt', 'select_lease_candidates', 'lease_delivery', 'select_leased_message',
            'select_fenced_delivery', 'drop_payload',
        ),
        sources=(
            'code/zato-rust/zato_common_core/src/pubsub_write.rs',
            'code/zato-rust/zato_common_core/src/pubsub_write_sql.rs',
        ),
        handle_function=_rust_handle_function,
    ),
)

# ################################################################################################################################
# ################################################################################################################################

# The functions of the package of direct writes of the tests, each with the one purpose it serves.
Direct_SQL_Purposes = (
    ('code/zato-common/src/zato/common/test/direct_sql/fault.py', 'interrupt_topic_rename',      'Fault injection'),
    ('code/zato-common/src/zato/common/test/direct_sql/fault.py', 'remove_topic_subscriptions',  'Fault injection'),
    ('code/zato-common/src/zato/common/test/direct_sql/fault.py', 'restore_previous_generation', 'Fault injection'),
    ('code/zato-common/src/zato/common/test/direct_sql/reset.py', 'reset_tables',                'Resetting tables between tests'),
    ('code/zato-common/src/zato/common/test/direct_sql/reset.py', 'reset_table_rows',            'Resetting tables between tests'),
    ('code/zato-common/src/zato/common/test/direct_sql/reset.py', 'truncate_tables',             'Resetting tables between tests'),
    ('code/zato-common/src/zato/common/test/direct_sql/reset.py', 'delete_shared_objects',       'Resetting tables between tests'),
    ('code/zato-common/src/zato/common/test/direct_sql/reset.py', 'recreate_public_schema',      'Resetting tables between tests'),
    ('code/zato-common/src/zato/common/test/direct_sql/reset.py', 'delete_config_job',           'Resetting tables between tests'),
    ('code/zato-common/src/zato/common/test/direct_sql/reset.py', 'delete_generic_connections',  'Resetting tables between tests'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'run_seed',                    'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'seed_rows',                   'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'seed_row',                    'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'seed_event_rows',             'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'seed_event_row',              'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'seed_bulk',                   'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'refresh_statistics',          'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'seed_config_row',             'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'seed_config_objects',         'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'seed_audit_events',           'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/seed.py',  'seed_event',                  'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/pubsub_seed.py', 'get_seeded_sub_key',    'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/pubsub_seed.py', 'seed_queues',           'Seeding test data in bulk'),
    ('code/zato-common/src/zato/common/test/direct_sql/pubsub_seed.py', 'seed_traces',           'Seeding test data in bulk'),
)

# The faults that change the active server without a takeover, each standing for a failover to a replica
# which did not receive the last change of the active server.
Takeover_Faults = (
    ('code/zato-common/src/zato/common/test/direct_sql/fault.py', 'restore_previous_generation'),
)

# The tests of the write path itself, which run its mechanisms and write outside of them on purpose.
Write_Path_Tests = (
    ('code/tests/python/zato-common/sql_conformance/writers/test_write_path.py',  'The refusal of writes outside a mechanism'),
    ('code/tests/python/zato-common/process_queue/test_call_database_queue.py',   'The queue of serialized writes'),
    ('code/tests/python/zato-common/process_queue/test_call_database_wait.py',    'The wait of serialized writes'),
    ('code/tests/python/zato-common/audit_log/storage_types.py',                  'The search index under updates and deletes of events'),
    ('code/tests/python/zato-common/audit_log_read/support.py',                   'The counts of events under updates and deletes of events'),
    ('code/tests/python/zato-common/audit_log_read/test_event_count.py',          'The counts of events under updates and deletes of events'),
    ('code/tests/python/zato-common/audit_log_read/test_open_exchanges.py',       'The open exchanges under updates and deletes of events'),
)

# The tests whose engines and direct writes reach a database of a customer or of a third party, never a database of Zato.
External_Database_Tests = (
    ('code/tests/python/tutorial_endpoints_check.py',                         'The Billing database of the tutorial'),
    ('code/tests/python/zato-common/pg8000_wire/test_pg8000_copy.py',         'The COPY protocol of the PostgreSQL driver'),
    ('code/tests/python/zato-common/pg8000_wire/test_pg8000_wire.py',         'The wire protocol of the PostgreSQL driver'),
    ('code/tests/python/zato-common/pg8000_wire/conftest.py',                 'The PostgreSQL server of the driver tests'),
    ('code/tests/python/zato-common/lib/live_sql/containers.py',              'The databases of outgoing SQL connections'),
    ('code/tests/python/zato-server/facility_sync_live/_schema.py',           'The database of a facility system'),
    ('code/tests/python/zato-server/mcp_sql_live/conftest.py',                'The database of an MCP SQL tool'),
    ('code/tests/python/zato-server/oracle_db_live/_engine_setup_check.py',   'An Oracle database of an outgoing connection'),
    ('code/tests/python/zato-server/oracle_db_live/_pool_workload.py',        'An Oracle database of an outgoing connection'),
    ('code/tests/python/zato-server/sql_outgoing_audit/common.py',            'The databases of outgoing SQL connections'),
)

# ################################################################################################################################
# ################################################################################################################################
