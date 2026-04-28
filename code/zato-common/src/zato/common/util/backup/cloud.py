# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import io

if 0:
    from libcloud.storage.base import StorageDriver

# libcloud
from libcloud.storage.providers import get_driver

# Zato
from zato.common.util.backup.config import BackupConfig, provider_map

# ################################################################################################################################
# ################################################################################################################################

def _get_libcloud_driver(config:'BackupConfig') -> 'StorageDriver':
    provider_const = provider_map[config.provider]
    driver_cls = get_driver(provider_const)
    out = driver_cls(config.access_key, config.secret_key)
    return out

# ################################################################################################################################

def _upload_to_cloud(config:'BackupConfig', object_name:'str', encrypted_data:'bytes') -> 'None':
    driver = _get_libcloud_driver(config)
    container = driver.get_container(config.bucket_name)
    stream = io.BytesIO(encrypted_data)
    driver.upload_object_via_stream(stream, container, object_name)

# ################################################################################################################################

def _download_from_cloud(config:'BackupConfig', object_name:'str') -> 'bytes':
    driver = _get_libcloud_driver(config)
    container = driver.get_container(config.bucket_name)
    cloud_object = container.get_object(object_name)
    chunks = driver.download_object_as_stream(cloud_object)
    out = b''.join(chunks)
    return out

# ################################################################################################################################

def _delete_from_cloud(config:'BackupConfig', object_name:'str') -> 'None':
    driver = _get_libcloud_driver(config)
    container = driver.get_container(config.bucket_name)
    cloud_object = container.get_object(object_name)
    driver.delete_object(cloud_object)

# ################################################################################################################################

def _list_cloud_objects(config:'BackupConfig') -> 'list':
    driver = _get_libcloud_driver(config)
    container = driver.get_container(config.bucket_name)
    out = list(container.list_objects())
    return out

# ################################################################################################################################

def _test_cloud_connection(config:'BackupConfig') -> 'None':
    """ Raises an exception if the connection or bucket is not accessible.
    """
    driver = _get_libcloud_driver(config)
    _ = driver.get_container(config.bucket_name)

# ################################################################################################################################
# ################################################################################################################################
