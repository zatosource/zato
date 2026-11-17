# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta
from time import monotonic

# SQLAlchemy
from sqlalchemy import func, select

# Local
from common import Rollup_Day_Count, Rollup_Rule_Count, Seeded_Decision_Count, Seeded_Definition_Count
from zato.common.rule_engine.sql.constants import Definition_Type_Sentence_Rule, Event_Type_Rule_Fired_Daily, \
    Event_Type_Version_Created, Event_Type_Version_Published, System_Actor
from zato.common.rule_engine.sql.document import serialize_document, serialize_string_list
from zato.common.rule_engine.sql.schema import metadata, rule_decision_table, rule_definition_table, rule_event_table, \
    rule_version_table
from zato.common.test.direct_sql.reset import truncate_tables
from zato.common.test.direct_sql.seed import refresh_statistics, seed_bulk, BulkLoad
from traffic import Author, business_key_for, catalog_for, duration_for, fired_rules_for, outcome_for, story_for, \
    version_for

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy import Table
    from sqlalchemy.engine import Engine
    from zato.common.rule_engine.sql.data import anydict, strlist
    from zato.common.rule_engine.sql.database import SessionFactory

    anydict = anydict
    Engine = Engine
    strlist = strlist
    SessionFactory = SessionFactory
    row_iterator = Iterator[tuple]
    tablelist = list[Table]

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

# The write-time hour bucket format, the same one decision_to_row uses.
Seed_Bucket_Format = '%Y-%m-%dT%H'

# ################################################################################################################################
# ################################################################################################################################

# The columns of rule_decision in seeding order - the id column is omitted so the engine assigns it itself.
_decision_columns = ('decision_id', 'ruleset_id', 'rules_version', 'occurred_at', 'time_bucket',
    'business_key', 'outcome', 'is_error', 'duration_ms', 'has_payload', 'payload', 'fired_rule_ids')

# The columns of rule_definition in seeding order - the id comes first and is assigned explicitly
# so version and event rows can reference their definitions without any lookup.
_definition_columns = ('id', 'parent_id', 'parent_key', 'name', 'object_type', 'current_version',
    'live_version', 'is_active', 'created_at', 'updated_at', 'document')

# The columns of rule_version in seeding order.
_version_columns = ('definition_id', 'version', 'author', 'comment', 'created_at', 'document')

# The columns of rule_event in seeding order.
_event_columns = ('definition_id', 'version', 'event_type', 'actor', 'subject_id', 'bucket_start', 'event_count',
    'created_at', 'payload')

# ################################################################################################################################
# ################################################################################################################################

def _tables_children_first() -> 'tablelist':
    """ Every rule-engine table, referencing tables before the ones they reference.

    The tables come from the schema itself rather than from a list here, because a table added
    to the schema later would otherwise leave the reset naming fewer tables than it has to.
    """
    out:'tablelist' = []

    for table in reversed(metadata.sorted_tables):
        out.append(table)

    return out

# ################################################################################################################################

def delete_all_rows(engine:'Engine') -> 'None':
    """ Empties every rule-engine table over the fastest path of the database - TRUNCATE on the network databases,
    which is instant regardless of the row count, and SQLite's DELETE without a WHERE clause, which is already
    its truncate optimization.
    """
    tables = _tables_children_first()
    truncate_tables(engine, tables)

# ################################################################################################################################

def _decision_rows(ruleset_ids:'tuple[int, int]') -> 'row_iterator':
    """ Yields every bulk-seeded decision row, each field derived deterministically from its index.
    """
    # Precompute the per-hour timestamps and bucket texts - a million strftime calls would dominate generation ..
    occurred_times:'list[datetime]' = []
    bucket_texts:'strlist' = []

    for hour in range(Seed_Span_Hours):
        occurred_at = Seed_Base_Time + timedelta(hours=hour)
        occurred_times.append(occurred_at)
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
            f'seed-{index:08d}',
            ruleset_id,
            version_for(index),
            occurred_times[hour],
            bucket_texts[hour],
            business_key_for(index),
            outcome,
            is_error,
            duration_for(index),
            keeps_story,
            payload,
            fired_texts[index % 8],
        )

# ################################################################################################################################

def seed_reporting_decisions(engine:'Engine', ruleset_ids:'tuple[int, int]') -> 'float':
    """ Bulk-seeds the million-row decision log the reporting scenario is measured over.
    Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    rows = _decision_rows(ruleset_ids)
    seed_bulk(engine, [BulkLoad(rule_decision_table, _decision_columns, rows, False)])

    tables = _tables_children_first()
    refresh_statistics(engine, tables)

    now = monotonic()
    out = now - start
    return out

# ################################################################################################################################

def _rollup_rows(ruleset_ids:'tuple[int, int]') -> 'row_iterator':
    """ Yields one daily firing-counter row per rule, day and ruleset.
    """
    rules_per_ruleset = Rollup_Rule_Count // 2

    for ruleset_index, ruleset_id in enumerate(ruleset_ids):

        for rule_index in range(rules_per_ruleset):

            # Every counter belongs to a stable rule identifier derived from the catalogs.
            catalog = catalog_for(ruleset_index)
            base_rule_id = catalog[rule_index % len(catalog)]
            subject_id = f'{base_rule_id}-{rule_index:04d}'

            for day in range(Rollup_Day_Count):
                bucket_start = Seed_Base_Time + timedelta(days=day)
                event_count = 1 + (rule_index + day) % 40

                yield (
                    ruleset_id,
                    1,
                    Event_Type_Rule_Fired_Daily,
                    System_Actor,
                    subject_id,
                    bucket_start,
                    event_count,
                    Seed_Base_Time,
                    None,
                )

# ################################################################################################################################

def seed_rollups(engine:'Engine', ruleset_ids:'tuple[int, int]') -> 'float':
    """ Bulk-seeds ninety days of daily firing counters for two thousand rules.
    Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    rows = _rollup_rows(ruleset_ids)
    seed_bulk(engine, [BulkLoad(rule_event_table, _event_columns, rows, False)])

    tables = _tables_children_first()
    refresh_statistics(engine, tables)

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
    for index in range(child_count):
        definition_id = Seed_Definition_Base + index
        parent_id = parent_ids[index % 2]
        document = _definition_document(index)

        yield (
            definition_id,
            parent_id,
            parent_id,
            f'Coverage check {index:05d}',
            Definition_Type_Sentence_Rule,
            Seed_Versions_Per_Definition,
            Seed_Versions_Per_Definition,
            True,
            Seed_Base_Time,
            Seed_Base_Time,
            document,
        )

# ################################################################################################################################

def _version_rows(child_count:'int') -> 'row_iterator':
    """ Yields the immutable version snapshots of every bulk-seeded definition.
    """
    for index in range(child_count):
        definition_id = Seed_Definition_Base + index
        document = _definition_document(index)

        for version in range(1, Seed_Versions_Per_Definition + 1):
            yield (
                definition_id,
                version,
                Author,
                f'Refine the coverage check, revision {version}',
                Seed_Base_Time,
                document,
            )

# ################################################################################################################################

def _definition_event_rows(child_count:'int') -> 'row_iterator':
    """ Yields the creation and publication history events of every bulk-seeded definition.
    """
    for index in range(child_count):
        definition_id = Seed_Definition_Base + index

        for event_type in (Event_Type_Version_Created, Event_Type_Version_Published):
            yield (
                definition_id,
                Seed_Versions_Per_Definition,
                event_type,
                Author,
                None,
                None,
                None,
                Seed_Base_Time,
                None,
            )

# ################################################################################################################################

def seed_definitions(engine:'Engine', parent_ids:'tuple[int, int]') -> 'float':
    """ Bulk-seeds the thousands of child definitions, their versions and their history events.
    Returns the elapsed seeding time in seconds.
    """
    start = monotonic()

    # The two parent rulesets already exist, so the children fill the rest of the population.
    child_count = Seeded_Definition_Count - 2

    # The definitions carry their own identities, which the versions and the events refer to.
    loads = [
        BulkLoad(rule_definition_table, _definition_columns, _definition_rows(parent_ids, child_count), True),
        BulkLoad(rule_version_table, _version_columns, _version_rows(child_count), False),
        BulkLoad(rule_event_table, _event_columns, _definition_event_rows(child_count), False),
    ]

    seed_bulk(engine, loads)

    tables = _tables_children_first()
    refresh_statistics(engine, tables)

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
