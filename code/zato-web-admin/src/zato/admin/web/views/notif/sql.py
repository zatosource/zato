# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from operator import itemgetter

# Zato
from zato.admin.web.forms.notif.sql import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import NotificationSQL

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    output_class = NotificationSQL
    url_name = 'notif-sql'
    template = 'zato/notif/sql.html'
    service_name = 'zato.notif.sql.get-list'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'cluster_id', 'is_active', 'def_id', 'interval', 'query', 'service_name')
        output_repeated = True

    def handle(self):

        if self.req.zato.cluster_id:
            sql_defs = self.req.zato.client.invoke('zato.outgoing.sql.get-list', {'cluster_id':self.req.zato.cluster_id}).data
            sql_defs.sort(key=itemgetter('name'))
        else:
            sql_defs = []

        return {
            'create_form': CreateForm(sql_defs=sql_defs, req=self.req),
            'edit_form': EditForm(prefix='edit', sql_defs=sql_defs, req=self.req)
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'cluster_id', 'is_active', 'def_id', 'interval', 'query', 'service_name')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {} the SQL notification `{}`'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'notif-sql-create'
    service_name = 'zato.notif.sql.create'

class Edit(_CreateEdit):
    url_name = 'notif-sql-edit'
    form_prefix = 'edit-'
    service_name = 'zato.notif.sql.edit'

class Delete(_Delete):
    url_name = 'notif-sql-delete'
    error_message = 'Could not delete the SQL notification'
    service_name = 'zato.notif.sql.delete'
