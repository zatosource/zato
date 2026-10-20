# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from hashlib import sha256
from tempfile import gettempdir

# Zato
from zato.common.file_transfer.api import Encoding
from zato.common.file_transfer.spool import delete_spool, Env_Spool_Directory, FileWriter, get_spool_directory, \
    new_spool_path, spool_bytes, spooled_file_from_path, SpoolWriter
from zato.common.test.file_transfer_harness.encoding_samples import sample_bytes

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _checksum(data:'bytes') -> 'str':
    hasher = sha256(data)
    out = hasher.hexdigest()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_spool_directory_is_the_one_from_the_environment(spool_directory:'any_') -> 'None':
    assert get_spool_directory() == str(spool_directory)

# ################################################################################################################################

def test_spool_directory_is_the_temporary_directory_by_default(monkeypatch:'any_') -> 'None':
    monkeypatch.delenv(Env_Spool_Directory)
    assert get_spool_directory() == gettempdir()

# ################################################################################################################################

def test_new_spool_path_is_an_empty_file_in_the_spool_directory(spool_directory:'any_') -> 'None':

    path = new_spool_path()

    assert os.path.dirname(path) == str(spool_directory)
    assert os.path.getsize(path) == 0

# ################################################################################################################################

def test_new_spool_paths_are_unique() -> 'None':

    first = new_spool_path()
    second = new_spool_path()

    assert first != second

# ################################################################################################################################

def test_delete_spool(spool_directory:'any_') -> 'None':

    path = new_spool_path()
    delete_spool(path)

    assert os.listdir(spool_directory) == []

# ################################################################################################################################

def test_writer_counts_and_hashes_every_chunk() -> 'None':

    chunks = [sample_bytes(Encoding.CP1250), sample_bytes(Encoding.CP1253), sample_bytes(Encoding.UTF_16_LE)]
    data = b''.join(chunks)

    writer = SpoolWriter()

    for chunk in chunks:
        writer.write(chunk)

    spooled = writer.finish()

    with open(spooled.path, 'rb') as spool_file:
        written = spool_file.read()

    assert written == data
    assert spooled.size == len(data)
    assert spooled.checksum == _checksum(data)

# ################################################################################################################################

def test_writer_with_no_chunks_is_an_empty_file() -> 'None':

    writer = SpoolWriter()
    spooled = writer.finish()

    assert spooled.size == 0
    assert spooled.checksum == _checksum(b'')
    assert os.path.getsize(spooled.path) == 0

# ################################################################################################################################

def test_writer_discard_deletes_the_spool_file(spool_directory:'any_') -> 'None':

    writer = SpoolWriter()
    writer.write(b'part of a file whose read did not complete')
    writer.discard()

    assert os.listdir(spool_directory) == []

# ################################################################################################################################

def test_spooled_file_from_path_reads_size_and_checksum() -> 'None':

    # More than one chunk, so the checksum is built up across reads
    data = sample_bytes(Encoding.CP1255) * 40_000

    path = new_spool_path()

    with open(path, 'wb') as spool_file:
        _ = spool_file.write(data)

    spooled = spooled_file_from_path(path)

    assert spooled.path == path
    assert spooled.size == len(data)
    assert spooled.checksum == _checksum(data)

# ################################################################################################################################

def test_spool_bytes() -> 'None':

    data = sample_bytes(Encoding.ISO_8859_8)
    spooled = spool_bytes(data)

    with open(spooled.path, 'rb') as spool_file:
        written = spool_file.read()

    assert written == data
    assert spooled.size == len(data)
    assert spooled.checksum == _checksum(data)

# ################################################################################################################################

def test_file_writer_writes_to_the_path_it_was_given(tmp_path:'any_', spool_directory:'any_') -> 'None':

    # The spool directory is the test's temporary directory, so the file goes to a directory of its own
    download_directory = os.path.join(str(tmp_path), 'downloads')
    os.makedirs(download_directory)

    path = os.path.join(download_directory, 'downloaded.csv')
    data = sample_bytes(Encoding.CP1257)

    writer = FileWriter(path)
    writer.write(data)
    described = writer.finish()

    with open(path, 'rb') as local_file:
        written = local_file.read()

    # The file is where it was asked to be and nothing went to the spool directory
    assert written == data
    assert described.path == path
    assert described.size == len(data)
    assert described.checksum == _checksum(data)
    assert os.listdir(spool_directory) == ['downloads']

# ################################################################################################################################

def test_file_writer_discard_deletes_its_file(tmp_path:'any_') -> 'None':

    path = os.path.join(str(tmp_path), 'downloaded.csv')

    writer = FileWriter(path)
    writer.write(b'part of a file whose download did not complete')
    writer.discard()

    assert not os.path.exists(path)

# ################################################################################################################################
# ################################################################################################################################
