# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.query.cassandra import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import CassandraQuery

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'query-cassandra'
    template = 'zato/query/cassandra.html'
    service_name = 'zato.query.cassandra.get-list'
    output_class = CassandraQuery

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'value')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'value')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the Cassandra query [{}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'query-cassandra-create'
    service_name = 'zato.query.cassandra.create'

class Edit(_CreateEdit):
    url_name = 'query-cassandra-edit'
    form_prefix = 'edit-'
    service_name = 'zato.query.cassandra.edit'

class Delete(_Delete):
    url_name = 'query-cassandra-delete'
    error_message = 'Could not delete the Cassandra query'
    service_name = 'zato.query.cassandra.delete'
