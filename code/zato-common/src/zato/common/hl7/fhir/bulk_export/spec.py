# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import asdict, dataclass, field
from json import dumps, loads

# Zato
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strdict, strlist

    any_       = any_
    anylist    = anylist
    stranydict = stranydict
    strdict    = strdict
    strlist    = strlist

# ################################################################################################################################
# ################################################################################################################################

_bulk = HL7.BulkExport

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class JobSpec:
    """ Everything the export program needs to run one job - it travels on the program's stdin
    and is never written to disk because it carries the decrypted secrets of the connection.
    """

    # The job and the connection it runs for
    job_id: 'str' = ''
    conn_id: 'int' = 0
    conn_name: 'str' = ''
    server_name: 'str' = ''

    # The FHIR server and how to authenticate with it - a ready Basic Auth header
    # or a bearer token definition with its secret or private key already decrypted
    address: 'str' = ''
    auth_type: 'str' = ''
    basic_auth_header: 'str' = ''
    bearer: 'stranydict' = field(default_factory=dict)
    bearer_data_format: 'str' = ''
    scopes: 'str' = ''

    # What to export
    level: 'str' = _bulk.Level.Group
    group_id: 'str' = ''
    patient_ids: 'strlist' = field(default_factory=list)
    types: 'strlist' = field(default_factory=list)
    since: 'str' = ''
    type_filter: 'strlist' = field(default_factory=list)

    # Destinations of this job alone - empty means the connection's own are used
    destinations: 'any_' = ''

    # Where files go and what happens to them afterwards
    download_dir: 'str' = ''
    delete_files: 'bool' = True
    delete_on_server: 'bool' = True

    # How the program reaches the server to hand each file over
    invoke_url: 'str' = ''
    invoke_username: 'str' = ''
    invoke_password: 'str' = ''

    # The audit log database the program writes to - the same one the server uses
    audit_env: 'strdict' = field(default_factory=dict)

# ################################################################################################################################

    @property
    def job_dir(self) -> 'str':
        out = os.path.join(self.download_dir, self.job_id)
        return out

# ################################################################################################################################

    def to_json(self) -> 'str':
        out = dumps(asdict(self))
        return out

# ################################################################################################################################

    @classmethod
    def from_json(class_, data:'str') -> 'JobSpec':
        out = class_(**loads(data))
        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class FileState:
    """ One file of the manifest and how far it has come.
    """
    resource_type: 'str' = ''
    url: 'str' = ''
    count: 'int' = 0
    path: 'str' = ''
    is_downloaded: 'bool' = False
    is_delivered: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class JobState:
    """ Where a job is - written to the job's directory after each step so a program started
    again for the same job can carry on from the files not yet delivered. It holds no secrets.
    """
    job_id: 'str' = ''
    conn_id: 'int' = 0
    conn_name: 'str' = ''
    status: 'str' = _bulk.Status.Running
    phase: 'str' = _bulk.Phase.Kickoff

    # What the FHIR server told us
    status_url: 'str' = ''
    transaction_time: 'str' = ''
    requires_access_token: 'bool' = True
    manifest: 'stranydict' = field(default_factory=dict)

    # The files, in the manifest's order, and what went wrong along the way
    files: 'list[FileState]' = field(default_factory=list)
    failures: 'strlist' = field(default_factory=list)

    # When the job started and when this state was last written, both UTC ISO-8601
    start_time: 'str' = ''
    update_time: 'str' = ''

# ################################################################################################################################

    def to_json(self) -> 'str':
        out = dumps(asdict(self), indent=2)
        return out

# ################################################################################################################################

    @classmethod
    def from_json(class_, data:'str') -> 'JobState':
        parsed = loads(data)

        # Files are nested dataclasses so they are rebuilt one by one ..
        files = []
        for item in parsed.pop('files'):
            files.append(FileState(**item))

        # .. and everything else maps to a field directly.
        out = class_(**parsed)
        out.files = files

        return out

# ################################################################################################################################

    def save(self, job_dir:'str') -> 'None':
        path = os.path.join(job_dir, _bulk.State_File_Name)
        with open(path, 'w') as file:
            _ = file.write(self.to_json())

# ################################################################################################################################

    @classmethod
    def load(class_, job_dir:'str') -> 'JobState':
        path = os.path.join(job_dir, _bulk.State_File_Name)
        with open(path) as file:
            out = class_.from_json(file.read())

        return out

# ################################################################################################################################

    @property
    def is_finished(self) -> 'bool':
        out = self.status != _bulk.Status.Running
        return out

# ################################################################################################################################
# ################################################################################################################################

def get_download_dir(server_work_dir:'str') -> 'str':
    """ Returns the directory exports are downloaded to - an environment variable overrides
    the default under the server's work directory.
    """
    out = os.environ.get(_bulk.Env_Dir)
    if not out:
        out = os.path.join(server_work_dir, _bulk.Default_Dir)

    return out

# ################################################################################################################################
# ################################################################################################################################
