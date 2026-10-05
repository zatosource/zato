# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Bulk exports page of one outgoing FHIR connection - its recent jobs, read from the audit log, and a way to start one.

# stdlib
from datetime import datetime, timezone
from logging import getLogger
from traceback import format_exc
from urllib.parse import quote

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse
from django.urls import reverse

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import method_allowed
from zato.common.api import GENERIC, HL7
from zato.common.audit_log.api import AuditSource
from zato.common.audit_log.bulk_export import get_job_list
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist, stranydict
    any_ = any_
    dictlist = dictlist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_bulk = HL7.BulkExport
_template = 'zato/outgoing/hl7/fhir-bulk-export.html'
_url_name = 'outgoing-hl7-fhir-bulk-export'
_run_url_name = 'outgoing-hl7-fhir-bulk-export-run'

# What a job that has not finished shows in its Finished column
_not_finished_label = ''

# How each status reads in the table
_status_labels = {
    _bulk.Status.Running: 'Running',
    _bulk.Status.Done: 'Done',
    _bulk.Status.Failed: 'Failed',
}

# ################################################################################################################################
# ################################################################################################################################

def _format_time(value_iso:'str', user_profile:'any_') -> 'str':
    """ An audit timestamp in the user's timezone and format, or an empty string if there is none.
    """
    if not value_iso:
        return _not_finished_label

    value = datetime.fromisoformat(value_iso)

    # The audit log writes UTC timestamps, with or without an offset of their own
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    out = from_utc_to_user(value, user_profile)
    return out

# ################################################################################################################################

def _get_connection_list(req:'any_', cluster_id:'str') -> 'dictlist':
    """ Every outgoing FHIR connection along with the URL of its own Bulk exports page.
    """
    response = req.zato.client.invoke('zato.generic.connection.get-list', {
        'cluster_id': req.zato.cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR,
        'paginate': False,
    })

    if not response.ok:
        raise Exception(response.details)

    out:'dictlist' = []

    for item in response.data:
        item_id = item['id']
        item_url = reverse(_url_name, args=[item_id, cluster_id])
        out.append({
            'id': str(item_id),
            'name': item['name'],
            'url': item_url,
        })

    return out

# ################################################################################################################################

def _build_item(job:'stranydict', conn_name:'str', cluster_id:'str', user_profile:'any_') -> 'stranydict':
    """ One row of the page - a job with its times formatted and its audit log link built.
    """
    conn_name_encoded = quote(conn_name)
    job_id = job['job_id']

    audit_log_url = '/zato/audit-log/?source={}&object_name={}&query={}&cluster={}'.format(
        AuditSource.FHIR_Bulk_Export, conn_name_encoded, job_id, cluster_id)

    out:'stranydict' = {
        'job_id': job_id,
        'started': _format_time(job['started_iso'], user_profile),
        'finished': _format_time(job['finished_iso'], user_profile),
        'status': _status_labels[job['status']],
        'phase': job['phase'],
        'files': job['files'],
        'resources': job['resources'],
        'errors': job['errors'],
        'error': job['error'],
        'audit_log_url': audit_log_url,
    }

    return out

# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_', conn_id:'str', cluster_id:'str') -> 'TemplateResponse':
    """ The recent bulk export jobs of one outgoing FHIR connection.
    """
    connection_list = _get_connection_list(req, cluster_id)

    for connection in connection_list:
        if connection['id'] == conn_id:
            conn_name = connection['name']
            break
    else:
        conn_name = ''

    items = []

    if conn_name:
        for job in get_job_list(conn_name):
            item = _build_item(job, conn_name, cluster_id, req.zato.user_profile)
            items.append(item)

    back_url = reverse('outgoing-hl7-fhir') + '?cluster={}'.format(req.zato.cluster_id)
    run_url = reverse(_run_url_name, args=[conn_id, cluster_id])
    conn_name_encoded = quote(conn_name)

    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'req': req,
        'conn_id': conn_id,
        'conn_name': conn_name,
        'conn_name_encoded': conn_name_encoded,
        'connection_list': connection_list,
        'back_url': back_url,
        'run_url': run_url,
        'audit_source': AuditSource.FHIR_Bulk_Export,
        'items': items,
    }

    out = TemplateResponse(req, _template, return_data)
    return out

# ################################################################################################################################

@method_allowed('POST')
def run(req:'any_', conn_id:'str', cluster_id:'str') -> 'HttpResponse':
    """ Starts a bulk export of the connection named in the request, answering with the job's id.
    """
    conn_name = req.POST['conn_name']

    try:
        response = req.zato.client.invoke(_bulk.Dispatch_Service, {'conn_name': conn_name})

        if response.ok:
            out = HttpResponse(dumps(response.data), content_type='application/javascript')
            return out
        else:
            raise Exception(response.details)

    except Exception:
        message = 'Bulk export could not be started, conn_name:`{}`, e:`{}`'.format(conn_name, format_exc())
        logger.error(message)

        out = HttpResponseServerError(message.encode('utf8'))
        return out

# ################################################################################################################################
# ################################################################################################################################
