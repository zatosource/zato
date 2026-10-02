# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Bulk Data Access side of the FHIR test server - the $export kick-off, the status endpoint that answers
# with the manifest once the export is ready, the NDJSON files it points to and the delete that lets them go.

# stdlib
import json
from http.client import ACCEPTED, NO_CONTENT, NOT_FOUND, OK
from threading import RLock
from urllib.parse import urlsplit

# Zato
from zato.common.api import HL7
from zato.common.crypto.api import CryptoManager
from zato.common.test.fhir.store import utc_now_instant

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.fhir.handler import FHIRRequestHandler
    from zato.common.test.fhir.store import FHIRStore, search_parameter_list
    from zato.common.typing_ import dictlist, stranydict, strlist, strset
    FHIRRequestHandler = FHIRRequestHandler
    FHIRStore = FHIRStore
    search_parameter_list = search_parameter_list
    dictlist = dictlist
    stranydict = stranydict
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

_bulk = HL7.BulkExport

# Where the status endpoint and the files of an export live
Status_Path_Prefix = '/bulk/status/'
Files_Path_Prefix  = '/bulk/files/'

# The last segment of a kick-off path
Export_Operation = '$export'

# How many path segments a kick-off has at each level - /$export, /Patient/$export and /Group/{id}/$export
_system_segments  = 1
_patient_segments = 2
_group_segments   = 3

# The headers a kick-off and a poll answer with
Header_Content_Location = 'Content-Location'
Header_Retry_After      = 'Retry-After'
Header_Progress         = 'X-Progress'

# The parameters a kick-off accepts
Param_Type        = '_type'
Param_Since       = '_since'
Param_Type_Filter = '_typeFilter'
Param_Patient     = 'patient'

# How a file of one resource type is named
File_Name_Pattern = '{resource_type}.{index}.ndjson'

# The keys a resource points at the patient it is about under
_patient_reference_keys = ('subject', 'patient')
_patient_type = 'Patient'
_group_type = 'Group'

# ################################################################################################################################
# ################################################################################################################################

class BulkExportConfig:
    """ How the server behaves during an export - all of it adjustable by a test before it kicks one off.
    """
    def __init__(self) -> 'None':

        # How many polls answer "still running" before the manifest is ready
        self.polls_until_ready = 1

        # What the server asks a client to wait between polls, in seconds
        self.retry_after = 0

        # Whether the files need the same credentials the kick-off did
        self.requires_access_token = True

        # How many resources one file holds at most - zero means all of a type in one file
        self.max_resources_per_file = 0

        # The OperationOutcome resources the export's error file lists - none means no error file
        self.error_outcomes:'dictlist' = []

        # An HTTP status to refuse a kick-off with - zero means the kick-off is accepted
        self.kickoff_status = 0

        # An HTTP status to fail every file download with - zero means the downloads succeed
        self.download_status = 0

# ################################################################################################################################
# ################################################################################################################################

class ExportRecord:
    """ One export the server has been asked for.
    """
    def __init__(self) -> 'None':
        self.export_id = ''
        self.level = ''
        self.group_id = ''
        self.parameters:'stranydict' = {}
        self.poll_count = 0
        self.transaction_time = ''
        self.files:'dict[str, bytes]' = {}
        self.file_types:'dict[str, str]' = {}
        self.file_counts:'dict[str, int]' = {}
        self.error_files:'strset' = set()
        self.is_deleted = False

# ################################################################################################################################
# ################################################################################################################################

class BulkExportState:
    """ What the server remembers about the exports it has run - what a test asserts on afterwards.
    """
    def __init__(self) -> 'None':
        self.config = BulkExportConfig()
        self.exports:'dict[str, ExportRecord]' = {}
        self.kickoff_headers:'dictlist' = []
        self.file_headers:'dictlist' = []
        self._lock = RLock()

    def get_export(self, export_id:'str') -> 'ExportRecord | None':
        with self._lock:
            out = self.exports.get(export_id)
        return out

    def add_export(self, record:'ExportRecord') -> 'None':
        with self._lock:
            self.exports[record.export_id] = record

# ################################################################################################################################
# ################################################################################################################################

def _matches_patient(resource:'stranydict', patient_ids:'strset') -> 'bool':
    """ Whether a resource is one of the patients asked for or is about one of them.
    """
    resource_type = resource['resourceType']

    if resource_type == _patient_type:
        out = resource['id'] in patient_ids
        return out

    for key in _patient_reference_keys:
        reference = resource.get(key)
        if reference:
            target = reference.get('reference', '')
            for patient_id in patient_ids:
                if target == f'{_patient_type}/{patient_id}':
                    return True

    return False

# ################################################################################################################################

def _is_since(resource:'stranydict', since:'str') -> 'bool':
    """ Whether a resource was last updated at or after the moment given - both are ISO instants, so they compare as text.
    """
    meta = resource.get('meta', {})
    last_updated = meta.get('lastUpdated', '')

    out = last_updated >= since
    return out

# ################################################################################################################################

def _split_list(value:'str') -> 'strlist':
    out = []

    for item in value.split(','):
        item = item.strip()
        if item:
            out.append(item)

    return out

# ################################################################################################################################

def _select_resources(store:'FHIRStore', parameters:'stranydict') -> 'dict[str, dictlist]':
    """ The resources an export includes, grouped by type, after the _type, _since and patient parameters.
    """
    out:'dict[str, dictlist]' = {}

    types = _split_list(parameters.get(Param_Type, ''))
    since = parameters.get(Param_Since, '')
    patient_ids = set(_split_list(parameters.get(Param_Patient, '')))

    for resource in store.get_all_current():

        resource_type = resource['resourceType']

        if types:
            if resource_type not in types:
                continue

        if since:
            if not _is_since(resource, since):
                continue

        if patient_ids:
            if not _matches_patient(resource, patient_ids):
                continue

        out.setdefault(resource_type, []).append(resource)

    return out

# ################################################################################################################################

def _to_ndjson(resources:'dictlist') -> 'bytes':
    lines = []

    for resource in resources:
        lines.append(json.dumps(resource))

    text = '\n'.join(lines)
    if text:
        text += '\n'

    out = text.encode('utf8')
    return out

# ################################################################################################################################

def _chunk(resources:'dictlist', size:'int') -> 'list[dictlist]':
    if size <= 0:
        return [resources]

    out = []

    for start in range(0, len(resources), size):
        out.append(resources[start:start + size])

    return out

# ################################################################################################################################

def build_files(record:'ExportRecord', store:'FHIRStore', config:'BulkExportConfig') -> 'None':
    """ Writes the export's files into its record - one or more per resource type, plus the error file if asked for.
    """
    by_type = _select_resources(store, record.parameters)

    for resource_type in sorted(by_type):

        chunks = _chunk(by_type[resource_type], config.max_resources_per_file)

        for index, chunk in enumerate(chunks, 1):
            file_name = File_Name_Pattern.format(resource_type=resource_type, index=index)
            record.files[file_name] = _to_ndjson(chunk)
            record.file_types[file_name] = resource_type
            record.file_counts[file_name] = len(chunk)

    if config.error_outcomes:
        file_name = File_Name_Pattern.format(resource_type=_bulk.Error_Resource_Type, index=1)
        record.files[file_name] = _to_ndjson(config.error_outcomes)
        record.file_types[file_name] = _bulk.Error_Resource_Type
        record.file_counts[file_name] = len(config.error_outcomes)
        record.error_files.add(file_name)

# ################################################################################################################################

def build_manifest(record:'ExportRecord', base_address:'str', config:'BulkExportConfig') -> 'stranydict':
    """ The manifest a completed export answers with, per the Bulk Data Access specification.
    """
    output = []
    error = []

    for file_name in sorted(record.files):

        entry = {
            'type': record.file_types[file_name],
            'url': f'{base_address}{Files_Path_Prefix}{record.export_id}/{file_name}',
            'count': record.file_counts[file_name],
        }

        if file_name in record.error_files:
            error.append(entry)
        else:
            output.append(entry)

    out = {
        'transactionTime': record.transaction_time,
        'request': f'{base_address}/{Export_Operation}',
        'requiresAccessToken': config.requires_access_token,
        'output': output,
        'error': error,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def handle_export_kickoff(handler:'FHIRRequestHandler', level:'str', group_id:'str', parameters:'stranydict') -> 'None':
    """ Accepts an export, answering 202 with where its status can be polled.
    """
    state = handler.server.bulk
    config = state.config

    state.kickoff_headers.append(dict(handler.headers.items()))

    if config.kickoff_status:
        handler.send_outcome(config.kickoff_status, 'processing', 'Export refused by test configuration')
        return

    record = ExportRecord()
    record.export_id = CryptoManager.generate_hex_string()
    record.level = level
    record.group_id = group_id
    record.parameters = parameters
    record.transaction_time = utc_now_instant()

    build_files(record, handler.server.store, config)
    state.add_export(record)

    status_url = f'{handler.server.base_address}{Status_Path_Prefix}{record.export_id}'

    handler.send_response(ACCEPTED)
    handler.send_header(Header_Content_Location, status_url)
    handler.send_header('Content-Length', '0')
    handler.end_headers()

# ################################################################################################################################

def handle_export_status(handler:'FHIRRequestHandler', export_id:'str') -> 'None':
    """ Answers 202 while the export is still running and the manifest once it is ready.
    """
    state = handler.server.bulk
    config = state.config

    record = state.get_export(export_id)

    if record is None:
        handler.send_outcome(NOT_FOUND, 'not-found', f'No such export -> {export_id}')
        return

    if record.is_deleted:
        handler.send_outcome(NOT_FOUND, 'not-found', f'Export deleted -> {export_id}')
        return

    record.poll_count += 1

    if record.poll_count <= config.polls_until_ready:
        handler.send_response(ACCEPTED)
        handler.send_header(Header_Retry_After, str(config.retry_after))
        handler.send_header(Header_Progress, f'{record.poll_count} of {config.polls_until_ready}')
        handler.send_header('Content-Length', '0')
        handler.end_headers()
        return

    manifest = build_manifest(record, handler.server.base_address, config)
    handler.send_json(OK, manifest, is_fhir=False)

# ################################################################################################################################

def handle_export_file(handler:'FHIRRequestHandler', export_id:'str', file_name:'str') -> 'None':
    """ Serves one NDJSON file of an export.
    """
    state = handler.server.bulk
    config = state.config

    state.file_headers.append(dict(handler.headers.items()))

    if config.download_status:
        handler.send_outcome(config.download_status, 'processing', 'Download refused by test configuration')
        return

    record = state.get_export(export_id)

    if record is None:
        handler.send_outcome(NOT_FOUND, 'not-found', f'No such export -> {export_id}')
        return

    if record.is_deleted:
        handler.send_outcome(NOT_FOUND, 'not-found', f'Export deleted -> {export_id}')
        return

    body = record.files.get(file_name)

    if body is None:
        handler.send_outcome(NOT_FOUND, 'not-found', f'No such file -> {file_name}')
        return

    handler.send_response(OK)
    handler.send_header('Content-Type', _bulk.Content_Type)
    handler.send_header('Content-Length', str(len(body)))
    handler.end_headers()
    _ = handler.wfile.write(body)

# ################################################################################################################################

def handle_bulk_get(handler:'FHIRRequestHandler', segments:'strlist', parameters:'search_parameter_list') -> 'bool':
    """ Routes a GET of the Bulk Data Access API - a kick-off at any of its three levels, a status poll
    or a file download - returning whether the path was one of these.
    """
    segment_count = len(segments)

    # A kick-off ends with the $export operation ..
    if segment_count:
        if segments[-1] == Export_Operation:

            if segment_count == _system_segments:
                level = _bulk.Level.System
                group_id = ''

            elif segment_count == _patient_segments:
                if segments[0] != _patient_type:
                    handler.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {handler.path}')
                    return True
                level = _bulk.Level.Patient
                group_id = ''

            elif segment_count == _group_segments:
                if segments[0] != _group_type:
                    handler.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {handler.path}')
                    return True
                level = _bulk.Level.Group
                group_id = segments[1]

            else:
                handler.send_outcome(NOT_FOUND, 'not-found', f'Unrecognized path -> {handler.path}')
                return True

            handle_export_kickoff(handler, level, group_id, dict(parameters))
            return True

    path = urlsplit(handler.path).path

    # .. a poll names the export ..
    if path.startswith(Status_Path_Prefix):
        export_id = path[len(Status_Path_Prefix):]
        handle_export_status(handler, export_id)
        return True

    # .. and a download names the export and the file.
    if path.startswith(Files_Path_Prefix):
        export_id, _, file_name = path[len(Files_Path_Prefix):].partition('/')
        handle_export_file(handler, export_id, file_name)
        return True

    return False

# ################################################################################################################################

def handle_export_delete(handler:'FHIRRequestHandler', export_id:'str') -> 'None':
    """ Lets the export's files go, after which its status and files are not found.
    """
    state = handler.server.bulk
    record = state.get_export(export_id)

    if record is None:
        handler.send_outcome(NOT_FOUND, 'not-found', f'No such export -> {export_id}')
        return

    record.is_deleted = True

    handler.send_response(NO_CONTENT)
    handler.send_header('Content-Length', '0')
    handler.end_headers()

# ################################################################################################################################
# ################################################################################################################################
