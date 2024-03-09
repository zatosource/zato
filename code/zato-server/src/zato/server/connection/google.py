# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from pathlib import Path

# google-api-client
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload

# httplib2
import httplib2

# oauth2client
from oauth2client.service_account import ServiceAccountCredentials

# stroll
from stroll import stroll

# Zato
from zato.common.typing_ import cast_, list_field
from zato.common.util.file_system import fs_safe_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class GoogleClient:
    """ A client class that builds connections to Google APIs.
    """
    conn:'any_'
    files:'any_'
    api_name: 'str'
    api_version: 'str'
    user: 'str'
    scopes: 'anylist' = list_field()
    service_file_dict: 'str'
    dir_map: 'stranydict'

    def __init__(self, api_name: 'str', api_version: 'str', user:'str', scopes: 'anylist', service_file_dict:'str') -> 'None':
        self.api_name = api_name
        self.api_version = api_version
        self.user = user
        self.scopes = scopes
        self.service_file_dict = service_file_dict

        # This is a mapping of remote directories already created to their Google Drive IDs
        self._dir_map = {}

# ################################################################################################################################

    def connect(self) -> 'any_':
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(self.service_file_dict, scopes=self.scopes)
        credentials = credentials.create_delegated(self.user)
        http = credentials.authorize(httplib2.Http())
        self.conn = discovery.build(self.api_name, self.api_version, http=http)
        self._files = self.conn.files()

# ################################################################################################################################

    def reset(self) -> 'None':
        self._dir_map.clear()

# ################################################################################################################################

    def _create_remote_resource(
        self,
        name:'str',
        resource_type:'str',
        mime_type:'strnone',
        *,
        parent_id:'strnone',
        request_wrapper:'any_'=None,
        full_path:'strnone'=None
    ) -> 'str':

        # A base request to create a remote resource ..
        request = {
            'name': name,
        }

        # This will exist with directories only
        if mime_type:
            request['mimeType'] = 'application/vnd.google-apps.folder'

        # Parent will be None in case this is the top-level directory,
        # and in such a case, we cannot send a list with a None object inside,
        # it needs to be None directly.
        request['parents'] = [parent_id] if parent_id else None # type: ignore

        # Log what we are about to do ..
        logger.info('Creating %s `%s` with a parent of `%s`', resource_type, name, parent_id)

        # .. files will use a wrapper class for their contents ..
        if request_wrapper:
            media_body = MediaFileUpload(full_path, resumable=True)
        else:
            media_body = None

        # .. create the resource ..
        resource = self._files.create(body=request, media_body=media_body, fields='id').execute()

        # .. log the metadata received ..
        logger.info('Created %s `%s` with an ID of `%s`', resource_type, name, resource['id'])

        # .. and return the newly created resource's ID to our caller.
        return resource['id']

# ################################################################################################################################

    def create_remote_directory(self, name:'str', *, parent_id:'strnone') -> 'str':

        # Invoke a reusable method to create a new directory
        return self._create_remote_resource(
            name, 'directory', 'application/vnd.google-apps.folder', parent_id=parent_id
        )

# ################################################################################################################################

    def create_remote_file(self, name:'str', full_path:'str', *, parent_id:'str') -> 'str':

        # Invoke a reusable method to create a new file
        return self._create_remote_resource(
            name, 'file', None, parent_id=parent_id, request_wrapper=MediaFileUpload, full_path=full_path
        )

# ################################################################################################################################

    def add_directory(self, new_dir_root:'Path', new_dir_root_str:'str', item_relative:'Path') -> 'None':

        full_remote_path = new_dir_root.joinpath(item_relative)

        # We need a list of components to visit and create consisting of all our parents
        # as well as our own item (directory) that we are currently visiting.
        components = list(reversed(full_remote_path.parents))
        components.append(item_relative)

        for component in components:
            component_str = str(component)

            # Ignore current directory markers
            if component_str == '.':
                continue

            # This is a real directory that we may possibly want to create out of its parts
            else:

                # We start to build all the parts at the top-level directory
                current_parent = new_dir_root_str
                current_path = [current_parent]

                for part in component.parts:

                    # Ignore the case where part is the same as current parent (i.e. top-level directory)
                    if current_parent == part:
                        continue

                    # Append our own part to the full list of parts visited so far ..
                    current_path.append(part)
                    current_path_str = '/'.join(current_path)

                    # .. which means that our parent's path is the same as above except for what we have just added.
                    # .. We build the parent in this way in order to have two separate Python lists that we can
                    # .. manipulate separately instead of having a single mutuable list only.
                    current_parent_path = current_path[:-1]
                    current_parent_path_str = '/'.join(current_parent_path)

                    # If we do not have such a directory cached yet, it means that we need
                    # to create it and assign it to our current part. There will be always
                    # a parent to assign the directory to because we started with the top-level element.
                    if current_path_str not in self._dir_map:
                        parent_id = self._dir_map[current_parent_path_str]
                        dir_id = self.create_remote_directory(part, parent_id=parent_id)
                        self._dir_map[current_path_str] = dir_id
                        logger.info('Caching directory %s -> %s', current_path_str, dir_id)
                        logger.info('Current cache: %s', self._dir_map)

                    # Iterate down the list of parts
                    current_parent = part

# ################################################################################################################################

    def sync_to_google_drive(
        self,
        local_path:'str',
        new_root_name:'str',
        parent_directory_id:'str'
    ) -> 'str':

        # Log information about what we are about to do
        logger.info('About to sync `%s` to Google Drive (%s)', local_path, self.user)

        # Each directory contains a timestamp in case we need to recreate it
        root_suffix = fs_safe_now()

        # This is the root directory in Google Drive that we are going to store the local directory under
        new_dir_root = new_root_name + '-' + root_suffix
        new_dir_root = Path(new_dir_root)

        # This is reusable
        new_dir_root_str = str(new_dir_root)

        # This is our own local root directory that needs to be synced to Google Drive
        local_path_root = Path(local_path)

        # First, create the remote root directory under which all local directories will be anchored.
        # Note that the remote root itself is attached to a directory whose ID we were given on input.
        root_dir_id = self.create_remote_directory(new_dir_root_str, parent_id=parent_directory_id)

        # Assign it to the mapping of directories to their IDs for later use
        self._dir_map[new_dir_root_str] = root_dir_id

        # Walk down a tree of directories and files. Note that directories will always be visited first
        # and that all the names are sorted alphabetically.
        for item in stroll(local_path, directories=True, sort=True):

            # Add static typing
            item = cast_('Path', item)

            # This object is relative to our local root that we are synchronizing from,
            # i.e. we are removing any local path part leading to it. In this way,
            # we can in next steps build full remote paths based on that.
            item_relative = item.relative_to(local_path_root)

            # This is a directory and, unless we have already seen it,
            # we need to create its remote reflection ..
            if item.is_dir():
                logger.info('Syncing local directory `%s`', item)
                self.add_directory(new_dir_root, new_dir_root_str, item_relative)

            # .. this is a file and we know that is parent directory
            # .. must have been already created by now.
            else:

                # Build a string path to our parent, relative to the local root dir,
                # which will allow us to look up the parent in the cache of directories already synced.
                file_parent_str = item_relative.parent.as_posix()
                file_parent_str = os.path.join(new_dir_root_str, file_parent_str)
                file_parent_str = os.path.normpath(file_parent_str)

                # We can be certain that it exists because, again, directories are visited first.
                parent_id = self._dir_map[file_parent_str]

                # Now we can upload the file
                item_full_path = item.absolute().as_posix()
                self.create_remote_file(item.name, item_full_path, parent_id=parent_id)

        return root_dir_id

# ################################################################################################################################
# ################################################################################################################################
