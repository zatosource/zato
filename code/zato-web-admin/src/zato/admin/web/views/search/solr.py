# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.search.solr import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common import SEARCH
from zato.common.odb.model import Solr

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'search-solr'
    template = 'zato/search/solr.html'
    service_name = 'zato.search.solr.get-list'
    output_class = Solr

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'timeout', 'ping_path', 'options')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'default_timeout': SEARCH.SOLR.DEFAULTS.TIMEOUT.value,
            'default_ping_path': SEARCH.SOLR.DEFAULTS.PING_PATH.value,
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'address', 'timeout', 'ping_path', 'options')
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
