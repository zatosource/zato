# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from shutil import rmtree

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# How many bits of randomness go into the names of the directories and connections that tests create
_name_bits = 48

# ################################################################################################################################
# ################################################################################################################################

class FileTransferAdapter:
    """ Everything one protocol must supply for the shared file transfer schedule tests to run against it.
    A protocol is added to the suite by writing one subclass of this and nothing else.
    """

    # The GENERIC.CONNECTION.TYPE.* value of the connections this protocol creates. The job name prefix
    # and the dispatch service follow from it through FileTransfer.Scheduler, so they are never declared here.
    conn_type = ''

    # Every connection a test creates starts with this, which is how the cleanup pass recognises its own leftovers
    conn_name_prefix = ''

    # How long an assertion about the remote side may keep polling before it gives up, in seconds.
    # A protocol whose writes are visible at once leaves this at zero and nothing waits.
    settle_timeout = 0.0

    # How long to sleep between two looks at the remote side while polling, in seconds
    settle_sleep_time = 0.2

    # Whether a file can be renamed in place, without which claiming a file cannot work at all
    supports_claim = True

    # Whether a file can be moved rather than only deleted once its target service has finished with it
    supports_move = True

    # Whether the remote side has directories that can hold other directories
    supports_subdirectories = True

    # Whether a file name may contain a space
    supports_names_with_spaces = True

    # Whether the test server can be stopped and started again while the suite runs
    supports_server_restart = True

    # Whether the remote side has symbolic links at all
    supports_symlinks = False

    # Whether two looks at an unchanged file report the same modification time, which is what
    # stability mode compares. A protocol without it can only run marker mode.
    preserves_last_modified = True

    # Whether two names differing only in case are two different files
    is_case_sensitive = True

# ################################################################################################################################

    def start_server(self) -> 'None':
        """ Starts the test server this protocol talks to.
        """
        raise Exception('Adapters must implement start_server')

# ################################################################################################################################

    def stop_server(self) -> 'None':
        """ Stops the test server and removes everything it used, which ends the suite for this protocol.
        """
        raise Exception('Adapters must implement stop_server')

# ################################################################################################################################

    def restart_server(self) -> 'None':
        """ Stops the test server and starts it again, keeping the files it serves.
        """
        raise Exception('Adapters must implement restart_server')

# ################################################################################################################################

    def pause_server(self) -> 'None':
        """ Takes the test server away for a while, keeping the files it serves, which is how a test
        asks for a remote side that cannot be reached. The suite goes on afterwards, so nothing
        the server serves may be removed here.
        """
        raise Exception('Adapters must implement pause_server')

# ################################################################################################################################

    def resume_server(self) -> 'None':
        """ Brings a paused test server back, with everything it serves as it was.
        """
        raise Exception('Adapters must implement resume_server')

# ################################################################################################################################

    def create_conn_payload(self, name:'str') -> 'anydict':
        """ The protocol-specific half of a zato.generic.connection.create request.
        """
        raise Exception('Adapters must implement create_conn_payload')

# ################################################################################################################################

    def edit_conn_payload(self, name:'str') -> 'anydict':
        """ The protocol-specific half of a zato.generic.connection.edit request.
        """
        raise Exception('Adapters must implement edit_conn_payload')

# ################################################################################################################################

    def remote_join(self, directory:'str', name:'str') -> 'str':
        """ Joins a name onto a remote directory the way this protocol writes its paths.
        """
        raise Exception('Adapters must implement remote_join')

# ################################################################################################################################

    def make_directory(self) -> 'str':
        """ Creates a fresh directory for one test's files and returns it in the shape
        that a schedule's directory field takes for this protocol.
        """
        raise Exception('Adapters must implement make_directory')

# ################################################################################################################################

    def make_subdirectory(self, directory:'str', name:'str') -> 'str':
        """ Creates a directory inside another one and returns its remote path.
        """
        raise Exception('Adapters must implement make_subdirectory')

# ################################################################################################################################

    def write_file(self, directory:'str', name:'str', data:'bytes') -> 'None':
        """ Puts a file on the remote side, replacing whatever was there before.
        """
        raise Exception('Adapters must implement write_file')

# ################################################################################################################################

    def append_file(self, directory:'str', name:'str', data:'bytes') -> 'None':
        """ Adds to the end of a file that is already there, which is how a test makes an upload
        look like it is still in progress.
        """
        raise Exception('Adapters must implement append_file')

# ################################################################################################################################

    def read_file(self, directory:'str', name:'str') -> 'bytes':
        """ Returns the contents of one file on the remote side.
        """
        raise Exception('Adapters must implement read_file')

# ################################################################################################################################

    def list_names(self, directory:'str') -> 'strlist':
        """ Returns the sorted names of everything one remote directory holds.
        """
        raise Exception('Adapters must implement list_names')

# ################################################################################################################################

    def exists(self, directory:'str', name:'str') -> 'bool':
        """ Whether one entry is present in a remote directory.
        """
        raise Exception('Adapters must implement exists')

# ################################################################################################################################

    def delete_file(self, directory:'str', name:'str') -> 'None':
        """ Removes one file from the remote side.
        """
        raise Exception('Adapters must implement delete_file')

# ################################################################################################################################

    def make_symlink(self, directory:'str', name:'str', target:'str') -> 'None':
        """ Creates a symbolic link inside a remote directory, only ever called by protocols
        that declare supports_symlinks.
        """
        raise Exception('Adapters must implement make_symlink')

# ################################################################################################################################

    def new_conn_name(self) -> 'str':
        """ A connection name that no other test uses.
        """
        suffix = CryptoManager.generate_hex_string(_name_bits)

        out = self.conn_name_prefix + suffix
        return out

# ################################################################################################################################
# ################################################################################################################################

class LocalBackedRemote:
    """ The inspection and path methods of an adapter whose test server serves a directory
    on this very machine. This is the only place where the remote side is inspected through
    the local filesystem, so a protocol served from somewhere else brings its own implementations
    and nothing above the adapter notices the difference.

    A protocol mixing this in supplies local_root, plus remote_directory_for and to_local
    to say how its remote paths map onto that directory.
    """

    # The directory on this machine that the test server serves, set by the adapter once its server is up
    local_root = ''

# ################################################################################################################################

    def remote_directory_for(self, name:'str') -> 'str':
        """ The remote path of a directory sitting directly under the served directory.
        """
        raise Exception('Local-backed adapters must implement remote_directory_for')

# ################################################################################################################################

    def to_local(self, remote_path:'str') -> 'str':
        """ The path on this machine of something the remote side calls remote_path.
        """
        raise Exception('Local-backed adapters must implement to_local')

# ################################################################################################################################

    def remote_join(self, directory:'str', name:'str') -> 'str':
        out = f'{directory}/{name}'
        return out

# ################################################################################################################################

    def _local_path(self, directory:'str', name:'str') -> 'str':
        """ The path on this machine of one entry of a remote directory.
        """
        remote_path = self.remote_join(directory, name)

        out = self.to_local(remote_path)
        return out

# ################################################################################################################################

    def make_directory(self) -> 'str':
        name = CryptoManager.generate_hex_string(_name_bits)
        out = self.remote_directory_for(name)

        local_path = self.to_local(out)
        os.mkdir(local_path)

        return out

# ################################################################################################################################

    def make_subdirectory(self, directory:'str', name:'str') -> 'str':
        local_path = self._local_path(directory, name)
        os.mkdir(local_path)

        out = self.remote_join(directory, name)
        return out

# ################################################################################################################################

    def write_file(self, directory:'str', name:'str', data:'bytes') -> 'None':
        local_path = self._local_path(directory, name)

        with open(local_path, 'wb') as local_file:
            _ = local_file.write(data)

# ################################################################################################################################

    def append_file(self, directory:'str', name:'str', data:'bytes') -> 'None':
        local_path = self._local_path(directory, name)

        with open(local_path, 'ab') as local_file:
            _ = local_file.write(data)

# ################################################################################################################################

    def read_file(self, directory:'str', name:'str') -> 'bytes':
        local_path = self._local_path(directory, name)

        with open(local_path, 'rb') as local_file:
            out = local_file.read()

        return out

# ################################################################################################################################

    def list_names(self, directory:'str') -> 'strlist':
        local_path = self.to_local(directory)

        # A directory that was never created holds nothing, which is what the caller wants to know
        if not os.path.exists(local_path):
            out:'strlist' = []
            return out

        out = sorted(os.listdir(local_path))
        return out

# ################################################################################################################################

    def exists(self, directory:'str', name:'str') -> 'bool':
        local_path = self._local_path(directory, name)

        out = os.path.exists(local_path)
        return out

# ################################################################################################################################

    def delete_file(self, directory:'str', name:'str') -> 'None':
        local_path = self._local_path(directory, name)
        os.remove(local_path)

# ################################################################################################################################

    def delete_directory(self, directory:'str') -> 'None':
        local_path = self.to_local(directory)
        rmtree(local_path, ignore_errors=True)

# ################################################################################################################################

    def make_symlink(self, directory:'str', name:'str', target:'str') -> 'None':
        local_path = self._local_path(directory, name)
        local_target = self._local_path(directory, target)

        os.symlink(local_target, local_path)

# ################################################################################################################################
# ################################################################################################################################
