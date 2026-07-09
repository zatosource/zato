# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from json import dumps, loads

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.odata.common import Content_Type_JSON, ODataSyntaxError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

batch_request_list = 'list[BatchRequest]'
batch_response_list = 'list[BatchResponse]'

# ################################################################################################################################
# ################################################################################################################################

# The line ending multipart bodies use on the wire.
_crlf = '\r\n'

# What each multipart part announces itself as.
_part_headers = 'Content-Type: application/http' + _crlf + 'Content-Transfer-Encoding: binary'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BatchRequest:
    """ One request inside a $batch - the URL is relative to the service root.
    """
    method: 'str' = 'GET'
    url: 'str' = ''
    headers: 'strstrdict | None' = None
    body: 'anydict | None' = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BatchResponse:
    """ One response from a $batch - the parsed JSON body, or None when there was none.
    """
    status_code: 'int' = 0
    headers: 'strstrdict'
    body: 'anydict | None' = None

# ################################################################################################################################
# ################################################################################################################################

def _render_request(request:'BatchRequest', content_id:'int | None'=None) -> 'str':
    """ Renders one request as the application/http payload of a multipart part,
    with a Content-ID when the request travels inside a changeset.
    """
    lines = [_part_headers]

    if content_id is not None:
        lines.append(f'Content-ID: {content_id}')

    lines.append('')
    lines.append(f'{request.method} {request.url} HTTP/1.1')

    if request.headers:
        for name, value in request.headers.items():
            lines.append(f'{name}: {value}')

    if request.body is not None:
        body = dumps(request.body)
        lines.append(f'Content-Type: {Content_Type_JSON}')
        lines.append('')
        lines.append(body)
    else:
        lines.append('')

    out = _crlf.join(lines)
    return out

# ################################################################################################################################

def build_multipart(requests:'batch_request_list') -> 'tuple[bytes, str]':
    """ Builds a multipart $batch body out of the requests - reads travel as individual
    parts and each contiguous run of writes is grouped into one changeset, the unit
    of atomicity the OData specification prescribes. Returns the body and its Content-Type.
    """
    batch_boundary = 'batch_' + CryptoManager.generate_hex_string()

    parts = []

    # Requests are numbered across the whole batch so Content-IDs stay unique.
    content_id = 0

    # A run of consecutive writes collects here until a read or the end flushes it.
    pending_changeset = []

    def _flush_changeset() -> 'None':
        """ Wraps the collected writes in one changeset part and clears the run.
        """
        if not pending_changeset:
            return

        changeset_boundary = 'changeset_' + CryptoManager.generate_hex_string()

        changeset_lines = [f'Content-Type: multipart/mixed; boundary={changeset_boundary}', '']

        for rendered in pending_changeset:
            changeset_lines.append(f'--{changeset_boundary}')
            changeset_lines.append(rendered)

        changeset_lines.append(f'--{changeset_boundary}--')

        parts.append(_crlf.join(changeset_lines))
        pending_changeset.clear()

    for request in requests:
        content_id += 1

        # Reads stand on their own, writes join the current changeset run.
        if request.method == 'GET':
            _flush_changeset()
            parts.append(_render_request(request))
        else:
            pending_changeset.append(_render_request(request, content_id))

    _flush_changeset()

    # Assemble the full multipart body around the batch boundary.
    body_lines = []

    for part in parts:
        body_lines.append(f'--{batch_boundary}')
        body_lines.append(part)

    body_lines.append(f'--{batch_boundary}--')
    body_lines.append('')

    body = _crlf.join(body_lines).encode('utf8')
    content_type = f'multipart/mixed; boundary={batch_boundary}'

    out = (body, content_type)
    return out

# ################################################################################################################################

def _extract_boundary(content_type:'str') -> 'str':
    """ Returns the boundary parameter of a multipart Content-Type.
    """
    for parameter in content_type.split(';'):
        parameter = parameter.strip()
        if parameter.startswith('boundary='):
            out = parameter[len('boundary='):].strip('"')
            break
    else:
        raise ODataSyntaxError(f'No boundary in Content-Type `{content_type}`')

    return out

# ################################################################################################################################

def _split_parts(body:'str', boundary:'str') -> 'list[str]':
    """ Splits a multipart body into its parts, dropping the preamble and the epilogue.
    """
    delimiter = f'--{boundary}'

    segments = body.split(delimiter)

    # The first segment is the preamble and the last one follows the closing delimiter.
    out = []
    for segment in segments[1:-1]:
        out.append(segment.strip(_crlf))

    return out

# ################################################################################################################################

def _parse_part(part:'str') -> 'BatchResponse':
    """ Parses one application/http part into a BatchResponse - the part headers come
    first, then the embedded HTTP response with its status line, headers and body.
    """
    part_headers, _, http_message = part.partition(_crlf + _crlf)

    # A changeset part carries a nested multipart body instead of a single response.
    if 'multipart/mixed' in part_headers:
        raise ODataSyntaxError('A changeset part cannot be parsed as a single response')

    status_line, _, rest = http_message.partition(_crlf)

    # The status line reads e.g. HTTP/1.1 201 Created.
    status_code = int(status_line.split(' ')[1])

    headers_text, _, body_text = rest.partition(_crlf + _crlf)

    # Our response to produce
    out = BatchResponse()
    out.headers = {}

    out.status_code = status_code

    for header_line in headers_text.split(_crlf):
        if ':' in header_line:
            name, _, value = header_line.partition(':')
            out.headers[name.strip()] = value.strip()

    body_text = body_text.strip()
    if body_text:
        try:
            out.body = loads(body_text)
        except ValueError:
            raise ODataSyntaxError(f'Could not parse a batch part body as JSON -> `{body_text}`')

    return out

# ################################################################################################################################

def parse_multipart(body:'bytes', content_type:'str') -> 'batch_response_list':
    """ Parses a multipart $batch response into the individual responses, in order -
    changeset parts are unwrapped so their responses appear inline like the others.
    """
    boundary = _extract_boundary(content_type)
    text = body.decode('utf8')

    # Our response to produce
    out:'batch_response_list' = []

    for part in _split_parts(text, boundary):

        part_headers = part.partition(_crlf + _crlf)[0]

        # A changeset arrives as a nested multipart whose parts are unwrapped in place.
        if 'multipart/mixed' in part_headers:
            changeset_boundary = _extract_boundary(part_headers)

            for changeset_part in _split_parts(part, changeset_boundary):
                out.append(_parse_part(changeset_part))

        else:
            out.append(_parse_part(part))

    return out

# ################################################################################################################################

def build_json(requests:'batch_request_list') -> 'anydict':
    """ Builds a V4 JSON $batch body out of the requests - writes reference the preceding
    write through 'dependsOn' within their atomicity group, mirroring what changesets
    express in the multipart format.
    """
    rendered = []

    # A run of consecutive writes shares one atomicity group.
    group_number = 0
    in_group = False

    for index, request in enumerate(requests, 1):

        item:'anydict' = {
            'id': str(index),
            'method': request.method,
            'url': request.url,
        }

        if request.headers:
            item['headers'] = request.headers

        if request.body is not None:
            item['body'] = request.body

        # Reads end any group in progress, writes open or continue one.
        if request.method == 'GET':
            in_group = False
        else:
            if not in_group:
                group_number += 1
                in_group = True

            item['atomicityGroup'] = f'group{group_number}'

        rendered.append(item)

    out = {'requests': rendered}
    return out

# ################################################################################################################################

def parse_json(data:'anydict') -> 'batch_response_list':
    """ Parses a V4 JSON $batch response into the individual responses, in request order.
    """

    # Our response to produce
    out:'batch_response_list' = []

    responses = sorted(data['responses'], key=_response_order)

    for item in responses:
        response = BatchResponse()
        response.status_code = item['status']
        response.headers = item.get('headers') or {}
        response.body = item.get('body')

        out.append(response)

    return out

# ################################################################################################################################

def _response_order(item:'anydict') -> 'int':
    """ Returns the ordering key of one JSON batch response - its request's numeric id.
    """
    out = int(item['id'])
    return out

# ################################################################################################################################
# ################################################################################################################################
