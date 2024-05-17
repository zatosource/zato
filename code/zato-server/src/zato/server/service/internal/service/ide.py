# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from operator import itemgetter
from pathlib import Path

# Zato
from zato.common.typing_ import anylist, intnone, list_field, strnone
from zato.common.util.open_ import open_r
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist

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

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class IDEResponse(Model):
    service_count: 'intnone' = None
    service_count_human: 'strnone' = None
    file_count: 'intnone' = None
    file_count_human: 'strnone' = None
    current_file_source_code: 'strnone' = None
    service_list: 'anylist' = list_field()
    current_file_name: 'strnone' = None
    current_fs_location: 'strnone' = None
    current_fs_location_url_safe: 'strnone' = None

    # A list of services that are contained in a particular file.
    current_file_service_list: 'anylist' = list_field()

    # A list of files that may potentially have a service of the given name.
    current_service_file_list: 'anylist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

class _IDEBase(Service):

    input = IDERequest
    output = IDEResponse

    def get_deployment_info_list(self):
        service_list_response = self.invoke('zato.service.get-deployment-info-list', **{
            'needs_details': True,
            'include_internal': False,
            'skip_response_elem': True,
        })
        for item in service_list_response:
            yield item

# ################################################################################################################################
# ################################################################################################################################

class ServiceIDE(_IDEBase):

    def handle(self):

        # Add type hints
        input = self.request.input # type: IDERequest

        # Default data structures to fill out with details
        file_item_dict = {}
        service_list = []

        # The service that we want to look up ..
        input_service_name = input.service_name

        # .. or a file that we need.
        input_fs_location = input.fs_location or ''
        input_fs_location = input_fs_location.replace('~', '/')

        # Full path to the file with the current service's source code
        current_fs_location = ''

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
            fs_location = item['fs_location']
            service_name = item['service_name']
            line_number = item['line_number']

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
            })

            # If the current service is among what this file contains or if the current file is what we have on input,
            # append the latter's name for later use.
            input_service_name_matches = input_service_name and input_service_name == service_name
            input_fs_location_matches = input_fs_location and input_fs_location == fs_location

            if input_service_name_matches or input_fs_location_matches:

                # This is the file that contains the service that we have on input
                # or if input location is the same as what we are processing right now in this loop's iteration.
                current_fs_location = fs_location

                # Append this location to the list of locations that the service is available under ..
                current_service_file_list.append(fs_location)

                # .. also, append the service name to the list of services this file contains ..
                current_file_service_list.append({
                    'name': service_name,
                    'fs_location': fs_location,
                    'fs_location_url_safe': make_fs_location_url_safe(fs_location),
                    'line_number': line_number,
                    'line_number_human': line_number_human,
                })

                # .. and read the service's source code for our caller's benefit.
                with open_r(fs_location) as f:
                    current_file_source_code = f.read()

        # This list may have file names that are not unique
        # but their FS locations will be always unique.
        file_list = []

        for fs_location, file_name in file_item_dict.items():
            file_list.append({
                'name': file_name,
                'fs_location': fs_location,
                'fs_location_url_safe': make_fs_location_url_safe(fs_location),
            })

        file_count = len(file_list)
        service_count = len(service_list)

        file_list_suffix = 's'# if needs_suffix(file_count) else ''
        service_list_suffix = 's'# if needs_suffix(service_count) else ''

        file_count_human = f'{file_count} file{file_list_suffix}'
        service_count_human = f'{service_count} service{service_list_suffix}'

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
        }

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class _GetBase(_IDEBase):

    def _get_service_list_by_fs_location(self, deployment_info_list:'any_', fs_location:'str') -> 'dictlist':
        out = []
        for item in deployment_info_list:
            if fs_location == item['fs_location']:
                out.append({
                    'name': item['service_name'],
                    'fs_location': fs_location,
                    'fs_location_url_safe': make_fs_location_url_safe(fs_location),
                    'line_number': item['line_number'],

                    # We subtract a little bit to make sure the class name is not in the first line
                    'line_number_human': item['line_number'] - 3
                })
        return sorted(out, key=itemgetter('name'))

# ################################################################################################################################

    def _build_get_response(self, deployment_info_list:'any_', fs_location:'str') -> 'IDEResponse':

        response = IDEResponse()
        response.service_list = []
        response.current_file_service_list = self._get_service_list_by_fs_location(deployment_info_list, fs_location)
        response.current_service_file_list = []
        response.current_fs_location = fs_location
        response.current_fs_location_url_safe = make_fs_location_url_safe(fs_location)
        response.current_file_name = os.path.basename(fs_location)
        response.current_file_source_code = open(fs_location).read()

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
        out = {}

        # .. this the default directory that will always exist
        out[self.server.hot_deploy_config.pickup_dir] = []

        # .. now, we can append all the user-defined directories ..
        for key, value in sorted(self.server.pickup_config.items()):
            if not value:
                continue
            if key.startswith(('hot-deploy.user', 'user_conf')):
                if not 'patterns' in value:
                    pickup_from = value['pickup_from']
                    if pickup_from.endswith('/'):
                        pickup_from = pickup_from[:-1]
                    out[pickup_from] = []

        # .. go through all the top-level roots ..
        for dir_name, files in out.items():

            # .. make sure we take into services and models into account here ..
            if dir_name.endswith('src-zato'):
                _dir_name = os.path.join(dir_name, 'impl', 'src')
            else:
                _dir_name = dir_name

            # .. extract all the Python files recursively ..
            for py_file in sorted(Path(_dir_name).glob('**/*.py')):
                py_file_name = str(py_file)
                files.append({
                    'file_name': py_file_name,
                    'file_name_url_safe': make_fs_location_url_safe(py_file_name),
                })

        # .. finally, we can return the response to our caller.
        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################
