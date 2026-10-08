# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a store accepts as its data - bytes as they are, text encoded, and a dict, a list
# or a service's input serialized to JSON - and the same for a queued delivery.

# stdlib
import os
from json import loads

# Zato
from zato.input_output import ServiceInput
from zato.server.connection.file_transfer_base import to_file_bytes, Key_Remote_Path, Key_Spool_Path

# Test support
from audit_env import audit_db_env
from smb_stub import new_smb_connection, ClientRecorder, Remote_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

    os = os

# ################################################################################################################################
# ################################################################################################################################

# The order the fields are written in
_order_fields = {'customer_id': 'C-1001', 'quantity': 3, 'region': 'north'}

# ################################################################################################################################
# ################################################################################################################################

class PublisherRecorder:
    """ Stands in for the connection's publisher - it remembers each envelope it was given.
    """

    def __init__(self) -> 'None':
        self.envelopes:'anylist' = []

    def publish(self, envelope:'any_') -> 'str':
        self.envelopes.append(envelope)
        return 'msg-id-1'

# ################################################################################################################################
# ################################################################################################################################

def _read_spool(envelope:'any_') -> 'bytes':
    """ The bytes a queued delivery left in its spool file, which is removed afterwards.
    """
    spool_path = envelope[Key_Spool_Path]

    with open(spool_path, 'rb') as spool_file:
        out = spool_file.read()

    os.remove(spool_path)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_bytes_pass_through() -> 'None':
    data = b'code,label\nA1,First\n'

    assert to_file_bytes(data, 'utf8') is data

# ################################################################################################################################

def test_text_is_encoded() -> 'None':
    data = 'code,label\nA1,First\n'

    assert to_file_bytes(data, 'utf8') == b'code,label\nA1,First\n'

# ################################################################################################################################

def test_dict_is_serialized_to_json() -> 'None':
    out = to_file_bytes(_order_fields, 'utf8')

    assert loads(out) == _order_fields

# ################################################################################################################################

def test_list_is_serialized_to_json() -> 'None':
    data = [{'customer_id': 'C-1001'}, {'customer_id': 'C-1002'}]

    out = to_file_bytes(data, 'utf8')

    assert loads(out) == data

# ################################################################################################################################

def test_service_input_is_serialized_to_json_in_request_order() -> 'None':
    data = ServiceInput(_order_fields)

    out = to_file_bytes(data, 'utf8')

    assert loads(out) == _order_fields
    assert list(loads(out)) == ['customer_id', 'quantity', 'region']

# ################################################################################################################################

def test_a_store_of_a_service_input_writes_json(tmp_path:'os.PathLike') -> 'None':
    """ A service that writes its own input to a file leaves the request's fields as a JSON document.
    """
    with audit_db_env(tmp_path):

        smb_client = ClientRecorder()
        conn = new_smb_connection(smb_client)

        conn.write(ServiceInput(_order_fields), Remote_Path)

        written_path, written_data = smb_client.written[0]

        assert written_path == Remote_Path
        assert loads(written_data) == _order_fields

# ################################################################################################################################

def test_a_queued_delivery_of_a_service_input_spools_json(tmp_path:'os.PathLike') -> 'None':
    """ A queued delivery of a service's input spools the same JSON document a direct store writes.
    """
    with audit_db_env(tmp_path):

        conn = new_smb_connection(ClientRecorder())
        publisher = PublisherRecorder()
        conn.wrapper.publisher = publisher

        _ = conn.publish(ServiceInput(_order_fields), Remote_Path)

        envelope = publisher.envelopes[0]

        assert envelope[Key_Remote_Path] == Remote_Path
        assert loads(_read_spool(envelope)) == _order_fields

# ################################################################################################################################

def test_a_queued_delivery_of_text_spools_its_bytes(tmp_path:'os.PathLike') -> 'None':
    with audit_db_env(tmp_path):

        conn = new_smb_connection(ClientRecorder())
        publisher = PublisherRecorder()
        conn.wrapper.publisher = publisher

        _ = conn.publish('code,label\nA1,First\n', Remote_Path)

        envelope = publisher.envelopes[0]

        assert _read_spool(envelope) == b'code,label\nA1,First\n'

# ################################################################################################################################
# ################################################################################################################################
