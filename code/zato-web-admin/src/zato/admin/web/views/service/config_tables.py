# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads
from logging import getLogger
from traceback import format_exc

# Django
from django.http import HttpResponse
from django.http.response import HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_template_name = 'zato/service/config-tables.html'

# A file bigger than this is worked on outside the dashboard - downloaded and changed
# in your own tools - rather than in the browser, so the server does not even send it here.
_max_editable_size = 256 * 1024

# The services the page reads the files through and writes them back with
_service_get_list = 'zato.user-conf.get-list'
_service_save = 'zato.user-conf.save'
_service_create = 'zato.user-conf.create'
_service_rename = 'zato.user-conf.rename'
_service_delete = 'zato.user-conf.delete'

# What each action the page takes invokes
_action_service = {
    'save': _service_save,
    'add': _service_create,
    'upload': _service_create,
    'rename': _service_rename,
    'delete': _service_delete,
}

# ################################################################################################################################
# ################################################################################################################################

def _json_response(data:'anydict', is_ok:'bool'=True) -> 'HttpResponse':

    payload = dumps(data).encode('utf-8')
    response_class = HttpResponse if is_ok else HttpResponseServerError

    out = response_class(payload, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The config files of the current cluster - one is picked at a time and everything
    about it reads off its own line.
    """
    table_list:'anylist' = []
    directory_list:'anylist' = []
    error = ''

    try:
        response = req.zato.client.invoke(_service_get_list, {'max_size': _max_editable_size})

        if response.ok:
            table_list = response.data['file_list']
            directory_list = response.data['directory_list']
        else:
            error = response.details
            logger.error('Config tables: could not read the files: %s', response.details)

    except Exception as e:
        error = str(e)
        logger.error('Config tables: could not read the files: %s', format_exc())

    # The header says where the files are, which is the first directory the server reads them from
    if directory_list:
        user_conf_directory = directory_list[0]
    else:
        user_conf_directory = ''

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'table_list_json': dumps(table_list),
        'directory_list_json': dumps(directory_list),
        'user_conf_directory': user_conf_directory,
        'max_editable_size': _max_editable_size,
        'error': error,
        'zato_clusters': True,
        'zato_template_name': _template_name,
    }

    out = TemplateResponse(req, _template_name, return_data)
    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def persist(req:'any_') -> 'HttpResponse':
    """ One change the page has made to a file, carried out where the server reads its files from.
    """
    try:
        body = req.body.decode('utf-8')
        request_data = loads(body)

        action = request_data['action']

        if action not in _action_service:
            raise Exception(f'Unknown action `{action}`')

        service_name = _action_service[action]
        response = req.zato.client.invoke(service_name, request_data['data'])

        if response.ok:
            return _json_response({'success': True, 'data': response.data})
        else:
            return _json_response({'success': False, 'error': response.details}, False)

    except Exception as e:
        logger.error('Config tables: %s', format_exc())
        return _json_response({'success': False, 'error': str(e)}, False)

# ################################################################################################################################
# ################################################################################################################################
