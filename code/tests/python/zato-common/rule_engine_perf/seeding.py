# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
from datetime import datetime, timedelta
from tempfile import gettempdir
from time import monotonic

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.defaults import default_cluster_id

# Local
from common import build_ssl_context, PerfDatabase, Rollup_Day_Count, Rollup_Rule_Count, \
    Seeded_Decision_Count, Seeded_Definition_Count, Type_MySQL, Type_PostgreSQL, Type_SQLite
from zato.common.rule_engine.sql.constants import Definition_Type_Sentence_Rule, Event_Type_Rule_Fired_Daily, \
    Event_Type_Version_Created, Event_Type_Version_Published, System_Actor
from zato.common.rule_engine.sql.document import serialize_document, serialize_string_list
from zato.common.rule_engine.sql.schema import rule_decision_table
from traffic import Author, business_key_for, catalog_for, duration_for, fired_rules_for, outcome_for, story_for, \
    version_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.rule_engine.sql.data import any_, anydict, strlist
    from zato.common.rule_engine.sql.database import SessionFactory

    any_ = any_
    anydict = anydict
    strlist = strlist
    SessionFactory = SessionFactory
    row_iterator = Iterator[tuple]

# ################################################################################################################################
# ################################################################################################################################

# When the seeded reporting timeline begins.
Seed_Base_Time = datetime(2026, 6, 1)

# Over how many hourly buckets the seeded decisions spread - five UTC days.
Seed_Span_Hours = 120

# The first explicitly assigned identity of a bulk-seeded definition.
Seed_Definition_Base = 1_000

# How many immutable versions every bulk-seeded definition carries.
Seed_Versions_Per_Definition = 3

# Every this many seeded decisions one is an error - the same shape live traffic has.
Seed_Error_Every = 50

# Every this many successful seeded decisions one keeps its full story - a production capture dial.
Seed_Story_Every = 10

# How many distinct searchable network tiers the seeded definition documents mention.
Seed_Network_Tier_Count = 50

# The NULL marker both LOAD DATA INFILE and COPY understand.
Seed_Null_Marker = '\\N'

# The timestamp format every database accepts as-is in bulk-loaded text. The microseconds
# are always given because SQLite stores timestamps as text of exactly this shape - without
# them a seeded value would compare as less-than the same moment written by the backend itself.
Seed_Time_Format = '%Y-%m-%d %H:%M:%S.%f'

# The write-time hour bucket format, the same one decision_to_row uses.
Seed_Bucket_Format = '%Y-%m-%dT%H'

# Default network ports when the connection details do not name one.
_mysql_default_port      = 3306
_postgresql_default_port = 5432

# ################################################################################################################################
# ################################################################################################################################

# The columns of rule_decision in seeding order - the id column is omitted so the engine assigns it itself.
_decision_columns = ('cluster_id, decision_id, ruleset_id, rules_version, occurred_at, time_bucket,'
    ' business_key, outcome, is_error, duration_ms, has_payload, payload, fired_rule_ids')

# The columns of rule_definition in seeding order - the id comes first and is assigned explicitly
# so version and event rows can reference their definitions without any lookup.
_definition_columns = ('id, cluster_id, parent_id, parent_key, name, object_type, current_version,'
    ' live_version, is_active, created_at, updated_at, document')

# The columns of rule_version in seeding order.
_version_columns = 'definition_id, version, author, comment, created_at, document'

# The columns of rule_event in seeding order.
_event_columns = 'cluster_id, definition_id, version, event_type, actor, subject_id, bucket_start, event_count, created_at, payload'

# ################################################################################################################################
# ################################################################################################################################

def connect_native(database:'PerfDatabase') -> 'any_':
    """ Opens a connection to the perf database through its native driver, bypassing SQLAlchemy -
    bulk seeding needs the fastest path there is.
    """
    details = database.details

    # SQLite is a direct file connection with durability off - seed data is throwaway ..
    if database.db_type == Type_SQLite:
        connection = sqlite3.connect(details['name'])
        _ = connection.execute('pragma synchronous=off')
        return connection

    # .. the network databases reuse the same TLS context the engine itself would build ..
    if database.uses_ssl:
        ssl_context = build_ssl_context(details)
    else:
        ssl_context = None

    port = int(details['port'])

    # .. MySQL additionally allows LOAD DATA LOCAL INFILE, the bulk-seeding path ..
    if database.db_type == Type_MySQL:
        import pymysql

        if not port:
            port = _mysql_default_port

        connection = pymysql.connect(
            host=details['host'],
            port=port,
            user=details['username'],
            password=details['password'],
            database=details['name'],
            ssl=ssl_context,
            local_infile=True,
        )

    # .. and PostgreSQL takes the context under its own keyword.
    else:
        import pg8000

        if not port:
            port = _postgresql_default_port

        connection = pg8000.connect(
            user=details['username'],
            password=details['password'],
            host=details['host'],
            port=port,
            database=details['name'],
            ssl=ssl_context,
        )

    return connection

# ################################################################################################################################

def _analyze_tables(connection:'any_', cursor:'any_', db_type:'str') -> 'None':
    """ Refreshes the optimizer statistics after a bulk load - without this the engines plan
    their queries against the empty-table statistics the load started from. Runs on committed
    rows because PostgreSQL's VACUUM cannot run inside a transaction.
    """
    if db_type == Type_MySQL:
        _ = cursor.execute('analyze table rule_decision, rule_event, rule_version, rule_definition')

    elif db_type == Type_PostgreSQL:

        # VACUUM builds the visibility map that allows index-only scans over the loaded rows.
        connection.autocommit = True
        _ = cursor.execute('vacuum analyze rule_decision')
        _ = cursor.execute('vacuum analyze rule_event')
        _ = cursor.execute('vacuum analyze rule_version')
        _ = cursor.execute('vacuum analyze rule_definition')
        connection.autocommit = False

    else:
        _ = cursor.execute('analyze')

# ################################################################################################################################

def delete_all_rows(database:'PerfDatabase') -> 'None':
    """ Empties all four rule-engine tables through the native driver. The network databases use TRUNCATE
    because it is instant regardless of the row count, while SQLite's DELETE without a WHERE clause
    is already its fast truncate-optimization path.
    """
    connection = connect_native(database)
    cursor = connection.cursor()

    if database.db_type == Type_SQLite:
        _ = cursor.execute('delete from rule_decision')
        _ = cursor.execute('delete from rule_event')
        _ = cursor.execute('delete from rule_version')
        _ = cursor.execute('delete from rule_definition')

    # MySQL cannot TRUNCATE a table referenced by foreign keys, so the checks pause for the reset.
    elif database.db_type == Type_MySQL:
        _ = cursor.execute('set foreign_key_checks = 0')
        _ = cursor.execute('truncate table rule_decision')
        _ = cursor.execute('truncate table rule_event')
        _ = cursor.execute('truncate table rule_version')
        _ = cursor.execute('truncate table rule_definition')
        _ = cursor.execute('set foreign_key_checks = 1')

    else:
        _ = cursor.execute('truncate table rule_decision, rule_event, rule_version, rule_definition restart identity')

    connection.commit()
    connection.close()

# ################################################################################################################################

def _write_seed_file(seed_path:'str', rows:'row_iterator') -> 'None':
    """ Writes the rows out tab-separated - the values are numbers and strings that never contain
    tabs, newlines or backslashes, so plain joining is all the encoding needed. None becomes
    the marker both engines recognize as NULL.
    """
    with open(seed_path, 'w') as seed_file:
        for row in rows:
            items:'strlist' = []

            for value in row:
                if value is None:
                    items.append(Seed_Null_Marker)
                else:
                    items.append(str(value))

            line = '\t'.join(items)
            _ = seed_file.write(line + '\n')

# ################################################################################################################################

def load_rows(cursor:'any_', db_type:'str', table:'str', columns:'str', rows:'row_iterator') -> 'None':
    """ Streams the rows into the table over the fastest path each engine has. SQLite is in-process,
    so executemany straight off the row generator is that path. The network databases get the rows
    as a tab-separated file fed to their bulk-load statements - LOAD DATA LOCAL INFILE and
    COPY FROM STDIN - which are engine-side loaders, an order of magnitude faster than any INSERT
    the wire protocol can carry. The file is deleted as soon as the load is done.
    """
    if db_type == Type_SQLite:
        placeholder_count = columns.count(',') + 1
        placeholders = ', '.join(['?'] * placeholder_count)
        cursor.executemany(f'insert into {table} ({columns}) values ({placeholders})', rows)
        return

    seed_path = os.path.join(gettempdir(), f'zato-rule-engine-seed-{os.getpid()}-{table}.tsv')
    _write_seed_file(seed_path, rows)

    if db_type == Type_MySQL:
        _ = cursor.execute(f"""
            load data local infile '{seed_path}'
            into table {table}
            fields terminated by '\\t'
            lines terminated by '\\n'
            ({columns})
        """)
    else:
        with open(seed_path, 'rb') as seed_file:
            _ = cursor.execute(f'copy {table} ({columns}) from stdin', stream=seed_file)

    os.remove(seed_path)

# ################################################################################################################################

def _decision_rows(ruleset_ids:'tuple[int, int]') -> 'row_iterator':
    """ Yields every bulk-seeded decision row, each field derived deterministically from its index.
    """
    # Precompute the per-hour timestamp texts - a million strftime calls would dominate generation ..
    occurred_texts:'strlist' = []
    bucket_texts:'strlist' = []

    for hour in range(Seed_Span_Hours):
        occurred_at = Seed_Base_Time + timedelta(hours=hour)
        occurred_texts.append(occurred_at.strftime(Seed_Time_Format))
        bucket_texts.append(occurred_at.strftime(Seed_Bucket_Format))

    # .. precompute the fired-rule texts too, their pattern repeats every eight indices ..
    fired_texts:'strlist' = []

    for index in range(8):
        fired_rule_ids = fired_rules_for(index)
        fired_texts.append(serialize_string_list(fired_rule_ids))

    # .. and derive every row from its index alone.
    for index in range(Seeded_Decision_Count):

        if index % 2 == 0:
            ruleset_id = ruleset_ids[0]
        else:
            ruleset_id = ruleset_ids[1]

        hour = index % Seed_Span_Hours
        outcome, is_error = outcome_for(index)

        # Errors always keep their story, a slice of the successes does too - a production capture dial.
        keeps_story = is_error or index % Seed_Story_Every == 1

        if keeps_story:
            fired_rule_ids = fired_rules_for(index)
            story = story_for(index, outcome, fired_rule_ids)
            payload = serialize_document(story)
        else:
            payload = None

        yield (
            default_cluster_id,
            f'seed-{index:08d}',
            ruleset_id,
            version_for(index),
            occurred_texts[hour],
            bucket_texts[hour],
            business_key_for(index),
            outcome,
            int(is_error),
            duration_for(index),
            int(keeps_story),
            payload,
            fired_texts[index % 8],
        )

# ################################################################################################################################

def seed_reporting_decisions(database:'PerfDatabase', ruleset_ids:'tuple[int, int]') -> 'float':
    """ Bulk-seeds the million-row decision log the reporting scenario is measured over.
    Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    connection = connect_native(database)
    cursor = connection.cursor()

    rows = _decision_rows(ruleset_ids)
    load_rows(cursor, database.db_type, 'rule_decision', _decision_columns, rows)

    connection.commit()
    _analyze_tables(connection, cursor, database.db_type)
    connection.close()

    now = monotonic()
    out = now - start
    return out

# ################################################################################################################################

def _rollup_rows(ruleset_ids:'tuple[int, int]') -> 'row_iterator':
    """ Yields one daily firing-counter row per rule, day and ruleset.
    """
    created_text = Seed_Base_Time.strftime(Seed_Time_Format)
    rules_per_ruleset = Rollup_Rule_Count // 2

    for ruleset_index, ruleset_id in enumerate(ruleset_ids):

        for rule_index in range(rules_per_ruleset):

            # Every counter belongs to a stable rule identifier derived from the catalogs.
            catalog = catalog_for(ruleset_index)
            base_rule_id = catalog[rule_index % len(catalog)]
            subject_id = f'{base_rule_id}-{rule_index:04d}'

            for day in range(Rollup_Day_Count):
                bucket_start = Seed_Base_Time + timedelta(days=day)
                bucket_text = bucket_start.strftime(Seed_Time_Format)
                event_count = 1 + (rule_index + day) % 40

                yield (
                    default_cluster_id,
                    ruleset_id,
                    1,
                    Event_Type_Rule_Fired_Daily,
                    System_Actor,
                    subject_id,
                    bucket_text,
                    event_count,
                    created_text,
                    None,
                )

# ################################################################################################################################

def seed_rollups(database:'PerfDatabase', ruleset_ids:'tuple[int, int]') -> 'float':
    """ Bulk-seeds ninety days of daily firing counters for two thousand rules.
    Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    connection = connect_native(database)
    cursor = connection.cursor()

    rows = _rollup_rows(ruleset_ids)
    load_rows(cursor, database.db_type, 'rule_event', _event_columns, rows)

    connection.commit()
    _analyze_tables(connection, cursor, database.db_type)
    connection.close()

    now = monotonic()
    out = now - start
    return out

# ################################################################################################################################

def _definition_document(index:'int') -> 'str':
    """ Returns the serialized document of one bulk-seeded definition, with a searchable network tier.
    """
    network_tier = f'network-tier-{index % Seed_Network_Tier_Count:04d}'
    document:'anydict' = {
        'conditions': [
            {'term': 'member.network_tier', 'operator': 'equals', 'value': network_tier},
            {'term': 'member.plan', 'operator': 'in', 'value': ['plan-standard', 'plan-plus', 'plan-complete']},
        ],
    }

    out = serialize_document(document)
    return out

# ################################################################################################################################

def _definition_rows(parent_ids:'tuple[int, int]', child_count:'int') -> 'row_iterator':
    """ Yields every bulk-seeded child definition row with an explicitly assigned identity.
    """
    created_text = Seed_Base_Time.strftime(Seed_Time_Format)

    for index in range(child_count):
        definition_id = Seed_Definition_Base + index
        parent_id = parent_ids[index % 2]
        document = _definition_document(index)

        yield (
            definition_id,
            default_cluster_id,
            parent_id,
            parent_id,
            f'Coverage check {index:05d}',
            Definition_Type_Sentence_Rule,
            Seed_Versions_Per_Definition,
            Seed_Versions_Per_Definition,
            1,
            created_text,
            created_text,
            document,
        )

# ################################################################################################################################

def _version_rows(child_count:'int') -> 'row_iterator':
    """ Yields the immutable version snapshots of every bulk-seeded definition.
    """
    created_text = Seed_Base_Time.strftime(Seed_Time_Format)

    for index in range(child_count):
        definition_id = Seed_Definition_Base + index
        document = _definition_document(index)

        for version in range(1, Seed_Versions_Per_Definition + 1):
            yield (
                definition_id,
                version,
                Author,
                f'Refine the coverage check, revision {version}',
                created_text,
                document,
            )

# ################################################################################################################################

def _definition_event_rows(child_count:'int') -> 'row_iterator':
    """ Yields the creation and publication history events of every bulk-seeded definition.
    """
    created_text = Seed_Base_Time.strftime(Seed_Time_Format)

    for index in range(child_count):
        definition_id = Seed_Definition_Base + index

        for event_type in (Event_Type_Version_Created, Event_Type_Version_Published):
            yield (
                default_cluster_id,
                definition_id,
                Seed_Versions_Per_Definition,
                event_type,
                Author,
                None,
                None,
                None,
                created_text,
                None,
            )

# ################################################################################################################################

def seed_definitions(database:'PerfDatabase', parent_ids:'tuple[int, int]') -> 'float':
    """ Bulk-seeds the thousands of child definitions, their versions and their history events.
    Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    # The two parent rulesets already exist, so the children fill the rest of the population.
    child_count = Seeded_Definition_Count - 2

    connection = connect_native(database)
    cursor = connection.cursor()

    definition_rows = _definition_rows(parent_ids, child_count)
    load_rows(cursor, database.db_type, 'rule_definition', _definition_columns, definition_rows)

    version_rows = _version_rows(child_count)
    load_rows(cursor, database.db_type, 'rule_version', _version_columns, version_rows)

    event_rows = _definition_event_rows(child_count)
    load_rows(cursor, database.db_type, 'rule_event', _event_columns, event_rows)

    # COPY does not touch the id sequence, so the next regular insert would collide
    # with a seeded identity - only PostgreSQL needs this, the others move their counters themselves.
    if database.db_type == Type_PostgreSQL:
        max_definition_id = Seed_Definition_Base + child_count
        _ = cursor.execute(f"select setval(pg_get_serial_sequence('rule_definition', 'id'), {max_definition_id})")

    connection.commit()
    _analyze_tables(connection, cursor, database.db_type)
    connection.close()

    now = monotonic()
    out = now - start
    return out

# ################################################################################################################################

def count_decision_rows(session_factory:'SessionFactory') -> 'int':
    """ Counts the physical decision rows - the zero-loss checks compare this with the generated totals.
    """
    session = session_factory()

    try:
        row_count = func.count(rule_decision_table.c.id)
        query = select(row_count)
        result = session.execute(query)
        out = result.scalar_one()
    finally:
        session.close()

    return out

# ################################################################################################################################
# ################################################################################################################################
