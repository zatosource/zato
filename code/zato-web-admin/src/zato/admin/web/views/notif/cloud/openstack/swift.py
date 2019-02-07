# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.notif.cloud.openstack.swift import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import NotificationOpenStackSwift as NotifOSS

logger = logging.getLogger(__name__)

common_required = ('name', 'is_active', 'def_id', 'containers', 'interval', 'name_pattern', 'name_pattern_neg', 'get_data',
    'get_data_patt_neg', 'service_name')

common_optional = ('get_data_patt',)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'notif-cloud-openstack-swift'
    template = 'zato/notif/cloud/openstack/swift.html'
    service_name = 'zato.notif.cloud.openstack.swift.get-list'
    output_class = NotifOSS
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'def_name',) + common_required
        output_optional = common_optional
        output_repeated = True

    def handle(self):

        def_list = []
        if self.req.zato.cluster_id:
            service_name = 'zato.cloud.openstack.swift.get-list'
            response = self.req.zato.client.invoke(service_name, {'cluster_id':self.req.zato.cluster_id})
            if response.has_data:
                def_list = response.data

        return {
            'create_form': CreateForm(def_list, req=self.req),
            'edit_form': EditForm(def_list, prefix='edit', req=self.req),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('cluster_id',) + common_required
        input_optional = common_optional
        output_required = ('id', 'name', 'def_name')

    def success_message(self, item):
        return 'Successfully {0} the OpenStack Swift notification [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'notif-cloud-openstack-swift-create'
    service_name = 'zato.notif.cloud.openstack.swift.create'

class Edit(_CreateEdit):
    url_name = 'notif-cloud-openstack-swift-edit'
    form_prefix = 'edit-'
    service_name = 'zato.notif.cloud.openstack.swift.edit'

class Delete(_Delete):
    url_name = 'notif-cloud-openstack-swift-delete'
    error_message = 'Could not delete the OpenStack Swift notification'
    service_name = 'zato.notif.cloud.openstack.swift.delete'
