# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.common import AuditSource

# ################################################################################################################################
# ################################################################################################################################

# Where each source's own main page is - what the source's name in the detail pane
# leads to. A source with no page of its own is not here and its name stays text.
_source_page_url = {
    AuditSource.Scheduler: '/zato/scheduler/dashboard/?range=0',
    AuditSource.Service: '/zato/service/',
    AuditSource.REST_Channel: '/zato/http-soap/?connection=channel&transport=plain_http',
    AuditSource.SOAP_Channel: '/zato/http-soap/?connection=channel&transport=soap',
    AuditSource.REST_Outgoing: '/zato/http-soap/?connection=outgoing&transport=plain_http',
    AuditSource.SOAP_Outgoing: '/zato/http-soap/?connection=outgoing&transport=soap',

    # A check's object is the connection it watches, so both lead where the connection is.
    AuditSource.REST_Outgoing_Health:
        '/zato/http-soap/?connection=outgoing&transport=plain_http',
    AuditSource.SOAP_Outgoing_Health: '/zato/http-soap/?connection=outgoing&transport=soap',
    AuditSource.FHIR_Health: '/zato/outgoing/hl7/fhir/',
    AuditSource.Email_SMTP_Health: '/zato/email/smtp/',

    AuditSource.MLLP_Channel: '/zato/channel/hl7/mllp/',
    AuditSource.MLLP_Outgoing: '/zato/outgoing/hl7/mllp/',
    AuditSource.FHIR: '/zato/outgoing/hl7/fhir/',
    AuditSource.CCDA: '/zato/channel/hl7/rest/',
    AuditSource.SQL_Outgoing: '/zato/outgoing/sql/',
    AuditSource.Email_IMAP: '/zato/email/imap/',
    AuditSource.Email_SMTP: '/zato/email/smtp/',
    AuditSource.PubSub: '/zato/pubsub/topic/',
    AuditSource.File_Outgoing: '/zato/outgoing/sftp/?type_=outconn-sftp',
    AuditSource.LLM: '/zato/outgoing/llm/?type_=outconn-llm',
    AuditSource.Odoo: '/zato/outgoing/odoo/',
    AuditSource.Microsoft_Cloud: '/zato/cloud/microsoft-365/',

    # A test transfer's object is the file transfer connection it exercises.
    AuditSource.Test_Transfer: '/zato/outgoing/sftp/?type_=outconn-sftp',
}

# Where one object's own page is - the source's page opened on that object.
# `{name}` is filled in with the object's name on the frontend.
_object_page_url = {}

for _source, _url in _source_page_url.items():

    # A page with a query string of its own takes the object's name as one more parameter ..
    if '?' in _url:
        _separator = '&'

    # .. and a page without one opens its query string with it.
    else:
        _separator = '?'

    _object_page_url[_source] = f'{_url}{_separator}query={{name}}'

# A scheduler job's own page is the scheduler listing filtered down to it.
_object_page_url[AuditSource.Scheduler] = '/zato/scheduler/?query={name}'

# Where what a source writes into an event's endpoint leads - only the sources
# that record a service are here, because only a service has a page of its own.
_endpoint_page_url = {
    AuditSource.REST_Channel: '/zato/service/?query={name}',
    AuditSource.SOAP_Channel: '/zato/service/?query={name}',
    AuditSource.Scheduler: '/zato/service/?query={name}',
}

# Where one run has its own page - `{job_id}`, `{run}` and `{cid}` are filled in on the
# frontend out of the event itself. A scheduled job's run is a page of the scheduler dashboard,
# a file transfer run is its own flow - the scheduler that fired it is plumbing there.
_run_page_url = {
    AuditSource.Scheduler:
        '/zato/scheduler/dashboard/job/{job_id}/run/{run}/?range=0&outcomes=all',
    AuditSource.File_Outgoing: '/zato/message-flow/?term={cid}',
}

# ################################################################################################################################
# ################################################################################################################################
