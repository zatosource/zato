# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from hashlib import sha256
from tempfile import gettempdir, mkstemp

# gevent
from gevent.fileobject import FileObjectThread

# ################################################################################################################################
# ################################################################################################################################

# The environment variable naming the directory that received files are spooled to.
Env_Spool_Directory = 'Zato_File_Transfer_Spool_Directory'

# How many bytes at a time a spool file is written, read and hashed in.
Chunk_Size = 1024 * 1024

# What a spool file's name ends with, so a stray one can be told apart in the spool directory.
_spool_suffix = '-zato-file-transfer-read.dat'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SpooledFile:
    """ One remote file read into a local spool file - the spool file's path, the size in bytes
    and the SHA-256 checksum of the bytes.
    """
    path:     str = ''
    size:     int = 0
    checksum: str = ''

# ################################################################################################################################
# ################################################################################################################################

def get_spool_directory() -> 'str':
    """ Returns the directory that received files are spooled to - the system's temporary directory
    unless the environment names another one.
    """
    if directory := os.environ.get(Env_Spool_Directory, ''):
        out = directory
    else:
        out = gettempdir()

    return out

# ################################################################################################################################

def new_spool_path() -> 'str':
    """ Creates a new, empty spool file and returns its path.
    """
    directory = get_spool_directory()

    spool_descriptor, out = mkstemp(suffix=_spool_suffix, dir=directory)
    os.close(spool_descriptor)

    return out

# ################################################################################################################################

def delete_spool(path:'str') -> 'None':
    os.remove(path)

# ################################################################################################################################

def spooled_file_from_path(path:'str') -> 'SpooledFile':
    """ Describes a spool file that something else has already written, reading it chunk by chunk
    to compute its size and checksum. Each chunk is read in a separate thread so as not to block the event loop.
    """
    hasher = sha256()
    size = 0

    thread_file = FileObjectThread(path, 'rb')

    try:
        while chunk := thread_file.read(Chunk_Size):
            hasher.update(chunk)
            chunk_size = len(chunk)
            size += chunk_size
    finally:
        thread_file.close()

    out = SpooledFile()
    out.path = path
    out.size = size
    out.checksum = hasher.hexdigest()

    return out

# ################################################################################################################################

def spool_bytes(data:'bytes') -> 'SpooledFile':
    """ Writes bytes already in memory to a new spool file.
    """
    writer = SpoolWriter()

    try:
        writer.write(data)
    except Exception:
        writer.discard()
        raise

    out = writer.finish()
    return out

# ################################################################################################################################
# ################################################################################################################################

class FileWriter:
    """ Writes the chunks of one file to a local path as they arrive, counting and hashing them on the way,
    so a file of any size is written without being held in memory.
    """

    def __init__(self, path:'str') -> 'None':
        self.path = path
        self.size = 0
        self._hasher = sha256()
        self._file = open(self.path, 'wb', buffering=Chunk_Size)

# ################################################################################################################################

    def write(self, chunk:'bytes') -> 'None':

        _ = self._file.write(chunk)
        self._hasher.update(chunk)

        chunk_size = len(chunk)
        self.size += chunk_size

# ################################################################################################################################

    def finish(self) -> 'SpooledFile':
        """ Closes the file once the last chunk is written and describes it.
        """
        self._file.close()

        out = SpooledFile()
        out.path = self.path
        out.size = self.size
        out.checksum = self._hasher.hexdigest()

        return out

# ################################################################################################################################

    def discard(self) -> 'None':
        """ Closes and deletes the file of a read that did not complete.
        """
        self._file.close()
        os.remove(self.path)

# ################################################################################################################################
# ################################################################################################################################

class SpoolWriter(FileWriter):
    """ Writes the chunks of one file to a new spool file as they arrive.
    """

    def __init__(self) -> 'None':
        path = new_spool_path()
        super().__init__(path)

# ################################################################################################################################
# ################################################################################################################################
