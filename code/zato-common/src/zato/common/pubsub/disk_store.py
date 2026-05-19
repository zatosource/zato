# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import threading
from logging import getLogger
from typing import NamedTuple

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.crypto.api import CryptoManager
    CryptoManager = CryptoManager

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_file_version  = '1'
_data_key      = 'data'
_encrypted_key = 'encrypted'

# ################################################################################################################################
# ################################################################################################################################

class LoadResult(NamedTuple):
    data:'str'
    data_class:'str'

# ################################################################################################################################
# ################################################################################################################################

class DiskMessageStore:
    """ Stores pub/sub message payloads on disk in a sharded directory tree.
    Each message is a plain-text key=value file. The `data` key is always last
    and its value extends to EOF, allowing multi-line payloads without escaping.
    """

    def __init__(self, base_dir:'str', crypto_manager:'CryptoManager | None' = None) -> 'None':

        # Store the configuration ..
        self.base_dir = base_dir
        self.crypto_manager = crypto_manager

        # .. and ensure the base directory exists.
        os.makedirs(base_dir, exist_ok=True)

# ################################################################################################################################

    def store(self, message_id:'str', topic_name:'str', data:'str', data_class:'str',
        encrypt:'bool' = False) -> 'str':
        """ Write a message payload file and return the data_ref (relative path).
        """

        # Build the sharded relative path ..
        data_reference = self.make_ref(message_id, topic_name)

        # .. resolve to absolute ..
        absolute_path = self._ref_to_path(data_reference)

        # .. ensure the parent directory exists ..
        parent_dir = os.path.dirname(absolute_path)
        os.makedirs(parent_dir, exist_ok=True)

        # .. optionally encrypt the payload before writing ..
        if encrypt:
            crypto_manager = cast_('CryptoManager', self.crypto_manager)
            data_to_write = crypto_manager.encrypt(data, needs_str=True)
        else:
            data_to_write = data

        # .. write the key=value file with data as the last entry ..
        version_line    = f'_version={_file_version}\n'
        message_id_line = f'msg_id={message_id}\n'
        topic_line      = f'topic_name={topic_name}\n'
        data_class_line = f'data_class={data_class}\n'
        encrypted_line  = f'{_encrypted_key}=true\n'
        data_line       = f'{_data_key}={data_to_write}'

        with open(absolute_path, 'w', encoding='utf-8') as file_handle:
            _ = file_handle.write(version_line)
            _ = file_handle.write(message_id_line)
            _ = file_handle.write(topic_line)
            _ = file_handle.write(data_class_line)

            if encrypt:
                _ = file_handle.write(encrypted_line)

            _ = file_handle.write(data_line)

        data_len = len(data)
        thread_name = threading.current_thread().name
        logger.info(
            'Stored message payload -> message_id:%s, topic:%s, path:%s, data_len:%s, encrypted:%s, thread:%s',
            message_id, topic_name, absolute_path, data_len, encrypt, thread_name)

        out = data_reference
        return out

# ################################################################################################################################

    def load(self, data_reference:'str') -> 'LoadResult':
        """ Read a message payload file and return (data, data_class).
        """

        # Resolve the absolute path ..
        absolute_path = self._ref_to_path(data_reference)
        file_exists   = os.path.exists(absolute_path)
        thread_name   = threading.current_thread().name

        logger.info(
            'Loading message payload -> data_ref:%s, path:%s, file_exists:%s, thread:%s',
            data_reference, absolute_path, file_exists, thread_name)

        # .. read the file content ..
        try:
            with open(absolute_path, 'r', encoding='utf-8') as file_handle:
                content = file_handle.read()
        except FileNotFoundError:
            logger.error(
                'FileNotFoundError in load -> data_ref:%s, path:%s, thread:%s',
                data_reference, absolute_path, thread_name, exc_info=True)
            raise

        # .. parse key=value lines (the `data` key is always last,
        # everything after `data=` is the value and may span multiple lines) ..
        data_class   = ''
        data         = ''
        is_encrypted = False

        data_marker = f'{_data_key}='
        encrypted_marker = f'{_encrypted_key}='
        data_marker_position = content.find(data_marker)

        if data_marker_position != -1:

            # .. everything after `data=` is the payload ..
            data_start = data_marker_position + len(data_marker)
            data = content[data_start:]

            # .. parse the header lines before data ..
            header = content[:data_marker_position]

            for line in header.splitlines():
                if line.startswith('data_class='):
                    data_class = line[len('data_class='):]
                elif line.startswith(encrypted_marker):
                    is_encrypted = line[len(encrypted_marker):] == 'true'

        # .. decrypt the payload if the file was encrypted ..
        if is_encrypted:
            crypto_manager = cast_('CryptoManager', self.crypto_manager)
            data = crypto_manager.decrypt(data)

        data_len = len(data)
        logger.info(
            'Loaded message payload -> data_ref:%s, path:%s, data_len:%s, data_class:%s, encrypted:%s',
            data_reference, absolute_path, data_len, data_class, is_encrypted)

        out = LoadResult(data=data, data_class=data_class)
        return out

# ################################################################################################################################

    def delete(self, data_reference:'str') -> 'None':
        """ Remove the payload file from disk.
        """

        # Resolve the path and attempt removal ..
        absolute_path = self._ref_to_path(data_reference)
        thread_name = threading.current_thread().name

        logger.info('Deleting message payload -> data_ref:%s, path:%s, thread:%s',
            data_reference, absolute_path, thread_name)

        try:
            os.remove(absolute_path)
        except FileNotFoundError:
            logger.info('Payload file already removed -> data_ref:%s, path:%s, thread:%s',
                data_reference, absolute_path, thread_name)

# ################################################################################################################################

    def rename_topic_dir(self, old_topic_name:'str', new_topic_name:'str') -> 'None':
        """ Rename the on-disk directory tree for a topic.
        """

        # Build the old and new paths ..
        old_path = os.path.join(self.base_dir, old_topic_name)
        new_path = os.path.join(self.base_dir, new_topic_name)

        if not os.path.exists(old_path):
            logger.info('Topic directory does not exist, nothing to rename -> old_path:%s', old_path)
            return

        # .. and rename.
        logger.info('Renaming topic directory -> old_path:%s, new_path:%s', old_path, new_path)
        os.rename(old_path, new_path)

# ################################################################################################################################

    def delete_topic_dir(self, topic_name:'str') -> 'None':
        """ Remove the entire on-disk directory tree for a topic.
        """

        # Build the path ..
        topic_path = os.path.join(self.base_dir, topic_name)

        if not os.path.exists(topic_path):
            logger.info('Topic directory does not exist, nothing to delete -> topic_path:%s', topic_path)
            return

        # .. and remove the tree.
        logger.info('Deleting topic directory -> topic_path:%s', topic_path)
        shutil.rmtree(topic_path)

# ################################################################################################################################

    def _ref_to_path(self, data_reference:'str') -> 'str':
        """ Resolve a relative data_ref to an absolute filesystem path.
        """

        out = os.path.join(self.base_dir, data_reference)
        return out

# ################################################################################################################################

    def make_ref(self, message_id:'str', topic_name:'str') -> 'str':
        """ Compute the sharded relative path for a message.

        Layout: <topic_name>/<shard1>/<shard2>/<message_id>.msg

        Shard levels are derived from the hex random portion of the message ID.
        Message IDs look like 'zpsm.20260517-113200-1234-abcdef1234567890f'
        so we take chars from the hex tail for even distribution.
        """

        # Extract the last 16-char hex segment for sharding ..
        hex_part = message_id.rsplit('-', 1)[-1]

        shard_level_1 = hex_part[:2]
        shard_level_2 = hex_part[2:4]

        # .. and build the relative path.
        file_name = f'{message_id}.msg'

        out = os.path.join(topic_name, shard_level_1, shard_level_2, file_name)
        return out

# ################################################################################################################################
# ################################################################################################################################
