# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic
from traceback import format_exc

# Zato
from zato.common.api import HL7, HTTP_SOAP
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.destination.constants import DestinationType
from zato.common.destination.model import parse_entries
from zato.common.exception import BadRequest
from zato.common.hl7.fhir.bulk_export.file import BulkExportFile, BulkExportResource
from zato.server.destination.dispatch import send as dispatch_send
from zato.server.hl7.fhir.bulk_export import build_job_spec, start_job
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.destination.model import DestinationEntry
    from zato.common.typing_ import any_, stranydict, strlist

    DestinationEntry = DestinationEntry
    any_             = any_
    stranydict       = stranydict
    strlist          = strlist

# ################################################################################################################################
# ################################################################################################################################

_bulk = HL7.BulkExport
_health_check = HTTP_SOAP.HealthCheck

# The destinations that receive a whole file at once rather than one resource at a time
_whole_file_types = (DestinationType.SFTP, DestinationType.SERVICE)

# How many resources of one file one destination refusing them may be reported before the rest is counted only
_max_reported_errors = 5

# ################################################################################################################################
# ################################################################################################################################

class Run(AdminService):
    """ Starts a bulk export of an outgoing FHIR connection - on the connection's schedule, from the Dashboard
    or from a service through client.export(), and returns the id of the job started.
    """
    name = _bulk.Dispatch_Service
    input = '-conn_name', '-level', '-group_id', '-patient_ids', '-types', '-since', '-type_filter', '-destinations'
    output = 'job_id'

    def handle(self) -> 'None':

        # The scheduler job carries the connection's identity in its extra data, everything else names it on input
        if self.request.input.conn_name:
            conn_name = self.request.input.conn_name
        else:
            conn_name = self.request.payload[_health_check.Extra_Conn_Name]

        overrides = {}
        for name in _bulk.OverrideFieldList:
            value = self.request.input.get(name)
            if value:
                overrides[name] = value

        item = self._config_manager.outconn_hl7_fhir.get(conn_name)
        if not item:
            raise BadRequest(self.cid, f'No such outgoing FHIR connection `{conn_name}`')

        conn_config = item['config']

        # A schedule of a tab that was switched off runs nothing, an export asked for by name always runs
        if not overrides and not conn_config[_bulk.Field_Is_Active]:
            raise BadRequest(self.cid, f'Bulk export of `{conn_name}` is not active')

        spec = build_job_spec(self.server, conn_config, overrides)
        job_id = start_job(self.server, spec)

        self.response.payload.job_id = job_id

# ################################################################################################################################
# ################################################################################################################################

class Deliver(AdminService):
    """ Hands one downloaded file of a bulk export to each destination of its connection, in order -
    a whole file at a time to SFTP and services, one resource at a time to Kafka and FHIR.
    """
    name = _bulk.Deliver_Service
    input = 'conn_name', 'file', '-destinations'
    output = 'is_ok', 'error'

    def handle(self) -> 'None':

        conn_name = self.request.input.conn_name
        file = BulkExportFile.from_dict(self.request.input.file)

        item = self._config_manager.outconn_hl7_fhir.get(conn_name)
        if not item:
            raise BadRequest(self.cid, f'No such outgoing FHIR connection `{conn_name}`')

        # A job started with destinations of its own delivers to them, any other to the connection's
        destinations = self.request.input.destinations
        if not destinations:
            destinations = item['config'][_bulk.Field_Destinations]

        entries = parse_entries(destinations)

        audit_log = AuditLog(self.server.name)
        errors:'strlist' = []

        # Every destination is attempted, whatever became of the one before it
        for entry in entries:

            if not entry.is_active:
                continue

            started = monotonic()
            error = self.deliver_to_entry(entry, file)
            duration_ms = int((monotonic() - started) * 1000)

            if error:
                errors.append(f'{entry.name} -> {error}')
                event_type = AuditEvent.Delivery_Failed
                outcome = AuditOutcome.Error
            else:
                event_type = AuditEvent.Delivered
                outcome = AuditOutcome.OK

            _ = audit_log.insert(
                AuditSource.FHIR_Bulk_Export,
                event_type,
                conn_name,
                cid=file.job_id,
                endpoint=entry.name,
                outcome=outcome,
                duration_ms=duration_ms,
                data=error,
                attrs={
                    'job_id': file.job_id,
                    'phase': _bulk.Phase.Deliver,
                    'resource_type': file.resource_type,
                    'file_name': file.file_name,
                    'count': str(file.count),
                },
            )

        self.response.payload.is_ok = not errors
        self.response.payload.error = '\n'.join(errors)

# ################################################################################################################################

    def deliver_to_entry(self, entry:'DestinationEntry', file:'BulkExportFile') -> 'str':
        """ Delivers one file to one destination and returns what went wrong, or an empty string.
        """
        try:
            if entry.type in _whole_file_types:
                out = self.deliver_whole_file(entry, file)
            else:
                out = self.deliver_each_resource(entry, file)

        except Exception:
            out = format_exc()

        return out

# ################################################################################################################################

    def deliver_whole_file(self, entry:'DestinationEntry', file:'BulkExportFile') -> 'str':
        result = dispatch_send(self, entry, file, self.cid)

        if result.is_rejected:
            out = result.status
        else:
            out = ''

        return out

# ################################################################################################################################

    def deliver_each_resource(self, entry:'DestinationEntry', file:'BulkExportFile') -> 'str':
        """ Sends the file one resource at a time, going on past a refused one so a single bad resource
        does not hold back the rest of the file.
        """
        errors = []
        error_count = 0

        for line in file.lines():
            resource = BulkExportResource(file, line)
            result = dispatch_send(self, entry, resource, self.cid)

            if result.is_rejected:
                error_count += 1
                if error_count <= _max_reported_errors:
                    errors.append(f'{resource.resource_id} -> {result.status}')

        if not error_count:
            return ''

        out = f'{error_count} of {file.count} resources refused: ' + ', '.join(errors)
        return out

# ################################################################################################################################
# ################################################################################################################################
