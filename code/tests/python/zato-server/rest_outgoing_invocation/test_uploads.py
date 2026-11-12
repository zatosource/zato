# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Uploads - a file sent in a multipart body under the multipart content type with its boundary, with the credentials
# and the default headers of the connection, and the response returned as for any other call.

# stdlib
import os
from http.client import CREATED

# pytest
import pytest

# Test support
from endpoint import EndpointResponse
from support import Basic_Password, Basic_Username, get_basic_authorization, new_basic_auth_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# What the uploaded file contains
_file_content = b'customer_id,name\n123,John Smith\n456,Jane Doe\n'

# ################################################################################################################################
# ################################################################################################################################

def _write_file(directory:'os.PathLike', name:'str') -> 'str':
    """ Writes the file to upload and returns its path.
    """
    out = os.path.join(str(directory), name)

    with open(out, 'wb') as file:
        _ = file.write(_file_content)

    return out

# ################################################################################################################################

def _get_boundary(content_type:'str') -> 'str':
    """ Returns the boundary a multipart content type names.
    """
    _, boundary = content_type.split('boundary=', 1)
    return boundary

# ################################################################################################################################
# ################################################################################################################################

def test_upload(endpoint:'TestEndpoint', server:'ServerStub', path:'str', tmp_path:'os.PathLike') -> 'None':
    """ A file is sent in a multipart body with the credentials and the default headers, and the response is returned.
    """
    endpoint.set_response(path, EndpointResponse(CREATED, 'Upload accepted'))

    file_path = _write_file(tmp_path, 'customers.csv')
    connection = new_basic_auth_connection(server, endpoint.http_base, path)

    response = connection.upload(Test_CID, file_path)

    assert response.status_code == CREATED
    assert response.text == 'Upload accepted'

    request = endpoint.get_request(path)

    content_type = request.get_header('Content-Type')
    assert content_type is not None
    assert content_type.startswith('multipart/form-data; boundary=')

    boundary = _get_boundary(content_type)
    expected_body = (
        f'--{boundary}\r\n'
        'Content-Disposition: form-data; name="data"; filename="customers.csv"\r\n'
        'Content-Type: text/plain\r\n'
        '\r\n'
    ).encode('utf8') + _file_content + f'\r\n--{boundary}--\r\n'.encode('utf8')

    assert request.method == 'POST'
    assert request.body == expected_body
    assert request.get_header('Content-Length') == str(len(expected_body))
    assert request.get_header('Authorization') == get_basic_authorization(Basic_Username, Basic_Password)
    assert request.get_header('X-Zato-CID') == Test_CID

# ################################################################################################################################

def test_upload_field_name_and_mime_type(endpoint:'TestEndpoint', server:'ServerStub', path:'str', tmp_path:'os.PathLike') -> 'None':
    """ The field name and the MIME type of an upload are those the call names.
    """
    file_path = _write_file(tmp_path, 'customers.csv')
    connection = new_basic_auth_connection(server, endpoint.http_base, path)

    _ = connection.upload(Test_CID, file_path, field_name='customer_file', mime_type='text/csv')

    request = endpoint.get_request(path)

    assert b'Content-Disposition: form-data; name="customer_file"; filename="customers.csv"\r\n' in request.body
    assert b'Content-Type: text/csv\r\n' in request.body

# ################################################################################################################################

def test_upload_missing_file(endpoint:'TestEndpoint', server:'ServerStub', path:'str', tmp_path:'os.PathLike') -> 'None':
    """ A file that does not exist raises an exception naming it, without a request being sent.
    """
    file_path = os.path.join(str(tmp_path), 'missing.csv')
    connection = new_basic_auth_connection(server, endpoint.http_base, path)

    with pytest.raises(Exception) as info:
        _ = connection.upload(Test_CID, file_path)

    assert info.value.args[0] == f'File to upload not found -> `{file_path}`'
    assert endpoint.get_requests(path) == []

# ################################################################################################################################

def test_upload_directory(endpoint:'TestEndpoint', server:'ServerStub', path:'str', tmp_path:'os.PathLike') -> 'None':
    """ A path that is not a file raises an exception naming it, without a request being sent.
    """
    directory = str(tmp_path)
    connection = new_basic_auth_connection(server, endpoint.http_base, path)

    with pytest.raises(Exception) as info:
        _ = connection.upload(Test_CID, directory)

    assert info.value.args[0] == f'Path is not a file -> `{directory}`'
    assert endpoint.get_requests(path) == []

# ################################################################################################################################
# ################################################################################################################################
