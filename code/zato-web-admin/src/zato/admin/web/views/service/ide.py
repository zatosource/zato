# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import BaseCallView, invoke_action_handler, method_allowed

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class IDE(BaseCallView):
    method_allowed = 'GET'
    url_name = 'service-ide'
    template = 'zato/service/ide.html'
    service_name = 'dev.service.ide'

    def get_input_dict(self):

        # This will point either to a service or to a full file name
        object_type = self.req.zato.args.object_type

        if object_type == 'service':
            current_service_name = self.req.zato.args.name
            fs_location = ''
        else:
            current_service_name = ''
            fs_location = self.req.zato.args.name

        return {
            'cluster_id': self.cluster_id,
            'service_name': current_service_name,
            'fs_location': fs_location,
        }

# ################################################################################################################################

    def build_http_response(self, response):

        return_data = {
            'cluster_id':self.req.zato.cluster_id,
            'current_object_name': self.req.zato.args.name,
            'current_object_name_url_safe': self.req.zato.args.name.replace('~', '/'),
            'data': response.data,
        }

        return TemplateResponse(self.req, self.template, return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_service(req, service_name):
    return invoke_action_handler(req, 'dev.service.ide.get-service', {'service_name': service_name})

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_file(req, fs_location):
    return invoke_action_handler(req, 'dev.service.ide.get-file', extra={'fs_location': fs_location})

# ################################################################################################################################
# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

# stdlib
import os
from dataclasses import dataclass
from operator import itemgetter

# Zato
from zato.common.typing_ import intnone, list_, list_field, strnone
from zato.common.util.api import needs_suffix
from zato.common.util.open_ import open_r
from zato.server.service import Model, Service

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
    service_list: 'list_' = list_field()
    current_file_name: 'strnone' = None
    current_fs_location: 'strnone' = None
    current_service_files: 'list_' = list_field()

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
    name = 'dev.service.ide'

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

        # This will point to files that contain the currently selected service.
        # It is possible that more than one file will have the same service
        # and we need to recognize such a case.
        current_service_files = []

        service_list_response = self.get_deployment_info_list()

        # The file_item_dict dictionary maps file system locations to file names which means that keys
        # are always unique (because FS locations are always unique).
        for item in service_list_response:
            file_name = item['file_name']
            fs_location = item['fs_location']
            service_name = item['service_name']

            # This maps a full file path to its extract file name.
            file_item_dict[fs_location] = file_name

            # Appending to our list of services is something that we can always do
            service_list.append({
                'name': service_name,
                'fs_location': fs_location,
            })

            # If the current service is among what this file contains or if the current file is what we have on input,
            # append the latter's name for later use.
            input_service_name_matches = input_service_name and input_service_name == service_name
            input_fs_location_matches = input_fs_location and input_fs_location == fs_location
            if input_service_name_matches or input_fs_location_matches:
                current_service_files.append(fs_location)

                # Note that we may potentially have mulitple services with the same name
                # and what we are doing here is potentially overwriting the already assigned
                # object that contains the source code.
                with open_r(fs_location) as f:
                    current_fs_location = fs_location
                    current_file_source_code = f.read()

        # This list may have file names that are not unique
        # but their FS locations will be always unique.
        file_list = []

        for fs_location, file_name in file_item_dict.items():
            file_list.append({
                'name': file_name,
                'fs_location': fs_location,
                'fs_location_url_safe': fs_location.replace('/', '~'),
            })

        file_count = len(file_list)
        service_count = len(service_list)

        file_list_suffix = 's' if needs_suffix(file_count) else ''
        service_list_suffix = 's' if needs_suffix(service_count) else ''

        file_count_human = f'{file_count} file{file_list_suffix}'
        service_count_human = f'{service_count} service{service_list_suffix}'

        response = {
            'service_list': sorted(service_list, key=itemgetter('name')),
            'file_list': sorted(file_list, key=itemgetter('name')),
            'file_count': file_count,
            'service_count': service_count,
            'file_count_human': file_count_human,
            'service_count_human': service_count_human,
            'current_service_files': current_service_files,
            'current_fs_location': current_fs_location,
            'current_file_source_code': current_file_source_code,
        }

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################

class GetService(_IDEBase):
    name = 'dev.service.ide.get-service'

    def handle(self):
        self.response.payload = '{}'

# ################################################################################################################################
# ################################################################################################################################

class GetFile(_IDEBase):
    name = 'dev.service.ide.get-file'

    def handle(self):

        # Reusable
        fs_location = self.request.input.fs_location

        # Build a response ..
        response = IDEResponse()
        response.service_list = []
        response.current_service_files = []
        response.current_file_name = os.path.basename(fs_location)
        response.current_file_source_code = open(fs_location).read()

        # .. and return it to our caller.
        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################
'''
