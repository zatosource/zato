# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from csv import reader as csv_reader
from io import BytesIO
from zipfile import ZipFile

# pytest
from pytest import mark, raises

# Zato
from zato.common.api import Documents
from zato.common.file_transfer.api import Encoding, Encoding_Human, Encoding_List, Encoding_Next_Line
from zato.common.model.file_transfer_ import Default_Head_Size, FileTransferItem
from zato.common.test.file_transfer_harness.encoding_samples import Encoding_Samples, sample_bytes, sample_lines, \
    sample_text
from zato.common.test.xdm_builder import build_ccd_package, read_sample

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

_source = Documents.Source

# The encodings whose byte order mark a file may open with
_unicode_encodings = (Encoding.UTF_8, Encoding.UTF_16_LE, Encoding.UTF_16_BE)

# What an EDIFACT segment ends with
_segment_terminator = "'"

# A byte that Windows-1250 and Windows-1252 read as two different letters
_central_european_byte = b'\xe8'

# The line break of the EBCDIC encodings
_next_line = '\x85'

# How many lines or records a text needs to be read in more than one chunk
_chunk_crossing_count = 200_000

# ################################################################################################################################
# ################################################################################################################################

def _item(data:'bytes', encoding:'str', file_name:'str' = 'invoices.txt') -> 'FileTransferItem':
    out = FileTransferItem.from_bytes('outconn-sftp', 'Partner SFTP', 'invoices.hourly', '/incoming', file_name,
        f'/incoming/{file_name}', '2026-10-20T08:00:00+00:00', data, encoding)
    return out

# ################################################################################################################################

def _lines_of(item:'FileTransferItem') -> 'strlist':
    out:'strlist' = []

    for line in item:
        out.append(line)

    return out

# ################################################################################################################################

def _records_of(item:'FileTransferItem', terminator:'str') -> 'strlist':
    out:'strlist' = []

    for record in item.records(terminator):
        out.append(record)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_every_encoding_has_a_label_and_a_sample() -> 'None':

    for encoding in Encoding_List:
        assert Encoding_Human[encoding]
        assert Encoding_Samples[encoding]

# ################################################################################################################################

@mark.parametrize('encoding', Encoding_List)
def test_text_is_read_in_the_encoding(encoding:'str') -> 'None':

    data = sample_bytes(encoding)
    item = _item(data, encoding)

    assert item.text == sample_text(encoding)
    assert item.size == len(data)

# ################################################################################################################################

@mark.parametrize('encoding', Encoding_List)
def test_lines_are_read_in_the_encoding(encoding:'str') -> 'None':

    item = _item(sample_bytes(encoding), encoding)

    assert _lines_of(item) == sample_lines(encoding)

# ################################################################################################################################

@mark.parametrize('encoding', Encoding_List)
def test_windows_line_breaks_are_not_part_of_lines(encoding:'str') -> 'None':

    item = _item(sample_bytes(encoding, '\r\n'), encoding)

    assert _lines_of(item) == sample_lines(encoding)

# ################################################################################################################################

@mark.parametrize('encoding', Encoding_List)
def test_records_are_read_in_the_encoding(encoding:'str') -> 'None':

    lines = sample_lines(encoding)

    text = ''
    for line in lines:
        text += line + _segment_terminator

    item = _item(text.encode(encoding), encoding)

    assert _records_of(item, _segment_terminator) == lines

# ################################################################################################################################

@mark.parametrize('encoding', Encoding_List)
def test_open_text_is_read_in_the_encoding(encoding:'str') -> 'None':

    item = _item(sample_bytes(encoding), encoding)

    with item.open_text() as text_file:
        text = text_file.read()

    assert text == sample_text(encoding)

# ################################################################################################################################

@mark.parametrize('encoding', Encoding_List)
def test_data_is_the_bytes_as_received(encoding:'str') -> 'None':

    data = sample_bytes(encoding)
    item = _item(data, encoding)

    assert item.data == data

# ################################################################################################################################

@mark.parametrize('encoding', _unicode_encodings)
def test_byte_order_mark_is_not_part_of_the_text(encoding:'str') -> 'None':

    data = sample_bytes(encoding, should_add_byte_order_mark=True)
    item = _item(data, encoding)

    assert item.text == sample_text(encoding)
    assert _lines_of(item) == sample_lines(encoding)
    assert _records_of(item, '\n') == sample_lines(encoding)

    # The bytes still open with the mark
    assert item.data == data

# ################################################################################################################################

@mark.parametrize('encoding', _unicode_encodings)
def test_byte_order_mark_is_not_part_of_open_text(encoding:'str') -> 'None':

    item = _item(sample_bytes(encoding, should_add_byte_order_mark=True), encoding)

    with item.open_text() as text_file:
        first_line = text_file.readline()

    expected = sample_lines(encoding)[0] + '\n'
    assert first_line == expected

# ################################################################################################################################

def test_byte_order_mark_alone_is_an_empty_text() -> 'None':

    item = _item(b'\xef\xbb\xbf', Encoding.UTF_8)

    assert item.text == ''
    assert _lines_of(item) == []

# ################################################################################################################################

def test_empty_file() -> 'None':

    item = _item(b'', Encoding.CP1250)

    assert item.size == 0
    assert item.data == b''
    assert item.text == ''
    assert _lines_of(item) == []
    assert _records_of(item, _segment_terminator) == []
    assert item.head() == b''

    chunks = list(item.chunks())
    assert chunks == []

# ################################################################################################################################

def test_the_same_bytes_read_in_two_encodings() -> 'None':

    western = _item(_central_european_byte, Encoding.CP1252)
    central = _item(_central_european_byte, Encoding.CP1250)

    assert western.text == 'è'
    assert central.text == 'č'

# ################################################################################################################################

@mark.parametrize('encoding', (Encoding.CP1250, Encoding.CP1253, Encoding.CP1255, Encoding.ISO_8859_2, Encoding.CP852))
def test_wrong_encoding_raises_an_error(encoding:'str') -> 'None':

    # A single-byte encoding's letters above the ASCII range are not valid UTF-8 on their own
    item = _item(sample_bytes(encoding), Encoding.UTF_8)

    with raises(UnicodeDecodeError):
        _ = item.text

    with raises(UnicodeDecodeError):
        _ = _lines_of(item)

    with raises(UnicodeDecodeError):
        _ = _records_of(item, _segment_terminator)

# ################################################################################################################################

def test_a_close_encoding_reads_a_different_text() -> 'None':

    # Every byte has a meaning in ISO-8859-1, so the euro sign of a Windows-1252 file raises nothing
    # and becomes a control character instead.
    item = _item(sample_bytes(Encoding.CP1252), Encoding.ISO_8859_1)

    assert '€' not in item.text
    assert '\x80' in item.text

# ################################################################################################################################

def test_records_trailing_text_without_a_terminator_is_the_last_record() -> 'None':

    item = _item("UNH+1'BGM+220'UNT+3".encode('ascii'), Encoding.UTF_8)

    assert _records_of(item, _segment_terminator) == ['UNH+1', 'BGM+220', 'UNT+3']

# ################################################################################################################################

def test_records_skip_line_breaks_between_them() -> 'None':

    item = _item("UNH+1'\r\nBGM+220'\n\nUNT+3'\n".encode('ascii'), Encoding.UTF_8)

    assert _records_of(item, _segment_terminator) == ['UNH+1', 'BGM+220', 'UNT+3']

# ################################################################################################################################

def test_records_span_the_chunks_text_is_read_in() -> 'None':

    # Enough records for the text to be read in more than one chunk, with records crossing the boundaries
    record_count = _chunk_crossing_count
    expected:'strlist' = []

    text = ''
    for index in range(record_count):
        record = f'Ελλάδα-{index}'
        expected.append(record)
        text += record + _segment_terminator

    item = _item(text.encode(Encoding.CP1253), Encoding.CP1253)

    assert _records_of(item, _segment_terminator) == expected

# ################################################################################################################################

def test_records_with_a_terminator_longer_than_one_character() -> 'None':

    item = _item('first||second||third'.encode(Encoding.CP1250), Encoding.CP1250)

    assert _records_of(item, '||') == ['first', 'second', 'third']

# ################################################################################################################################

def test_chunks_give_back_every_byte_in_order() -> 'None':

    data = sample_bytes(Encoding.CP1257) * 100
    item = _item(data, Encoding.CP1257)

    received = b''
    chunk_sizes:'intlist' = []

    for chunk in item.chunks(64):
        received += chunk
        chunk_size = len(chunk)
        chunk_sizes.append(chunk_size)

    assert received == data
    assert max(chunk_sizes) == 64

# ################################################################################################################################

def test_head_is_the_first_bytes() -> 'None':

    data = sample_bytes(Encoding.CP037) * 1000
    item = _item(data, Encoding.CP037)

    assert item.head() == data[:Default_Head_Size]
    assert item.head(10) == data[:10]

# ################################################################################################################################

def test_open_gives_the_bytes() -> 'None':

    data = sample_bytes(Encoding.UTF_16_BE, should_add_byte_order_mark=True)
    item = _item(data, Encoding.UTF_16_BE)

    with item.open() as binary_file:
        received = binary_file.read()

    assert received == data

# ################################################################################################################################

def test_csv_reader_reads_open_text() -> 'None':

    text = 'name;city\r\nMüller;Zürich\r\nPeña;Málaga\r\n'
    item = _item(text.encode(Encoding.CP1252), Encoding.CP1252, 'customers.csv')

    rows = []

    with item.open_text() as text_file:
        for row in csv_reader(text_file, delimiter=';'):
            rows.append(row)

    assert rows == [['name', 'city'], ['Müller', 'Zürich'], ['Peña', 'Málaga']]

# ################################################################################################################################

def test_ebcdic_text_is_not_ascii() -> 'None':

    encoding = Encoding.CP037
    item = _item(sample_bytes(encoding), encoding)

    # The bytes of an EBCDIC file mean something else in ASCII ..
    assert not item.data.startswith(b'Invoice')

    # .. while its text is read as it was written.
    assert item.text.startswith('Invoice')

# ################################################################################################################################

@mark.parametrize('encoding', Encoding_Next_Line)
def test_ebcdic_next_line_breaks_end_lines(encoding:'str') -> 'None':

    item = _item(sample_bytes(encoding, _next_line), encoding)

    assert _lines_of(item) == sample_lines(encoding)
    assert item.text == sample_text(encoding)
    assert item.to_dict()['data'] == sample_text(encoding)

# ################################################################################################################################

@mark.parametrize('encoding', Encoding_Next_Line)
def test_ebcdic_next_line_breaks_are_not_part_of_records(encoding:'str') -> 'None':

    lines = sample_lines(encoding)

    text = ''
    for line in lines:
        text += line + _segment_terminator + _next_line

    item = _item(text.encode(encoding), encoding)

    assert _records_of(item, _segment_terminator) == lines

# ################################################################################################################################

def test_a_next_line_character_outside_ebcdic_is_text() -> 'None':

    # In ISO-8859-1 the byte 0x85 is a control character and not a line break
    item = _item(b'first\x85second\n', Encoding.ISO_8859_1)

    assert _lines_of(item) == ['first\x85second']

# ################################################################################################################################

def test_lines_span_the_chunks_text_is_read_in() -> 'None':

    expected:'strlist' = []

    text = ''
    for index in range(_chunk_crossing_count):
        line = f'עברית-{index}'
        expected.append(line)
        text += line + '\r\n'

    item = _item(text.encode(Encoding.CP1255), Encoding.CP1255)

    assert _lines_of(item) == expected

# ################################################################################################################################

def test_empty_lines_are_kept_and_a_last_line_needs_no_line_break() -> 'None':

    item = _item(b'first\n\nthird\n\nfifth', Encoding.UTF_8)

    assert _lines_of(item) == ['first', '', 'third', '', 'fifth']

# ################################################################################################################################

def test_documents_of_a_bare_file() -> 'None':

    data = read_sample('Discharge_Summary.ccda')
    item = _item(data, Encoding.UTF_8, 'Discharge_Summary.xml')

    documents = item.documents()

    assert len(documents) == 1
    assert documents[0].data == data
    assert documents[0].file_name == 'Discharge_Summary.xml'
    assert documents[0].source == _source.Attachment

# ################################################################################################################################

def test_documents_of_a_plain_archive() -> 'None':

    buffer = BytesIO()

    with ZipFile(buffer, 'w') as zip_file:
        zip_file.writestr('first.txt', sample_bytes(Encoding.CP1250))
        zip_file.writestr('second.txt', sample_bytes(Encoding.CP1255))

    item = _item(buffer.getvalue(), Encoding.UTF_8, 'bundle.zip')

    documents = item.documents()

    assert len(documents) == 2
    assert documents[0].file_name == 'first.txt'
    assert documents[0].data == sample_bytes(Encoding.CP1250)
    assert documents[1].file_name == 'second.txt'
    assert documents[1].data == sample_bytes(Encoding.CP1255)

# ################################################################################################################################

def test_documents_of_an_xdm_package() -> 'None':

    item = _item(build_ccd_package(), Encoding.UTF_8, 'package.zip')

    documents = item.documents()

    assert len(documents) == 2
    assert documents[0].source == _source.XDM
    assert documents[0].data == read_sample('CCD.ccda')

# ################################################################################################################################
# ################################################################################################################################
