# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The lines that the followed redirects of a push write to the log.

# stdlib
from http.client import PERMANENT_REDIRECT, TEMPORARY_REDIRECT
from logging import INFO

# pytest
import pytest

# Test support
from redirect_wire_support import Delivery, new_message, new_payload, redirect_to, Sub_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import TestEndpoint
    from rest_outgoing_stub.connection import ServerStub
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The logger of the delivery of pushes
_logger_name = 'zato.server.base.parallel.delivery_rest'

# What the line of each followed redirect contains
_redirect_text = 'redirected with'

# What the line of a permanent redirect adds
_moved_text = 'moved permanently'

# The size of the payload of each push
_payload_size = 256

# ################################################################################################################################
# ################################################################################################################################

def _get_redirect_lines(caplog:'pytest.LogCaptureFixture') -> 'strlist':
    """ Returns the messages of the INFO lines of the delivery that describe a followed redirect.
    """
    out:'strlist' = []

    for record in caplog.records:

        if record.name != _logger_name:
            continue

        if record.levelno != INFO:
            continue

        message = record.getMessage()

        if _redirect_text in message:
            out.append(message)

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('status', [TEMPORARY_REDIRECT, PERMANENT_REDIRECT])
def test_each_redirect_writes_one_line(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    status:'int',
    caplog:'pytest.LogCaptureFixture',
    ) -> 'None':

    caplog.set_level(INFO, logger=_logger_name)

    source_path = path + '/source'
    target_path = path + '/target'

    source = loopback_first.http_base + source_path
    target = loopback_first.http_base + target_path

    response = redirect_to(target, status)
    loopback_first.set_responses(source_path, [response])

    payload = new_payload(_payload_size)
    message = new_message(payload)

    delivery = Delivery(server, loopback_first.http_base, source_path)
    delivery.push(message)

    lines = _get_redirect_lines(caplog)
    line_count = len(lines)

    assert line_count == 1

    # The line names the message, the subscription, the status, the source and the target ..
    line = lines[0]

    assert message['msg_id'] in line
    assert Sub_Key in line
    assert f' {status} ' in line
    assert f'`{source}`' in line
    assert f'`{target}`' in line

    # .. and only a permanent redirect states that the endpoint moved.
    is_moved = _moved_text in line
    assert is_moved == (status == PERMANENT_REDIRECT)

# ################################################################################################################################

def test_chain_writes_one_line_per_redirect(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    caplog:'pytest.LogCaptureFixture',
    ) -> 'None':

    caplog.set_level(INFO, logger=_logger_name)

    source_path = path + '/source'
    middle_path = path + '/middle'
    target_path = path + '/target'

    middle = loopback_first.http_base + middle_path
    target = loopback_first.http_base + target_path

    source_response = redirect_to(middle)
    middle_response = redirect_to(target, PERMANENT_REDIRECT)

    loopback_first.set_responses(source_path, [source_response])
    loopback_first.set_responses(middle_path, [middle_response])

    payload = new_payload(_payload_size)
    message = new_message(payload)

    delivery = Delivery(server, loopback_first.http_base, source_path)
    delivery.push(message)

    first_line, second_line = _get_redirect_lines(caplog)

    assert f'`{middle}`' in first_line
    assert _moved_text not in first_line

    assert f'`{target}`' in second_line
    assert _moved_text in second_line

# ################################################################################################################################

def test_direct_push_writes_no_line(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    caplog:'pytest.LogCaptureFixture',
    ) -> 'None':

    caplog.set_level(INFO, logger=_logger_name)

    payload = new_payload(_payload_size)
    message = new_message(payload)

    delivery = Delivery(server, loopback_first.http_base, path)
    delivery.push(message)

    lines = _get_redirect_lines(caplog)
    assert lines == []

# ################################################################################################################################
# ################################################################################################################################
