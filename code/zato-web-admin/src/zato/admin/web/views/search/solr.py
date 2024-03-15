# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms.search.solr import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, id_only_service, Index as _Index, method_allowed
from zato.common.api import SEARCH
from zato.common.odb.model import Solr

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'search-solr'
    template = 'zato/search/solr.html'
    service_name = 'zato.search.solr.get-list'
    output_class = Solr
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'timeout', 'ping_path', 'options', 'pool_size')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'default_timeout': SEARCH.SOLR.DEFAULTS.TIMEOUT,
            'default_ping_path': SEARCH.SOLR.DEFAULTS.PING_PATH,
            'default_pool_size': SEARCH.SOLR.DEFAULTS.POOL_SIZE,
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'address', 'timeout', 'ping_path', 'options', 'pool_size')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the Solr connection [{}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'search-solr-create'
    service_name = 'zato.search.solr.create'

class Edit(_CreateEdit):
    url_name = 'search-solr-edit'
    form_prefix = 'edit-'
    service_name = 'zato.search.solr.edit'

class Delete(_Delete):
    url_name = 'search-solr-delete'
    error_msolrsage = 'Could not delete the Solr connection'
    service_name = 'zato.search.solr.delete'

@method_allowed('POST')
def ping(req, id, cluster_id):
    ret = id_only_service(req, 'zato.search.solr.ping', id, 'Could not ping the Solr connection, e:`{}`')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse(ret.data.info)
