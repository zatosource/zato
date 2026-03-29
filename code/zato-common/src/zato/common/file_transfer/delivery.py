# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import hashlib
from abc import ABC, abstractmethod

# Zato
from zato.common.file_transfer.const import DeliveryMethod
from zato.common.file_transfer.model import DeliveryResult

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class DeliveryHandler(ABC):

    @abstractmethod
    def deliver(
        self,
        content:'bytes',
        destination:'str',
        filename:'str',
    ) -> 'DeliveryResult':
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

class SFTPDeliveryHandler(DeliveryHandler):

    def __init__(self, connection_pool:'any_'=None) -> 'None':
        self.connection_pool = connection_pool

    def deliver(
        self,
        content:'bytes',
        destination:'str',
        filename:'str',
    ) -> 'DeliveryResult':

        try:
            parts = destination.split(':', 1)
            connection_name = parts[0] if parts else ''
            remote_path = parts[1] if len(parts) > 1 else '/'

            if not remote_path.endswith('/'):
                remote_path += '/'

            full_path = remote_path + filename

            if self.connection_pool:
                conn = self.connection_pool.get(connection_name)
                if conn:
                    conn.put(content, full_path)

            checksum = hashlib.sha256(content).hexdigest()
            return DeliveryResult(checksum=checksum)

        except Exception as e:
            return DeliveryResult(is_ok=False, error=str(e))

# ################################################################################################################################
# ################################################################################################################################

class FTPDeliveryHandler(DeliveryHandler):

    def __init__(self, connection_pool:'any_'=None) -> 'None':
        self.connection_pool = connection_pool

    def deliver(
        self,
        content:'bytes',
        destination:'str',
        filename:'str',
    ) -> 'DeliveryResult':

        try:
            parts = destination.split(':', 1)
            connection_name = parts[0] if parts else ''
            remote_path = parts[1] if len(parts) > 1 else '/'

            if not remote_path.endswith('/'):
                remote_path += '/'

            full_path = remote_path + filename

            if self.connection_pool:
                conn = self.connection_pool.get(connection_name)
                if conn:
                    from io import BytesIO
                    conn.storbinary(f'STOR {full_path}', BytesIO(content))

            checksum = hashlib.sha256(content).hexdigest()
            return DeliveryResult(checksum=checksum)

        except Exception as e:
            return DeliveryResult(is_ok=False, error=str(e))

# ################################################################################################################################
# ################################################################################################################################

class HTTPDeliveryHandler(DeliveryHandler):

    def __init__(self, connection_pool:'any_'=None) -> 'None':
        self.connection_pool = connection_pool

    def deliver(
        self,
        content:'bytes',
        destination:'str',
        filename:'str',
    ) -> 'DeliveryResult':

        try:
            parts = destination.split(':', 1)
            connection_name = parts[0] if parts else ''
            path = parts[1] if len(parts) > 1 else '/'

            if self.connection_pool:
                conn = self.connection_pool.get(connection_name)
                if conn:
                    response = conn.post(path, data=content, headers={
                        'Content-Disposition': f'attachment; filename="{filename}"'
                    })
                    if response.status_code >= 400:
                        return DeliveryResult(is_ok=False, error=f'HTTP error: {response.status_code}')

            checksum = hashlib.sha256(content).hexdigest()
            return DeliveryResult(checksum=checksum)

        except Exception as e:
            return DeliveryResult(is_ok=False, error=str(e))

# ################################################################################################################################
# ################################################################################################################################

class AMQPDeliveryHandler(DeliveryHandler):

    def __init__(self, connection_pool:'any_'=None) -> 'None':
        self.connection_pool = connection_pool

    def deliver(
        self,
        content:'bytes',
        destination:'str',
        filename:'str',
    ) -> 'DeliveryResult':

        try:
            parts = destination.split(':', 1)
            connection_name = parts[0] if parts else ''
            routing_key = parts[1] if len(parts) > 1 else ''

            if self.connection_pool:
                conn = self.connection_pool.get(connection_name)
                if conn:
                    conn.publish(content, routing_key=routing_key, properties={
                        'content_type': 'application/octet-stream',
                        'headers': {'filename': filename},
                    })

            checksum = hashlib.sha256(content).hexdigest()
            return DeliveryResult(checksum=checksum)

        except Exception as e:
            return DeliveryResult(is_ok=False, error=str(e))

# ################################################################################################################################
# ################################################################################################################################

class SMTPDeliveryHandler(DeliveryHandler):

    def __init__(self, connection_pool:'any_'=None) -> 'None':
        self.connection_pool = connection_pool

    def deliver(
        self,
        content:'bytes',
        destination:'str',
        filename:'str',
    ) -> 'DeliveryResult':

        try:
            parts = destination.split(':', 1)
            connection_name = parts[0] if parts else ''
            recipient = parts[1] if len(parts) > 1 else ''

            if self.connection_pool:
                conn = self.connection_pool.get(connection_name)
                if conn:
                    from email.mime.multipart import MIMEMultipart
                    from email.mime.base import MIMEBase
                    from email import encoders

                    msg = MIMEMultipart()
                    msg['To'] = recipient
                    msg['Subject'] = f'File delivery: {filename}'

                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(content)
                    encoders.encode_base64(attachment)
                    attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(attachment)

                    conn.send_message(msg)

            checksum = hashlib.sha256(content).hexdigest()
            return DeliveryResult(checksum=checksum)

        except Exception as e:
            return DeliveryResult(is_ok=False, error=str(e))

# ################################################################################################################################
# ################################################################################################################################

class S3DeliveryHandler(DeliveryHandler):

    def __init__(self, connection_pool:'any_'=None) -> 'None':
        self.connection_pool = connection_pool

    def deliver(
        self,
        content:'bytes',
        destination:'str',
        filename:'str',
    ) -> 'DeliveryResult':

        try:
            parts = destination.split(':', 1)
            connection_name = parts[0] if parts else ''
            bucket_and_path = parts[1] if len(parts) > 1 else ''

            bucket_parts = bucket_and_path.split('/', 1)
            bucket = bucket_parts[0]
            prefix = bucket_parts[1] if len(bucket_parts) > 1 else ''

            if prefix and not prefix.endswith('/'):
                prefix += '/'

            key = prefix + filename

            if self.connection_pool:
                conn = self.connection_pool.get(connection_name)
                if conn:
                    conn.put_object(Bucket=bucket, Key=key, Body=content)

            checksum = hashlib.sha256(content).hexdigest()
            return DeliveryResult(checksum=checksum)

        except Exception as e:
            return DeliveryResult(is_ok=False, error=str(e))

# ################################################################################################################################
# ################################################################################################################################

class AzureBlobDeliveryHandler(DeliveryHandler):

    def __init__(self, connection_pool:'any_'=None) -> 'None':
        self.connection_pool = connection_pool

    def deliver(
        self,
        content:'bytes',
        destination:'str',
        filename:'str',
    ) -> 'DeliveryResult':

        try:
            parts = destination.split(':', 1)
            connection_name = parts[0] if parts else ''
            container_and_path = parts[1] if len(parts) > 1 else ''

            container_parts = container_and_path.split('/', 1)
            container = container_parts[0]
            prefix = container_parts[1] if len(container_parts) > 1 else ''

            if prefix and not prefix.endswith('/'):
                prefix += '/'

            blob_name = prefix + filename

            if self.connection_pool:
                conn = self.connection_pool.get(connection_name)
                if conn:
                    blob_client = conn.get_blob_client(container=container, blob=blob_name)
                    blob_client.upload_blob(content, overwrite=True)

            checksum = hashlib.sha256(content).hexdigest()
            return DeliveryResult(checksum=checksum)

        except Exception as e:
            return DeliveryResult(is_ok=False, error=str(e))

# ################################################################################################################################
# ################################################################################################################################

class DeliveryRouter:

    def __init__(self, connection_pool:'any_'=None) -> 'None':
        self.handlers = {
            DeliveryMethod.Sftp: SFTPDeliveryHandler(connection_pool),
            DeliveryMethod.Ftp: FTPDeliveryHandler(connection_pool),
            DeliveryMethod.Ftps: FTPDeliveryHandler(connection_pool),
            DeliveryMethod.Http: HTTPDeliveryHandler(connection_pool),
            DeliveryMethod.Https: HTTPDeliveryHandler(connection_pool),
            DeliveryMethod.Amqp: AMQPDeliveryHandler(connection_pool),
            DeliveryMethod.Smtp: SMTPDeliveryHandler(connection_pool),
            DeliveryMethod.S3: S3DeliveryHandler(connection_pool),
            DeliveryMethod.Azure_Blob: AzureBlobDeliveryHandler(connection_pool),
        }

    def deliver(
        self,
        content:'bytes',
        protocol:'str',
        destination:'str',
        filename:'str',
    ) -> 'DeliveryResult':

        try:
            method = DeliveryMethod(protocol)
        except ValueError:
            return DeliveryResult(is_ok=False, error=f'Unknown delivery method: {protocol}')

        handler = self.handlers.get(method)
        if not handler:
            return DeliveryResult(is_ok=False, error=f'No handler for delivery method: {protocol}')

        return handler.deliver(content, destination, filename)

# ################################################################################################################################
# ################################################################################################################################
