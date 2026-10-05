# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from datetime import datetime, timezone
from http.client import OK
from json import dumps, loads
from logging import basicConfig, getLogger, INFO
from shutil import rmtree
from time import monotonic
from traceback import format_exc

# requests
from requests import post as requests_post

# urllib3
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

# Zato
from zato.common.api import HL7
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import AuditEvent, AuditOutcome, AuditSource
from zato.common.const import ServiceConst
from zato.common.hl7.fhir.bulk_export.client import BulkExportClient, BulkExportError
from zato.common.hl7.fhir.bulk_export.file import new_file
from zato.common.hl7.fhir.bulk_export.pid import acquire_pid_file
from zato.common.hl7.fhir.bulk_export.spec import FileState, JobSpec, JobState

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strdict, strnone

    stranydict = stranydict
    strdict    = strdict
    strnone    = strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_bulk = HL7.BulkExport

# How a downloaded file is named - the manifest's order keeps files of one resource type apart
File_Name_Pattern = '{resource_type}.{index:04d}.ndjson'

# The keys of a manifest and of its output entries
Manifest_Transaction_Time = 'transactionTime'
Manifest_Requires_Token   = 'requiresAccessToken'
Manifest_Output           = 'output'
Manifest_Error            = 'error'
Output_Type               = 'type'
Output_URL                = 'url'
Output_Count              = 'count'

# How long the deliver service may take for one file
Deliver_Timeout = 3600

# ################################################################################################################################
# ################################################################################################################################

def utcnow_iso() -> 'str':
    out = datetime.now(tz=timezone.utc).isoformat()
    return out

# ################################################################################################################################
# ################################################################################################################################

class Program:
    """ Runs one export from kick-off to clean-up, writing its state after each step and an audit event for each.
    """
    def __init__(self, spec:'JobSpec', state:'JobState') -> 'None':
        self.spec = spec
        self.state = state
        self.job_dir = spec.job_dir
        self.client = BulkExportClient(spec, self.on_progress)
        self.audit_log = AuditLog(spec.server_name)

# ################################################################################################################################

    def audit(
        self,
        event_type:'str',
        phase:'str',
        outcome:'str',
        *,
        endpoint:'str'='',
        status:'int'=0,
        duration_ms:'int'=0,
        data:'str'='',
        resource_type:'str'='',
        file_name:'str'='',
        count:'int'=0,
        ) -> 'None':
        """ Writes one event of this job - all of them share the job's id as their cid so the job reads as one story.
        """
        attrs = {
            'job_id': self.spec.job_id,
            'phase': phase,
            'resource_type': resource_type,
            'file_name': file_name,
            'count': str(count),
        }

        if status:
            status_text = str(status)
        else:
            status_text = ''

        _ = self.audit_log.insert(
            AuditSource.FHIR_Bulk_Export,
            event_type,
            self.spec.conn_name,
            cid=self.spec.job_id,
            endpoint=endpoint,
            outcome=outcome,
            status=status_text,
            duration_ms=duration_ms,
            data=data,
            attrs=attrs,
        )

# ################################################################################################################################

    def save(self, phase:'str') -> 'None':
        self.state.phase = phase
        self.state.update_time = utcnow_iso()
        self.state.save(self.job_dir)

# ################################################################################################################################

    def on_progress(self, progress:'str', wait:'int') -> 'None':
        logger.info('Bulk export %s is in progress -> `%s`, polling again in %ss', self.spec.job_id, progress, wait)

# ################################################################################################################################

    def run(self) -> 'None':
        try:
            self.run_impl()
        except BulkExportError as e:
            self.fail(e.message, e.status)
        except Exception:
            self.fail(format_exc(), 0)

# ################################################################################################################################

    def fail(self, message:'str', status:'int') -> 'None':
        """ Records why the job stopped - its directory stays as it is so the job can be picked up again.
        """
        logger.warning('Bulk export %s failed -> %s', self.spec.job_id, message)

        self.state.failures.append(message)
        self.state.status = _bulk.Status.Failed
        self.save(_bulk.Phase.Failed)

        self.audit(AuditEvent.Run_Completed, _bulk.Phase.Failed, AuditOutcome.Error, status=status, data=message)

# ################################################################################################################################

    def run_impl(self) -> 'None':

        # A job with no status URL yet has not been kicked off ..
        if not self.state.status_url:
            self.kickoff()

        # .. one with a status URL but no manifest is still running on the server ..
        if not self.state.manifest:
            self.poll()

        # .. the files are downloaded and handed over one by one, skipping what an earlier run finished ..
        for index, file_state in enumerate(self.state.files):

            if not file_state.is_downloaded:
                self.download(index, file_state)

            if not file_state.is_delivered:
                self.deliver(file_state)

        # .. and the job is complete.
        self.cleanup()

# ################################################################################################################################

    def kickoff(self) -> 'None':
        started = monotonic()
        url = self.client.build_kickoff_url()

        try:
            status_url, status = self.client.kickoff()
        except BulkExportError as e:
            self.audit(AuditEvent.Request_Sent, _bulk.Phase.Kickoff, AuditOutcome.Error,
                endpoint=url, status=e.status, data=e.message)
            raise

        duration_ms = int((monotonic() - started) * 1000)

        self.state.status_url = status_url
        self.save(_bulk.Phase.Poll)

        self.audit(AuditEvent.Request_Sent, _bulk.Phase.Kickoff, AuditOutcome.OK,
            endpoint=url, status=status, duration_ms=duration_ms, data=dumps(self.client.build_kickoff_params()))

# ################################################################################################################################

    def poll(self) -> 'None':
        started = monotonic()

        try:
            manifest = self.client.poll(self.state.status_url)
        except BulkExportError as e:
            self.audit(AuditEvent.Response_Received, _bulk.Phase.Poll, AuditOutcome.Error,
                endpoint=self.state.status_url, status=e.status, data=e.message)
            raise

        duration_ms = int((monotonic() - started) * 1000)

        self.state.manifest = manifest
        self.state.transaction_time = manifest.get(Manifest_Transaction_Time, '')

        requires_token = manifest.get(Manifest_Requires_Token)
        if requires_token is None:
            requires_token = True
        self.state.requires_access_token = requires_token

        # The server's own files come first, then the files describing what it could not export
        self.state.files = []
        self._add_files(manifest.get(Manifest_Output, []))
        self._add_files(manifest.get(Manifest_Error, []))

        self.save(_bulk.Phase.Download)

        self.audit(AuditEvent.Response_Received, _bulk.Phase.Manifest, AuditOutcome.OK,
            endpoint=self.state.status_url, status=OK, duration_ms=duration_ms, data=dumps(manifest),
            count=len(self.state.files))

# ################################################################################################################################

    def _add_files(self, entries:'list[stranydict]') -> 'None':
        for entry in entries:
            file_state = FileState()
            file_state.resource_type = entry[Output_Type]
            file_state.url = entry[Output_URL]

            # The count is optional in the specification
            count = entry.get(Output_Count)
            if count is None:
                count = 0
            file_state.count = count

            self.state.files.append(file_state)

# ################################################################################################################################

    def download(self, index:'int', file_state:'FileState') -> 'None':
        started = monotonic()

        file_name = File_Name_Pattern.format(resource_type=file_state.resource_type, index=index)
        path = os.path.join(self.job_dir, file_name)

        try:
            lines = self.client.download(file_state.url, path, needs_auth=self.state.requires_access_token)
        except BulkExportError as e:
            self.audit(AuditEvent.Received, _bulk.Phase.Download, AuditOutcome.Error,
                endpoint=file_state.url, status=e.status, data=e.message,
                resource_type=file_state.resource_type, file_name=file_name)
            raise

        duration_ms = int((monotonic() - started) * 1000)

        # A manifest without counts tells us nothing to compare with ..
        if file_state.count and file_state.count != lines:
            data = f'Expected {file_state.count} resources in `{file_name}` but found {lines}'
            self.state.failures.append(data)
            outcome = AuditOutcome.Error
        else:
            data = ''
            outcome = AuditOutcome.OK

        # .. and the count the file actually holds is what is passed on.
        file_state.count = lines
        file_state.path = path
        file_state.is_downloaded = True
        self.save(_bulk.Phase.Download)

        self.audit(AuditEvent.Received, _bulk.Phase.Download, outcome,
            endpoint=file_state.url, status=OK, duration_ms=duration_ms, data=data,
            resource_type=file_state.resource_type, file_name=file_name, count=lines)

# ################################################################################################################################

    def deliver(self, file_state:'FileState') -> 'None':
        """ Hands one file to the server's deliver service, which sends it to each destination of the connection.
        """
        started = monotonic()

        file = new_file(
            self.spec.job_id,
            self.spec.conn_name,
            file_state.resource_type,
            file_state.count,
            file_state.path,
            file_state.url,
        )

        url = self.spec.invoke_url + ServiceConst.API_Invoke_Url_Path.format(_bulk.Deliver_Service)
        request = {
            'conn_name': self.spec.conn_name,
            'file': file.to_dict(),
            'destinations': self.spec.destinations,
        }

        response = requests_post(
            url,
            data=dumps(request),
            auth=(self.spec.invoke_username, self.spec.invoke_password),
            timeout=Deliver_Timeout,
            verify=False,
        )

        duration_ms = int((monotonic() - started) * 1000)

        # The service answers whether every destination accepted the file ..
        if response.status_code == OK:
            result = loads(response.text)
            is_ok = result['is_ok']
            error = result['error']
        else:
            is_ok = False
            error = f'{response.status_code} -> {response.text}'

        # .. a failure of any destination stops the job here so the file is tried again when the job is resumed.
        if not is_ok:
            self.audit(AuditEvent.Delivery_Failed, _bulk.Phase.Deliver, AuditOutcome.Error,
                endpoint=url, status=response.status_code, duration_ms=duration_ms, data=error,
                resource_type=file_state.resource_type, file_name=file.file_name, count=file_state.count)
            raise BulkExportError(f'Delivery of `{file.file_name}` failed -> {error}', response.status_code)

        file_state.is_delivered = True
        self.save(_bulk.Phase.Deliver)

        self.audit(AuditEvent.Delivered, _bulk.Phase.Deliver, AuditOutcome.OK,
            endpoint=url, status=response.status_code, duration_ms=duration_ms,
            resource_type=file_state.resource_type, file_name=file.file_name, count=file_state.count)

# ################################################################################################################################

    def cleanup(self) -> 'None':

        # The server is told its copy of the export can go ..
        if self.spec.delete_on_server:
            status = self.client.delete(self.state.status_url)
            self.audit(AuditEvent.Note, _bulk.Phase.Cleanup, AuditOutcome.OK, endpoint=self.state.status_url, status=status)

        # .. the job is done no matter what happens to the files now ..
        self.state.status = _bulk.Status.Done
        self.save(_bulk.Phase.Done)

        total = 0
        for file_state in self.state.files:
            total += file_state.count

        if self.state.failures:
            outcome = AuditOutcome.Error
            data = '\n'.join(self.state.failures)
        else:
            outcome = AuditOutcome.OK
            data = ''

        self.audit(AuditEvent.Run_Completed, _bulk.Phase.Done, outcome, data=data, count=total)

        # .. and the downloaded files go unless the connection keeps them.
        if self.spec.delete_files:
            rmtree(self.job_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

def load_or_create_state(spec:'JobSpec') -> 'JobState':
    """ Returns the state an earlier run of the job left behind or a fresh one for a job that starts now.
    """
    path = os.path.join(spec.job_dir, _bulk.State_File_Name)

    if os.path.exists(path):
        out = JobState.load(spec.job_dir)
        out.status = _bulk.Status.Running
        return out

    out = JobState()
    out.job_id = spec.job_id
    out.conn_id = spec.conn_id
    out.conn_name = spec.conn_name
    out.start_time = utcnow_iso()

    return out

# ################################################################################################################################

def run_job(spec:'JobSpec') -> 'JobState':
    """ Runs one job to its end in this process and returns the state it finished in.
    """
    os.makedirs(spec.job_dir, exist_ok=True)

    state = load_or_create_state(spec)
    program = Program(spec, state)
    program.run()

    return state

# ################################################################################################################################

def main() -> 'None':

    basicConfig(stream=sys.stdout, level=INFO, format='%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')

    # The server is reached by its own address, which its certificate need not name
    disable_warnings(InsecureRequestWarning)

    # The spec arrives on stdin so its secrets are never on the command line or on disk
    spec = JobSpec.from_json(sys.stdin.read())

    # The audit log database is the one the server uses
    os.environ.update(spec.audit_env)

    os.makedirs(spec.job_dir, exist_ok=True)

    if not acquire_pid_file(spec.job_dir):
        logger.info('Bulk export %s is already running, exiting', spec.job_id)
        return

    logger.info('Bulk export %s starting for `%s`', spec.job_id, spec.conn_name)
    state = run_job(spec)
    logger.info('Bulk export %s finished with status `%s`', spec.job_id, state.status)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
