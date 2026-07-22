# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.outgoing.file_transfer_schedule import CreateForm
from zato.admin.web.views import get_js_dt_format, get_sample_dt, method_allowed
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# .. the per-connection list of schedules ..
_schedules_template = 'zato/outgoing/file-transfer-schedules.html'

# .. and the multi-step wizard that creates a new one.
_wizard_template = 'zato/outgoing/file-transfer-schedule-wizard.html'

# UI preview data - the real list will come from the schedules stored
# with the connection once the backend services exist.
_preview_schedules = [
    {
        'name': 'invoices.hourly',
        'is_active': True,
        'directory': '/incoming/invoices',
        'pattern': '*.csv',
        'ready': 'When it stops changing',
        'service': 'invoices.process-incoming-file',
        'run_every': 'Every 5 minutes',
    },
    {
        'name': 'orders.nightly',
        'is_active': True,
        'directory': '/incoming/orders',
        'pattern': 'order-*.xml',
        'ready': 'Marker file with the .done suffix',
        'service': 'orders.import-from-file',
        'run_every': 'Every 1 day',
    },
    {
        'name': 'reports.archive',
        'is_active': False,
        'directory': '/incoming/reports',
        'pattern': 'report-*.zip',
        'ready': 'When it stops changing',
        'service': 'reports.ingest-feed',
        'run_every': 'Every 2 hours',
    },
]

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def sftp_schedules(req:'any_', conn_id:'str', cluster_id:'str', name_slug:'str') -> 'TemplateResponse':
    """ The list of file transfer schedules of one SFTP connection.
    """
    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'req': req,
        'conn_id': conn_id,
        'name_slug': name_slug,
        'conn_name': req.GET['name'],
        'transfer_label': 'SFTP',
        'items': _preview_schedules,
    }

    out = TemplateResponse(req, _schedules_template, return_data)
    return out

# ################################################################################################################################

@method_allowed('GET')
def sftp_schedule_wizard_create(req:'any_', conn_id:'str', cluster_id:'str', name_slug:'str') -> 'TemplateResponse':
    """ A multi-step wizard for a new file transfer schedule of one SFTP connection.
    """
    form = CreateForm(req=req)

    # The first run starts an hour from now, in the user's own timezone and format.
    form.fields['start_date'].initial = get_sample_dt(req.zato.user_profile)

    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'req': req,
        'conn_id': conn_id,
        'name_slug': name_slug,
        'conn_name': req.GET['name'],
        'transfer_label': 'SFTP',
        'form': form,
    }

    # The date-time picker needs the user profile's formats.
    return_data.update(get_js_dt_format(req.zato.user_profile))

    out = TemplateResponse(req, _wizard_template, return_data)
    return out

# ################################################################################################################################

@method_allowed('POST')
def sftp_schedule_create_action(req:'any_') -> 'HttpResponse':
    """ UI preview stub - accepts the wizard's form and pretends the schedule was created.
    The real implementation will store the schedule with the connection and sync its scheduler job.
    """
    out = HttpResponse(dumps({'id': req.POST['name'], 'message': 'OK'}), content_type='application/javascript')
    return out

# ################################################################################################################################
# ################################################################################################################################
