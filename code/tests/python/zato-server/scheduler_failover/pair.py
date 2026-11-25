# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The jobs that the active-standby suites run - the enmasse file that defines them, with the dates of their grid,
# and its offline import into the configuration database of a server.

# stdlib
import logging
import os
from datetime import datetime, timedelta, timezone

# Zato
from zato.common.test.conftest_base_pubsub import render_template
from zato.common.test.container_output import run_command_with_output

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.scheduler_failover')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The module of the service that each job invokes.
    Service_File_Name = 'zato_test_scheduler_run_log.py'

    # The enmasse file with the jobs.
    Scheduler_Template = 'scheduler_failover/_enmasse_template.yaml'

    # How long ago the grid of the interval jobs begins, in seconds.
    Grid_Start_Age_Seconds = 3600

    # How long before the jobs are imported the one-time job of the past was due, in seconds.
    Past_Start_Age_Seconds = 60

    # How long after the jobs are imported the one-time job of the gap is due, in seconds.
    Gap_Start_Delay_Seconds = 180

    # How long the enmasse command may take, in seconds.
    Command_Timeout_Seconds = 300

    # The type of the shared objects with the run state of the jobs.
    Run_State_Object_Type = 'scheduler.job'

# ################################################################################################################################

_tests_dir = os.path.join(os.path.dirname(__file__), '..')
_tests_dir = os.path.abspath(_tests_dir)

_repository_dir = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin = os.path.join(_repository_dir, 'code', 'bin', 'zato')

# The format of the start dates in the enmasse file, which are in UTC.
_date_format = '%Y-%m-%dT%H:%M:%S'

# ################################################################################################################################
# ################################################################################################################################

def format_date(value:'datetime') -> 'str':
    out = value.strftime(_date_format)
    return out

# ################################################################################################################################

def import_jobs(quickstart_directory:'str', server_directory:'str', rendered_yaml:'str', extra_env:'strstrdict') -> 'None':
    """ Imports the enmasse file with the jobs, offline, into the configuration database of a server,
    with the given variables added to the environment of the command.
    """
    rendered_path = os.path.join(quickstart_directory, 'enmasse.yaml')

    with open(rendered_path, 'w') as rendered_file:
        _ = rendered_file.write(rendered_yaml)

    env = os.environ.copy()
    env['Zato_Needs_Config_Reload'] = 'False'
    env.update(extra_env)

    command = [_zato_bin, 'enmasse', '--import', '--input', rendered_path, server_directory]
    exit_code = run_command_with_output(command, 'enmasse', logger, env, ModuleCtx.Command_Timeout_Seconds)

    if exit_code != 0:
        raise Exception(f'enmasse import failed with exit code {exit_code}')

# ################################################################################################################################

def render_job_file(placeholders:'strstrdict') -> 'tuple[str, datetime]':
    """ Renders the enmasse file with the jobs, adding their dates to the placeholders, and returns it
    with the date of the one-time job of the gap.
    """
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    grid_start = now - timedelta(seconds=ModuleCtx.Grid_Start_Age_Seconds)
    past_start = datetime.now(timezone.utc) - timedelta(seconds=ModuleCtx.Past_Start_Age_Seconds)
    gap_start = datetime.now(timezone.utc) + timedelta(seconds=ModuleCtx.Gap_Start_Delay_Seconds)
    gap_start = gap_start.replace(microsecond=0)

    placeholders['grid_start'] = format_date(grid_start)
    placeholders['past_start'] = format_date(past_start)
    placeholders['gap_start'] = format_date(gap_start)

    template_path = os.path.join(_tests_dir, ModuleCtx.Scheduler_Template)
    rendered_yaml = render_template(template_path, placeholders)

    out = (rendered_yaml, gap_start)
    return out

# ################################################################################################################################
# ################################################################################################################################
