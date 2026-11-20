# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from functools import partial
from time import monotonic

# Playwright helpers
from file_transfer_schedule import fill_schedule_wizard, open_create_wizard, open_schedules
from scheduler_job import create_interval_job, get_job_id, job_row_selector, navigate_to_jobs, set_job_active
from smb_connection import create_connection, edit_connection, get_item_id, navigate_to_list, row_selector

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist, callable_

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

    # The type of a console message that reports an error of a script
    Console_Error = 'error'

    # The failure of a request that the browser aborted because the network of the host changed
    Network_Changed = 'net::ERR_NETWORK_CHANGED'

    # How many times a page is opened, and a change is made, before the changes of the network fail the run
    Navigate_Attempts = 5
    Change_Attempts = 3

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

        # Whether the browser aborted a request of the page because the network of the host changed
        self.is_network_changed = False

        # A script error of a page leaves its dialogs unopened, so each one is printed the moment it is raised.
        self.page.on('pageerror', self._on_page_error)
        self.page.on('console', self._on_console)
        self.page.on('requestfailed', self._on_request_failed)

# ################################################################################################################################

    def _on_request_failed(self, request:'any_') -> 'None':
        if request.failure == ModuleCtx.Network_Changed:
            self.is_network_changed = True

# ################################################################################################################################

    def _navigate(self, open_page:'callable_') -> 'None':
        """ Opens a page of the Dashboard. The browser aborts the requests that are in progress whenever a container
        joins or leaves a network of the host, which leaves the scripts of a page unloaded, so such a page is opened again.
        """
        for _ in range(ModuleCtx.Navigate_Attempts):

            self.is_network_changed = False
            open_page()

            if not self.is_network_changed:
                return

        raise Exception(f'The network of the host changed during each of {ModuleCtx.Navigate_Attempts} loads of a page')

# ################################################################################################################################

    def _change(self, make_change:'callable_', open_page:'callable_', is_done:'callable_') -> 'None':
        """ Makes one change on the page that is open. A change that fails while the network of the host changes
        is made again on the page opened anew, unless that page shows that the change was made before the failure.
        """
        for attempt in range(1, ModuleCtx.Change_Attempts + 1):

            self.is_network_changed = False

            try:
                make_change()
                return

            except Exception:
                if not self.is_network_changed:
                    raise
                if attempt == ModuleCtx.Change_Attempts:
                    raise

            print(f'{ModuleCtx.Progress_Prefix} The network of the host changed during a change, opening the page again',
                flush=True)

            self._navigate(open_page)

            if is_done():
                return

# ################################################################################################################################

    def _open_connections(self) -> 'None':
        navigate_to_list(self.page, self.base_url)

# ################################################################################################################################

    def _open_schedules(self, conn_name:'str') -> 'None':
        navigate_to_list(self.page, self.base_url)
        open_schedules(self.page, conn_name)

# ################################################################################################################################

    def _open_jobs(self) -> 'None':
        navigate_to_jobs(self.page, self.base_url)

# ################################################################################################################################

    def _has_row(self, selector:'str') -> 'bool':
        out = self.page.locator(selector).count() > 0
        return out

# ################################################################################################################################

    def _has_no_row(self, selector:'str') -> 'bool':
        out = self.page.locator(selector).count() == 0
        return out

# ################################################################################################################################

    def _is_never_done(self) -> 'bool':
        """ An edit is made again in full, because the page does not show whether it was made.
        """
        return False

# ################################################################################################################################

    def _is_edited(self, _selector:'str') -> 'bool':
        """ An edited schedule looks the same in its list as before the edit, so the edit is made again in full.
        """
        out = self._is_never_done()
        return out

# ################################################################################################################################

    def _on_page_error(self, error:'any_') -> 'None':
        print(f'{ModuleCtx.Progress_Prefix} Page error: {error}', flush=True)

# ################################################################################################################################

    def _on_console(self, message:'any_') -> 'None':
        if message.type == ModuleCtx.Console_Error:
            print(f'{ModuleCtx.Progress_Prefix} Console error: {message.text}', flush=True)

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

        self._navigate(self._open_connections)

        # A connection that is not there yet is created ..
        if name not in previous_connections:
            create = partial(create_connection,
                self.page, name, connection['host'], connection['port'], connection['username'], connection['password'])
            is_created = partial(self._has_row, row_selector(name))
            self._change(create, self._open_connections, is_created)
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

                edit = partial(self._edit_connection, name, connection['host'], connection['port'], connection['username'],
                    password)
                self._change(edit, self._open_connections, self._is_never_done)
                self._report(version, ModuleCtx.Edited, name, started)

        schedules = _schedules_of(connection)
        self._apply_schedules(version, name, schedules, previous_schedules)

# ################################################################################################################################

    def _edit_connection(self, name:'str', host:'str', port:'int', username:'str', password:'str') -> 'None':
        item_id = get_item_id(self.page, name)
        edit_connection(self.page, item_id, host, port, username, password)

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
        open_page = partial(self._open_schedules, conn_name)
        self._navigate(open_page)

        handlers = {
            ModuleCtx.Created: self._create_schedule,
            ModuleCtx.Edited:  self._edit_schedule,
            ModuleCtx.Deleted: self._delete_schedule,
        }

        # A created schedule is in the list, a deleted one is not, and an edit is not visible in it
        done_checks = {
            ModuleCtx.Created: self._has_row,
            ModuleCtx.Edited:  self._is_edited,
            ModuleCtx.Deleted: self._has_no_row,
        }

        for action, schedule in changes:
            started = monotonic()
            schedule_name = schedule['name']

            make_change = partial(handlers[action], schedule)
            is_done = partial(done_checks[action], row_selector(schedule_name))
            self._change(make_change, open_page, is_done)

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
            self._navigate(self._open_jobs)

            extra = '\n'.join(job['extra'])
            create = partial(create_interval_job,
                self.page, name, job['service'], job['seconds'], ModuleCtx.Start_Date, extra, job['is_active'])
            is_created = partial(self._has_row, job_row_selector(name))
            self._change(create, self._open_jobs, is_created)

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
            self._navigate(self._open_jobs)

            set_active = partial(self._set_job_active, name, job['is_active'])
            self._change(set_active, self._open_jobs, self._is_never_done)

            self._report(version, ModuleCtx.Edited, name, started)

# ################################################################################################################################

    def _set_job_active(self, name:'str', is_active:'bool') -> 'None':
        job_id = get_job_id(self.page, name)
        set_job_active(self.page, job_id, is_active)

# ################################################################################################################################
# ################################################################################################################################
