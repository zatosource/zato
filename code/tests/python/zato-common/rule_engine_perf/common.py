# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ssl
from typing import NamedTuple

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql.data import anydict, strlist

    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# Database types the perf databases report in their connection details.
Type_SQLite     = 'sqlite'
Type_MySQL      = 'mysql'
Type_PostgreSQL = 'postgresql'

# ################################################################################################################################

# The headline floor - the decisions-per-second claim, asserted on every database, plain and over TLS.
Min_Decision_Rate_Per_Second     = 200
Min_Decision_Rate_Per_Second_SSL = 200

# The synchronous insert_batch path clears a calibrated floor - half of the slowest measured run,
# so the suite catches regressions without flaking (the runs measured 2,248 to 7,695 decisions/s).
Min_Batch_Rate_Per_Second     = 1000
Min_Batch_Rate_Per_Second_SSL = 1000

# Every reporting query over the million-row log must answer within this many seconds.
Max_Report_Query_Seconds     = 2.0
Max_Report_Query_Seconds_SSL = 2.0

# Every editor-path operation over 5,000 definitions must answer within this many seconds.
Max_Definition_Query_Seconds     = 2.0
Max_Definition_Query_Seconds_SSL = 2.0

# The retention sweep over half the million-row log must finish within this many seconds -
# calibrated at roughly twice the slowest measured run (MySQL needed 220 seconds, PostgreSQL 6).
Max_Retention_Seconds     = 480.0
Max_Retention_Seconds_SSL = 480.0

# ################################################################################################################################

# How many decisions the sustained ingest run pushes through the live writer.
Ingest_Decision_Count = 100_000

# How many submitter threads push those decisions concurrently.
Ingest_Submitter_Count = 4

# How many decisions one synchronous insert_batch call carries.
Batch_Size = 200

# How many synchronous batches the batch scenario inserts.
Batch_Count = 100

# How many decision rows the reporting scenario is measured over.
Seeded_Decision_Count = 1_000_000

# How many rule definitions the editor-path scenario is measured over.
Seeded_Definition_Count = 5_000

# How many distinct rules have daily firing counters behind the trend queries.
Rollup_Rule_Count = 2_000

# Over how many days those firing counters span.
Rollup_Day_Count = 90

# How long a submitter sleeps when the writer's bounded buffer reports saturation.
Full_Buffer_Sleep_Seconds = 0.002

# ################################################################################################################################
# ################################################################################################################################

class PerfDatabase(NamedTuple):
    """ One database the perf scenarios run against, with everything both SQLAlchemy and native seeding need.
    """

    label:        'str'
    db_type:      'str'
    url:          'str'
    connect_args: 'anydict'
    details:      'anydict'
    uses_ssl:     'bool'

# ################################################################################################################################

class Floors(NamedTuple):
    """ The floors and ceilings of one run - the plain or the TLS set.
    """

    min_decision_rate:            'int'
    min_batch_rate:               'int'
    max_report_query_seconds:     'float'
    max_definition_query_seconds: 'float'
    max_retention_seconds:        'float'

# ################################################################################################################################

class Measurement(NamedTuple):
    """ One measured number and the requirement it cleared, for the final quotable table.
    """

    name:        'str'
    value:       'str'
    requirement: 'str'

# ################################################################################################################################
# ################################################################################################################################

measurement_list = list[Measurement]
float_list = list[float]

# ################################################################################################################################
# ################################################################################################################################

def build_ssl_context(details:'anydict') -> 'ssl.SSLContext':
    """ Builds the TLS context that trusts the throwaway CA of the test-managed containers.
    """
    out = ssl.create_default_context(cafile=details['ssl_ca_file'])
    return out

# ################################################################################################################################

def sqlite_database(database_path:'str') -> 'PerfDatabase':
    """ Returns the file-backed SQLite database of one run.
    """
    details = {
        'type': Type_SQLite,
        'name': database_path,
    }

    # The background writer thread and the submitters share the one engine,
    # so the connections must be usable across threads.
    connect_args = {'check_same_thread': False}

    out = PerfDatabase(
        label='SQLite',
        db_type=Type_SQLite,
        url=f'sqlite:///{database_path}',
        connect_args=connect_args,
        details=details,
        uses_ssl=False,
    )
    return out

# ################################################################################################################################

def database_from_details(label:'str', details:'anydict') -> 'PerfDatabase':
    """ Turns the connection details of a test-managed container into one perf database.
    """
    db_type = details['type']
    username = details['username']
    password = details['password']
    host = details['host']
    port = details['port']
    name = details['name']

    # Each server database has its one driver of choice ..
    if db_type == Type_MySQL:
        url = f'mysql+pymysql://{username}:{password}@{host}:{port}/{name}'
    else:
        url = f'postgresql+pg8000://{username}:{password}@{host}:{port}/{name}'

    # .. and a TLS-required container hands us the CA its server certificate chains up to.
    uses_ssl = 'ssl' in details

    if uses_ssl:
        ssl_context = build_ssl_context(details)
        connect_args:'anydict' = {'ssl': ssl_context}
    else:
        connect_args = {}

    out = PerfDatabase(
        label=label,
        db_type=db_type,
        url=url,
        connect_args=connect_args,
        details=details,
        uses_ssl=uses_ssl,
    )
    return out

# ################################################################################################################################

def floors_for(database:'PerfDatabase') -> 'Floors':
    """ Returns the plain or the TLS floor set of one run.
    """
    if database.uses_ssl:
        out = Floors(
            min_decision_rate=Min_Decision_Rate_Per_Second_SSL,
            min_batch_rate=Min_Batch_Rate_Per_Second_SSL,
            max_report_query_seconds=Max_Report_Query_Seconds_SSL,
            max_definition_query_seconds=Max_Definition_Query_Seconds_SSL,
            max_retention_seconds=Max_Retention_Seconds_SSL,
        )
    else:
        out = Floors(
            min_decision_rate=Min_Decision_Rate_Per_Second,
            min_batch_rate=Min_Batch_Rate_Per_Second,
            max_report_query_seconds=Max_Report_Query_Seconds,
            max_definition_query_seconds=Max_Definition_Query_Seconds,
            max_retention_seconds=Max_Retention_Seconds,
        )

    return out

# ################################################################################################################################

def percentile(sorted_values:'float_list', fraction:'float') -> 'float':
    """ Returns the value at the given fraction of an already sorted population.
    """
    last_index = len(sorted_values) - 1
    position = fraction * last_index
    index = int(position)

    out = sorted_values[index]
    return out

# ################################################################################################################################
# ################################################################################################################################
