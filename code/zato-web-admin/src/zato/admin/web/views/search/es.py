# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.search.es import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.api import SEARCH
from zato.common.odb.model import ElasticSearch

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'search-es'
    template = 'zato/search/es.html'
    service_name = 'zato.search.es.get-list'
    output_class = ElasticSearch
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'hosts', 'timeout', 'body_as')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'default_timeout': 90,
            'default_body_as': SEARCH.ES.DEFAULTS.BODY_AS
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'hosts', 'timeout', 'body_as')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the ElasticSearch connection [{}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'search-es-create'
    service_name = 'zato.search.es.create'

class Edit(_CreateEdit):
    url_name = 'search-es-edit'
    form_prefix = 'edit-'
    service_name = 'zato.search.es.edit'

class Delete(_Delete):
    url_name = 'search-es-delete'
    error_message = 'Could not delete the ElasticSearch connection'
    service_name = 'zato.search.es.delete'
