# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from batch import run_batch_scenario
from common import floors_for, Measurement, PerfDatabase
from definitions_load import run_definitions_scenario
from ingest import run_ingest_scenario
from reporting_load import run_reporting_scenario
from retention_load import run_retention_scenario
from zato.common.rules.sql import create_database_engine, create_schema, RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from common import measurement_list

    measurement_list = measurement_list

# ################################################################################################################################
# ################################################################################################################################

def _print_summary(label:'str', measurements:'measurement_list') -> 'None':
    """ Prints the final quotable table - every measured number next to the requirement it cleared.
    """
    # Size each column to its widest content ..
    name_width = len('Measurement')
    value_width = len('Measured')

    for measurement in measurements:
        name_width = max(name_width, len(measurement.name))
        value_width = max(value_width, len(measurement.value))

    # .. and print the aligned rows.
    print('', flush=True)
    print(f'Rule engine SQL layer performance - {label}', flush=True)
    header = Measurement('Measurement', 'Measured', 'Requirement')
    rows = [header]
    rows.extend(measurements)

    for row in rows:
        name_text = row.name.ljust(name_width)
        value_text = row.value.rjust(value_width)
        print(f'  {name_text}  {value_text}  {row.requirement}', flush=True)

    print('', flush=True)

# ################################################################################################################################

def run_complete_perf(database:'PerfDatabase') -> 'None':
    """ Runs every scenario against one database and prints the quotable summary table.
    """
    print(f'Running the rule engine SQL layer performance proof on {database.label}', flush=True)

    # One engine and one schema serve the whole run ..
    engine = create_database_engine(database.url, connect_args=database.connect_args)
    create_schema(engine)
    backend = RuleSQLBackend.from_engine(engine)
    floors = floors_for(database)

    try:
        measurements:'measurement_list' = []

        # .. the headline sustained ingest through the live writer ..
        ingest_measurements = run_ingest_scenario(backend, database, floors)
        measurements.extend(ingest_measurements)

        # .. the synchronous batch path ..
        batch_measurements = run_batch_scenario(backend, database, floors)
        measurements.extend(batch_measurements)

        # .. the editor paths over thousands of definitions ..
        definition_measurements = run_definitions_scenario(backend, database, floors)
        measurements.extend(definition_measurements)

        # .. the dashboard paths over the million-row log ..
        reporting_measurements, state = run_reporting_scenario(backend, database, floors)
        measurements.extend(reporting_measurements)

        # .. and the retention sweep over that same still-seeded log.
        retention_measurements = run_retention_scenario(backend, floors, state)
        measurements.extend(retention_measurements)

        _print_summary(database.label, measurements)

    # Release the engine's connection pool in every case.
    finally:
        engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
