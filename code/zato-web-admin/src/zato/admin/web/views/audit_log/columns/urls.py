# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.common import AuditSource
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

# Where each source's own main page is - what the source's name in the detail pane
# leads to. A source with no page of its own is not here and its name stays text.
_source_page_url = {
    AuditSource.Scheduler: f'/zato/scheduler/dashboard/?cluster={default_cluster_id}&range=0',
    AuditSource.REST_Channel: f'/zato/http-soap/?cluster={default_cluster_id}&connection=channel&transport=plain_http',
    AuditSource.SOAP_Channel: f'/zato/http-soap/?cluster={default_cluster_id}&connection=channel&transport=soap',
    AuditSource.REST_Outgoing: f'/zato/http-soap/?cluster={default_cluster_id}&connection=outgoing&transport=plain_http',
    AuditSource.SOAP_Outgoing: f'/zato/http-soap/?cluster={default_cluster_id}&connection=outgoing&transport=soap',

    # A check's object is the connection it watches, so both lead where the connection is.
    AuditSource.REST_Outgoing_Health:
        f'/zato/http-soap/?cluster={default_cluster_id}&connection=outgoing&transport=plain_http',
    AuditSource.SOAP_Outgoing_Health: f'/zato/http-soap/?cluster={default_cluster_id}&connection=outgoing&transport=soap',

    AuditSource.MLLP_Channel: f'/zato/channel/hl7/mllp/?cluster={default_cluster_id}',
    AuditSource.MLLP_Outgoing: f'/zato/outgoing/hl7/mllp/?cluster={default_cluster_id}',
    AuditSource.FHIR: f'/zato/outgoing/hl7/fhir/?cluster={default_cluster_id}',
    AuditSource.SQL_Outgoing: f'/zato/outgoing/sql/?cluster={default_cluster_id}',
    AuditSource.Email_IMAP: f'/zato/email/imap/?cluster={default_cluster_id}',
    AuditSource.Email_SMTP: f'/zato/email/smtp/?cluster={default_cluster_id}',
    AuditSource.PubSub: f'/zato/pubsub/topic/?cluster={default_cluster_id}',
    AuditSource.File_Outgoing: f'/zato/outgoing/sftp/?cluster={default_cluster_id}&type_=outconn-sftp',
    AuditSource.LLM: f'/zato/outgoing/llm/?cluster={default_cluster_id}&type_=outconn-llm',
    AuditSource.Odoo: f'/zato/outgoing/odoo/?cluster={default_cluster_id}',
    AuditSource.Microsoft_Cloud: f'/zato/cloud/microsoft-365/?cluster={default_cluster_id}',

    # A test transfer's object is the file transfer connection it exercises.
    AuditSource.Test_Transfer: f'/zato/outgoing/sftp/?cluster={default_cluster_id}&type_=outconn-sftp',
}

# Where one object's own page is - the source's page opened on that object.
# `{name}` is filled in with the object's name on the frontend.
_object_page_url = {}

for _source, _url in _source_page_url.items():
    _object_page_url[_source] = f'{_url}&query={{name}}'

# A scheduler job's own page is the scheduler listing filtered down to it.
_object_page_url[AuditSource.Scheduler] = f'/zato/scheduler/?cluster={default_cluster_id}&query={{name}}'

# Where what a source writes into an event's endpoint leads - only the sources
# that record a service are here, because only a service has a page of its own.
_endpoint_page_url = {
    AuditSource.REST_Channel: f'/zato/service/?cluster={default_cluster_id}&query={{name}}',
    AuditSource.SOAP_Channel: f'/zato/service/?cluster={default_cluster_id}&query={{name}}',
    AuditSource.Scheduler: f'/zato/service/?cluster={default_cluster_id}&query={{name}}',
}

# Where one run of a scheduled job has its own page - `{job_id}` and `{run}` are
# filled in on the frontend out of the event's own attrs.
_run_page_url = {
    AuditSource.Scheduler:
        f'/zato/scheduler/dashboard/job/{{job_id}}/run/{{run}}/?cluster={default_cluster_id}&range=0&outcomes=all',
}

# ################################################################################################################################
# ################################################################################################################################
