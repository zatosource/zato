# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import bz2
import logging
from base64 import b64encode
from datetime import datetime
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.json_internal import dumps
from zato.common.util.api import current_host, translation_name

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode

logger = logging.getLogger(__name__)

@method_allowed('GET')
def index(req):
    return_data = {
        'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'search_form':req.zato.search_form,
    }

    return TemplateResponse(req, 'zato/kvdb/data_dict/impexp.html', return_data)

@method_allowed('POST')
def import_(req, cluster_id):
    try:
        data = req.read()
        if isinstance(data, unicode):
            data = data.encode('utf8')

        bz2.decompress(data) # A preliminary check to weed out files obviously incorrect
        req.zato.client.invoke('zato.kvdb.data-dict.impexp.import', {'data':b64encode(data)})
    except Exception:
        msg = 'Could not import the data dictionaries, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        return HttpResponse(dumps({'success': True}))

@method_allowed('GET')
def export(req, cluster_id):

    def _get_last_id(service):
        response = req.zato.client.invoke(service, {})
        if response.data:
            return response.data.value

    def _get_last_dict_id():
        return _get_last_id('zato.kvdb.data-dict.dictionary.get-last-id')

    def _get_last_translation_id():
        return _get_last_id('zato.kvdb.data-dict.translation.get-last-id')

    def _get_dict_list():
        for item in req.zato.client.invoke('zato.kvdb.data-dict.dictionary.get-list', {}):
            yield item.id, item.system, item.key, item.value

    def _get_translation_list():
        for item in req.zato.client.invoke('zato.kvdb.data-dict.translation.get-list', {}):
            yield item.id, item.system1, item.key1, item.value1, item.system2, \
                  item.key2, item.value2, item.id1, item.id2

    return_data = {'meta': {'current_host':current_host(), 'timestamp_utc':datetime.utcnow().isoformat(), 'user':req.user.username}}
    return_data['data'] = {'dict_list':[], 'translation_list':[]}

    return_data['data']['last_dict_id'] = _get_last_dict_id()
    return_data['data']['last_translation_id'] = _get_last_translation_id()

    for id, system, key, value in _get_dict_list():
        return_data['data']['dict_list'].append({'id':id, 'system':system, 'key':key, 'value':value})

    for id, system1, key1, value1, system2, key2, value2, id1, id2 in _get_translation_list():
        return_data['data']['translation_list'].append(
            {translation_name(system1, key1, value1, system2, key2): {'id':id, 'value2':value2, 'id1':id1, 'id2':id2}})

    data = dumps(return_data, indent=4)
    if isinstance(data, unicode):
        data = data.encode('utf8')

    data = bz2.compress(data)

    response = HttpResponse(data, content_type='application/x-bzip2')
    response['Content-Disposition'] = 'attachment; filename={}'.format('zato-data-dict-export.json.bz2')

    return response
