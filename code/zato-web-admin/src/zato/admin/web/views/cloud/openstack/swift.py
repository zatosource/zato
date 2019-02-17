# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.cloud.openstack.swift import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import OpenStackSwift

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cloud-openstack-swift'
    template = 'zato/cloud/openstack/swift.html'
    service_name = 'zato.cloud.openstack.swift.get-list'
    output_class = OpenStackSwift
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = (
            'id', 'name', 'is_active', 'auth_url', 'retries', 'starting_backoff', 'max_backoff', 'auth_version', 'key', 'pool_size')
        output_optional = (
            'user', 'is_snet', 'tenant_name', 'should_validate_cert', 'cacert', 'should_retr_ratelimit', 'needs_tls_compr',
            'custom_options')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('cluster_id', 'name', 'is_active', 'auth_url', 'retries', 'starting_backoff', 'max_backoff',
           'auth_version', 'key', 'user', 'is_snet', 'tenant_name', 'should_validate_cert', 'cacert', 'should_retr_ratelimit',
           'needs_tls_compr', 'custom_options', 'pool_size')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {0} the OpenStack Swift connection [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'cloud-openstack-swift-create'
    service_name = 'zato.cloud.openstack.swift.create'

class Edit(_CreateEdit):
    url_name = 'cloud-openstack-swift-edit'
    form_prefix = 'edit-'
    service_name = 'zato.cloud.openstack.swift.edit'

class Delete(_Delete):
    url_name = 'cloud-openstack-swift-delete'
    error_message = 'Could not delete the OpenStack Swift connection'
    service_name = 'zato.cloud.openstack.swift.delete'
