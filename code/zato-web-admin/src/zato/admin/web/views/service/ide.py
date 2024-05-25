# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import BaseCallView, invoke_action_handler, method_allowed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest, HttpResponse
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class IDE(BaseCallView):
    method_allowed = 'GET'
    url_name = 'service-ide'
    template = 'zato/service/ide.html'
    service_name = 'zato.service.ide.service-ide'

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

    def build_http_response(self, response:'any_') -> 'TemplateResponse':

        return_data = {
            'cluster_id': self.req.zato.cluster_id,
            'cluster_name': self.req.zato.cluster.name,
            'current_object_name': self.req.zato.args.name,
            'current_object_name_url_safe': self.req.zato.args.name.replace('~', '/'),
            'data': response.data,
        }

        return TemplateResponse(self.req, self.template, return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_service(req:'HttpRequest', service_name:'str') -> 'HttpResponse':
    return invoke_action_handler(req, 'zato.service.ide.get-service', extra={'service_name': service_name})

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_file(req:'HttpRequest', fs_location:'str') -> 'HttpResponse':

    if not fs_location:
        raise Exception(f'FS location missing on input to get_file "{repr(fs_location)}"')

    return invoke_action_handler(req, 'zato.service.ide.get-file', extra={'fs_location': fs_location})

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def create_file(req:'HttpRequest') -> 'HttpResponse':

    file_name = req.POST['file_name']
    root_directory = req.POST['root_directory']

    return invoke_action_handler(req, 'zato.service.ide.create-file', extra={
        'root_directory': root_directory,
        'file_name': file_name,
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def rename_file(req:'HttpRequest') -> 'HttpResponse':

    root_directory = req.POST['root_directory']
    current_file_name = req.POST['current_file_name']
    new_file_name = req.POST['new_file_name']

    return invoke_action_handler(req, 'zato.service.ide.rename-file', extra={
        'root_directory': root_directory,
        'current_file_name': current_file_name,
        'new_file_name': new_file_name,
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def delete_file(req:'HttpRequest') -> 'HttpResponse':
    fs_location = req.POST['fs_location']
    return invoke_action_handler(req, 'zato.service.ide.delete-file', extra={
        'fs_location': fs_location,
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_file_list(req:'HttpRequest') -> 'HttpResponse':
    return invoke_action_handler(req, 'zato.service.ide.get-file-list')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def get_service_list(req:'HttpRequest') -> 'HttpResponse':

    fs_location = req.GET['fs_location']
    should_wait_for_services = req.GET.get('should_wait_for_services')
    should_convert_pickup_to_work_dir = req.GET.get('should_convert_pickup_to_work_dir')

    return invoke_action_handler(req, 'zato.service.ide.service-ide', extra={
        'fs_location': fs_location,
        'should_wait_for_services': should_wait_for_services,
        'should_convert_pickup_to_work_dir': should_convert_pickup_to_work_dir,
    })

# ################################################################################################################################
# ################################################################################################################################
