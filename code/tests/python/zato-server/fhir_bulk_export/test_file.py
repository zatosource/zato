# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The file object a service receives - its resources read one line at a time, nothing read until asked for,
# an error file told apart by its resource type, and the round trip through the form it travels to a service in.

# stdlib
from json import dumps

# Zato
from zato.common.api import HL7
from zato.common.hl7.fhir.bulk_export.file import BulkExportFile, BulkExportResource, new_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_bulk = HL7.BulkExport

_job_id = 'job-file-1'
_conn_name = 'fhir.exports'
_url = 'http://fhir.example.com/files/Patient.1.ndjson'

_resources = [
    {'resourceType': 'Patient', 'id': 'p1'},
    {'resourceType': 'Patient', 'id': 'p2'},
    {'resourceType': 'Patient'},
]

# ################################################################################################################################
# ################################################################################################################################

def _write(tmp_path:'any_', name:'str'='Patient.0001.ndjson') -> 'str':
    """ Writes the resources one per line, with a blank line and Windows line endings thrown in.
    """
    lines = []
    for resource in _resources:
        lines.append(dumps(resource))

    path = tmp_path / name
    _ = path.write_bytes('\r\n'.join(lines).encode('utf8') + b'\r\n\r\n')

    out = str(path)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_resources_are_read_one_line_at_a_time(tmp_path:'any_') -> 'None':
    path = _write(tmp_path)
    file = new_file(_job_id, _conn_name, 'Patient', len(_resources), path, _url)

    assert file.job_id == _job_id
    assert file.connection_name == _conn_name
    assert file.resource_type == 'Patient'
    assert file.file_name == 'Patient.0001.ndjson'
    assert file.is_error_file is False

    # Iterating the file yields each resource parsed, the blank line and line endings never getting in the way
    assert list(file) == _resources
    assert len(file) == len(_resources)

    # The file can be read as many times as needed
    assert list(file.resources()) == _resources

    # The lines are what is on disk, without their endings
    lines = list(file.lines())
    assert lines[0] == dumps(_resources[0]).encode('utf8')

# ################################################################################################################################

def test_a_file_that_does_not_exist_is_not_read_until_asked(tmp_path:'any_') -> 'None':
    path = str(tmp_path / 'missing.ndjson')
    file = new_file(_job_id, _conn_name, 'Patient', 5, path, _url)

    # Building and describing the file touches nothing on disk
    assert file.count == 5
    assert file.file_name == 'missing.ndjson'
    assert file.to_dict()['path'] == path

# ################################################################################################################################

def test_an_error_file_is_told_apart_by_its_type(tmp_path:'any_') -> 'None':
    path = _write(tmp_path, 'OperationOutcome.0002.ndjson')
    file = new_file(_job_id, _conn_name, _bulk.Error_Resource_Type, 1, path, _url)

    assert file.is_error_file is True

# ################################################################################################################################

def test_the_file_round_trips_through_its_dict(tmp_path:'any_') -> 'None':
    path = _write(tmp_path)
    file = new_file(_job_id, _conn_name, 'Patient', len(_resources), path, _url)

    data = file.to_dict()
    read_back = BulkExportFile.from_dict(data)

    assert read_back.to_dict() == data
    assert read_back.job_id == _job_id
    assert read_back.path == path
    assert read_back.url == _url
    assert read_back.is_error_file is False
    assert list(read_back) == _resources

# ################################################################################################################################

def test_a_resource_carries_its_id_and_the_file_it_came_from(tmp_path:'any_') -> 'None':
    path = _write(tmp_path)
    file = new_file(_job_id, _conn_name, 'Patient', len(_resources), path, _url)

    lines = list(file.lines())

    first = BulkExportResource(file, lines[0])
    assert first.resource_id == 'p1'
    assert first.data == lines[0].decode('utf8')
    assert first.file is file

    # A resource without an id travels under an empty one
    last = BulkExportResource(file, lines[-1])
    assert last.resource_id == ''

# ################################################################################################################################
# ################################################################################################################################
