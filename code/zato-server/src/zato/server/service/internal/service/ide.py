# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from operator import itemgetter
from pathlib import Path
from time import sleep

# Zato
from zato.common.api import Default_Service_File_Data
from zato.common.exception import BadRequest
from zato.common.typing_ import anylist, intnone, list_field, strnone
from zato.common.util.api import get_demo_py_fs_locations, wait_for_file
from zato.common.util.open_ import open_r, open_w
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist, strlistdict

# ################################################################################################################################
# ################################################################################################################################

def make_fs_location_url_safe(data:'str') -> 'str':
    return data.replace('/', '~')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class IDERequest(Model):
    service_name: 'strnone' = None
    fs_location: 'strnone' = None
    should_wait_for_services: 'bool' = False
    should_convert_pickup_to_work_dir: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class IDEResponse(Model):
    service_count: 'intnone' = None
    service_count_human: 'strnone' = None
    file_count: 'intnone' = None
    file_count_human: 'strnone' = None
    current_file_source_code: 'strnone' = ''
    service_list: 'anylist' = list_field()
    current_file_name: 'strnone' = None
    current_fs_location: 'strnone' = None
    current_fs_location_url_safe: 'strnone' = None
    current_root_directory: 'strnone' = None
    root_directory_count: 'intnone' = None

    # A list of services that are contained in a particular file.
    current_file_service_list: 'anylist' = list_field()

    # A list of files that may potentially have a service of the given name.
    current_service_file_list: 'anylist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RootDirInfo(Model):
    current_root_directory: 'strnone' = None
    root_directory_count: 'intnone' = None

# ################################################################################################################################
# ################################################################################################################################

class _IDEBase(Service):

    input = IDERequest
    output = IDEResponse

# ################################################################################################################################

    def _normalize_fs_location(self, fs_location:'str') -> 'str':

        # .. resolve the basic variables ..
        fs_location = os.path.expanduser(fs_location)

        # .. make sure it's an actual path ..
        fs_location = fs_location.replace('~', '/')

        # .. this is always required ..
        fs_location = os.path.abspath(fs_location)

        # .. now, we can return it to our caller.
        return fs_location

# ################################################################################################################################

    def _validate_path(self, orig_path:'str') -> 'None':

        # If we have any path on input ..
        if orig_path:

            # .. collect all the root, top-level directories we can deploy services to ..
            all_root_dirs = self._get_all_root_directories()

            # .. get its canonical version ..
            path = self._normalize_fs_location(orig_path)

            # .. go through all the deployment roots ..
            for item in all_root_dirs:

                # .. check if the input path is one that belongs to that root ..
                if path.startswith(item):

                    # .. we have our match, we can stop searching ..
                    break

            # .. if we are here, it means we didn't find a matching root directory ..
            # .. so we need to raise an exception to indicate that ..
            else:
                raise ValueError(f'Invalid path `{orig_path}`')

# ################################################################################################################################

    def before_handle(self):

        # In the Create service, we're looking up the 'root_directory' key,
        # in other services, it's called 'fs_location'.
        orig_path = self.request.input.get('root_directory') or self.request.input.get('fs_location')

        # If we have any path on input ..
        if orig_path:

            # .. validate if it's a correct one.
            self._validate_path(orig_path)

# ################################################################################################################################

    def _get_service_list_by_fs_location(self, deployment_info_list:'any_', fs_location:'str') -> 'dictlist':

        # Local variables
        all_root_dirs = self._get_all_root_directories()

        # Response to produce
        out = []

        for item in deployment_info_list:
            if fs_location == item['fs_location']:

                # This is reusable
                _target_fs_location = self._convert_work_to_pickup_dir(fs_location)
                root_dir_info = self._get_current_root_dir_info(_target_fs_location, all_root_dirs)

                out.append({
                    'name': item['service_name'],
                    'fs_location': fs_location,
                    'fs_location_url_safe': make_fs_location_url_safe(fs_location),
                    'line_number': item['line_number'],
                    'current_root_directory': root_dir_info.current_root_directory,
                    'root_directory_count': root_dir_info.root_directory_count,

                    # We subtract a little bit to make sure the class name is not in the first line
                    'line_number_human': item['line_number'] - 3
                })
        return sorted(out, key=itemgetter('name'))

# ################################################################################################################################

    def _get_all_root_directories(self) -> 'strlistdict':

        # Our response to produce
        out = {}

        # .. this the default directory that will always exist
        out[self.server.hot_deploy_config.pickup_dir] = []

        # .. now, we can append all the user-defined directories ..
        pickup_config_items = sorted(self.server.pickup_config.items())
        for key, value in pickup_config_items:
            if not value:
                continue
            if key.startswith(('hot-deploy.user', 'user_conf')):
                pickup_from = value['pickup_from']
                if pickup_from.endswith('/'):
                    pickup_from = pickup_from[:-1]
                if not os.path.isabs(pickup_from):
                    pickup_from = os.path.join(self.server.base_dir, pickup_from)
                out[pickup_from] = []

        return out

# ################################################################################################################################

    def _get_default_root_directory(self, all_root_dirs:'strlistdict | None'=None) -> 'str':

        all_root_dirs = all_root_dirs or self._get_all_root_directories()

        for item in all_root_dirs:

            windows_matches = r'incoming\services' in item
            non_windows_matches = 'incoming/services' in item

            if windows_matches or non_windows_matches:
                return item

        else:
            raise ValueError(f'Default root directory not found among {sorted(all_root_dirs)}')

# ################################################################################################################################

    def _get_current_root_dir_info(self, fs_location:'str', all_root_dirs:'strlistdict | None'=None) -> 'RootDirInfo':

        # Our response to produce
        out = RootDirInfo()

        # Collect all the root, top-level directories we can deploy services to ..
        all_root_dirs = all_root_dirs or self._get_all_root_directories()

        # .. check which one the current file belongs to ..
        for item in all_root_dirs:
            if fs_location.startswith(item):
                current_root_directory = item
                break
        else:
            current_root_directory = None

        # .. populate the response accordingly ..
        out.current_root_directory = current_root_directory
        out.root_directory_count = len(all_root_dirs)

        # .. and return it to our caller.
        return out

# ################################################################################################################################

    def get_deployment_info_list(self):
        service_list_response = self.invoke('zato.service.get-deployment-info-list', **{
            'needs_details': True,
            'include_internal': False,
            'skip_response_elem': True,
        })
        for item in service_list_response:
            yield item

# ################################################################################################################################

    def _convert_work_to_pickup_dir(self, fs_location:'str') -> 'str':

        # Windows ..
        if 'hot-deploy\\current' in fs_location:
            needs_replace = True

        # .. non-Windows ..
        elif 'hot-deploy/current' in fs_location:
            needs_replace = True

        # .. we don't need to fix it up ..
        else:
            needs_replace = False

        # .. we enter here if we need to fix up the name ..
        if needs_replace:
            file_name = os.path.basename(fs_location)
            default_root_dir = self._get_default_root_directory()
            out = os.path.join(default_root_dir, file_name)

        # .. otherwise, we use it as-is ..
        else:
            out = fs_location

        # .. now, we can return it to our caller.
        return out

# ################################################################################################################################

    def _convert_pickup_to_work_dir(self, fs_location:'str') -> 'str':

        # Windows ..
        if 'pickup\\incoming\\services' in fs_location:
            needs_replace = True

        # .. non-Windows ..
        elif 'pickup/incoming/services' in fs_location:
            needs_replace = True

        # .. we don't need to fix it up ..
        else:
            needs_replace = False

        # .. we enter here if we need to fix up the name ..
        if needs_replace:
            file_name = os.path.basename(fs_location)
            base_work_dir = self.server.work_dir
            hot_deploy_dir = self.server.fs_server_config.hot_deploy.current_work_dir
            out = os.path.join(base_work_dir, hot_deploy_dir, file_name)
            out = os.path.abspath(out)

        # .. otherwise, we use it as-is ..
        else:
            out = fs_location

        # .. now, we can return it to our caller.
        return out

# ################################################################################################################################

    def _wait_for_services(self, fs_location:'str', max_wait_time:'int'=3) -> 'None':
        now = datetime.utcnow()
        until = now + timedelta(seconds=max_wait_time)

        while now < until:
            self.logger.info('Waiting for %s', fs_location)
            for item in self.get_deployment_info_list():
                if item['fs_location'] == fs_location:
                    return

            now = datetime.utcnow()
            sleep(0.2)

# ################################################################################################################################
# ################################################################################################################################

class ServiceIDE(_IDEBase):

    def handle(self):

        # Add type hints
        input:'IDERequest' = self.request.input

        # Local variables
        all_root_dirs = self._get_all_root_directories()

        # Default data structures to fill out with details
        file_item_dict = {}
        service_list = []

        # The service that we want to look up ..
        input_service_name = input.service_name

        # .. or a file that we need.
        input_fs_location = input.fs_location or ''
        if input_fs_location:
            input_fs_location = self._normalize_fs_location(input_fs_location)

        # Full path to the file with the current service's source code
        current_fs_location = input_fs_location

        # It's possible that we've been called right after a file was deployed,
        # in which case we need to wait for a moment until any services
        # from that file are deployed.
        if self.request.input.should_wait_for_services:
            if input_fs_location:
                if os.path.exists(input_fs_location):
                    self._wait_for_services(input_fs_location)

        # Current's service source code
        current_file_source_code = ''

        # All services stored in the current file
        current_file_service_list = []

        # This will point to files that contain the currently selected service.
        # It is possible that more than one file will have the same service
        # and we need to recognize such a case.
        current_service_file_list = []

        service_list_response = self.get_deployment_info_list()

        # The file_item_dict dictionary maps file system locations to file names which means that keys
        # are always unique (because FS locations are always unique).
        for item in service_list_response:
            file_name = item['file_name']
            service_name = item['service_name']
            line_number = item['line_number']

            # The location we received may point to a hot-deployment directory
            # but not the original one that the file was saved in. Rather, it may be
            # the work directory that the file was moved to. This is why we need
            # to potentially fix up the location and make it point to the original one.
            fs_location = item['fs_location']
            fs_location = self._convert_work_to_pickup_dir(fs_location)

            # This is reusable
            root_dir_info = self._get_current_root_dir_info(fs_location, all_root_dirs)

            # We subtract a little bit to make sure the class name is not in the first line
            line_number_human = item['line_number'] - 3

            # This maps a full file path to its extract file name.
            file_item_dict[fs_location] = file_name

            # Appending to our list of services is something that we can always do
            service_list.append({
                'name': service_name,
                'fs_location': fs_location,
                'fs_location_url_safe': make_fs_location_url_safe(fs_location),
                'line_number': line_number,
                'line_number_human': line_number_human,
                'current_root_directory': root_dir_info.current_root_directory,
                'root_directory_count': root_dir_info.root_directory_count,
            })

            # If the current service is among what this file contains or if the current file is what we have on input,
            # append the latter's name for later use.
            input_service_name_matches = input_service_name and input_service_name == service_name
            input_fs_location_matches = input_fs_location and input_fs_location == fs_location

            if input_service_name_matches or input_fs_location_matches:

                # This is the file that contains the service that we have on input
                # or if input location is the same as what we are processing right now in this loop's iteration.
                current_fs_location = fs_location

                # This is reusable
                root_dir_info = self._get_current_root_dir_info(current_fs_location, all_root_dirs)

                # Append this location to the list of locations that the service is available under ..
                current_service_file_list.append(fs_location)

                # .. also, append the service name to the list of services this file contains ..
                current_file_service_list.append({
                    'name': service_name,
                    'fs_location': fs_location,
                    'fs_location_url_safe': make_fs_location_url_safe(fs_location),
                    'line_number': line_number,
                    'line_number_human': line_number_human,
                    'current_root_directory': root_dir_info.current_root_directory,
                    'root_directory_count': root_dir_info.root_directory_count,
                })

                # .. and read the service's source code for our caller's benefit.
                if os.path.exists(fs_location):
                    with open_r(fs_location) as f:
                        current_file_source_code = f.read()

        # This list may have file names that are not unique
        # but their FS locations will be always unique.
        file_list = []

        for fs_location, file_name in file_item_dict.items():

            # This is reusable
            root_dir_info = self._get_current_root_dir_info(fs_location, all_root_dirs)

            file_list.append({
                'name': file_name,
                'fs_location': fs_location,
                'fs_location_url_safe': make_fs_location_url_safe(fs_location),
                'current_root_directory': root_dir_info.current_root_directory,
                'root_directory_count': root_dir_info.root_directory_count,
            })

        file_count = len(file_list)
        service_count = len(service_list)

        file_list_suffix = 's'# if needs_suffix(file_count) else ''
        service_list_suffix = 's'# if needs_suffix(service_count) else ''

        file_count_human = f'{file_count} file{file_list_suffix}'
        service_count_human = f'{service_count} service{service_list_suffix}'

        # Let's try to find the root directory based on the current file ..
        root_dir_info = self._get_current_root_dir_info(current_fs_location)

        # .. we go here if we found one ..
        if root_dir_info.current_root_directory:
            current_root_directory = root_dir_info.current_root_directory

        # .. we go here if we didn't find one, which may happen if the current file has no services inside ..
        else:
            current_root_directory = self._get_default_root_directory(all_root_dirs)

        response = {
            'service_list': sorted(service_list, key=itemgetter('name')),
            'file_list': sorted(file_list, key=itemgetter('name')),
            'file_count': file_count,
            'service_count': service_count,
            'file_count_human': file_count_human,
            'service_count_human': service_count_human,
            'current_file_service_list': current_file_service_list,
            'current_service_file_list': current_service_file_list,
            'current_fs_location': current_fs_location,
            'current_file_source_code': current_file_source_code,
            'current_root_directory': current_root_directory,
            'root_directory_count': root_dir_info.root_directory_count,
        }

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class _GetBase(_IDEBase):

    def _build_get_response(self, deployment_info_list:'any_', fs_location:'str') -> 'IDEResponse':

        response = IDEResponse()
        response.service_list = []
        response.current_file_service_list = self._get_service_list_by_fs_location(deployment_info_list, fs_location)
        response.current_service_file_list = []

        if fs_location:

            wait_for_file(fs_location, 3, interval=0.2)

            response.current_fs_location = fs_location
            response.current_fs_location_url_safe = make_fs_location_url_safe(fs_location)
            response.current_file_name = os.path.basename(fs_location)

            # We waited above but is still may not exist
            if os.path.exists(fs_location):
                response.current_file_source_code = open(fs_location).read()

        # .. get information about the current root directory ..
        info = self._get_current_root_dir_info(fs_location)

        # .. populate the response accordingly ..
        response.current_root_directory = info.current_root_directory
        response.root_directory_count = info.root_directory_count

        # .. and return it to our caller.
        return response

# ################################################################################################################################
# ################################################################################################################################

class GetService(_GetBase):

    def handle(self):

        deployment_info_list = list(self.get_deployment_info_list())

        for item in deployment_info_list:

            if item['service_name'] == self.request.input.service_name:

                # Extract the full file system path
                fs_location = item['fs_location']

                # Build a response ..
                response = self._build_get_response(deployment_info_list, fs_location)

                # .. this is what we return to our caller ..
                self.response.payload = response

                # .. no need to iterate further.
                break

# ################################################################################################################################
# ################################################################################################################################

class GetFile(_GetBase):

    def handle(self):

        # Reusable
        fs_location = self.request.input.fs_location
        fs_location = self._convert_pickup_to_work_dir(fs_location)
        deployment_info_list = self.get_deployment_info_list()

        # Build a response ..
        response = self._build_get_response(deployment_info_list, fs_location)

        # .. and return it to our caller.
        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class GetFileList(_GetBase):

    def handle(self):

        # Our response to produce
        out = self._get_all_root_directories()

        # .. go through all the top-level roots ..
        for dir_name, files in out.items():

            # .. make sure we take services and models into account here ..
            if dir_name.endswith('src-zato'):
                _dir_name = os.path.join(dir_name, 'impl', 'src')
            else:
                _dir_name = dir_name

            # .. extract all the Python files recursively ..
            for pattern in ['*.py', '*.ini', '*.yml', '*.yaml', '*.zrules']:
                for py_file in sorted(Path(_dir_name).rglob(pattern)):
                    py_file_name = str(py_file)
                    root_dir_info = self._get_current_root_dir_info(py_file_name)
                    files.append({
                        'file_name': py_file_name,
                        'file_name_url_safe': make_fs_location_url_safe(py_file_name),
                        'current_root_directory': root_dir_info.current_root_directory,
                        'root_directory_count': root_dir_info.root_directory_count,
                    })

        # .. finally, we can return the response to our caller.
        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class CreateFile(_GetBase):

    # Our I/O
    input = 'root_directory', 'file_name', '-data'
    output = 'data', 'full_path', 'full_path_url_safe'

    def handle(self):

        # Local variables
        input_data = self.request.input.data or ''
        file_name = self.request.input.file_name
        root_directory = self.request.input.root_directory

        # We will expect for the full path to begin with one of these
        all_root_dirs = self._get_all_root_directories()

        # Combine the two to get a full path ..
        full_path = os.path.join(root_directory, file_name)

        # .. normalize it ..
        full_path = self._normalize_fs_location(full_path)

        # .. make sure this is a Python file ..
        if not full_path.endswith('.py'):
            full_path += '.py'

        # .. make sure it's an allowed one ..
        self._validate_path(full_path)

        # .. make sure all the directories leading to the file exist ..
        Path(full_path).parent.mkdir(parents=True, exist_ok=True)

        # .. prepare the data to write to and return ..
        if input_data:
            needs_new_file = True
            data_for_new_file = input_data

        else:
            if os.path.exists(full_path):
                needs_new_file = False
                with open_r(full_path) as f:
                    data_for_new_file = f.read()
            else:
                needs_new_file = True
                data_for_new_file = Default_Service_File_Data.format(**{
                    'full_path': full_path,
                })

        # .. ensure it has a prefix that we recognize ..
        for item in all_root_dirs:

            # .. we have a match ..
            if full_path.startswith(item):

                # .. otherwise, simply create it unless it already existed ..
                if needs_new_file:
                    with open_w(full_path) as f:
                        _ = f.write(data_for_new_file)
                    self.logger.info('Created path %s', full_path)
                else:
                    self.logger.info('Path already exists %s', full_path)

                # .. no need to continue further ..
                break

        # .. if it has no such prefix, we need to report an error ..
        else:
            msg = f'Invalid path `{full_path}`, must start with one of: `{sorted(all_root_dirs)}`'
            raise ValueError(msg)

        self.response.payload.data = data_for_new_file
        self.response.payload.full_path = full_path
        self.response.payload.full_path_url_safe = make_fs_location_url_safe(full_path)

# ################################################################################################################################
# ################################################################################################################################

class DeleteFile(_GetBase):

    # Our I/O
    input = 'fs_location'
    output = 'full_path', 'full_path_url_safe'

    def _validate_fs_location(self, fs_location:'str') -> 'None':

        # Make sure we have a path on input ..
        if not fs_location:
            raise BadRequest(self.cid, f'No path given on input `{fs_location}`')

        # .. and that it exists ..
        if not os.path.exists(fs_location):
            raise BadRequest(self.cid, f'Path does not exist `{fs_location}`')

        # .. and that it's actually a file.
        if not os.path.isfile(fs_location):
            raise BadRequest(self.cid, f'Path is not a file `{fs_location}`')

# ################################################################################################################################

    def handle(self):

        # Local variables
        fs_location = self.request.input.fs_location

        # .. turn the pickup location into a work directory one ..
        work_dir_fs_location = self._convert_pickup_to_work_dir(fs_location)

        # .. validate both locations ..
        self._validate_fs_location(fs_location)
        self._validate_fs_location(work_dir_fs_location)

        # .. if we're here, it means that we can actually delete both locations ..
        os.remove(fs_location)
        self.logger.info('Deleted path %s', fs_location)

        os.remove(work_dir_fs_location)
        self.logger.info('Deleted path %s', work_dir_fs_location)

        # .. now, delete it from our in-RAM service store ..
        self.server.service_store.delete_objects_by_file_path(work_dir_fs_location, delete_from_odb=True)

        # .. find the location with the demo service ..
        demo_py_fs = get_demo_py_fs_locations(self.server.base_dir)

        # .. finally, tell the caller what our default file with services is ..
        self.response.payload.full_path = demo_py_fs.pickup_incoming_full_path
        self.response.payload.full_path_url_safe = make_fs_location_url_safe(demo_py_fs.pickup_incoming_full_path)

# ################################################################################################################################
# ################################################################################################################################

class RenameFile(_GetBase):

    # Our I/O
    input = 'root_directory', 'current_file_name', 'new_file_name'
    output = 'full_path', 'full_path_url_safe'

    def handle(self) -> 'None':

        # Local variables
        input = self.request.input

        # We always work with combined and absolute paths
        current_file_path = os.path.join(input.root_directory, input.current_file_name)
        current_file_path = self._normalize_fs_location(current_file_path)

        new_file_path = os.path.join(input.root_directory, input.new_file_name)
        new_file_path = self._normalize_fs_location(current_file_path)

        # Make sure that both paths are allowed
        self._validate_path(current_file_path)
        self._validate_path(new_file_path)

        # First, get the contents of the old file ..
        with open_r(current_file_path) as f:
            data = f.read()

        # .. now, we can delete it ..
        _ = self.invoke(DeleteFile, fs_location=current_file_path)

        # .. and create a new one ..
        response = self.invoke(CreateFile, **{
            'root_directory': input.root_directory,
            'file_name': input.new_file_name,
            'data': data,
        })

        # .. finally, build a response for our caller.
        self.response.payload.full_path = response['full_path']
        self.response.payload.full_path_url_safe = response['full_path_url_safe']

# ################################################################################################################################
# ################################################################################################################################
