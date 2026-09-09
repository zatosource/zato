# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from logging import getLogger
from traceback import format_exc
from urllib.parse import quote, urlencode

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse
from django.urls import reverse

# Zato
from zato.admin.web import from_user_to_utc, from_utc_to_user
from zato.admin.web.forms.outgoing.file_transfer_schedule import CreateForm
from zato.admin.web.views import get_js_dt_format, get_sample_dt, method_allowed, slugify
from zato.admin.web.views.scheduler import default_last_duration_ms, default_last_run_utc, get_last_run_by_id
from zato.common.api import FileTransfer, GENERIC
from zato.common.json_internal import dumps
from zato.common.util.interval import interval_from_unit, interval_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, dictlist, stranydict
    any_ = any_
    anylist = anylist
    dictlist = dictlist
    stranydict = stranydict

    dictlists = list['dictlist']

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_scheduler = FileTransfer.Scheduler

# .. the per-connection list of schedules ..
_schedules_template = 'zato/outgoing/file-transfer-schedules.html'

# .. and the multi-step wizard that creates or edits one.
_wizard_template = 'zato/outgoing/file-transfer-schedule-wizard.html'

# How each connection type reads on screen.
_transfer_labels = {
    'sftp': 'SFTP',
    'smb': 'SMB',
    'ftp': 'FTP',
}

# Where the back-to-the-connections link of each type points to.
_back_links = {
    'sftp': ('out-sftp', 'outconn-sftp'),
    'smb': ('out-smb', 'outconn-smb'),
    'ftp': ('out-ftp', 'outconn-ftp'),
}

# Which generic connection type each transfer type stands for.
_connection_types = {
    'sftp': GENERIC.CONNECTION.TYPE.OUTCONN_SFTP,
    'smb': GENERIC.CONNECTION.TYPE.OUTCONN_SMB,
    'ftp': GENERIC.CONNECTION.TYPE.OUTCONN_FTP,
}

# Where the command shell of each transfer type lives - SMB has none.
_command_shell_links = {
    'sftp': 'out-sftp-command-shell',
    'ftp': 'out-ftp-command-shell',
}

# Characters a path handed to a command shell's ls has escaped with a backslash.
_shell_escaped_chars = ('\\', '"', "'", ' ')

# The stored fields of a schedule, as the edit service's input names them.
_schedule_stored_fields = ('name', 'is_active', 'directory', 'pattern', 'ready_how', 'stability_delay', 'marker_suffix',
    'should_claim', 'service', 'on_success', 'move_directory', 'start_date', 'arrival_window', 'max_attempts',
    'retry_backoff', 'quarantine_directory', 'expected_files', 'expected_by', 'expected_days')

# The stored fields the wizard's form edits.
_schedule_form_fields = ('arrival_window', 'max_attempts', 'retry_backoff', 'quarantine_directory',
    'expected_files', 'expected_by', 'expected_days')

# ################################################################################################################################
# ################################################################################################################################

def get_schedules_by_conn_id(req:'any_', conn_id:'str') -> 'dictlist':
    """ Returns the schedules stored with a connection, straight from the schedule services.
    """
    response = req.zato.client.invoke('zato.outgoing.file-transfer.schedule.get-list', {
        'cluster_id': req.zato.cluster_id,
        'conn_id': conn_id,
    })

    if not response.ok:
        raise Exception(response.details)

    out = response.data
    return out

# ################################################################################################################################

def get_schedules(item:'any_') -> 'dictlist':
    """ Returns the schedules a connection list item carries in its opaque attributes.
    """
    out = getattr(item, _scheduler.Schedules_Field, None)

    # The attribute is only there for connections that have any schedules.
    if out is None:
        out = []

    return out

# ################################################################################################################################

def get_connection_last_run_list(req:'any_', schedule_lists:'dictlists') -> 'dictlist':
    """ Returns, for each list of schedules given, the most recent run among all of its schedules.
    """

    # Every job of every list ..
    job_id_list = []
    for schedules in schedule_lists:
        for schedule in schedules:
            job_id = str(schedule['job_id'])
            job_id_list.append(job_id)

    # .. and one call covers all of them.
    if job_id_list:
        last_run_by_id = get_last_run_by_id(req, job_id_list)
    else:
        last_run_by_id = {}

    out:'dictlist' = []

    for schedules in schedule_lists:

        job_ids = []
        for schedule in schedules:
            job_id = str(schedule['job_id'])
            job_ids.append(job_id)

        last_run_utc = default_last_run_utc
        last_duration_ms = default_last_duration_ms

        for job_id in job_ids:

            # The timestamps are ISO 8601 in UTC, so the later one is the greater string.
            if last_run := last_run_by_id.get(job_id):
                if last_run['last_run_utc'] > last_run_utc:
                    last_run_utc = last_run['last_run_utc']
                    last_duration_ms = last_run['last_duration_ms']

        # The cell keeps every job's id for the refresh.
        last_run_job_ids = ','.join(job_ids)

        out.append({
            'last_run_job_ids': last_run_job_ids,
            'last_run_utc': last_run_utc,
            'last_duration_ms': last_duration_ms,
        })

    return out

# ################################################################################################################################

def set_connection_last_run(req:'any_', items:'anylist') -> 'None':
    """ Sets the Last run fields of each connection list item to the latest run among its schedules.
    """
    schedule_lists = []
    for item in items:
        schedules = get_schedules(item)
        schedule_lists.append(schedules)

    last_run_list = get_connection_last_run_list(req, schedule_lists)

    for item, last_run in zip(items, last_run_list):
        item.update(last_run)

# ################################################################################################################################

def get_connection_command_shell_url(req:'any_', transfer_type:'str', conn_id:'str', conn_name:'str',
    schedules:'dictlist') -> 'str':
    """ Returns the URL of a connection's command shell. With exactly one schedule, the shell opens
    with ls of that schedule's directory and pattern, otherwise with its default command.
    """
    schedule_count = len(schedules)
    has_single_schedule = schedule_count == 1

    if has_single_schedule:
        command = _shell_command(schedules[0])
    else:
        command = ''

    name_slug = slugify(conn_name)

    out = _command_shell_url(transfer_type, conn_id, req.zato.cluster_id, name_slug, conn_name, command)
    return out

# ################################################################################################################################

def _get_connection_list(req:'any_', transfer_type:'str', cluster_id:'str') -> 'dictlist':
    """ Returns every connection of the given transfer type along with the URL of its own schedule list.
    """
    response = req.zato.client.invoke('zato.generic.connection.get-list', {
        'cluster_id': req.zato.cluster_id,
        'type_': _connection_types[transfer_type],
        'paginate': False,
    })

    if not response.ok:
        raise Exception(response.details)

    out:'dictlist' = []

    for item in response.data:
        item_id = item['id']
        item_name = item['name']
        item_slug = slugify(item_name)
        item_url = reverse('out-file-transfer-schedules', args=[transfer_type, item_id, cluster_id, item_slug])
        item_name_encoded = quote(item_name)
        out.append({
            'name': item_name,
            'url': f'{item_url}?name={item_name_encoded}',
        })

    return out

# ################################################################################################################################

def _interval_response(run_every:'int', run_unit:'str') -> 'stranydict':
    """ Returns how a schedule's interval reads along with the count and unit it is stored as.
    """
    interval_fields = interval_from_unit(run_every, run_unit)
    interval = interval_text(**interval_fields)

    out = {
        'interval': interval,
        'run_every': run_every,
        'run_unit': run_unit,
    }
    return out

# ################################################################################################################################

def _shell_escape(path:'str') -> 'str':
    """ Returns a path in the shape a command shell's ls globs it, e.g. /my dir/*.csv becomes /my\\ dir/*.csv.
    """
    out = path
    for char in _shell_escaped_chars:
        out = out.replace(char, '\\' + char)
    return out

# ################################################################################################################################

def _shell_command(schedule:'stranydict') -> 'str':
    """ The command a shell opened for a schedule starts with - ls of the schedule's directory and pattern,
    e.g. /incoming/invoices/ and orders_*.csv give ls /incoming/invoices/orders_*.csv.
    """
    directory = schedule['directory'].rstrip('/')
    pattern = schedule['pattern']

    path = f'{directory}/{pattern}'
    escaped_path = _shell_escape(path)

    out = 'ls ' + escaped_path
    return out

# ################################################################################################################################

def _command_shell_url(transfer_type:'str', conn_id:'str', cluster_id:'str', name_slug:'str', conn_name:'str',
    command:'str') -> 'str':
    """ The URL of the connection's command shell, opening with the given command typed in - or, if there is none,
    with the shell's own default.
    """
    url_name = _command_shell_links[transfer_type]
    url = reverse(url_name, args=[conn_id, cluster_id, name_slug])

    query = {'name': conn_name}
    if command:
        query['command'] = command

    query_string = urlencode(query)

    out = f'{url}?{query_string}'
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def schedules(req:'any_', transfer_type:'str', conn_id:'str', cluster_id:'str', name_slug:'str') -> 'TemplateResponse':
    """ The list of file transfer schedules of one SFTP, SMB or FTP connection.
    """
    conn_name = req.GET['name']
    items = []

    # Only the types that have a command shell get a column linking each schedule to it.
    has_command_shell = transfer_type in _command_shell_links

    for schedule in get_schedules_by_conn_id(req, conn_id):

        # The Last run cells are keyed by the scheduler job that runs the schedule.
        job_id = str(schedule['job_id'])

        item = {
            'id': schedule['id'],
            'name': schedule['name'],
            'is_active': schedule['is_active'],
            'directory': schedule['directory'],
            'pattern': schedule['pattern'],
            'service': schedule['service'],
            'job_id': job_id,
        }

        interval_response = _interval_response(schedule['run_every'], schedule['run_unit'])
        item.update(interval_response)

        if has_command_shell:
            command = _shell_command(schedule)
            item['command_shell_url'] = _command_shell_url(
                transfer_type, conn_id, cluster_id, name_slug, conn_name, command)

        items.append(item)

    # One call covers the last run times of every schedule on the page ..
    job_id_list = []
    for item in items:
        job_id_list.append(item['job_id'])

    last_run_by_id = get_last_run_by_id(req, job_id_list)

    # .. and a schedule whose job has not run yet has nothing to show.
    for item in items:
        if last_run := last_run_by_id.get(item['job_id']):
            item['last_run_utc'] = last_run['last_run_utc']
            item['last_duration_ms'] = last_run['last_duration_ms']
        else:
            item['last_run_utc'] = default_last_run_utc
            item['last_duration_ms'] = default_last_duration_ms

    # The link back to the connection list of the right type
    back_url_name, back_type = _back_links[transfer_type]
    back_url = reverse(back_url_name) + '?cluster={}&type_={}'.format(req.zato.cluster_id, back_type)

    # Every connection of this type, so the page's select can switch to any of them
    connection_list = _get_connection_list(req, transfer_type, cluster_id)

    # How the page's badge reads, e.g. SFTP schedules or SMB schedules
    badge_label = _transfer_labels[transfer_type] + ' schedules'

    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'req': req,
        'transfer_type': transfer_type,
        'conn_id': conn_id,
        'name_slug': name_slug,
        'conn_name': conn_name,
        'connection_list': connection_list,
        'badge_label': badge_label,
        'back_url': back_url,
        'has_command_shell': has_command_shell,

        'interval_units': _scheduler.UnitList,
        'items': items,
    }

    out = TemplateResponse(req, _schedules_template, return_data)
    return out

# ################################################################################################################################

@method_allowed('POST')
def schedule_name_exists(req:'any_') -> 'HttpResponse':
    """ Says whether a schedule of the given name already exists under a connection - schedules live
    with their connection rather than in a table of their own, which is why the shared check cannot see them.
    """
    value = req.POST['value']
    conn_id = req.POST['conn_id']
    schedule_id = req.POST['schedule_id']

    # Look the name up among the connection's schedules ..
    exists = False

    for schedule in get_schedules_by_conn_id(req, conn_id):

        # .. the schedule being edited keeps its own name ..
        if schedule_id:
            if schedule['id'] == schedule_id:
                continue

        # .. and any other schedule of the same name means the name is taken.
        if schedule['name'] == value:
            exists = True
            break

    out = HttpResponse(dumps({'exists': exists}), content_type='application/json')
    return out

# ################################################################################################################################

def _wizard_response(
    req,           # type: any_
    transfer_type, # type: str
    conn_id,       # type: str
    name_slug,     # type: str
    form,          # type: CreateForm
    is_edit,       # type: bool
    schedule_id,   # type: str
    ) -> 'TemplateResponse':
    """ Renders the schedule wizard - the same template serves both the create and the edit flow.
    """
    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'req': req,
        'transfer_type': transfer_type,
        'conn_id': conn_id,
        'name_slug': name_slug,
        'conn_name': req.GET['name'],
        'transfer_label': _transfer_labels[transfer_type],
        'form': form,
        'is_edit': is_edit,
        'schedule_id': schedule_id,
    }

    # The date-time picker needs the user profile's formats.
    return_data.update(get_js_dt_format(req.zato.user_profile))

    out = TemplateResponse(req, _wizard_template, return_data)
    return out

# ################################################################################################################################

@method_allowed('GET')
def schedule_wizard_create(req:'any_', transfer_type:'str', conn_id:'str', cluster_id:'str',
    name_slug:'str') -> 'TemplateResponse':
    """ A multi-step wizard for a new file transfer schedule of one SFTP, SMB or FTP connection.
    """
    form = CreateForm(req=req)

    # The first run starts an hour from now, in the user's own timezone and format.
    form.fields['start_date'].initial = get_sample_dt(req.zato.user_profile)

    out = _wizard_response(req, transfer_type, conn_id, name_slug, form, False, '')
    return out

# ################################################################################################################################

@method_allowed('GET')
def schedule_wizard_edit(req:'any_', transfer_type:'str', conn_id:'str', cluster_id:'str', name_slug:'str',
    schedule_id:'str') -> 'TemplateResponse':
    """ The schedule wizard prefilled with one existing schedule of an SFTP, SMB or FTP connection.
    """

    # Find the schedule being edited ..
    for schedule in get_schedules_by_conn_id(req, conn_id):
        if schedule['id'] == schedule_id:
            break
    else:
        raise Exception(f'Schedule `{schedule_id}` not found')

    # .. and preset each form field with what is stored.
    form = CreateForm(req=req)

    form.fields['name'].initial = schedule['name']
    form.fields['is_active'].initial = schedule['is_active']
    form.fields['directory'].initial = schedule['directory']
    form.fields['pattern'].initial = schedule['pattern']
    form.fields['ready_how'].initial = schedule['ready_how']
    form.fields['stability_delay'].initial = schedule['stability_delay']
    form.fields['marker_suffix'].initial = schedule['marker_suffix']
    form.fields['should_claim'].initial = schedule['should_claim']
    form.fields['scheduler_service'].initial = schedule['service']
    form.fields['on_success'].initial = schedule['on_success']
    form.fields['move_directory'].initial = schedule['move_directory']
    form.fields['run_every'].initial = schedule['run_every']
    form.fields['run_unit'].initial = schedule['run_unit']

    for field in _schedule_form_fields:
        form.fields[field].initial = schedule[field]

    # The start date is stored in UTC and edited in the user's own timezone and format.
    form.fields['start_date'].initial = from_utc_to_user(schedule['start_date'] + '+00:00', req.zato.user_profile)

    out = _wizard_response(req, transfer_type, conn_id, name_slug, form, True, schedule_id)
    return out

# ################################################################################################################################

def _schedule_request_from_post(req:'any_') -> 'stranydict':
    """ Maps the wizard's form fields to the input of the schedule create and edit services.
    """

    # The start date is entered in the user's own timezone and format and it is stored in UTC
    start_date = from_user_to_utc(req.POST['start_date'], req.zato.user_profile).isoformat()

    out = {
        'cluster_id': req.zato.cluster_id,
        'conn_id': req.POST['conn_id'],
        'name': req.POST['name'],
        'is_active': bool(req.POST.get('is_active')),
        'directory': req.POST['directory'],
        'pattern': req.POST['pattern'],
        'ready_how': req.POST['ready_how'],
        'stability_delay': req.POST['stability_delay'],
        'marker_suffix': req.POST['marker_suffix'],
        'should_claim': bool(req.POST.get('should_claim')),
        'service': req.POST['scheduler_service'],
        'on_success': req.POST['on_success'],
        'move_directory': req.POST['move_directory'],
        'run_every': req.POST['run_every'],
        'run_unit': req.POST['run_unit'],
        'start_date': start_date,
        'arrival_window': req.POST['arrival_window'],
        'max_attempts': req.POST['max_attempts'],
        'retry_backoff': req.POST['retry_backoff'],
        'quarantine_directory': req.POST['quarantine_directory'],
        'expected_files': req.POST['expected_files'],
        'expected_by': req.POST['expected_by'],
        'expected_days': req.POST['expected_days'],
    }

    return out

# ################################################################################################################################

def _schedule_action(req:'any_', service_name:'str', request:'stranydict') -> 'HttpResponse':
    """ Invokes one of the schedule services on the wizard's behalf, returning JSON the wizard understands.
    """
    try:
        response = req.zato.client.invoke(service_name, request)

        if response.ok:
            out = HttpResponse(dumps(response.data), content_type='application/javascript')
            return out
        else:
            raise Exception(response.details)

    except Exception:
        message = 'Caught an exception, e:`{}`'.format(format_exc())
        logger.error(message)

        # The stubs expect bytes here even though a string would work at runtime too
        out = HttpResponseServerError(message.encode('utf8'))
        return out

# ################################################################################################################################

@method_allowed('POST')
def schedule_create_action(req:'any_') -> 'HttpResponse':
    """ Creates a new file transfer schedule from what the wizard posted.
    """
    request = _schedule_request_from_post(req)

    out = _schedule_action(req, 'zato.outgoing.file-transfer.schedule.create', request)
    return out

# ################################################################################################################################

@method_allowed('POST')
def schedule_edit_action(req:'any_') -> 'HttpResponse':
    """ Updates an existing file transfer schedule from what the wizard posted.
    """
    request = _schedule_request_from_post(req)
    request['id'] = req.POST['id']

    out = _schedule_action(req, 'zato.outgoing.file-transfer.schedule.edit', request)
    return out

# ################################################################################################################################

@method_allowed('POST')
def schedule_edit_interval_action(req:'any_') -> 'HttpResponse':
    """ Changes the interval of one schedule, leaving everything else as stored.
    """
    conn_id = req.POST['conn_id']
    schedule_id = req.POST['id']

    # The popover's number field posts the count as a string.
    run_every = int(req.POST['run_every'])
    run_unit = req.POST['run_unit']

    # Find the schedule being edited ..
    for schedule in get_schedules_by_conn_id(req, conn_id):
        if schedule['id'] == schedule_id:
            break
    else:
        raise Exception(f'Schedule `{schedule_id}` not found')

    # .. and hand the edit service everything it stores, with only the interval changed.
    request = {
        'cluster_id': req.zato.cluster_id,
        'conn_id': conn_id,
        'id': schedule_id,
        'run_every': run_every,
        'run_unit': run_unit,
    }

    for field in _schedule_stored_fields:
        request[field] = schedule[field]

    response = _schedule_action(req, 'zato.outgoing.file-transfer.schedule.edit', request)

    # Anything but success is the error page the other schedule actions return.
    if response.status_code != OK:
        return response

    interval_response = _interval_response(run_every, run_unit)
    body = dumps(interval_response)

    out = HttpResponse(body, content_type='application/json')
    return out

# ################################################################################################################################

@method_allowed('POST')
def schedule_delete_action(req:'any_') -> 'HttpResponse':
    """ Deletes a file transfer schedule along with its scheduler job.
    """
    request = {
        'cluster_id': req.zato.cluster_id,
        'conn_id': req.POST['conn_id'],
        'id': req.POST['id'],
    }

    out = _schedule_action(req, 'zato.outgoing.file-transfer.schedule.delete', request)
    return out

# ################################################################################################################################
# ################################################################################################################################
