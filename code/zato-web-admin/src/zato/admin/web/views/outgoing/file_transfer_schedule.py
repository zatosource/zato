# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse
from django.urls import reverse

# Zato
from zato.admin.web import from_user_to_utc, from_utc_to_user
from zato.admin.web.forms.outgoing.file_transfer_schedule import CreateForm
from zato.admin.web.views import get_js_dt_format, get_sample_dt, method_allowed
from zato.common.api import FileTransfer
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_scheduler = FileTransfer.Scheduler

# .. the per-connection list of schedules ..
_schedules_template = 'zato/outgoing/file-transfer-schedules.html'

# .. and the multi-step wizard that creates or edits one.
_wizard_template = 'zato/outgoing/file-transfer-schedule-wizard.html'

# How each connection type reads on screen
_transfer_labels = {
    'sftp': 'SFTP',
    'smb': 'SMB',
}

# Where the back-to-the-connections link of each type points to
_back_links = {
    'sftp': ('out-sftp', 'outconn-sftp'),
    'smb': ('out-smb', 'outconn-smb'),
}

# ################################################################################################################################
# ################################################################################################################################

def _get_schedule_list(req:'any_', conn_id:'str') -> 'any_':
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

def _ready_how_human(schedule:'stranydict') -> 'str':
    """ How a schedule's readiness mode reads on the list, e.g. Marker file with the .done suffix.
    """
    if schedule['ready_how'] == _scheduler.ReadyHow.Marker:
        out = 'Marker file with the {} suffix'.format(schedule['marker_suffix'])
    else:
        out = _scheduler.ReadyHowHuman[_scheduler.ReadyHow.Stability]

    return out

# ################################################################################################################################

def _run_every_human(schedule:'stranydict') -> 'str':
    """ How a schedule's interval reads on the list, e.g. Every 5 minutes or Every 1 day.
    """
    run_every = schedule['run_every']
    run_unit = schedule['run_unit']

    # One hour reads better than one hours
    if run_every == 1:
        run_unit = run_unit.rstrip('s')

    out = f'Every {run_every} {run_unit}'
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def schedules(req:'any_', transfer_type:'str', conn_id:'str', cluster_id:'str', name_slug:'str') -> 'TemplateResponse':
    """ The list of file transfer schedules of one SFTP or SMB connection.
    """
    items = []

    for schedule in _get_schedule_list(req, conn_id):
        items.append({
            'id': schedule['id'],
            'name': schedule['name'],
            'is_active': schedule['is_active'],
            'directory': schedule['directory'],
            'pattern': schedule['pattern'],
            'ready': _ready_how_human(schedule),
            'service': schedule['service'],
            'run_every': _run_every_human(schedule),
        })

    # The link back to the connection list of the right type
    back_url_name, back_type = _back_links[transfer_type]
    back_url = reverse(back_url_name) + '?cluster={}&type_={}'.format(req.zato.cluster_id, back_type)

    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'req': req,
        'transfer_type': transfer_type,
        'conn_id': conn_id,
        'name_slug': name_slug,
        'conn_name': req.GET['name'],
        'transfer_label': _transfer_labels[transfer_type],
        'back_url': back_url,
        'items': items,
    }

    out = TemplateResponse(req, _schedules_template, return_data)
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
    """ A multi-step wizard for a new file transfer schedule of one SFTP or SMB connection.
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
    """ The schedule wizard prefilled with one existing schedule of an SFTP or SMB connection.
    """

    # Find the schedule being edited ..
    for schedule in _get_schedule_list(req, conn_id):
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
