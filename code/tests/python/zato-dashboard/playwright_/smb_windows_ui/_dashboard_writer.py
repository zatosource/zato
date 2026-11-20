# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# Playwright helpers
from file_transfer_schedule import fill_schedule_wizard, open_create_wizard, open_schedules
from scheduler_job import create_interval_job, get_job_id, navigate_to_jobs, set_job_active
from smb_connection import create_connection, edit_connection, get_item_id, navigate_to_list, row_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, anylist

    namedict = dict[str, anydict]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The start date of each schedule and job, in the format of the date fields of the Dashboard. It is in the past
    # whatever the time zone of the Dashboard, so each schedule and job runs from the moment it is created.
    Start_Date = '01-01-2020 00:00:00'

    # The keys of a schedule and of a job that change with each build of the definitions without changing what runs
    Start_Date_Key = 'start_date'

    # The key of a job that the writer changes through the Dashboard, the others are fixed once the job is created
    Job_Active_Key = 'is_active'

    # The key of the schedules of a connection
    Schedules_Key = 'schedules'

    # What is done with a schedule
    Created = 'created'
    Edited  = 'edited'
    Deleted = 'deleted'

    # How long a deleted schedule may take to leave the list, in milliseconds
    Delete_Timeout = 5000

    # The prefix of each progress line
    Progress_Prefix = '[SMB UI]'

# ################################################################################################################################
# ################################################################################################################################

def _by_name(items:'anylist') -> 'namedict':
    out:'namedict' = {}

    for item in items:
        out[item['name']] = item

    return out

# ################################################################################################################################

def _schedules_of(connection:'anydict') -> 'anylist':
    """ Returns the schedules of a connection, of which a connection without schedules has no key at all.
    """
    if ModuleCtx.Schedules_Key in connection:
        out = connection[ModuleCtx.Schedules_Key]
    else:
        out = []

    return out

# ################################################################################################################################

def _without_keys(item:'anydict', *keys:'str') -> 'anydict':
    out:'anydict' = {}

    for key, value in item.items():
        if key not in keys:
            out[key] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class DashboardWriter:
    """ Creates and changes the definitions of the guests through the Dashboard. Each version is changed only
    where its definitions differ from those last applied, so a test that changes one connection or one job
    waits for that change only.
    """
    def __init__(self, page:'Page', base_url:'str') -> 'None':
        self.page = page
        self.base_url = base_url
        self.applied:'namedict' = {}

# ################################################################################################################################

    def _report(self, version:'str', action:'str', name:'str', started:'float') -> 'None':
        elapsed = monotonic() - started
        print(f'{ModuleCtx.Progress_Prefix} win{version} {action} {name} in {elapsed:.1f}s', flush=True)

# ################################################################################################################################

    def apply(self, version:'str', definitions:'anydict') -> 'None':
        """ Brings the connections, the schedules and the job of one guest in the Dashboard to the given definitions.
        """
        started = monotonic()

        # A version applied for the first time has nothing to compare with ..
        if version in self.applied:
            previous = self.applied[version]
        else:
            previous = {'smb': [], 'scheduler': []}

        previous_connections = _by_name(previous['smb'])
        previous_jobs = _by_name(previous['scheduler'])

        # .. the connections go first, because the schedules belong to them ..
        for connection in definitions['smb']:
            self._apply_connection(version, connection, previous_connections)

        # .. and the job writes through one of them.
        for job in definitions['scheduler']:
            self._apply_job(version, job, previous_jobs)

        self.applied[version] = definitions
        self._report(version, 'applied', 'the definitions', started)

# ################################################################################################################################

    def _apply_connection(self, version:'str', connection:'anydict', previous_connections:'namedict') -> 'None':
        started = monotonic()
        name = connection['name']

        navigate_to_list(self.page, self.base_url)

        # A connection that is not there yet is created ..
        if name not in previous_connections:
            create_connection(
                self.page, name, connection['host'], connection['port'], connection['username'], connection['password'])
            self._report(version, ModuleCtx.Created, name, started)
            previous_schedules:'anylist' = []

        # .. one that is, is edited if its address or its credentials changed.
        else:
            previous = previous_connections[name]
            previous_schedules = _schedules_of(previous)

            address = connection['host'], connection['port'], connection['username'], connection['password']
            previous_address = previous['host'], previous['port'], previous['username'], previous['password']

            if address != previous_address:

                # An empty password keeps the one the connection has
                if connection['password'] == previous['password']:
                    password = ''
                else:
                    password = connection['password']

                item_id = get_item_id(self.page, name)
                edit_connection(self.page, item_id, connection['host'], connection['port'], connection['username'], password)
                self._report(version, ModuleCtx.Edited, name, started)

        schedules = _schedules_of(connection)
        self._apply_schedules(version, name, schedules, previous_schedules)

# ################################################################################################################################

    def _apply_schedules(self, version:'str', conn_name:'str', schedules:'anylist', previous_schedules:'anylist') -> 'None':

        current = _by_name(schedules)
        previous = _by_name(previous_schedules)

        # Nothing is opened when no schedule changes ..
        changes:'anylist' = []

        for name, schedule in current.items():
            if name not in previous:
                changes.append((ModuleCtx.Created, schedule))
            else:
                compared = _without_keys(schedule, ModuleCtx.Start_Date_Key)
                previous_compared = _without_keys(previous[name], ModuleCtx.Start_Date_Key)
                if compared != previous_compared:
                    changes.append((ModuleCtx.Edited, schedule))

        for name, schedule in previous.items():
            if name not in current:
                changes.append((ModuleCtx.Deleted, schedule))

        if not changes:
            return

        # .. otherwise, each change is made on the list of the schedules of the connection.
        navigate_to_list(self.page, self.base_url)
        open_schedules(self.page, conn_name)

        handlers = {
            ModuleCtx.Created: self._create_schedule,
            ModuleCtx.Edited:  self._edit_schedule,
            ModuleCtx.Deleted: self._delete_schedule,
        }

        for action, schedule in changes:
            started = monotonic()
            schedule_name = schedule['name']

            handler = handlers[action]
            handler(schedule)

            self._report(version, action, f'{conn_name} / {schedule_name}', started)

# ################################################################################################################################

    def _create_schedule(self, schedule:'anydict') -> 'None':
        open_create_wizard(self.page)
        fill_schedule_wizard(self.page, schedule, ModuleCtx.Start_Date)

# ################################################################################################################################

    def _edit_schedule(self, schedule:'anydict') -> 'None':
        schedule_row = row_selector(schedule['name'])

        self.page.click(f'{schedule_row} a:has-text("Edit")')
        _ = self.page.wait_for_selector('#file-transfer-wizard', state='visible')

        fill_schedule_wizard(self.page, schedule, ModuleCtx.Start_Date)

# ################################################################################################################################

    def _delete_schedule(self, schedule:'anydict') -> 'None':
        schedule_row = row_selector(schedule['name'])

        self.page.click(f'{schedule_row} a:has-text("Delete")')
        _ = self.page.wait_for_selector('#popup_container', state='visible')

        self.page.click('#popup_ok')
        _ = self.page.wait_for_selector(schedule_row, state='detached', timeout=ModuleCtx.Delete_Timeout)

# ################################################################################################################################

    def _apply_job(self, version:'str', job:'anydict', previous_jobs:'namedict') -> 'None':
        started = monotonic()
        name = job['name']

        # A job that is not there yet is created ..
        if name not in previous_jobs:
            navigate_to_jobs(self.page, self.base_url)

            extra = '\n'.join(job['extra'])
            create_interval_job(
                self.page, name, job['service'], job['seconds'], ModuleCtx.Start_Date, extra, job['is_active'])

            self._report(version, ModuleCtx.Created, name, started)
            return

        # .. one that is, may only be activated or deactivated ..
        previous = previous_jobs[name]

        fixed = _without_keys(job, ModuleCtx.Start_Date_Key, ModuleCtx.Job_Active_Key)
        previous_fixed = _without_keys(previous, ModuleCtx.Start_Date_Key, ModuleCtx.Job_Active_Key)

        if fixed != previous_fixed:
            raise Exception(f'Job {name} may only be activated or deactivated -> {previous_fixed} -> {fixed}')

        # .. which happens only if its active flag changed.
        if job['is_active'] != previous['is_active']:
            navigate_to_jobs(self.page, self.base_url)

            job_id = get_job_id(self.page, name)
            set_job_active(self.page, job_id, job['is_active'])

            self._report(version, ModuleCtx.Edited, name, started)

# ################################################################################################################################
# ################################################################################################################################
