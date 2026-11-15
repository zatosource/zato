# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.server.control.envelope import decode, encode, MessageType, ModuleCtx, new_message, split

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path

    Path = Path

# ################################################################################################################################
# ################################################################################################################################

def test_a_small_body_is_part_of_the_datagram(tmp_path:'Path') -> 'None':
    body_dir = str(tmp_path)
    body = {'name': 'my.service', 'items': [1, 2, 3]}

    message = new_message(MessageType.Event, body, 'my-cid')
    message.seq = 7
    message.slot = 2

    datagram = encode(message, body_dir)
    header, _ = split(datagram)

    # No file holds the body ..
    assert 'path' not in header
    assert os.listdir(body_dir) == []

    # .. and the message is the same after the round trip.
    decoded = decode(datagram)

    assert decoded.type == MessageType.Event
    assert decoded.seq == 7
    assert decoded.slot == 2
    assert decoded.cid == 'my-cid'
    assert decoded.body == body

# ################################################################################################################################

def test_a_large_body_is_in_a_file_that_its_reader_removes(tmp_path:'Path') -> 'None':
    body_dir = str(tmp_path)
    body_size = ModuleCtx.Max_Inline_Body + 1
    body = 'a' * body_size

    message = new_message(MessageType.Event, body)
    datagram = encode(message, body_dir)
    header, inline_body = split(datagram)

    # The datagram names the file and is within the size that a receiver reads ..
    assert header['path'].startswith(body_dir)
    assert inline_body == b''
    assert len(datagram) <= ModuleCtx.Max_Datagram

    # .. and the reader receives the body and removes the file.
    decoded = decode(datagram)

    assert decoded.body == body
    assert os.listdir(body_dir) == []

# ################################################################################################################################

def test_a_body_with_newlines_and_quotes_keeps_its_header(tmp_path:'Path') -> 'None':
    body_dir = str(tmp_path)
    body = 'line one\nline "two"\n'

    message = new_message(MessageType.Query, body, 'my-cid')
    datagram = encode(message, body_dir)

    decoded = decode(datagram)

    assert decoded.cid == 'my-cid'
    assert decoded.body == body

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = pytest.main([__file__])

# ################################################################################################################################
# ################################################################################################################################
