# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import re

# Django
from django.http import JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import BaseCallView, invoke_action_handler, method_allowed
from zato.common.fhir.display import parse_and_render as fhir_parse_and_render
from zato.common.hl7.grid import parse_and_build as hl7_parse_and_build

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest, HttpResponse
    from zato.common.typing_ import any_, anylist, stranydict, strlist
    anylist = anylist
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# What an ER7 segment line looks like - a three-character segment id followed by the field separator,
# any segment counts because a payload may be a fragment that does not start with MSH.
_er7_segment_prefix = re.compile('^[A-Z][A-Z0-9]{2}\\|')

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

def _json_parse_and_render(data:'str') -> 'str':
    """ Renders a JSON payload pretty-printed - a payload that is not JSON renders as an empty string.
    """
    try:
        parsed = json.loads(data)
    except Exception:
        return ''

    out = json.dumps(parsed, indent=2)
    return out

# ################################################################################################################################

def _key_value_parse_and_render(data:'str') -> 'str':
    """ Renders key=value lines as an aligned key: value list -
    a payload without any such line renders as an empty string.
    """
    lines:'strlist' = []

    for line in data.splitlines():
        if '=' not in line:
            continue
        name, _, value = line.partition('=')
        name = name.strip()
        value = value.strip()
        lines.append(f'{name}: {value}')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def _key_value_build_tree(data:'str') -> 'anylist':
    """ Builds grid view nodes out of key=value lines - one leaf per line.
    """
    out:'anylist' = []

    for line in data.splitlines():

        if '=' not in line:
            continue

        name, _, value = line.partition('=')
        name = name.strip()
        value = value.strip()

        node = {'name': name, 'value': value, 'kind': 'element', 'children': []}
        out.append(node)

    return out

# ################################################################################################################################

def _build_json_views(data:'str') -> 'stranydict':
    """ JSON renders as pretty-printed text only - its grid view
    is built in the browser without a round trip.
    """
    parsed_text = _json_parse_and_render(data)

    out = {'parsed_text': parsed_text, 'parsed_tree': []}
    return out

# ################################################################################################################################

def _build_key_value_views(data:'str') -> 'stranydict':
    """ Builds both views of key=value lines.
    """
    parsed_text = _key_value_parse_and_render(data)
    parsed_tree = _key_value_build_tree(data)

    out = {'parsed_text': parsed_text, 'parsed_tree': parsed_tree}
    return out

# ################################################################################################################################

def _build_fhir_views(data:'str') -> 'stranydict':
    """ FHIR renders as text only - its payloads are JSON,
    so the browser builds the grid view on its own.
    """
    parsed_text = fhir_parse_and_render(data)

    out = {'parsed_text': parsed_text, 'parsed_tree': []}
    return out

# ################################################################################################################################

def _build_auto_views(data:'str') -> 'stranydict':
    """ Builds the views of a payload the same way the direct invoke's auto mode treats it -
    a payload opening with an ER7 segment line means HL7 v2, a first line with =
    means key=value, anything else is tried as JSON.
    """

    # HL7 first because its lines never carry a leading = and JSON never opens with a segment id
    stripped = data.lstrip()

    if _er7_segment_prefix.match(stripped):
        out = hl7_parse_and_build(data)
        return out

    parts = data.split('\n', 1)
    first_line = parts[0]

    if '=' in first_line:
        out = _build_key_value_views(data)
    else:
        out = _build_json_views(data)

    return out

# ################################################################################################################################

# Per-format view builders - each returns an empty parsed_text when the payload does not parse
_payload_view_builders = {
    'auto': _build_auto_views,
    'json': _build_json_views,
    'key-value': _build_key_value_views,
    'hl7-v2': hl7_parse_and_build,
    'fhir': _build_fhir_views,
}

@method_allowed('POST')
def parse_payload(req:'HttpRequest') -> 'JsonResponse':
    """ Renders the parsed views of a payload for the IDE's request and response panes -
    parsing happens right here in the Django process, the same way the audit-log browser does it.
    """
    body = json.loads(req.body)

    data = body['data']
    data_format = body['data_format']

    builder = _payload_view_builders[data_format]
    views = builder(data)

    out = JsonResponse(views)
    return out

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
