# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps, loads

# Zato
from zato.common.file_transfer.api import Default_Encoding, Encoding
from zato.common.model.file_transfer_ import FileTransferItem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_conn_type = 'outconn-sftp'
_conn_name = 'Partner SFTP'
_schedule_name = 'invoices.hourly'
_directory = '/incoming/invoices'
_file_name = 'invoice_20260801.csv'
_full_path = '/incoming/invoices/invoice_20260801.csv'
_last_modified = '2026-08-01T10:15:30+00:00'

# Two bytes that no UTF-8 decoding accepts, standing in for a binary file
_undecodable = b'\xff\xfe'

# ################################################################################################################################
# ################################################################################################################################

def _item(data:'bytes', encoding:'str' = Default_Encoding) -> 'FileTransferItem':
    out = FileTransferItem.from_bytes(_conn_type, _conn_name, _schedule_name, _directory, _file_name, _full_path,
        _last_modified, data, encoding)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFileTransferItem:
    """ What a file transfer item holds and how it turns into a dict.
    """

    def test_attributes_are_kept_as_given(self) -> 'None':

        data = b'INVOICE,1,100.00\n'
        item = _item(data)

        assert item.conn_type == _conn_type
        assert item.conn_name == _conn_name
        assert item.schedule_name == _schedule_name
        assert item.directory == _directory
        assert item.file_name == _file_name
        assert item.full_path == _full_path
        assert item.size == len(data)
        assert item.last_modified == _last_modified
        assert item.encoding == Default_Encoding

        # The contents are read as bytes from the spool file
        assert item.data == data
        assert isinstance(item.data, bytes)

# ################################################################################################################################

    def test_to_dict_holds_every_attribute_with_data_as_text(self) -> 'None':

        data = 'Λογαριασμοί, 송장\n'.encode('utf8')
        item = _item(data)

        expected = {
            'conn_type': _conn_type,
            'conn_name': _conn_name,
            'schedule_name': _schedule_name,
            'directory': _directory,
            'file_name': _file_name,
            'full_path': _full_path,
            'size': len(data),
            'last_modified': _last_modified,
            'encoding': Default_Encoding,
            'data': 'Λογαριασμοί, 송장\n',
        }

        assert item.to_dict() == expected

# ################################################################################################################################

    def test_to_dict_reads_the_text_in_the_encoding_of_the_item(self) -> 'None':

        text = 'Ψάρι, εγώ\n'
        data = text.encode(Encoding.ISO_8859_7)
        item = _item(data, Encoding.ISO_8859_7)

        result = item.to_dict()

        assert result['encoding'] == Encoding.ISO_8859_7
        assert result['data'] == text

# ################################################################################################################################

    def test_to_dict_size_is_the_byte_count_not_the_text_length(self) -> 'None':

        # Multi-byte characters make the text shorter than the bytes it came from
        data = 'Λογαριασμοί'.encode('utf8')
        item = _item(data)

        result = item.to_dict()

        assert result['size'] == len(data)
        assert len(result['data']) < result['size']

# ################################################################################################################################

    def test_to_dict_replaces_undecodable_bytes(self) -> 'None':

        item = _item(_undecodable)
        result = item.to_dict()

        # Nothing is raised and each bad byte becomes the replacement character
        assert result['data'] == '\ufffd\ufffd'
        assert result['size'] == len(_undecodable)

# ################################################################################################################################

    def test_to_dict_is_json_serializable(self) -> 'None':

        item = _item(b'INVOICE,1,100.00\n')

        # This is what makes the item usable as a service's response
        serialized = dumps(item.to_dict())
        assert loads(serialized) == item.to_dict()

# ################################################################################################################################

    def test_to_dict_does_not_change_the_item(self) -> 'None':

        data = b'INVOICE,1,100.00\n'
        item = _item(data)

        _ = item.to_dict()

        assert item.data == data
        assert isinstance(item.data, bytes)

# ################################################################################################################################

    def test_repr_names_the_file_and_where_it_came_from(self) -> 'None':

        item = _item(b'abc')
        text = repr(item)

        assert 'FileTransferItem' in text
        assert f'full_path:`{_full_path}`' in text
        assert 'size:`3`' in text
        assert f'encoding:`{Default_Encoding}`' in text
        assert f'conn_name:`{_conn_name}`' in text
        assert f'schedule_name:`{_schedule_name}`' in text

# ################################################################################################################################

    def test_data_is_read_from_the_spool_file_each_time(self) -> 'None':

        item = _item(b'first')

        # The item holds no copy of the bytes, so what the spool file holds is what is read
        with open(item.path, 'wb') as spool_file:
            _ = spool_file.write(b'second')

        assert item.data == b'second'

# ################################################################################################################################

    def test_close_deletes_the_spool_file(self, spool_directory:'any_') -> 'None':

        item = _item(b'INVOICE,1,100.00\n')
        assert os.path.exists(item.path)

        item.close()

        assert not os.path.exists(item.path)
        assert os.listdir(spool_directory) == []

# ################################################################################################################################

    def test_spool_file_is_in_the_spool_directory(self, spool_directory:'any_') -> 'None':

        item = _item(b'abc')

        directory = os.path.dirname(item.path)
        assert directory == str(spool_directory)

# ################################################################################################################################
# ################################################################################################################################
