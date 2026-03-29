# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import fnmatch
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

# Zato
from zato.common.file_transfer.const import PickupSourceType, PostProcessingAction

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class FileInfo:
    name: 'str'
    path: 'str'
    size: 'int'
    modified_time: 'float'

# ################################################################################################################################
# ################################################################################################################################

class BasePickupSource(ABC):

    def __init__(self, connection:'any_'=None) -> 'None':
        self.connection = connection
        self._connected = False

    @abstractmethod
    def connect(self) -> 'None':
        raise NotImplementedError()

    @abstractmethod
    def disconnect(self) -> 'None':
        raise NotImplementedError()

    @abstractmethod
    def list_files(self, remote_path:'str', pattern:'str'='*') -> 'List[FileInfo]':
        raise NotImplementedError()

    @abstractmethod
    def download(self, file_info:'FileInfo') -> 'bytes':
        raise NotImplementedError()

    @abstractmethod
    def mark_processed(
        self,
        file_info:'FileInfo',
        action:'PostProcessingAction',
        archive_path:'str'='',
    ) -> 'None':
        raise NotImplementedError()

    def __enter__(self) -> 'BasePickupSource':
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> 'None':
        self.disconnect()

# ################################################################################################################################
# ################################################################################################################################

class SFTPPickupSource(BasePickupSource):

    def connect(self) -> 'None':
        if self.connection:
            self._connected = True

    def disconnect(self) -> 'None':
        self._connected = False

    def list_files(self, remote_path:'str', pattern:'str'='*') -> 'List[FileInfo]':
        files = []

        if not self.connection:
            return files

        try:
            for entry in self.connection.listdir_attr(remote_path):
                if fnmatch.fnmatch(entry.filename, pattern):
                    if not entry.st_mode or not (entry.st_mode & 0o40000):
                        full_path = f'{remote_path.rstrip("/")}/{entry.filename}'
                        files.append(FileInfo(
                            name=entry.filename,
                            path=full_path,
                            size=entry.st_size or 0,
                            modified_time=entry.st_mtime or 0,
                        ))
        except Exception as e:
            logger.warning('Error listing SFTP files: %s', e)

        return files

    def download(self, file_info:'FileInfo') -> 'bytes':
        if not self.connection:
            raise RuntimeError('Not connected')

        from io import BytesIO
        buffer = BytesIO()
        self.connection.getfo(file_info.path, buffer)
        return buffer.getvalue()

    def mark_processed(
        self,
        file_info:'FileInfo',
        action:'PostProcessingAction',
        archive_path:'str'='',
    ) -> 'None':

        if not self.connection:
            return

        action_val = action.value if isinstance(action, PostProcessingAction) else action

        if action_val == PostProcessingAction.Delete.value:
            self.connection.remove(file_info.path)

        elif action_val == PostProcessingAction.Move.value and archive_path:
            dest = f'{archive_path.rstrip("/")}/{file_info.name}'
            self.connection.rename(file_info.path, dest)

# ################################################################################################################################
# ################################################################################################################################

class FTPPickupSource(BasePickupSource):

    def connect(self) -> 'None':
        if self.connection:
            self._connected = True

    def disconnect(self) -> 'None':
        self._connected = False

    def list_files(self, remote_path:'str', pattern:'str'='*') -> 'List[FileInfo]':
        files = []

        if not self.connection:
            return files

        try:
            self.connection.cwd(remote_path)
            entries = []
            self.connection.dir(entries.append)

            for entry in entries:
                parts = entry.split()
                if len(parts) >= 9:
                    filename = ' '.join(parts[8:])
                    if fnmatch.fnmatch(filename, pattern):
                        if not entry.startswith('d'):
                            size = int(parts[4]) if parts[4].isdigit() else 0
                            full_path = f'{remote_path.rstrip("/")}/{filename}'
                            files.append(FileInfo(
                                name=filename,
                                path=full_path,
                                size=size,
                                modified_time=0,
                            ))
        except Exception as e:
            logger.warning('Error listing FTP files: %s', e)

        return files

    def download(self, file_info:'FileInfo') -> 'bytes':
        if not self.connection:
            raise RuntimeError('Not connected')

        from io import BytesIO
        buffer = BytesIO()
        self.connection.retrbinary(f'RETR {file_info.path}', buffer.write)
        return buffer.getvalue()

    def mark_processed(
        self,
        file_info:'FileInfo',
        action:'PostProcessingAction',
        archive_path:'str'='',
    ) -> 'None':

        if not self.connection:
            return

        action_val = action.value if isinstance(action, PostProcessingAction) else action

        if action_val == PostProcessingAction.Delete.value:
            self.connection.delete(file_info.path)

        elif action_val == PostProcessingAction.Move.value and archive_path:
            dest = f'{archive_path.rstrip("/")}/{file_info.name}'
            self.connection.rename(file_info.path, dest)

# ################################################################################################################################
# ################################################################################################################################

class S3PickupSource(BasePickupSource):

    def __init__(self, connection:'any_'=None, bucket:'str'='') -> 'None':
        super().__init__(connection)
        self.bucket = bucket

    def connect(self) -> 'None':
        if self.connection:
            self._connected = True

    def disconnect(self) -> 'None':
        self._connected = False

    def list_files(self, remote_path:'str', pattern:'str'='*') -> 'List[FileInfo]':
        files = []

        if not self.connection:
            return files

        try:
            prefix = remote_path.lstrip('/')
            if prefix and not prefix.endswith('/'):
                prefix += '/'

            response = self.connection.list_objects_v2(Bucket=self.bucket, Prefix=prefix)

            for obj in response.get('Contents', []):
                key = obj['Key']
                filename = key.split('/')[-1]

                if filename and fnmatch.fnmatch(filename, pattern):
                    files.append(FileInfo(
                        name=filename,
                        path=key,
                        size=obj.get('Size', 0),
                        modified_time=obj.get('LastModified', 0).timestamp() if hasattr(obj.get('LastModified'), 'timestamp') else 0,
                    ))
        except Exception as e:
            logger.warning('Error listing S3 files: %s', e)

        return files

    def download(self, file_info:'FileInfo') -> 'bytes':
        if not self.connection:
            raise RuntimeError('Not connected')

        response = self.connection.get_object(Bucket=self.bucket, Key=file_info.path)
        return response['Body'].read()

    def mark_processed(
        self,
        file_info:'FileInfo',
        action:'PostProcessingAction',
        archive_path:'str'='',
    ) -> 'None':

        if not self.connection:
            return

        action_val = action.value if isinstance(action, PostProcessingAction) else action

        if action_val == PostProcessingAction.Delete.value:
            self.connection.delete_object(Bucket=self.bucket, Key=file_info.path)

        elif action_val == PostProcessingAction.Move.value and archive_path:
            dest_key = f'{archive_path.lstrip("/").rstrip("/")}/{file_info.name}'
            self.connection.copy_object(
                Bucket=self.bucket,
                CopySource={'Bucket': self.bucket, 'Key': file_info.path},
                Key=dest_key,
            )
            self.connection.delete_object(Bucket=self.bucket, Key=file_info.path)

# ################################################################################################################################
# ################################################################################################################################

class AzureBlobPickupSource(BasePickupSource):

    def __init__(self, connection:'any_'=None, container:'str'='') -> 'None':
        super().__init__(connection)
        self.container = container

    def connect(self) -> 'None':
        if self.connection:
            self._connected = True

    def disconnect(self) -> 'None':
        self._connected = False

    def list_files(self, remote_path:'str', pattern:'str'='*') -> 'List[FileInfo]':
        files = []

        if not self.connection:
            return files

        try:
            prefix = remote_path.lstrip('/')
            if prefix and not prefix.endswith('/'):
                prefix += '/'

            container_client = self.connection.get_container_client(self.container)
            blobs = container_client.list_blobs(name_starts_with=prefix)

            for blob in blobs:
                filename = blob.name.split('/')[-1]

                if filename and fnmatch.fnmatch(filename, pattern):
                    files.append(FileInfo(
                        name=filename,
                        path=blob.name,
                        size=blob.size or 0,
                        modified_time=blob.last_modified.timestamp() if hasattr(blob.last_modified, 'timestamp') else 0,
                    ))
        except Exception as e:
            logger.warning('Error listing Azure Blob files: %s', e)

        return files

    def download(self, file_info:'FileInfo') -> 'bytes':
        if not self.connection:
            raise RuntimeError('Not connected')

        blob_client = self.connection.get_blob_client(container=self.container, blob=file_info.path)
        return blob_client.download_blob().readall()

    def mark_processed(
        self,
        file_info:'FileInfo',
        action:'PostProcessingAction',
        archive_path:'str'='',
    ) -> 'None':

        if not self.connection:
            return

        action_val = action.value if isinstance(action, PostProcessingAction) else action

        if action_val == PostProcessingAction.Delete.value:
            blob_client = self.connection.get_blob_client(container=self.container, blob=file_info.path)
            blob_client.delete_blob()

        elif action_val == PostProcessingAction.Move.value and archive_path:
            dest_path = f'{archive_path.lstrip("/").rstrip("/")}/{file_info.name}'

            source_blob = self.connection.get_blob_client(container=self.container, blob=file_info.path)
            dest_blob = self.connection.get_blob_client(container=self.container, blob=dest_path)

            dest_blob.start_copy_from_url(source_blob.url)
            source_blob.delete_blob()

# ################################################################################################################################
# ################################################################################################################################

class IMAPPickupSource(BasePickupSource):

    def __init__(self, connection:'any_'=None, folder:'str'='INBOX') -> 'None':
        super().__init__(connection)
        self.folder = folder

    def connect(self) -> 'None':
        if self.connection:
            self.connection.select(self.folder)
            self._connected = True

    def disconnect(self) -> 'None':
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self._connected = False

    def list_files(self, remote_path:'str', pattern:'str'='*') -> 'List[FileInfo]':
        files = []

        if not self.connection:
            return files

        try:
            _, message_numbers = self.connection.search(None, 'ALL')

            for num in message_numbers[0].split():
                _, msg_data = self.connection.fetch(num, '(RFC822)')

                import email
                msg = email.message_from_bytes(msg_data[0][1])

                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue

                    filename = part.get_filename()
                    if filename and fnmatch.fnmatch(filename, pattern):
                        content = part.get_payload(decode=True)
                        files.append(FileInfo(
                            name=filename,
                            path=f'{num.decode()}:{filename}',
                            size=len(content) if content else 0,
                            modified_time=0,
                        ))
        except Exception as e:
            logger.warning('Error listing IMAP files: %s', e)

        return files

    def download(self, file_info:'FileInfo') -> 'bytes':
        if not self.connection:
            raise RuntimeError('Not connected')

        parts = file_info.path.split(':', 1)
        msg_num = parts[0].encode()
        target_filename = parts[1] if len(parts) > 1 else ''

        _, msg_data = self.connection.fetch(msg_num, '(RFC822)')

        import email
        msg = email.message_from_bytes(msg_data[0][1])

        for part in msg.walk():
            filename = part.get_filename()
            if filename == target_filename:
                return part.get_payload(decode=True) or b''

        return b''

    def mark_processed(
        self,
        file_info:'FileInfo',
        action:'PostProcessingAction',
        archive_path:'str'='',
    ) -> 'None':

        if not self.connection:
            return

        action_val = action.value if isinstance(action, PostProcessingAction) else action

        parts = file_info.path.split(':', 1)
        msg_num = parts[0]

        if action_val == PostProcessingAction.Delete.value:
            self.connection.store(msg_num, '+FLAGS', '\\Deleted')
            self.connection.expunge()

        elif action_val == PostProcessingAction.Move.value and archive_path:
            self.connection.copy(msg_num, archive_path)
            self.connection.store(msg_num, '+FLAGS', '\\Deleted')
            self.connection.expunge()

# ################################################################################################################################
# ################################################################################################################################

def get_pickup_source(source_type:'PickupSourceType', connection:'any_'=None, **kwargs) -> 'BasePickupSource':

    source_type_val = source_type.value if isinstance(source_type, PickupSourceType) else source_type

    if source_type_val == PickupSourceType.Sftp.value:
        return SFTPPickupSource(connection)

    elif source_type_val == PickupSourceType.Ftp.value:
        return FTPPickupSource(connection)

    elif source_type_val == PickupSourceType.S3.value:
        return S3PickupSource(connection, bucket=kwargs.get('bucket', ''))

    elif source_type_val == PickupSourceType.Azure_Blob.value:
        return AzureBlobPickupSource(connection, container=kwargs.get('container', ''))

    elif source_type_val == PickupSourceType.Imap.value:
        return IMAPPickupSource(connection, folder=kwargs.get('folder', 'INBOX'))

    else:
        raise ValueError(f'Unknown pickup source type: {source_type}')

# ################################################################################################################################
# ################################################################################################################################
